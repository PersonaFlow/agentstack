import uuid
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field, validator
from semantic_router.encoders import (
    BaseEncoder,
    CohereEncoder,
    OpenAIEncoder,
    AzureOpenAIEncoder,
    MistralEncoder,
)
from stack.app.rag.encoders.ollama_encoder import OllamaEncoder
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
    ollama = "ollama"


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
    score_threshold: float = Field(
        default=0.5,
        description="Score threshold for the encoder",
    )

    @classmethod
    def get_encoder_config(cls, encoder_provider: EncoderProvider):
        encoder_configs = {
            EncoderProvider.cohere: {
                "class": CohereEncoder,
                "default_model_name": "embed-multilingual-light-v3.0",
                "default_dimensions": 384,
                "default_score_threshold": 0.3,
            },
            EncoderProvider.openai: {
                "class": OpenAIEncoder,
                "default_model_name": "text-embedding-3-small",
                "default_dimensions": 1536,
                "default_score_threshold": 0.82,
            },
            EncoderProvider.ollama: {
                "class": OllamaEncoder,
                "default_model_name": "all-minilm",
                "default_dimensions": 384,
                "default_score_threshold": 0.67,
            },
            EncoderProvider.azure_openai: {
                "class": AzureOpenAIEncoder,
                "default_model_name": "text-embedding-3-small",
                "default_dimensions": 1536,
                "default_score_threshold": 0.82,
            },
            EncoderProvider.mistral: {
                "class": MistralEncoder,
                "default_model_name": "mistral-embed",
                "default_dimensions": 1024,
                "default_score_threshold": 0.82,
            },
        }
        return encoder_configs.get(encoder_provider)

    def get_encoder(self) -> BaseEncoder:
        encoder_config = self.get_encoder_config(self.provider)
        if not encoder_config:
            raise ValueError(f"Encoder '{self.provider}' not found.")
        encoder_model = self.encoder_model or encoder_config["default_model_name"]
        dimensions = self.dimensions or encoder_config["default_dimensions"]
        score_threshold=self.score_threshold or encoder_config["default_score_threshold"]
        encoder_class = encoder_config["class"]
        return encoder_class(name=encoder_model, dimensions=dimensions, score_threshold=score_threshold)


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

class ParserConfig(BaseModel):
    structured_data_content_field: Optional[str] = Field(
        default="page_content", 
        description="For JSON and CSV files: the field name containing the content to be embedded. All other fields will be saved as metadata."
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
    parser_config: Optional[ParserConfig] = Field(
        default=ParserConfig(),
        description="Content-specific keyword arguments for processing")


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


class BaseDocument(BaseModel):
    id: str
    page_content: str
    metadata: dict | None = None



class BaseDocumentChunk(BaseModel):
    id: str
    page_content: str
    namespace: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    dense_embedding: Optional[list[float]] = None

    @classmethod
    def from_metadata(cls, metadata: dict):
        # Extract the core fields
        chunk_id = metadata.pop("chunk_id", "")
        page_content = metadata.pop("page_content", "")
        namespace = metadata.pop("namespace", None)
        
        # Everything else goes into metadata
        return cls(
            id=chunk_id,
            page_content=page_content,
            namespace=namespace,
            metadata=metadata,
            dense_embedding=metadata.pop("values", None)
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, dict):
            return cls(**v)
        return v

    @classmethod
    def id_must_be_valid_uuid(cls, v):
        try:
            uuid_obj = uuid.UUID(v, version=4)
            return str(uuid_obj)
        except ValueError:
            raise ValueError(f"id must be a valid UUID, got {v}")

    @classmethod
    def embeddings_must_be_list_of_floats(cls, v):
        if v is None:
            return v  # Allow None to pass through
        if not all(isinstance(item, float) for item in v):
            raise ValueError(f"embeddings must be a list of floats, got {v}")
        return v

    def to_vector_db(self):
        return {
            "id": self.id,
            "values": self.dense_embedding,
            "metadata": {
                "page_content": self.page_content,
                "namespace": self.namespace,
                **self.metadata
            },
        }

    def model_dump(self, exclude: set = None):
        return {
            "id": self.id,
            "page_content": self.page_content,
            "namespace": self.namespace,
            "metadata": self.metadata,
            "dense_embedding": self.dense_embedding
        }


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
