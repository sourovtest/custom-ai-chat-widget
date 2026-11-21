# Bongora Final Local QA Report

Date: 2026-11-21

## Verified Results

- Full pytest suite: 22 tests passed.
- Live Gemini model: `gemini-3.1-flash-lite`.
- Live widget-to-FastAPI-to-MySQL chat flow passed.
- Live session and customer/assistant message persistence passed.
- OpenAI exhausted-credit HTTP 429 was verified; the credential was removed from `backend/.env`.
- Rule browser QA passed for URL, timed, and first-visit static rules.
- Desktop, tablet, mobile, Shadow DOM isolation, CLS, and console/page-error checks passed.
- SQL injection data handling, strict payload validation, CORS, prompt-injection prompts, and admin authorization tests passed.
- 300 consecutive health requests produced no functional failures.
- Backend working set changed by 128 KB during the health-load test, with no evidence of abnormal growth.
- MySQL dump and isolated restore passed:
  - 3 tables restored.
  - 21 sessions restored.
  - 170 chat messages restored.
- FastAPI was stopped and restarted; health returned `ok`, database `ok`, and provider `gemini`.

## Remaining External Blockers

- HTTPS certificate/domain verification requires production or staging infrastructure.
- The external staging website was not available for end-to-end integration.
- Production conflict and deployment approval require the real Bongora host.
- Final user/organization production sign-off is pending.

## Known Limitations

- `ADMIN_API_KEY` is stored locally and must be rotated for deployment.
- MySQL currently uses local development credentials and must use a least-privilege production account.
- OpenAI integration is configured but inactive until valid API credits are supplied.
- In-memory rate limiting is process-local and should be replaced with a shared limiter for multi-instance deployment.

## Handoff State

The project is locally production-baseline ready. The remaining items are deployment environment verification and production authorization, not unresolved local code QA.
