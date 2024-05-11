import uuid
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field, validator
from semantic_router.encoders import BaseEncoder, CohereEncoder, OpenAIEncoder

# from stack.app.rag.ollama_encoder import OllamaEncoder
from stack.app.core.configuration import get_settings

settings = get_settings()


class VectorDatabaseType(Enum):
    qdrant = "qdrant"


class VectorDatabase(BaseModel):
    type: VectorDatabaseType = Field(
        default=settings.VECTOR_DB_NAME,
        description="Vector database type. Must be one of VectorDatabaseType enum.",
    )
    config: dict = Field(
        default=settings.VECTOR_DB_CONFIG,
        description="Vector database configuration object.",
    )


# Ingest Schemas


class ContextType(str, Enum):
    """Context where files or generated embeddings are used."""

    assistants = "assistants"
    threads = "threads"
    rag = "rag"
    personas = "personas"


class EncoderProvider(str, Enum):
    cohere = "cohere"
    openai = "openai"
    huggingface = "huggingface"
    azure_openai = "azure_openai"
    mistral = "mistral"
    # ollama = "ollama"


class EncoderConfig(BaseModel):
    provider: EncoderProvider = Field(
        default=settings.VECTOR_DB_ENCODER_NAME, description="Embedding provider"
    )
    encoder_model: str = Field(
        default=settings.VECTOR_DB_ENCODER_MODEL,
        description="Model name for the encoder",
    )
    dimensions: int = Field(
        default=settings.VECTOR_DB_ENCODER_DIMENSIONS,
        description="Dimension of the encoder output",
    )

    @classmethod
    def get_encoder_config(cls, encoder_provider: EncoderProvider):
        encoder_configs = {
            EncoderProvider.cohere: {
                "class": CohereEncoder,
                "default_model_name": "embed-multilingual-light-v3.0",
                "default_dimensions": 384,
            },
            EncoderProvider.openai: {
                "class": OpenAIEncoder,
                "default_model_name": "text-embedding-3-small",
                "default_dimensions": 1536,
            },
            # TODO: huggingface encoders requires pytorch and transformers which adds a lot of weight to the docker image.
            # ...will need to branstorm solution
            # EncoderProvider.huggingface: {
            #     "class": HuggingFaceEncoder,
            #     "default_model_name": settings.HUGGINGFACE_EMBEDDING_MODEL_NAME or "distilbert-base-uncased",
            #     "default_dimensions": 1024,
            # },
            # TODO: Add Azure OpenAI Encoder
            # EncoderProvider.azure_openai: {
            #     "class": AzureOpenAIEncoder,
            #     "default_model_name": "text-embedding-3-small",
            #     "default_dimensions": 1536,
            # },
            # TODO: Create an ollama encoder
        }
        return encoder_configs.get(encoder_provider)

    def get_encoder(self) -> BaseEncoder:
        encoder_config = self.get_encoder_config(self.provider)
        if not encoder_config:
            raise ValueError(f"Encoder '{self.provider}' not found.")
        encoder_model = self.encoder_model or encoder_config["default_model_name"]
        dimensions = self.dimensions or encoder_config["default_dimensions"]
        encoder_class = encoder_config["class"]
        return encoder_class(name=encoder_model, dimensions=dimensions)


class UnstructuredConfig(BaseModel):
    partition_strategy: Literal["auto", "hi_res"] = Field(
        default=settings.DEFAULT_PARTITION_STRATEGY
    )
    hi_res_model_name: Literal["detectron2_onnx", "chipper"] = Field(
        default=settings.DEFAULT_HI_RES_MODEL_NAME,
        description="Only for `hi_res` strategy",
    )
    process_tables: bool = Field(
        default=settings.PROCESS_UNSTRUCTURED_TABLES,
        description="Only for `hi_res` strategy",
    )


