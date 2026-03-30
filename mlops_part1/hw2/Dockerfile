FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

COPY . .

RUN uv sync --frozen

RUN useradd -m appuser && chown -R appuser:appuser /app

USER appuser

CMD ["uv", "run", "python", "app.py"]