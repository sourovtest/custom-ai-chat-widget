# Bongora Widget Integration

## Script snippet

```html
<script
  src="https://your-bongora-host.example/frontend/widget.js"
  data-api-url="https://api.bongora.example"
  defer
></script>
```

## Requirements

- Serve `frontend/widget.js` over HTTPS.
- Serve the API over HTTPS.
- Add the exact production website origin to `CORS_ALLOWED_ORIGINS`.
- Set MySQL credentials, `ADMIN_API_KEY`, and an optional approved AI provider key.
- Never place the API key or `ADMIN_API_KEY` in the integration snippet or widget source.

## Deployment

1. Back up MySQL and apply `database/schema.sql` through the reviewed migration process.
2. Copy `backend/.env.example` to `backend/.env` and populate production values.
3. Install `backend/requirements.txt`.
4. Start FastAPI behind a reverse proxy or application platform with HTTPS.
5. Deploy `frontend/widget.js` and verify the script version is cached safely.
6. Verify `/health`, a test chat session, and one known active rule.

## Troubleshooting

- `offline` status: verify API health, HTTPS certificates, CORS origin, and DNS.
- `401`: configure `ADMIN_API_KEY` and send `X-Admin-Key` for `/api/rules` CRUD routes.
- `503`: verify MySQL connectivity or provider fallback configuration.
- `429`: the API is applying its in-memory 60-request-per-minute IP limit.
- Session not restoring: verify UUID v4 storage and that host storage is not disabled.

## Recovery

- Restore from a verified database backup before replaying missed chat records.
- Revert to the previous `widget.js` file and API deployment if a release fails.
- Rotate any exposed credentials immediately and restart the application.
