import uuid
from enum import Enum
from typing import Literal, Optional
from fastapi import UploadFile
from pydantic import BaseModel, Field, validator
from semantic_router.encoders import BaseEncoder, CohereEncoder, OpenAIEncoder, HuggingFaceEncoder, AzureOpenAIEncoder
from app.core.configuration import get_settings
from urllib.parse import unquote, urlparse

settings = get_settings()

class DatabaseType(Enum):
    qdrant = "qdrant"


class VectorDatabase(BaseModel):
    type: DatabaseType
    config: dict


# Ingest Schemas
class EncoderProvider(str, Enum):
    cohere = "cohere"
    openai = "openai"
    huggingface = "huggingface"
    azure_openai = "azure_openai"


class EncoderConfig(BaseModel):
    provider: EncoderProvider = Field(
        default=EncoderProvider.cohere, description="Embedding provider"
    )
    model_name: str = Field(
        default="embed-multilingual-light-v3.0",
        description="Model name for the encoder",
    )
    dimensions: int = Field(default=384, description="Dimension of the encoder output")

    _encoder_config = {
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
        # TODO: Create an ollama encoder, possibly as a contrib
    }

    def get_encoder(self) -> BaseEncoder:
        config = self._encoder_config.get(self.provider)
        if not config:
            raise ValueError(f"Encoder '{self.provider}' not found.")
        model_name = self.model_name or config["default_model_name"]
        encoder_class = config["class"]
        return encoder_class(name=model_name)


class UnstructuredConfig(BaseModel):
    partition_strategy: Literal["auto", "hi_res"] = Field(default="auto")
    hi_res_model_name: Literal["detectron2_onnx", "chipper"] = Field(
        default="detectron2_onnx", description="Only for `hi_res` strategy"
    )
    process_tables: bool = Field(
        default=False, description="Only for `hi_res` strategy"
    )


class SplitterConfig(BaseModel):
    name: Literal["semantic", "by_title"] = Field(
        default="semantic", description="Splitter name, `semantic` or `by_title`"
    )
    min_tokens: int = Field(default=30, description="Only for `semantic` method")
    max_tokens: int = Field(
        default=400, description="Only for `semantic` and `recursive` methods"
    )
    rolling_window_size: int = Field(
        default=1,
        description="Only for `semantic` method, cumulative window size "
        "for comparing similarity between elements",
    )
    prefix_title: bool = Field(
        default=True, description="Add to split titles, headers, only `semantic` method"
    )
    prefix_summary: bool = Field(
        default=True, description="Add to split sub-document summary"
    )


class DocumentProcessorConfig(BaseModel):
    summarize: bool = Field(default=False, description="Create a separate index of document summaries")
    encoder: EncoderConfig = EncoderConfig()
    unstructured: UnstructuredConfig = UnstructuredConfig()
    splitter: SplitterConfig = SplitterConfig()



# Files
class FileType(Enum):
    pdf = "pdf"
    docx = "docx"
    txt = "txt"
    pptx = "pptx"
    md = "markdown"
    csv = "csv"
    xlsx = "xlsx"
    html = "html"
    json = "json"

class IngestFile(BaseModel):
    url: Optional[str] = None
    name: Optional[str] = None
    content: Optional[bytes] = None  # Add this attribute to store file content

    @classmethod
    def from_url(cls, url: str):
        return cls(url=url, name=url.split("/")[-1])

    @classmethod
    def from_upload_file(cls, upload_file: UploadFile):
        return cls(
            url=f"file://{upload_file.filename}",
            name=upload_file.filename,
            content=upload_file.file.read(),
        )

    @property
    def type(self) -> FileType | None:
        filename = self.name or self.url
        if filename:
            extension = filename.split(".")[-1].lower()
            try:
                return FileType(extension)
            except KeyError:
                raise ValueError(f"Unsupported file type for filename: {filename}")
        return None

    @property
    def suffix(self) -> str:
        file_type = self.type
        if file_type is not None:
            # return file_type.suffix()
            return f".{file_type.value}"
        else:
            raise ValueError("File type is undefined, cannot determine suffix.")

class IngestRequestPayload(BaseModel):
    index_name: str
    vector_database: Optional[VectorDatabase] = None
    document_processor: DocumentProcessorConfig = DocumentProcessorConfig()
    files: Optional[list[IngestFile]] = None
    webhook_url: Optional[str] = None

# Query Schemas
class QueryRequestPayload(BaseModel):
    input: str
    index_name: str
    vector_database: Optional[VectorDatabase] = None
    encoder: EncoderConfig = EncoderConfig()
    thread_id: Optional[str] = None
    enable_rerank: Optional[bool] = False
    interpreter_mode: Optional[bool] = False
    exclude_fields: list[str] = None


class QueryResponseData(BaseModel):
    content: str
    doc_url: str
    page_number: Optional[int]
    metadata: Optional[dict] = None


# Documents

class BaseDocument(BaseModel):
    id: str
    content: str
    doc_url: str
    metadata: dict | None = None


class BaseDocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    doc_url: str | None = None
    source: str | None = None
    source_type: str | None = None
    chunk_index: int | None = None
    title: str | None = None
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
            "doc_url",
            "content",
            "source",
            "source_type",
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
            "doc_url": self.doc_url,
            "content": self.content,
            "source": self.source,
            "source_type": self.source_type,
            "title": self.title or "",
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
            "data": [chunk.dict(exclude=exclude) for chunk in self.data],
        }

# Vector DBs

class DatabaseType(Enum):
    qdrant = "qdrant"


class VectorDatabase(BaseModel):
    type: DatabaseType
    config: dict



# Delete docs
class DeleteFile(BaseModel):
    url: str


class DeleteRequestPayload(BaseModel):
    index_name: str
    files: list[DeleteFile]
    vector_database: VectorDatabase
    encoder: EncoderConfig = EncoderConfig()


class DeleteResponse(BaseModel):
    num_of_deleted_chunks: int


class DeleteResponsePayload(BaseModel):
    success: bool
    data: DeleteResponse
