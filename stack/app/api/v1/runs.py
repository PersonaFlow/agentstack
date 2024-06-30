from typing import Optional
from pydantic import BaseModel
from operator import itemgetter
import structlog
from langchain.pydantic_v1 import ValidationError

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.exceptions import RequestValidationError

from langchain_core.runnables import RunnableConfig
from langsmith.utils import tracing_is_enabled
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, HumanMessage, StrOutputParser
from langchain.schema.runnable import RunnableMap

from stack.app.agents.configurable_agent import agent, get_llm
from stack.app.core.auth.request_validators import AuthenticatedUser
from stack.app.schema.thread import Thread
from stack.app.repositories.assistant import (
    AssistantRepository,
    get_assistant_repository,
)
from stack.app.repositories.thread import ThreadRepository, get_thread_repository
from stack.app.schema.feedback import FeedbackCreateRequest
from stack.app.schema.title import TitleRequest
from stack.app.utils.stream import astream_state, to_sse
from sse_starlette import EventSourceResponse
from stack.app.core.configuration import get_settings


settings = get_settings()
if settings.ENABLE_LANGSMITH_TRACING:
    from langsmith import Client
    from langchain.callbacks.tracers import LangChainTracer

    langsmith_tracer = LangChainTracer(project_name=settings.LANGSMITH_PROJECT_NAME)
    langsmith_client = Client()

if settings.ENABLE_LANGFUSE_TRACING:
    from langfuse.callback import CallbackHandler

    langfuse_tracer = CallbackHandler(
        secret_key=settings.LANGFUSE_SECRET_KEY,
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        host=settings.LANGFUSE_HOST,
    )

if settings.ENABLE_PHOENIX_TRACING:
    from phoenix.trace.langchain import LangChainInstrumentor

    LangChainInstrumentor().instrument()

DEFAULT_TAG = "Runs"
logger = structlog.get_logger()
router = APIRouter()


class CreateRunPayload(BaseModel):
    """Payload for creating a run."""

    assistant_id: Optional[str] = None
    thread_id: Optional[str] = None
    input: list[dict]
    config: Optional[RunnableConfig] = None


async def _run_input_and_config(
    payload: CreateRunPayload,
    assistant_repository: AssistantRepository,
    thread_repository: ThreadRepository,
):
    if payload.thread_id and not payload.assistant_id:
        thread: Thread = thread_repository.retrieve_thread(payload.thread_id)
        payload.assistant_id = thread.assistant_id

    if not payload.thread_id:
        thread = await thread_repository.create_thread(
            data={
                "assistant_id": payload.assistant_id,
                "user_id": payload.user_id,
            }
        )
        payload.thread_id = str(thread.id)

    assistant = await assistant_repository.retrieve_assistant(
        assistant_id=payload.assistant_id
    )

    if not assistant:
        logger.exception("Invalid Assistant ID Provided", exc_info=False)
        raise ValueError(f"Invalid Assistant ID Provided")

    config: RunnableConfig = {
        **assistant.config,
        "configurable": {
            **assistant.config["configurable"],
            **((payload.config or {}).get("configurable") or {}),
            "user_id": payload.user_id,
            "thread_id": payload.thread_id,
            "assistant_id": payload.assistant_id,
        },
        "callbacks": [],
    }
    if settings.ENABLE_LANGSMITH_TRACING:
        config["callbacks"].append(langsmith_tracer)

    if settings.ENABLE_LANGFUSE_TRACING:
        config["callbacks"].append(langfuse_tracer)

    try:
        if payload.input is not None:
            agent.get_input_schema(config).validate(payload.input)
    except ValidationError as e:
        raise RequestValidationError(e.errors(), body=payload)

    return payload.input, config


@router.post(
    "/stream",
    tags=[DEFAULT_TAG],
    response_class=EventSourceResponse,
    operation_id="stream_run",
    summary="Stream an LLM run.",
    description="""
                Endpoint to stream an LLM response. If the thread_id is not provided, a new thread will be created as long as the assistant_id is included. <br>
                Note that the input should be a list of messages in the format: <br>
                content: string <br>
                role: string <br>
                additional_kwargs: dict <br>
                example: bool <br>
                """,
)
async def stream_run(
    auth: AuthenticatedUser,
    payload: CreateRunPayload,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository),
    thread_repository: ThreadRepository = Depends(get_thread_repository),
):
    if settings.ENABLE_LANGSMITH_TRACING:
        global trace_url
        trace_url = None

    input_, config = await _run_input_and_config(
        payload, assistant_repository, thread_repository
    )

    return EventSourceResponse(to_sse(astream_state(agent, input_, config)))


