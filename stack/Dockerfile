FROM python:3.11-slim as base
ENV ENVIRONMENT='' \
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
    VECTOR_DB_ENCODER_DIMENSIONS=1536 \
    VECTOR_DB_ENCODER_MODEL='' \
    VECTOR_DB_DEFAULT_NAMESPACE='' \
    DEFAULT_PARTITION_STRATEGY='' \
    DEFAULT_HI_RES_MODEL_NAME='' \
    PROCESS_UNSTRUCTURED_TABLES=true \
    CREATE_SUMMARY_COLLECTION=true \
    DEFAULT_CHUNKING_STRATEGY='' \
    DEFAULT_SEMANTIC_CHUNK_MIN_TOKENS=100 \
    DEFAULT_SEMANTIC_CHUNK_MAX_TOKENS=1000 \
    SEMANTIC_ROLLING_WINDOW_SIZE=1 \
    PREFIX_TITLES=true \
    PREFIX_SUMMARY=true \
    ENABLE_RERANK_BY_DEFAULT=false \
    MAX_QUERY_TOP_K=5 \
    PERSONAFLOW_API_KEY='' \
    COHERE_API_KEY='' \
    UNSTRUCTURED_API_KEY='' \
    UNSTRUCTURED_BASE_URL='' \
    MAX_FILE_UPLOAD_SIZE=25000000 \
    ENVIRONMENT='' \
    TAVILY_API_KEY='' \
    AZURE_OPENAI_DEPLOYMENT_NAME='' \
    AZURE_OPENAI_API_BASE='' \
    AZURE_OPENAI_API_KEY='' \
    AZURE_OPENAI_API_VERSION=''

COPY stack/local.pex /bin/app

ENTRYPOINT ["/usr/local/bin/python3.11", "/bin/app"]
