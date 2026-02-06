FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY packages ./packages
COPY backend ./backend

WORKDIR /app/backend
RUN uv sync

EXPOSE 8000
RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