@router.post(
    "",
    tags=[DEFAULT_TAG],
    response_model=dict,
    operation_id="create_run",
    summary="Create a run",
    description="Create a run to be processed by the LLM.",
)
async def create_run(
    auth: AuthenticatedUser,
    payload: CreateRunPayload,
    background_tasks: BackgroundTasks,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository),
    thread_repository: ThreadRepository = Depends(get_thread_repository),
):
    input_, config = await _run_input_and_config(
        payload, assistant_repository, thread_repository
    )
    background_tasks.add_task(agent.ainvoke, input_, config)
    return {"status": "ok"}


@router.get(
    "/input_schema",
    tags=[DEFAULT_TAG],
    response_model=dict,
    operation_id="get_input_schema",
    summary="Return the input schema of the runnable.",
    description="Return the input schema of the runnable.",
)
async def input_schema() -> dict:
    return agent.get_input_schema().schema()


@router.get(
    "/output_schema",
    tags=[DEFAULT_TAG],
    response_model=dict,
    operation_id="get_output_schema",
    summary="Return the output schema of the runnable.",
    description="Return the output schema of the runnable.",
)
async def output_schema() -> dict:
    return agent.get_output_schema().schema()


@router.get(
    "/config_schema",
    tags=[DEFAULT_TAG],
    response_model=dict,
    operation_id="get_config_schema",
    summary="Return the config schema of the runnable.",
    description="Return the config schema of the runnable.",
)
async def config_schema() -> dict:
    return agent.config_schema().schema()


TITLE_GENERATOR_TEMPLATE = """
Write an extremely concise title for this conversation in 5 words or less.
Title must be 5 Words or Less. No Punctuation or Quotation.
All first letters of every word should be capitalized and write the title in the same language only.

Conversation:
{chat_history}
"""


@router.post(
    "/title",
    tags=[DEFAULT_TAG],
    response_model=Thread,
    operation_id="generate_title",
    summary="Generate a title to name the thread.",
    description="Generates a title for the conversation by sending a list of interactions to the model.",
)
async def title_endpoint(
    auth: AuthenticatedUser,
    request: TitleRequest,
    thread_repository: ThreadRepository = Depends(get_thread_repository),
    assistant_repo: AssistantRepository = Depends(get_assistant_repository),
) -> Thread:
    converted_chat_history = []
    for message in request.history:
        if message.type == "human":
            converted_chat_history.append(HumanMessage(content=message.content))
        elif message.type == "ai":
            converted_chat_history.append(AIMessage(content=message.content))

    thread = await thread_repository.retrieve_thread(request.thread_id)
    assistant = await assistant_repo.retrieve_assistant(thread.assistant_id)
    llm_type = assistant.config["configurable"]["type==chatbot/llm_type"]
    agent_type = assistant.config["configurable"]["type==agent/agent_type"]
    type = assistant.config["configurable"]["type"]
    model = agent_type if type == "agent" else llm_type
    llm = get_llm(model)

    _context = RunnableMap({"chat_history": itemgetter("chat_history")})

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TITLE_GENERATOR_TEMPLATE),
            MessagesPlaceholder(variable_name="chat_history"),
        ]
    )

    response_synthesizer = prompt | llm | StrOutputParser()

    chain = _context | response_synthesizer

    callbacks = []
    try:
        title = chain.invoke(
            {
                "chat_history": converted_chat_history,
            },
            config={"callbacks": callbacks},
        )
        if settings.ENABLE_LANGSMITH_TRACING:
            callbacks.append(langsmith_tracer)

        if settings.ENABLE_LANGFUSE_TRACING:
            callbacks.append(langfuse_tracer)

        thread = await thread_repository.update_thread(
            request.thread_id, {"name": title}
        )
        return thread

    except Exception as e:
        logger.debug(f"API Endpoint Exception - Failed to generate title: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate title.")


if settings.ENABLE_LANGSMITH_TRACING and tracing_is_enabled():

    @router.post(
        "/feedback",
        tags=["Feedback"],
        response_model=dict,
        summary="Send feedback on an individual run to langsmith",
        description="Send feedback on an individual run to langsmith. **Disabled if ENABLE_LANGSMITH_TRACING is not explicitly set to `true`**.",
    )
    def create_run_feedback(feedback_create_req: FeedbackCreateRequest) -> dict:
        langsmith_client.create_feedback(
            feedback_create_req.run_id,
            feedback_create_req.key,
            score=feedback_create_req.score,
            value=feedback_create_req.value,
            comment=feedback_create_req.comment,
            source_info={},
        )

        return {"status": "ok"}
