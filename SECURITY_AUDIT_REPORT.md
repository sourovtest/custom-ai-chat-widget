# Bongora Local Security Audit

Date: 2026-11-21

## Passed Local Controls

- API payload fields use strict Pydantic models and reject unknown fields.
- Customer text is validated and persisted as data; SQL injection payload tests passed.
- SQL repositories use parameterized database operations.
- CORS allows only explicitly configured local origins.
- Security headers include `X-Content-Type-Options`, `Referrer-Policy`, and `X-Frame-Options`.
- Admin CRUD routes require `X-Admin-Key` and fail closed when authentication is not configured.
- Prompt-injection and fabricated founder-information guards passed.
- The widget uses Shadow DOM and safe text rendering.
- Credentials are held in `backend/.env`, which is ignored by Git.
- The exposed OpenAI key was removed after exhausted-credit verification.
- The live Gemini key and database credential remain local environment secrets and are not recorded in reports.

## Local Test Evidence

- 22 pytest tests passed.
- Live Gemini chat and MySQL persistence passed.
- Rules authorization and public active-rule delivery passed.
- 300 health requests completed without application failure.
- Database backup and isolated restore passed.

## Deployment Requirements

- Replace MySQL root credentials with a least-privilege account.
- Rotate `ADMIN_API_KEY` for production.
- Run all API and widget traffic over HTTPS.
- Configure exact production CORS origins.
- Configure secrets through a deployment secret manager or protected environment.
- Add a shared production rate limiter if running multiple application instances.
- Complete third-party penetration testing and production-domain validation before public launch.
