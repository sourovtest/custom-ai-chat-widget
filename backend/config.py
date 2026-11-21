import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))


def _read_origins() -> tuple[str, ...]:
    configured_origins = os.getenv("ALLOWED_ORIGINS")
    if configured_origins is None:
        configured_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    origins = tuple(
        origin.strip().rstrip("/")
        for origin in configured_origins.split(",")
        if origin.strip()
    )
    if "*" in origins:
        raise ValueError("ALLOWED_ORIGINS must list explicit origins, not '*'.")
    return origins


@dataclass(frozen=True)
class Settings:
    cors_allowed_origins: tuple[str, ...]
    brand_name: str
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str
    gemini_api_key: str
    openai_api_key: str
    ai_provider: str
    ai_model: str
    ai_timeout_seconds: float
    ai_max_retries: int
    admin_api_key: str


def _load_settings() -> Settings:
    mysql_port = int(os.getenv("MYSQL_PORT", "3306"))
    if not 1 <= mysql_port <= 65535:
        raise ValueError("MYSQL_PORT must be between 1 and 65535.")
    ai_timeout_seconds = float(os.getenv("AI_TIMEOUT_SECONDS", "10"))
    if not 1 <= ai_timeout_seconds <= 60:
        raise ValueError("AI_TIMEOUT_SECONDS must be between 1 and 60.")
    ai_max_retries = int(os.getenv("AI_MAX_RETRIES", "1"))
    if not 0 <= ai_max_retries <= 3:
        raise ValueError("AI_MAX_RETRIES must be between 0 and 3.")
    ai_provider = os.getenv("AI_PROVIDER", "fallback").strip().lower()
    if ai_provider not in {"fallback", "gemini", "openai"}:
        raise ValueError("AI_PROVIDER must be fallback, gemini, or openai.")
    shared_api_key = os.getenv("AI_API_KEY", "").strip()
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if ai_provider == "gemini":
        gemini_api_key = gemini_api_key or shared_api_key
    elif ai_provider == "openai":
        openai_api_key = openai_api_key or shared_api_key

    return Settings(
        cors_allowed_origins=_read_origins(),
        brand_name=os.getenv("BRAND_NAME", "Support").strip() or "Support",
        mysql_host=os.getenv("MYSQL_HOST", "127.0.0.1").strip(),
        mysql_port=mysql_port,
        mysql_user=os.getenv("MYSQL_USER", "").strip(),
        mysql_password=os.getenv("MYSQL_PASSWORD", ""),
        mysql_database=os.getenv("MYSQL_DATABASE", "").strip(),
        gemini_api_key=gemini_api_key,
        openai_api_key=openai_api_key,
        ai_provider=ai_provider,
        ai_model=os.getenv("AI_MODEL", "").strip(),
        ai_timeout_seconds=ai_timeout_seconds,
        ai_max_retries=ai_max_retries,
        admin_api_key=os.getenv("ADMIN_API_KEY", "").strip(),
    )


settings = _load_settings()
