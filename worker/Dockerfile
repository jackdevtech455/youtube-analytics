FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY packages ./packages
COPY worker ./worker

WORKDIR /app/worker
RUN uv sync

CMD ["uv", "run", "python", "-m", "yta_worker.main"]
