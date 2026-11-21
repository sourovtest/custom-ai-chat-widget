from datetime import datetime
from pathlib import Path
from uuid import uuid4
import re
import time
from collections import defaultdict, deque
import logging

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from mysql.connector.errors import Error

from .config import settings
from .chat_repository import ChatRepository
from .database import create_connection_pool
from .ai_brain import AIBrain, AIResult
from secrets import compare_digest
import json
from .rule_repository import RuleRepository

app = FastAPI(title=f"{settings.brand_name} Chatbot")

logger = logging.getLogger("bongora")

rate_windows: dict[str, deque[float]] = defaultdict(deque)
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60
MAX_RATE_LIMIT_CLIENTS = 10000


@app.middleware("http")
async def security_headers(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    for tracked_ip, tracked_window in list(rate_windows.items()):
        while tracked_window and now - tracked_window[0] > RATE_LIMIT_WINDOW_SECONDS:
            tracked_window.popleft()
        if not tracked_window:
            rate_windows.pop(tracked_ip, None)
    if client_ip not in rate_windows and len(rate_windows) >= MAX_RATE_LIMIT_CLIENTS:
        oldest_ip = min(rate_windows, key=lambda ip: rate_windows[ip][-1])
        rate_windows.pop(oldest_ip, None)
    window = rate_windows[client_ip]
    while window and now - window[0] > RATE_LIMIT_WINDOW_SECONDS:
        window.popleft()
    if len(window) >= RATE_LIMIT_REQUESTS:
        logger.warning("Rate limit reached for chat client")
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again shortly."},
        )
    window.append(now)

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Admin-Key"],
)


@app.get("/health")
def health():
    try:
        connection = create_connection_pool().get_connection()
        try:
            connection.ping(reconnect=False, attempts=1, delay=0)
        finally:
            connection.close()
        database_status = "ok"
    except (Error, RuntimeError):
        database_status = "unavailable"
    return {
        "status": "ok" if database_status == "ok" else "degraded",
        "database": database_status,
        "ai_provider": settings.ai_provider,
        "founder_guard_intent": ai_brain.detect_intent(
            f"{settings.brand_name}-এর প্রতিষ্ঠাতা কে?"
        ),
    }


@app.get("/widget.js", include_in_schema=False)
def widget_script():
    widget_path = Path(__file__).resolve().parents[1] / "frontend" / "widget.js"
    return FileResponse(
        widget_path,
        media_type="application/javascript",
        headers={"Cache-Control": "public, max-age=300"},
    )


SESSION_TOKEN_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_token: str | None = Field(default=None, max_length=128)
    message: str = Field(min_length=1, max_length=1000)
    page_path: str = Field(default="/", min_length=1, max_length=500)
    default_role: str | None = Field(default=None, max_length=64)

    @field_validator("default_role")
    @classmethod
    def validate_default_role(cls, value: str | None) -> str | None:
        if value is None:
            return None
        allowed = {
            "sales", "sales assistant",
            "support", "customer support",
            "faq", "faq assistant",
            "vendor", "vendor assistant",
            "custom ai persona",
        }
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("Unsupported default role.")
        return normalized


class SessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_token: str | None = Field(default=None, max_length=128)


class RuleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_name: str = Field(min_length=1, max_length=255)
    trigger_event: str = Field(min_length=1, max_length=255)
    action_type: str = Field(min_length=1, max_length=100)
    static_message: str | None = Field(default=None, max_length=10000)
    assigned_role: str | None = Field(default=None, max_length=255)
    trigger_config: dict[str, object] = Field(default_factory=dict)
    priority: int = Field(default=100, ge=0, le=65535)
    is_active: bool = True
    execution_frequency: str = Field(default="once_per_session", max_length=32)

    @field_validator("trigger_event")
    @classmethod
    def validate_trigger_event(cls, value: str) -> str:
        allowed = {"on_first_visit", "time_on_page", "url_match"}
        if value not in allowed:
            raise ValueError("Unsupported trigger event.")
        return value

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, value: str) -> str:
        allowed = {"Static Message", "AI Persona"}
        if value not in allowed:
            raise ValueError("Unsupported action type.")
        return value

    @field_validator("execution_frequency")
    @classmethod
    def validate_execution_frequency(cls, value: str) -> str:
        allowed = {"once", "once_per_session", "always"}
        if value not in allowed:
            raise ValueError("Unsupported execution frequency.")
        return value


def validate_session_token(value: str) -> str:
    if not SESSION_TOKEN_PATTERN.fullmatch(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session token.",
        )
    return value.lower()


repository = ChatRepository()
ai_brain = AIBrain(settings)
rule_repository = RuleRepository()


def require_admin_key(x_admin_key: str | None = Header(default=None)) -> None:
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Administrator authentication is not configured.",
        )
    if not x_admin_key or not compare_digest(x_admin_key, settings.admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Administrator authentication required.",
        )


