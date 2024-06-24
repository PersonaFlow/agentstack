from pydantic import BaseModel, Field, validator
import uuid
from datetime import datetime
from langchain.schema.messages import AnyMessage
from typing import Any, Dict, List, Optional, Sequence, Union


class Thread(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="A unique identifier for the thread. It's a UUID type and is automatically generated by the database.",
    )
    user_id: str = Field(..., description="The user id associated with the thread.")
    assistant_id: Optional[uuid.UUID] = Field(
        None, description="(Optional) The assistant id associated with the thread."
    )
    name: Optional[str] = Field(
        None, description="(Optional) The conversation title of the thread."
    )
    kwargs: Optional[dict] = Field(
        None, description="(Optional) Additional kwargs associated with the thread."
    )
    created_at: datetime = Field(..., description="Created date")
    updated_at: datetime = Field(..., description="Last updated date")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.replace(microsecond=0).isoformat(),
        }


class CreateThreadSchema(BaseModel):
    assistant_id: uuid.UUID = Field(
        ..., description="(Optional) The assistant id associated with the thread."
    )
    user_id: str = Field(..., description="The user id associated with the thread.")
    name: Optional[str] = Field(
        None, description="(Optional) The conversation title of the thread."
    )
    kwargs: Optional[dict] = Field(
        None, description="(Optional) Additional kwargs associated with the thread."
    )

    @validator("user_id")
    def must_not_be_empty(cls, v):
        if not v:
            raise ValueError("This field must not be empty")
        return v


class UpdateThreadSchema(BaseModel):
    assistant_id: Optional[uuid.UUID] = Field(
        None, description="(Optional) The assistant id associated with the thread."
    )
    name: Optional[str] = Field(
        None, description="(Optional) The conversation title of the thread."
    )
    kwargs: Optional[dict] = Field(
        None, description="(Optional) Additional kwargs associated with the thread."
    )


class GroupedThreads(BaseModel):
    """Grouped threads by time period."""
    Today: Optional[List[Thread]] = Field(None, alias="Today")
    Yesterday: Optional[List[Thread]] = Field(None, alias="Yesterday")
    Past_7_Days: Optional[List[Thread]] = Field(None, alias="Past 7 Days")
    Past_30_Days: Optional[List[Thread]] = Field(None, alias="Past 30 Days")
    This_Year: Optional[List[Thread]] = Field(None, alias="This Year")
    Previous_Years: Optional[List[Thread]] = Field(None, alias="Previous Years")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.replace(microsecond=0).isoformat(),
        }


class ThreadPostRequest(BaseModel):
    """Payload for adding state to a thread."""

    values: Union[Sequence[AnyMessage], Dict[str, Any]] = Field(
        ...,
        description="The state values to add to the thread. It can be a list of messages or a dictionary.",
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="The configuration values to add to the thread. It can be a dictionary.",
    )


