# Bongora Standalone AI Chatbot

A standalone chatbot widget and API for Bongora, built with Vanilla JavaScript, FastAPI, and MySQL.

For step-by-step Bengali instructions for chat users and administrators, see [USER_MANUAL.md](./USER_MANUAL.md).
For AI-assisted continuation and integration with other websites, see [AI_HANDOVER.md](./AI_HANDOVER.md).

## Quick Start (3 Steps)

Requirements: Python 3.10+, MySQL 8+, and an API key for Gemini or OpenAI (or use the built-in fallback).

### 1. Clone and install

```powershell
git clone <repository-url> chatbot
cd chatbot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

### 2. Configure the environment and database

```powershell
Copy-Item backend\.env.example backend\.env
```

Edit `backend/.env`: set `BRAND_NAME`, `ALLOWED_ORIGINS`, `MYSQL_*`, `AI_PROVIDER`, and `AI_API_KEY`. Create the database and tables:

```powershell
mysql -u <database-user> -p -e "CREATE DATABASE chatbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
Get-Content database\schema.sql | mysql -u <database-user> -p chatbot
```

Use a least-privilege MySQL account. Never commit `.env` or paste API keys into a public issue.

### 3. Start the API

```powershell
uvicorn backend.main:app --reload
```

The API and embeddable script are available at `http://127.0.0.1:8000` and `http://127.0.0.1:8000/widget.js`. Health check: `http://127.0.0.1:8000/health`.

### One-click start on Windows

After configuring `backend/.env` and creating the database, double-click **Start Chatbot.bat** in the project folder. On its first run it creates `.venv` and installs the backend dependencies, starts the API, and opens the local chat preview at `http://127.0.0.1:8000/`. If `backend/.env` is missing, it creates the file from the example and asks you to configure it before starting again. Keep the **Bongora Chatbot Server** window open while chatting; close it to stop the server.

## 1-Snippet Website Integration

Host the API on a public HTTPS URL, then copy this snippet into the website page before `</body>`. Replace the URL, brand, color, and role. `ALLOWED_ORIGINS` in the API environment must include the website's exact origin.

```html
<script>
  window.ChatbotConfig = {
    apiUrl: "https://your-chatbot-api.com",
    brandName: "Your Brand",
    primaryColor: "#111827",
    welcomeMessage: "Hello! How can we help you today?",
    defaultRole: "sales"
  };
</script>
<script src="https://your-chatbot-api.com/widget.js" defer></script>
```

Supported `defaultRole` values are `sales`, `support`, `faq`, and `vendor`. The global configuration is optional; equivalent `data-api-url`, `data-brand-name`, `data-primary-color`, `data-welcome-message`, and `data-default-role` attributes can be set on the widget script. If `apiUrl` is omitted, the widget uses the script's origin.

The widget is served by FastAPI directly, so a separate static host is not needed. Serve both the API and widget over HTTPS in production.

## Widget browser QA

Install the isolated QA dependencies and Chromium from the project root:

```powershell
python -m venv .qa-venv
.\.qa-venv\Scripts\python.exe -m pip install -r tests\requirements-qa.txt
$env:PLAYWRIGHT_BROWSERS_PATH = (Join-Path (Get-Location) ".playwright-browsers")
.\.qa-venv\Scripts\python.exe -m playwright install chromium
.\.qa-venv\Scripts\python.exe tests\playwright_widget_qa.py
```

The isolated browser test serves `index.html` locally and mocks the chat API for deterministic widget QA; it does not contact external services.

## Configuration

`backend/.env.example` documents supported settings. `ALLOWED_ORIGINS` accepts a comma-separated list of exact browser origins (the legacy `CORS_ALLOWED_ORIGINS` name is also supported). Do not commit `backend/.env` or real credentials.

## API

- `GET /health` — liveness check.
- `GET /widget.js` — the embeddable browser widget script.
- `POST /api/chat/session` — create or restore a chat session.
- `POST /api/chat/send` — validate a customer message, persist it, and return a chat reply with the last five context messages.
- `GET /api/chat/sessions/{session_token}/messages` — retrieve stored conversation history.

Session and message endpoints require a UUID v4 session token. Database writes use parameterized MySQL queries. Chat storage failures return HTTP 503 without exposing database details.

## AI provider configuration

Set `AI_PROVIDER=fallback`, `gemini`, or `openai`. Set `AI_API_KEY` to the key for the selected provider and optionally configure `AI_MODEL`, `AI_TIMEOUT_SECONDS`, and `AI_MAX_RETRIES`. Legacy `GEMINI_API_KEY` and `OPENAI_API_KEY` variables remain supported. Without a provider or when a provider request fails, the API uses its deterministic fallback and never fabricates prices, stock, delivery, or order status.

## Admin rules

Start the local server, then open `http://127.0.0.1:8000/admin`. Enter the `ADMIN_API_KEY` from `backend/.env`. The Admin Panel creates, edits, activates, deactivates, and deletes validated rules. Public widget delivery exposes only active rules; CRUD operations require `X-Admin-Key`.
