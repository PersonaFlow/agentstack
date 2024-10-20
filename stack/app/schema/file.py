from pydantic import BaseModel, Field
import uuid
from enum import Enum
from typing import Optional, Any
from datetime import datetime
from stack.app.schema.rag import ContextType


class FilePurpose(Enum):
    PERSONAS = "personas"
    ASSISTANTS = "assistants"
    THREADS = "threads"
    RAG = "rag"


class FileType(Enum):
    pdf = "PDF"
    docx = "DOCX"
    txt = "TXT"
    pptx = "PPTX"
    md = "MARKDOWN"
    csv = "CSV"
    xlsx = "XLSX"
    html = "HTML"
    json = "JSON"

    def suffix(self) -> str:
        suffixes = {
            "TXT": ".txt",
            "PDF": ".pdf",
            "MARKDOWN": ".md",
            "DOCX": ".docx",
            "CSV": ".csv",
            "XLSX": ".xlsx",
            "PPTX": ".pptx",
            "HTML": ".html",
            "JSON": ".json",
        }
        return suffixes[self.value]


class FileSchema(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="A unique identifier for the file. It's a UUID type and is automatically generated by the database.",
    )
    user_id: str = Field(..., description="The ID of the user who created the file.")
    purpose: ContextType = Field(
        ...,
        description="The context for file: eg. 'assistants', 'rag', 'threads', or 'personas'.",
    )
    filename: str = Field(..., description="The preferred name for the file.")
    bytes: int = Field(
        ..., description="The file size in bytes, calculated when the file is uploaded."
    )
    mime_type: str = Field(..., description="The mime type of the file.")
    source: str = Field(
        ...,
        description="The source of the file. For local files, this will be the local file path plus filename and extension.",
    )
    kwargs: dict = Field(..., description="Any additional kwargs for the file.")
    created_at: datetime = Field(..., description="Created date")
    updated_at: datetime = Field(..., description="Last updated date")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.replace(microsecond=0).isoformat(),
        }

    @property
    def type(self) -> FileType | None:
        extension = self.source.split(".")[-1].lower()
        try:
            return FileType[extension]
        except KeyError:
            raise ValueError(f"Unsupported file type for extension: {extension}")

    @property
    def suffix(self) -> str:
        file_type = self.type
        if file_type is not None:
            return file_type.suffix()
        else:
            raise ValueError("File type is undefined, cannot determine suffix.")


class UploadFileSchema(BaseModel):
    user_id: str = Field(
        ...,
        description="The ID of the user who uploaded the file. This is the user ID of the logged-in user.",
    )
    purpose: Optional[ContextType] = Field(
        default=ContextType.assistants,
        description="The context for file: eg. 'assistants', 'rag', 'threads', or 'personas'.",
    )
    kwargs: Optional[str] = Field(
        None,
        description="The file kwargs, containing any additional information about the file. This is a string sent in JSON format.",
    )


class DeleteFileResponse(BaseModel):
    file_id: uuid.UUID = Field(..., description="The ID of the file that was deleted.")
    num_of_deleted_chunks: Optional[int] = Field(
        None,
        description="The number of chunks deleted from the vector store for this file.",
    )
    num_of_assistants: int = Field(
        ...,
        description="The number of assistants that were using this file, of which the file was removed.",
    )
    assistants: list[dict[str, Any]] = Field(
        ...,
        description="A list of the IDs and names of the asistants that were using this file, of which the file was removed.",
    )