class SplitterConfig(BaseModel):
    name: Literal["semantic", "by_title"] = Field(
        default=settings.DEFAULT_CHUNKING_STRATEGY, description="Splitter method"
    )
    min_tokens: int = Field(
        default=settings.DEFAULT_SEMANTIC_CHUNK_MIN_TOKENS,
        description="Only for `semantic` method",
    )
    max_tokens: int = Field(
        default=settings.DEFAULT_SEMANTIC_CHUNK_MAX_TOKENS,
        description="Only for `semantic` and `recursive` methods",
    )
    rolling_window_size: int = Field(
        default=settings.SEMANTIC_ROLLING_WINDOW_SIZE,
        description="Only for `semantic` method, cumulative window size "
        "for comparing similarity between elements",
    )
    prefix_titles: bool = Field(
        default=settings.PREFIX_TITLES,
        description="Add to prefix titles in chunk, only `semantic` method",
    )
    prefix_summary: bool = Field(
        default=settings.PREFIX_SUMMARY, description="Add to split sub-document summary"
    )


class DocumentProcessorConfig(BaseModel):
    summarize: bool = Field(
        default=settings.CREATE_SUMMARY_COLLECTION,
        description="Create a separate collection of document summaries",
    )
    encoder: EncoderConfig = Field(
        default=EncoderConfig(),
        description="Embeddings provider coniguration. If not provided, this comes from the env config.",
    )
    unstructured: UnstructuredConfig = Field(
        default=UnstructuredConfig(),
        description="UnstructuredIO configuration. If not provided, this comes from the env config.",
    )
    splitter: SplitterConfig = Field(
        default=SplitterConfig(),
        description="Document partition manager configuration. If not provided, this comes from the env config.",
    )


class IngestRequestPayload(BaseModel):
    files: list[uuid.UUID] = Field(..., description="An array of file ids to ingest")
    purpose: Optional[ContextType] = Field(
        default=ContextType.assistants,
        description="Context of where the embeddings will be used.",
    )
    index_name: Optional[str] = Field(
        default=settings.VECTOR_DB_COLLECTION_NAME,
        description="Name of the vector database follection to ingest the files into. If not provided, the `VECTOR_DB_COLLECTION_NAME` env var is used.",
    )
    namespace: Optional[str] = Field(
        None,
        description="Context of the embeddings: This is the assistant_id, thread_id, file_id, or random uuid that is used for filtering the results.",
    )
    vector_database: Optional[VectorDatabase] = Field(
        default=VectorDatabase(),
        description="Vector database to store the embeddings. If not provided, this comes from the env config.",
    )
    document_processor: Optional[DocumentProcessorConfig] = Field(
        default=DocumentProcessorConfig(),
        description="Document processor configuration. If not provided, this comes from the env config.",
    )
    webhook_url: Optional[str] = Field(
        None,
        description="Webhook url to send the notification to when the ingestion is completed.",
    )


# Query Schemas
class QueryRequestPayload(BaseModel):
    input: str = Field(..., description="Input text to query")
    namespace: Optional[str] = Field(
        None,
        description="Context of the query: This is the assistant_id, thread_id, file_id, or random uuid that is used for filtering the results.",
    )
    context: Optional[ContextType] = Field(
        default=ContextType.assistants,
        description="Context of where the embeddings will be used.",
    )
    index_name: Optional[str] = Field(
        default=settings.VECTOR_DB_COLLECTION_NAME,
        description="Name of the vector database follection to query from. If not provided, the `VECTOR_DB_COLLECTION_NAME` env var is used.",
    )
    vector_database: Optional[VectorDatabase] = Field(
        default=VectorDatabase(),
        description="Vector database to query from. If not provided, this comes from the env config.",
    )
    encoder: Optional[EncoderConfig] = Field(
        default=EncoderConfig(),
        description="Embeddings provider configuration. If not provided, this comes from the env config.",
    )
    enable_rerank: Optional[bool] = Field(
        default=settings.ENABLE_RERANK_BY_DEFAULT,
        description="Enable reranking of the results. *NOTE: `COHERE_API_KEY` env var is required to use this feature.*",
    )
    interpreter_mode: Optional[bool] = Field(
        False, description="Enable code interpreter mode."
    )
    exclude_fields: Optional[list[str]] = Field(
        None, description="List of fields to exclude from the results."
    )


