FROM python:3.11-slim

WORKDIR /app

# System deps (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY services /app/services

RUN poetry config virtualenvs.create false \
 && poetry install --only main --no-interaction --no-ansi

ENV PYTHONPATH=/app/src

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
