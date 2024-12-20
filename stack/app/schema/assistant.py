from pydantic import BaseModel, Field, validator
import uuid
from typing import Optional
from enum import Enum
from datetime import datetime
from stack.app.agents.tools import AvailableTools
from stack.app.agents.llm import LLMType, BotType, AgentType


class Tool(BaseModel):
    type: AvailableTools = Field(
        title="Tool Type",
        description="The type of tool as defined by the AvailableTools enum.",
    )
    description: Optional[str] = Field(
        title="Tool Description", description="A brief description of the tool."
    )
    name: Optional[str] = Field(
        title="Tool Name",
        description="The name of the tool.",
    )
    config: Optional[dict] = Field(
        title="Tool Configuration",
        description="A field for additional configuration of the tool.",
    )
    multi_use: Optional[bool] = Field(
        default=False,
        title="Multi-Use",
        description="Whether or not this is a multi-use tool.",
    )


class Configurable(BaseModel):
    type: BotType = Field(
        default="agent", title="Bot Type", description="The type of bot."
    )
    agent_type: AgentType = Field(
        default="GPT 4o Mini",
        title="Agent Type",
        description="The type of agent, applicable if the bot type is 'agent'.",
    )
    interrupt_before_action: Optional[bool] = Field(
        default=False,
        title="Tool Confirmation",
        description="If set to True, you'll be prompted to continue before each tool is executed. If False, tools will be executed automatically by the agent.",
    )
    retrieval_description: Optional[str] = Field(
        default="Can be used to look up information that was uploaded for this assistant.",
        title="Retrieval Description",
        description="Tool description providing instructions to the LLM for it's use.",
    )
    system_message: Optional[str] = Field(
        default="You are a helpful assistant.",
        title="Instructions",
        description="Instructions for the assistant.",
    )
    tools: Optional[list[Tool]] = Field(
        default=[], title="Tools", description="List of tools available for the agent."
    )
    llm_type: Optional[LLMType] = Field(
        default="GPT 4o Mini",
        title="LLM Type",
        description="The type of language model, applicable if the bot type is 'chat_retrieval' or 'chatbot'.",
    )


class RunnableConfigurableAlternativesConfig(BaseModel):
    configurable: Configurable


class Assistant(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="A unique identifier for the assistant. It's a UUID type and is automatically generated by the database.",
    )
    user_id: Optional[str] = Field(
        None, description="The user id that created the assistant."
    )
    name: str = Field(..., description="The name of the assistant.", min_length=1)
    config: RunnableConfigurableAlternativesConfig = Field(
        ...,
        description="The assistant config, containing specific configuration parameters.",
    )
    kwargs: Optional[dict] = Field(
        None,
        description="The assistant kwargs, containing any additional information about the assistant such as public vs internal, etc.",
    )
    file_ids: Optional[list[str]] = Field(
        None,
        description="A list of file IDs to be associated with this assistant for use with Retrieval.",
    )
    public: Optional[bool] = Field(
        False, description="Whether the assistant is public."
    )
    created_at: datetime = Field(..., description="Created date")
    updated_at: datetime = Field(..., description="Last updated date")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.replace(microsecond=0).isoformat(),
        }


class CreateAssistantSchema(BaseModel):
    name: str = Field(..., description="The name of the assistant.", min_length=1)
    config: dict = Field(
        ...,
        description="The assistant config, containing specific configuration parameters.",
    )
    kwargs: Optional[dict] = Field(
        None,
        description="The assistant kwargs, containing any additional information about the assistant such as public vs internal, etc.",
    )
    file_ids: Optional[list[str]] = Field(
        None,
        description="A list of file IDs to be associated with this assistant for use with Retrieval.",
    )
    public: Optional[bool] = Field(
        False, description="Whether the assistant is public."
    )

    @validator("name", "config")
    def must_not_be_empty(cls, v):
        if not v:
            raise ValueError("name, config must not be empty")
        return v


class UpdateAssistantSchema(BaseModel):
    name: Optional[str] = Field(None, description="The name of the assistant.")
    config: Optional[dict] = Field(
        None,
        description="The assistant config, containing specific configuration parameters.",
    )
    kwargs: Optional[dict] = Field(
        None,
        description="The assistant kwargs, containing any additional information about the assistant such as public vs internal, etc.",
    )
    file_ids: Optional[list[str]] = Field(
        None,
        description="A list of file IDs to be associated with this assistant for use with Retrieval.",
    )
    public: Optional[bool] = Field(
        False, description="Whether the assistant is public."
    )


class CreateAssistantFileSchema(BaseModel):
    file_id: str = Field(
        ..., description="The file ID to be associated with the assistant."
    )


class CreateAssistantFileSchemaResponse(BaseModel):
    file_id: str = Field(
        ..., description="The file ID to be associated with the assistant."
    )
    assistant_id: str = Field(
        ..., description="The assistant ID to which the file was associated."
    )
