#!/usr/bin/env sh
set -eu
cd /app/backend
uv run alembic upgrade head
exec uv run uvicorn yta_api.main:app --host 0.0.0.0 --port 8000
