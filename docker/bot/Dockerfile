FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

FROM base AS migration

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "app.database.migrate"]

FROM base AS production

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

USER appuser

CMD ["python", "-m", "app.main"]