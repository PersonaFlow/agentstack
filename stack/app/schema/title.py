from pydantic import BaseModel, Field
from typing import List, Optional


class Source(BaseModel):
    url: str
    title: Optional[str]


class Metadata(BaseModel):
    run_id: Optional[str]
    sources: Optional[List[Source]]

class ChatMessage(BaseModel):
    content: str
    type: str

class TitleRequest(BaseModel):
    thread_id: str = Field(
        ..., description="The id of the thread to generate the title for."
    )
    history: Optional[List[ChatMessage]] = Field(
        None,
        description="(Optional) The conversation history of the thread. This is used as context for the model when generating the title.",
    )
