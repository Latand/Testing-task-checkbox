FROM python:3.11-slim as builder

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /usr/local /usr/local

COPY . /app

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]