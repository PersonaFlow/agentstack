"""
configuration.py
----------

This module is responsible for managing configuration settings for the Backend API.

"""
import os
import sys
import enum
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ValidationError
import structlog
from typing import Optional

logger = structlog.get_logger()


class EnvironmentEnum(enum.Enum):
    LOCAL = "LOCAL"
    DEVELOPMENT = "DEVELOPMENT"
    STAGE = "STAGE"
    PRODUCTION = "PRODUCTION"


class LogLevelEnum(enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# We load env variables here to allow for db migration scripts to run
# If we have the `ENVIRONMENT`variable already, we are running in Docker or Kubernetes
# and do not need to load the.env file
environment = os.getenv("ENVIRONMENT")
if not environment:
    env_path = "../../../.env.local"
    load_dotenv(env_path)


class Settings(BaseSettings):
    class Config:
        case_sensitive = True

    TITLE: str = "PersonaFlow"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "PersonaFlow API"
    ENVIRONMENT: EnvironmentEnum = os.getenv("ENVIRONMENT", "PRODUCTION")
    LOG_LEVEL: LogLevelEnum = (
        LogLevelEnum.DEBUG
        if ENVIRONMENT == EnvironmentEnum.LOCAL
        else LogLevelEnum.ERROR
    )

    BASE_DIR: Path = Path(__file__).parents[2]
    APP_DIR: Path = BASE_DIR.joinpath("stack")
    FILE_DATA_DIRECTORY: Path = BASE_DIR.parent.joinpath("file_data")
    PATCH_DIR: Path = BASE_DIR.parent.joinpath("patches")

    # Auth
    JWT_ISSUER: Optional[str] = os.getenv("JWT_ISSUER", None)
    JWT_ALGORITHM: Optional[str] = os.getenv("JWT_ALGORITHM", "HS256")
    AUTH_SECRET_KEY: Optional[str] = os.getenv("AUTH_SECRET_KEY", None)
    TOKEN_EXPIRY_HOURS: Optional[int] = os.getenv("TOKEN_EXPIRY_HOURS", 24)


    # Required if you intend to use reranking functionality to query documents
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY", None)
    MIXTRAL_FIREWORKS_API_KEY: Optional[str] = os.getenv(
        "MIXTRAL_FIREWORKS_API_KEY", None
    )

    # Used for processing of unstructured documents to be ingested into vector db
    # "semantic" splitting method will not work without these
    UNSTRUCTURED_API_KEY: str = os.getenv("UNSTRUCTURED_API_KEY", "")
    UNSTRUCTURED_BASE_URL: str = os.getenv(
        "UNSTRUCTURED_BASE_URL", "http://localhost:8000"
    )

    # If using openai
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)

    # Tavily external search service api key - used for assistant external search tool (Optional)
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY", None)

    # Number of iterations assistant is allowed to run to accomplish task or improve results or response (Required)
    LANGGRAPH_RECURSION_LIMIT: int = os.getenv("LANGGRAPH_RECURSION_LIMIT", 25)

    EXCLUDE_REQUEST_LOG_ENDPOINTS: list[str] = ["/docs"]

    # Defaults to 25mb
    MAX_FILE_UPLOAD_SIZE: int = int(os.getenv("MAX_FILE_UPLOAD_SIZE", 25000000))

    # Postgres Database environment variables
    INTERNAL_DATABASE_USER: str = os.getenv("INTERNAL_DATABASE_USER", "postgres")
    INTERNAL_DATABASE_PASSWORD: str = os.getenv(
        "INTERNAL_DATABASE_PASSWORD", "postgres"
    )
    INTERNAL_DATABASE_HOST: str = os.getenv("INTERNAL_DATABASE_HOST", "localhost")
    INTERNAL_DATABASE_PORT: int = os.getenv("INTERNAL_DATABASE_PORT", 5432)
    INTERNAL_DATABASE_DATABASE: str = os.getenv(
        "INTERNAL_DATABASE_DATABASE", "internal"
    )
    INTERNAL_DATABASE_SCHEMA: str = os.getenv("INTERNAL_DATABASE_SCHEMA", "personaflow")

    @property
    def INTERNAL_DATABASE_URI(self):  # noqa
        return (
            f"postgresql+asyncpg://{self.INTERNAL_DATABASE_USER}:{self.INTERNAL_DATABASE_PASSWORD}"
            f"@{self.INTERNAL_DATABASE_HOST}:{self.INTERNAL_DATABASE_PORT}/{self.INTERNAL_DATABASE_DATABASE}"
        )

    #  LLM Configurations
    OPENAI_PROXY_URL: Optional[str] = os.getenv("OPENAI_PROXY_URL", None)
    GPT_4_MODEL_NAME: Optional[str] = os.getenv(
        "GPT_4_MODEL_NAME", "gpt-4-1106-preview"
    )
    GPT_35_MODEL_NAME: Optional[str] = os.getenv(
        "GPT_35_MODEL_NAME", "gpt-3.5-turbo-1106"
    )

    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = os.getenv(
        "AZURE_OPENAI_DEPLOYMENT_NAME", None
    )
    AZURE_OPENAI_API_BASE: Optional[str] = os.getenv("AZURE_OPENAI_API_BASE", None)
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY", None)
    AZURE_OPENAI_API_VERSION: Optional[str] = os.getenv(
        "AZURE_OPENAI_API_VERSION", None
    )

    ANTHROPIC_MODEL_NAME: Optional[str] = os.getenv(
        "ANTHROPIC_MODEL_NAME", "claude-3-haiku-20240307"
    )

    AWS_BEDROCK_REGION: Optional[str] = os.getenv("AWS_BEDROCK_REGION", "us-west-2")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID", None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY", None)
    AWS_BEDROCK_CHAT_MODEL_ID: Optional[str] = os.getenv(
        "AWS_BEDROCK_CHAT_MODEL_ID", "anthropic.claude-v2"
    )

    GOOGLE_VERTEX_MODEL: Optional[str] = os.getenv("GOOGLE_VERTEX_MODEL", "gemini-pro")

    MIXTRAL_FIREWORKS_MODEL_NAME: Optional[str] = os.getenv(
        "MIXTRAL_FIREWORKS_MODEL_NAME",
        "accounts/fireworks/models/mixtral-8x7b-instruct",
    )

    OLLAMA_MODEL: Optional[str] = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_BASE_URL: Optional[str] = os.getenv(
        "OLLAMA_BASE_URL", "http://localhost:11434"
    )
    # **** All variables below can be overriden by API parameters ****

    # Vector DB environment variables
    VECTOR_DB_API_KEY: str = os.getenv("VECTOR_DB_API_KEY", "")
    VECTOR_DB_NAME: str = os.getenv("VECTOR_DB_NAME", "qdrant")
    VECTOR_DB_HOST: str = os.getenv("VECTOR_DB_HOST", "localhost")
    VECTOR_DB_PORT: int = os.getenv("VECTOR_DB_PORT", 6333)
    VECTOR_DB_COLLECTION_NAME: str = os.getenv("VECTOR_DB_COLLECTION_NAME", "documents")
    VECTOR_DB_ENCODER_DIMENSIONS: int = os.getenv("VECTOR_DB_ENCODER_DIMENSIONS", 1536)
    VECTOR_DB_ENCODER_MODEL: str = os.getenv(
        "VECTOR_DB_ENCODER_MODEL", "text-embedding-3-small"
    )
    VECTOR_DB_ENCODER_NAME: str = os.getenv("VECTOR_DB_ENCODER_NAME", "openai")
    VECTOR_DB_DEFAULT_NAMESPACE: str = os.getenv(
        "VECTOR_DB_DEFAULT_NAMESPACE", "default"
    )

    @property
    def VECTOR_DB_CONFIG(self):
        return {
            "host": f"http://{self.VECTOR_DB_HOST}:{self.VECTOR_DB_PORT}",
            "api_key": self.VECTOR_DB_API_KEY,
        }

    DEFAULT_PARTITION_STRATEGY: str = os.getenv("DEFAULT_PARTITION_STRATEGY", "auto")
    DEFAULT_HI_RES_MODEL_NAME: str = os.getenv(
        "DEFAULT_HI_RES_MODEL_NAME", "detectron2_onnx"
    )
    PROCESS_UNSTRUCTURED_TABLES: bool = (
        True if os.getenv("PROCESS_UNSTRUCTURED_TABLES", "false") == "true" else False
    )

    DEFAULT_CHUNKING_STRATEGY: str = os.getenv("DEFAULT_CHUNKING_STRATEGY", "semantic")
    DEFAULT_SEMANTIC_CHUNK_MIN_TOKENS: int = int(
        os.getenv("DEFAULT_SEMANTIC_CHUNK_MIN_TOKENS", 30)
    )
    DEFAULT_SEMANTIC_CHUNK_MAX_TOKENS: int = int(
        os.getenv("DEFAULT_SEMANTIC_CHUNK_MAX_TOKENS", 800)
    )
    SEMANTIC_ROLLING_WINDOW_SIZE: int = int(
        os.getenv("SEMANTIC_ROLLING_WINDOW_SIZE", 1)
    )
    PREFIX_TITLES: bool = (
        False if os.getenv("PREFIX_TITLES", "true") == "false" else True
    )
    PREFIX_SUMMARY: bool = (
        False if os.getenv("PREFIX_SUMMARY", "true") == "false" else True
    )

    CREATE_SUMMARY_COLLECTION: bool = (
        True if os.getenv("CREATE_SUMMARY_COLLECTION", "false") == "true" else False
    )

    ENABLE_RERANK_BY_DEFAULT: bool = (
        True if os.getenv("ENABLE_RERANK_BY_DEFAULT", "false") == "true" else False
    )

    MAX_QUERY_TOP_K: int = int(os.getenv("MAX_QUERY_TOP_K", 5))

    # For Langsmith tracing (Optional)
    ENABLE_LANGSMITH_TRACING: bool = (
        True if os.getenv("ENABLE_LANGSMITH_TRACING", "false") == "true" else False
    )
    LANGCHAIN_API_KEY: Optional[str] = os.getenv("LANGCHAIN_API_KEY", None)
    LANGCHAIN_ENDPOINT: str = os.getenv(
        "LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"
    )
    LANGSMITH_PROJECT_NAME: str = os.getenv("LANGSMITH_PROJECT_NAME", "project")

    # Langfuse Configurations (Optional)
    ENABLE_LANGFUSE_TRACING: bool = (
        True if os.getenv("ENABLE_LANGFUSE_TRACING", "false") == "true" else False
    )
    LANGFUSE_SECRET_KEY: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY", "")
    LANGFUSE_PUBLIC_KEY: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_HOST: Optional[str] = os.getenv("LANGFUSE_HOST", "http://localhost:3000")

    ENABLE_PHOENIX_TRACING: bool = (
        True if os.getenv("ENABLE_PHOENIX_TRACING", "false") == "true" else False
    )


def get_settings() -> Settings:
    return Settings()


try:
    settings = Settings()
except ValidationError as e:
    error_messages = [err for err in e.errors()]
    logger.error(f"Settings validation error: {error_messages}")
    sys.exit(1)