@app.post("/api/chat/session")
def create_chat_session(payload: SessionRequest, request: Request):
    session_token = payload.session_token or str(uuid4())
    session_token = validate_session_token(session_token)
    ip_address = request.client.host if request.client else None

    try:
        session_id = repository.get_or_create_session(session_token, ip_address)
    except (Error, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat storage is temporarily unavailable.",
        )

    return {"session_token": session_token, "session_id": session_id}


@app.post("/api/chat/send")
def send_chat_message(payload: ChatRequest, request: Request):
    session_token = validate_session_token(payload.session_token or str(uuid4()))
    message = payload.message.strip()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message cannot be empty.",
        )

    try:
        ip_address = request.client.host if request.client else None
        session_id = repository.get_or_create_session(session_token, ip_address)
        context = repository.get_last_messages(session_token, limit=5)
        repository.add_message(
            session_token,
            session_id,
            "customer",
            message,
        )
        founder_intent = (
            "প্রতিষ্ঠাতা" in message
            or "founder" in message.lower()
            or "co-founder" in message.lower()
        )
        if founder_intent:
            language = ai_brain.detect_language(message)
            role = ai_brain.route_role(payload.page_path)
            sentiment = ai_brain.detect_sentiment(message)
            reply = ai_brain.fallback_reply(
                message,
                payload.page_path,
                language,
                "company_founder",
            )
            ai_result = AIResult(
                reply=reply,
                language=language,
                intent="company_founder",
                role=role,
                sentiment=sentiment,
                provider="fallback",
            )
        else:
            ai_result = ai_brain.generate_reply(
                message,
                payload.page_path,
                context,
                payload.default_role,
            )
            reply = ai_result.reply
        repository.add_message(
            session_token,
            session_id,
            "assistant",
            reply,
        )
        history = repository.get_last_messages(session_token, limit=5)
    except (Error, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service is temporarily unavailable.",
        )

    return {
        "session_token": session_token,
        "reply": reply,
        "context": history,
        "metadata": {
            "language": ai_result.language,
            "intent": ai_result.intent,
            "role": ai_result.role,
            "sentiment": ai_result.sentiment,
            "provider": ai_result.provider,
            "input_tokens": ai_result.input_tokens,
            "output_tokens": ai_result.output_tokens,
            "founder_guard_triggered": founder_intent,
        },
    }


@app.get("/api/chat/sessions/{session_token}/messages")
def get_chat_history(session_token: str):
    session_token = validate_session_token(session_token)
    try:
        rows = repository.get_history(session_token)
    except (Error, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat history is temporarily unavailable.",
        )

    messages = [
        {
            "id": int(row["id"]),
            "sender_type": str(row["sender_type"]),
            "message": str(row["message"]),
            "timestamp": row["timestamp"].isoformat()
            if isinstance(row["timestamp"], datetime)
            else str(row["timestamp"]),
        }
        for row in rows
    ]
    return {"session_token": session_token, "messages": messages}


@app.get("/api/rules")
def list_rules(x_admin_key: str | None = Header(default=None)):
    require_admin_key(x_admin_key)
    try:
        return {"rules": rule_repository.list_rules()}
    except (Error, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rule storage is temporarily unavailable.",
        )


@app.get("/api/rules/active")
def list_active_rules():
    try:
        rules = rule_repository.list_rules()
        return {
            "rules": [
                rule for rule in rules
                if rule.get("is_active") is True
            ]
        }
    except (Error, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active rules are temporarily unavailable.",
        )


@app.post("/api/rules", status_code=status.HTTP_201_CREATED)
def create_rule(payload: RuleRequest, x_admin_key: str | None = Header(default=None)):
    require_admin_key(x_admin_key)
    try:
        rule = rule_repository.create_rule(payload.model_dump())
    except (Error, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rule storage is temporarily unavailable.",
        )
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rule could not be created.",
        )
    return rule


@app.put("/api/rules/{rule_id}")
def update_rule(
    rule_id: int,
    payload: RuleRequest,
    x_admin_key: str | None = Header(default=None),
):
    require_admin_key(x_admin_key)
    if rule_id < 1:
        raise HTTPException(status_code=400, detail="Invalid rule ID.")
    try:
        rule = rule_repository.update_rule(rule_id, payload.model_dump())
    except (Error, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rule storage is temporarily unavailable.",
        )
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found.")
    return rule


@app.delete("/api/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: int, x_admin_key: str | None = Header(default=None)):
    require_admin_key(x_admin_key)
    if rule_id < 1:
        raise HTTPException(status_code=400, detail="Invalid rule ID.")
    try:
        deleted = rule_repository.delete_rule(rule_id)
    except (Error, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rule storage is temporarily unavailable.",
        )
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found.")
