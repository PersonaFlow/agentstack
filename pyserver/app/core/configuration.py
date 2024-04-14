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
    env_path = '../.env.local'
    load_dotenv(env_path)

class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        case_sensitive = True

    TITLE: str = "PersonaFlow"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "PersonaFlow API"
    ENVIRONMENT: EnvironmentEnum = os.getenv("ENVIRONMENT", "PRODUCTION")
    LOG_LEVEL: LogLevelEnum = LogLevelEnum.DEBUG if ENVIRONMENT == EnvironmentEnum.LOCAL else LogLevelEnum.ERROR

    BASE_DIR: Path = Path(__file__).parents[1]
    APP_DIR: Path = BASE_DIR.joinpath("app")
    FILE_DATA_DIRECTORY: Path = BASE_DIR.parent.joinpath("file_data")
    PATCH_DIR: Path = BASE_DIR.parent.joinpath("patches")

    # Key to be sent as x-api-key header to authenticate requests
    # WARNING: Auth disabled if not provided
    PERSONAFLOW_API_KEY: Optional[str] = os.getenv("PERSONAFLOW_API_KEY", None)

    # Required if you intend to use reranking functionality to query documents
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY", None)

    # Used for processing of unstructured documents to be ingested into vector db
    # "semantic" splitting method will not work without these
    UNSTRUCTURED_API_KEY: str = os.getenv("UNSTRUCTURED_API_KEY")
    UNSTRUCTURED_BASE_URL: str = os.getenv("UNSTRUCTURED_BASE_URL")

    # If using openai
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)

    # Tavily external search service api key - used for assistant external search tool (Optional)
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY", None)

    # For Langsmith tracing (Optional)
    ENABLE_LANGSMITH_TRACING: bool = True if os.getenv("ENABLE_LANGSMITH_TRACING", "false") == "true" else False
    LANGCHAIN_API_KEY: Optional[str] = os.getenv("LANGCHAIN_API_KEY", None)
    LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    LANGSMITH_PROJECT_NAME: str = os.getenv("LANGSMITH_PROJECT_NAME", "project")

    # Number of iterations assistant is allowed to run to accomplish task or improve results or response (Required)
    LANGGRAPH_RECURSION_LIMIT: int = os.getenv("LANGGRAPH_RECURSION_LIMIT", 5)

    # Postgres Database environment variables
    INTERNAL_DATABASE_USER: str = os.getenv("INTERNAL_DATABASE_USER", "internal")
    INTERNAL_DATABASE_PASSWORD: str = os.getenv("INTERNAL_DATABASE_PASSWORD", "internal")
    INTERNAL_DATABASE_HOST: str = os.getenv("INTERNAL_DATABASE_HOST", "localhost")
    INTERNAL_DATABASE_PORT: int = os.getenv("INTERNAL_DATABASE_PORT", 5432)
    INTERNAL_DATABASE_DATABASE: str = os.getenv("INTERNAL_DATABASE_DATABASE", "internal")
    INTERNAL_DATABASE_SCHEMA: str = os.getenv("INTERNAL_DATABASE_SCHEMA", "pyserver")

    EXCLUDE_REQUEST_LOG_ENDPOINTS: list[str] = ["/docs"]

    # Defaults to 25mb
    MAX_FILE_UPLOAD_SIZE: int = int(os.getenv("MAX_FILE_UPLOAD_SIZE", 25000000))


    @property
    def INTERNAL_DATABASE_URI(self):  # noqa
        return (
            f"postgresql+asyncpg://{self.INTERNAL_DATABASE_USER}:{self.INTERNAL_DATABASE_PASSWORD}"
            f"@{self.INTERNAL_DATABASE_HOST}:{self.INTERNAL_DATABASE_PORT}/{self.INTERNAL_DATABASE_DATABASE}"
        )

    #  Azure OpenAI deployment details (Optional)
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", None)
    AZURE_OPENAI_API_BASE: Optional[str] = os.getenv("AZURE_OPENAI_API_BASE", None)
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY", None)
    AZURE_OPENAI_API_VERSION: Optional[str] = os.getenv("AZURE_OPENAI_API_VERSION", None)

    # **** All variables below can be overriden by the APIs ****

    # Vector DB environment variables
    VECTOR_DB_API_KEY: str = os.getenv("VECTOR_DB_API_KEY")
    VECTOR_DB_NAME: str = os.getenv("VECTOR_DB_NAME", "qdrant")
    VECTOR_DB_HOST: str = os.getenv("VECTOR_DB_HOST", "localhost")
    VECTOR_DB_PORT: int = os.getenv("VECTOR_DB_PORT", 6333)
    VECTOR_DB_COLLECTION_NAME: str = os.getenv("VECTOR_DB_COLLECTION_NAME", "documents")
    VECTOR_DB_ENCODER_DIMENSIONS: int = os.getenv("VECTOR_DB_ENCODER_DIMENSIONS", 1536)
    VECTOR_DB_ENCODER_MODEL: str = os.getenv("VECTOR_DB_ENCODER_MODEL", "text-embedding-3-small")
    VECTOR_DB_ENCODER_NAME: str = os.getenv("VECTOR_DB_ENCODER_NAME", "openai")

    @property
    def VECTOR_DB_CONFIG(self):
        return {
            "host": f"http://{self.VECTOR_DB_HOST}:{self.VECTOR_DB_PORT}",
            "api_key": self.VECTOR_DB_API_KEY,
        }

    DEFAULT_PARTITION_STRATEGY: str = os.getenv("DEFAULT_PARTITION_STRATEGY", "auto")
    DEFAULT_HI_RES_MODEL_NAME: str = os.getenv("DEFAULT_HI_RES_MODEL_NAME", "detectron2_onnx")
    PROCESS_UNSTRUCTURED_TABLES: bool = True if os.getenv("PROCESS_UNSTRUCTURED_TABLES", "false") == "true" else False

    DEFAULT_CHUNKING_STRATEGY: str = os.getenv("DEFAULT_CHUNKING_STRATEGY", "semantic")
    DEFAULT_SEMANTIC_CHUNK_MIN_TOKENS: int = int(os.getenv("DEFAULT_SEMANTIC_CHUNK_MIN_TOKENS", 30))
    DEFAULT_SEMANTIC_CHUNK_MAX_TOKENS: int = int(os.getenv("DEFAULT_SEMANTIC_CHUNK_MAX_TOKENS", 500))
    SEMANTIC_ROLLING_WINDOW_SIZE: int = int(os.getenv("SEMANTIC_ROLLING_WINDOW_SIZE", 1))
    SPLIT_TITLES: bool = False if os.getenv("SPLIT_TITLES", "true") == "false" else True
    SPLIT_SUMMARY: bool = False if os.getenv("SPLIT_SUMMARY", "true") == "false" else True

    CREATE_SUMMARY_COLLECTION: bool = True if os.getenv("CREATE_SUMMARY_COLLECTION", "false") == "true" else False

    ENABLE_RERANK_BY_DEFAULT: bool = True if os.getenv("ENABLE_RERANK_BY_DEFAULT", "false") == "true" else False

def get_settings() -> Settings:
    return Settings()

try:
    settings = Settings()
except ValidationError as e:
    error_messages = [err for err in e.errors()]
    logger.error(f"Settings validation error: {error_messages}")
    sys.exit(1)


