# YouTube Tracker Analytics (Readable MVP v2)

Key improvements vs v1:
- Timezone-aware timestamps (no `utcnow`)
- `pydantic-settings` for config
- Alembic migrations (no `create_all` at startup)
- No relative imports
- More modular worker/services layout
- More descriptive names + fully-typed function signatures (excluding `self`)

## Run

```bash
cp .env.example .env
# edit YOUTUBE_API_KEY
docker compose up -d --build
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Worker scheduling (why it's a loop, not cron)
The worker is a long-running service container. This keeps scheduling + state in one place and makes logs easy:
```bash
docker compose logs -f worker
```

If you later prefer cron, you can swap the worker command to a one-shot module and trigger it with a cron container.
