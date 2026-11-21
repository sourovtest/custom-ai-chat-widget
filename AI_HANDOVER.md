# AI Handover: Reusable Chatbot

This document gives a future AI or developer enough context to continue work and integrate the chatbot with another website. It describes the current implementation and its limits; it does not authorize deployment or deferred feature work.

## Read First

1. `AUTONOMOUS_AI_INSTRUCTIONS.md` — project rules, security requirements, and deferred inquiry-reporting requirements.
2. `PROJECT_PROGRESS.md` — verified status, QA evidence, blockers, and next authorized action.
3. `README.md` — setup, configuration, API, and embed example.
4. `INTEGRATION_GUIDE.md` — production deployment and troubleshooting.
5. `FINAL_QA_REPORT.md` and `SECURITY_AUDIT_REPORT.md` — previously recorded local evidence and limitations.

## Current Architecture

- Widget: `frontend/widget.js`, vanilla JavaScript, Shadow DOM, and browser `localStorage` session persistence.
- API: FastAPI in `backend/main.py`; chatbot requests and rules use JSON endpoints.
- Storage: MySQL chat sessions, messages, and chatbot rules. The current schema has no product catalog, customer account, seller account, or inquiry-ticket tables.
- Admin Panel: `admin/index.html`, served locally at `http://127.0.0.1:8000/admin`; it currently manages chatbot rules, not customer reports.
- Windows local startup: double-click `Start Chatbot.bat`. It starts the local API and opens the preview. The API listens on loopback; this is not a production hosting setup.

## Integrate With Another Website

The widget can be embedded on a website independently of its frontend framework. The backend still needs a reachable API, configured database, and a production HTTPS deployment for persistent API-backed chat.

1. Deploy this project's FastAPI backend and MySQL database to an approved host. Put credentials in that host's environment configuration; do not put them in website HTML or JavaScript.
2. Configure `BRAND_NAME`, `MYSQL_*`, the selected AI provider and its key, `ADMIN_API_KEY`, and `ALLOWED_ORIGINS` in the backend environment. Add the exact website origin, such as `https://shop.example`, to `ALLOWED_ORIGINS`; do not use `*`.
3. Serve the backend over HTTPS. FastAPI serves the widget at `/widget.js`; no separate widget file host is required.
4. Add this snippet to the target website, normally before `</body>`, and replace the example values:

```html
<script>
  window.ChatbotConfig = {
    apiUrl: "https://your-chatbot-api.example",
    brandName: "Your Store",
    primaryColor: "#174b3e",
    welcomeMessage: "How can we help?",
    defaultRole: "support"
  };
</script>
<script src="https://your-chatbot-api.example/widget.js" defer></script>
```

5. Verify the target origin is allowed by CORS, both website and API use HTTPS, and any host Content Security Policy permits loading the API's script and connecting to its API origin. Then test open/close, a chat request, reload/session restore, mobile layout, and browser console/network errors on staging.

Supported `defaultRole` values are `sales`, `support`, `faq`, and `vendor`. The global configuration is optional; the widget script also accepts `data-api-url`, `data-brand-name`, `data-primary-color`, `data-welcome-message`, and `data-default-role` attributes. If `apiUrl` is omitted, the widget derives the API origin from the script URL. Never include AI keys, `ADMIN_API_KEY`, database credentials, or customer auth tokens in the snippet.

### Website-specific integration boundary

Generic embedding does not automatically connect the chatbot to a site's login, product catalog, seller records, order system, or authorization. Product recommendations and sales-role routing exist, but verified product existence, live price, and stock require a separately designed trusted catalog integration. Inspect the target website's API, authentication, CORS/CSP, and data model before implementing such connections; do not guess schemas or trust IDs supplied only by the browser.

## Deferred Customer Inquiry Reporting

The user requested that future work:

- Associate logged-in conversations with a customer ID/name from server-verified website authentication.
- Link product-specific inquiries to canonical product and seller IDs from a trusted catalog.
- Give the main administrator one clear inbox for all inquiries.
- Let a seller see only inquiries for products that seller owns, enforced by server-side authorization.
- Preserve anonymous chat, minimize personal data, and test identity, association, and access boundaries.

This requirement is documented in `AUTONOMOUS_AI_INSTRUCTIONS.md` but is **not implemented**. Begin only after explicit user authorization and inspection of the real website's authentication and catalog interfaces. The current Admin Panel has no inquiry inbox or notifications.

## Remaining Work and Known Boundaries

Use the current `PROJECT_PROGRESS.md` as the status source. Phase 5 remains incomplete pending external deployment and final approval. Recorded outstanding work includes:

- Deploy to approved HTTPS infrastructure and verify on a real staging website.
- Test integration against the actual host's CSS, CSP, CORS, authentication, and mobile behavior.
- Obtain approval before production integration.
- Replace in-memory rate limiting if a multi-instance production deployment requires shared limits.
- Use a least-privilege production MySQL account and verify production secrets and recovery procedures.
- Complete final sign-off only after evidence and user approval.
- Implement deferred product/customer inquiry reporting only when authorized and after the host interfaces are understood.

Do not claim production readiness, live catalog support, customer identity integration, seller authorization, or inquiry reporting unless each has been implemented and verified.

## Local Verification

From the repository root on Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
$env:PLAYWRIGHT_BROWSERS_PATH = (Join-Path (Get-Location) ".playwright-browsers")
.\.qa-venv\Scripts\python.exe tests\playwright_widget_qa.py
```

The browser suite uses mocked chat API requests for deterministic widget testing; it is not proof of a real website integration. Check `PROJECT_PROGRESS.md` for the latest verified counts and caveats before reporting QA status.

## Change and Publish Safely

- Work on one explicitly authorized milestone at a time; inspect the target website before any production integration.
- Update `PROJECT_PROGRESS.md` only with verified results. Do not mark deferred items complete.
- Keep `.env`, API keys, database passwords, and administrator keys out of Git and all handover documents. Verify ignored environment files before staging.
- Run the relevant tests and `git diff --check`; review staged paths before committing or pushing.