# Documents


class BaseDocument(BaseModel):
    id: str
    page_content: str
    metadata: dict | None = None


class BaseDocumentChunk(BaseModel):
    id: str
    document_id: str
    page_content: str
    file_id: str | None = None
    namespace: str | None = None
    source: str | None = None
    source_type: str | None = None
    chunk_index: int | None = None
    title: str | None = None
    purpose: ContextType | None = None
    token_count: int | None = None
    page_number: int | None = None
    metadata: dict | None = None
    dense_embedding: Optional[list[float]] = None

    @classmethod
    def from_metadata(cls, metadata: dict):
        exclude_keys = {
            "chunk_id",
            "chunk_index",
            "document_id",
            "file_id",
            "namespace",
            "page_content",
            "source",
            "source_type",
            "purpose",
            "title",
            "token_count",
            "page_number",
        }
        # Prepare metadata for the constructor and for embedding into the object
        constructor_metadata = {
            k: v for k, v in metadata.items() if k not in exclude_keys
        }
        filtered_metadata = {
            k: v for k, v in metadata.items() if k in exclude_keys and k != "chunk_id"
        }

        def to_int(value):
            try:
                return int(value) if str(value).isdigit() else None
            except (TypeError, ValueError):
                return None

        chunk_index = to_int(metadata.get("chunk_index"))
        token_count = to_int(metadata.get("token_count"))

        # Remove explicitly passed keys from filtered_metadata to avoid duplication
        for key in ["chunk_index", "token_count"]:
            filtered_metadata.pop(key, None)

        return cls(
            id=metadata.get("chunk_id", ""),
            chunk_index=chunk_index,
            token_count=token_count,
            **filtered_metadata,  # Pass filtered metadata for constructor
            metadata=constructor_metadata,  # Pass the rest as part of the metadata
            dense_embedding=metadata.get("values"),
        )

    @validator("id")
    def id_must_be_valid_uuid(cls, v):
        try:
            uuid_obj = uuid.UUID(v, version=4)
            return str(uuid_obj)
        except ValueError:
            raise ValueError(f"id must be a valid UUID, got {v}")

    @validator("dense_embedding")
    def embeddings_must_be_list_of_floats(cls, v):
        if v is None:
            return v  # Allow None to pass through
        if not all(isinstance(item, float) for item in v):
            raise ValueError(f"embeddings must be a list of floats, got {v}")
        return v

    def to_vector_db(self):
        metadata = {
            "chunk_id": self.id,
            "chunk_index": self.chunk_index or "",
            "document_id": self.document_id,
            "file_id": self.file_id,
            "namespace": self.namespace,
            "page_content": self.page_content,
            "source": self.source,
            "source_type": self.source_type,
            "title": self.title or "",
            "purpose": self.purpose,
            "token_count": self.token_count,
            **(self.metadata or {}),
        }
        result = {
            "id": self.id,
            "values": self.dense_embedding,
            "metadata": metadata,
        }
        return result


class QueryResponsePayload(BaseModel):
    success: bool
    data: list[BaseDocumentChunk]

    def model_dump(self, exclude: set = None):
        return {
            "success": self.success,
            "data": [chunk.model_dump(exclude=exclude) for chunk in self.data],
        }


# Delete docs
class DeleteFile(BaseModel):
    url: str


class DeleteRequestPayload(BaseModel):
    files: list[DeleteFile] = Field(..., description="Array of files to delete")
    index_name: Optional[str] = Field(
        settings.VECTOR_DB_COLLECTION_NAME,
        description="Name of the vector database follection to do the deletion. If not provided, the `VECTOR_DB_COLLECTION_NAME` env var is used.",
    )
    vector_database: Optional[VectorDatabase] = Field(
        VectorDatabase(), description="Vector database to use for the deletion."
    )
    encoder: Optional[EncoderConfig] = Field(
        EncoderConfig(), description="Encoder configuration to use for the deletion."
    )


class DeleteDocumentsResponse(BaseModel):
    num_deleted_chunks: int
