FROM python:3.11-slim as base
ENV ENV_FILE=../.env.production \
    ENVIRONMENT=PRODUCTION \
    OPENAI_API_KEY='' \
    LANGCHAIN_API_KEY='' \
    LANGCHAIN_ENDPOINT='' \
    LANGCHAIN_TRACING_V2='' \
    APPLICATIONINSIGHTS_CONNECTION_STRING='' \
    ENABLE_LANGSMITH_TRACING='' \
    LANGSMITH_PROJECT_NAME='' \
    LANGGRAPH_RECURSION_LIMIT=5 \
    INTERNAL_DATABASE_USER='' \
    INTERNAL_DATABASE_PASSWORD='' \
    INTERNAL_DATABASE_HOST='' \
    INTERNAL_DATABASE_PORT=5432 \
    INTERNAL_DATABASE_DATABASE='' \
    INTERNAL_DATABASE_SCHEMA='' \
    VECTOR_DB_HOST='' \
    VECTOR_DB_PORT=6333 \
    VECTOR_DB_NAME='' \
    VECTOR_DB_API_KEY='' \
    LLIMEADE_API_KEY='' \
    COHERE_API_KEY='' \
    UNSTRUCTURED_API_KEY='' \
    UNSTRUCTURED_BASE_URL='' \
    ENVIRONMENT='' \
    TAVILY_API_KEY='' \
    AZURE_OPENAI_DEPLOYMENT_NAME='' \
    AZURE_OPENAI_API_BASE='' \
    AZURE_OPENAI_API_KEY='' \
    AZURE_OPENAI_API_VERSION='' \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
RUN apt-get update && apt-get upgrade && apt-get clean

FROM base as builder
WORKDIR /app
RUN if [ -f "$ENV_FILE" ]; then set -a && . "$ENV_FILE" && set +a; fi
COPY pyproject.toml poetry.lock /app/
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.in-project true \
    && poetry install --without dev --no-root

FROM base as runner
WORKDIR /app
COPY --from=builder /app /app
COPY . /app
EXPOSE 9000
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
