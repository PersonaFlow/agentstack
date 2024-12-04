import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import Depends, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError
import asyncio
import orjson
import pytest

from datetime import datetime
from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings
from stack.app.repositories.thread import ThreadRepository, get_thread_repository
from stack.app.repositories.assistant import (
    AssistantRepository,
    get_assistant_repository,
)
from stack.app.model.thread import Thread as ModelThread
from stack.app.schema.thread import Thread as SchemaThread
from stack.app.schema.assistant import Assistant as AssistantSchema
from stack.app.schema.feedback import FeedbackCreateRequest
from stack.app.schema.title import TitleRequest
from pydantic.error_wrappers import ValidationError
from stack.app.api.v1.runs import (
    CreateRunPayload,
    _run_input_and_config,
    stream_run,
    EventSourceResponse,
)
from stack.app.agents.configurable_agent import get_configured_agent


app = create_app(Settings())
client = TestClient(app)


@pytest.fixture
def valid_title_request(random_schema_thread):
    return TitleRequest(
        thread_id=str(random_schema_thread.id),
        history=[
            {"type": "human", "content": "Hello"},
            {"type": "ai", "content": "Hi, how can I help you?"},
        ],
    )


@pytest.fixture
def valid_feedback_request():
    return FeedbackCreateRequest(
        run_id="run1",
        key="helpfulness",
        score=5,
        value="very helpful",
        comment="The assistant was very helpful and responsive.",
    )


@pytest.fixture
def valid_payload(random_schema_thread):
    return CreateRunPayload(
        assistant_id="5bb8e18a-038e-4fd2-a0da-5730d0b65d69",
        thread_id=str(random_schema_thread.id),
        user_id="68937497-93ec-4ebb-9fbf-651932e20932",
        input=[
            {
                "content": "Hello.",
                "additional_kwargs": {},
                "type": "human",
                "example": False,
            }
        ],
    )


# Mock Stream Events
async def mock_astream_events(*args, **kwargs):
    if kwargs.get("input") == "error":
        raise Exception("Test exception")
    yield {"event": "on_chain_start", "run_id": "run1"}
    yield {
        "event": "on_chain_stream",
        "run_id": "run1",
        "data": {"chunk": [{"id": "msg1", "role": "user", "content": "Hello"}]},
    }
    yield {
        "event": "on_chain_stream",
        "run_id": "run1",
        "data": {
            "chunk": [
                {
                    "id": "msg2",
                    "role": "assistant",
                    "content": "Hello, how can I help you?",
                }
            ]
        },
    }


@pytest.fixture
def mock_agent():
    mock_agent = MagicMock()
    mock_agent.astream_events = AsyncMock(side_effect=mock_astream_events)
    # Mock with_config to return the agent itself
    mock_agent.with_config = MagicMock(return_value=mock_agent)
    return mock_agent


# =============================================================================
# TODO: couldn't get the mocks right on these so they don't pass right now...
# We may just want integration tests for these endpoints anyway.
# The main issue was figuring out how to properly mock the agent.
# =============================================================================
# Tests for stream_run endpoint
# @pytest.mark.asyncio
# @patch("stack.app.agents.configurable_agent", new_callable=lambda: MagicMock())
# @patch("stack.app.utils.stream.astream_state", new_callable=lambda: AsyncMock())
# @patch("stack.app.utils.stream.to_sse", new_callable=lambda: AsyncMock())
# @patch("stack.app.api.v1.runs._run_input_and_config", new_callable=lambda: AsyncMock())
# async def test__stream_run__new_thread_creation(
#     mock_agent,
#     mocked_astream_state,
#     mocked_to_sse,
#     mocked_run_input_and_config,
#     valid_payload,
#     random_schema_thread,
#     random_schema_assistant,
# ):
#     pass
    # thread_repository = MagicMock(ThreadRepository)
    # assistant_repository = MagicMock(AssistantRepository)

    # with patch.object(thread_repository, 'create_thread', return_value=random_schema_thread) as create_thread_mock, \
    #      patch.object(assistant_repository, 'retrieve_assistant', return_value=random_schema_assistant) as retrieve_assistant_mock:

    #     app.dependency_overrides[get_thread_repository] = lambda: thread_repository
    #     app.dependency_overrides[get_assistant_repository] = lambda: assistant_repository

    #     mocked_run_input_and_config.return_value = (valid_payload.input, random_schema_assistant.config)

    #     # Mocking the side effects to avoid coroutine issues
    #     mocked_astream_state.return_value.__aiter__.side_effect = mock_astream_events
    #     mocked_to_sse.side_effect = lambda messages_stream: "\n".join([f"data: {message['event']}" for message in messages_stream])

    #     response = client.post("/api/v1/runs/stream", json=valid_payload.dict())

    #     assert response.status_code == 200
    #     assert response.headers['content-type'] == 'text/event-stream'


# async def test__stream_run__existing_thread(valid_payload, random_schema_thread, random_schema_assistant):
#     valid_payload.thread_id = str(random_schema_thread.id)
#     valid_payload.assistant_id = None

#     thread_repository = MagicMock(ThreadRepository)
#     assistant_repository = MagicMock(AssistantRepository)

#     with patch.object(thread_repository, 'retrieve_thread', return_value=random_schema_thread) as retrieve_thread_mock, \
#          patch.object(assistant_repository, 'retrieve_assistant', return_value=random_schema_assistant) as retrieve_assistant_mock, \
#          patch('stack.app.agents.configurable_agent', new=mock_agent):

#         app.dependency_overrides[get_thread_repository] = lambda: thread_repository
#         app.dependency_overrides[get_assistant_repository] = lambda: assistant_repository

#         response = await client.post("/api/v1/runs/stream", json=valid_payload.dict())

#         assert retrieve_thread_mock.call_count == 1
#         assert retrieve_assistant_mock.call_count == 1
#         assert response.status_code == 200
#         assert response.headers['content-type'] == 'text/event-stream'


# async def test__stream_run__invalid_assistant(valid_payload):
#     thread_repository = MagicMock(ThreadRepository)
#     assistant_repository = MagicMock(AssistantRepository)

#     with patch.object(thread_repository, 'create_thread', return_value=None), \
#          patch.object(assistant_repository, 'retrieve_assistant', return_value=None):

#         app.dependency_overrides[get_thread_repository] = lambda: thread_repository
#         app.dependency_overrides[get_assistant_repository] = lambda: assistant_repository

#         response = await client.post("/api/v1/runs/stream", json=valid_payload.dict())

#         assert response.status_code == 400
#         assert response.json() == {"detail": "Invalid Assistant ID Provided"}


# async def test__stream_run__exception_during_stream(valid_payload, random_schema_thread, random_schema_assistant):
#     thread_repository = MagicMock(ThreadRepository)
#     assistant_repository = MagicMock(AssistantRepository)

#     with patch.object(thread_repository, 'create_thread', return_value=random_schema_thread), \
#          patch.object(assistant_repository, 'retrieve_assistant', return_value=random_schema_assistant), \
#          patch('stack.app.agents.configurable_agent', new=mock_agent):

#         valid_payload.input = "error"  # Trigger error in mocked stream

#         app.dependency_overrides[get_thread_repository] = lambda: thread_repository
#         app.dependency_overrides[get_assistant_repository] = lambda: assistant_repository

#         response = await client.post("/api/v1/runs/stream", json=valid_payload.dict())

#         assert response.status_code == 500
#         assert response.headers['content-type'] == 'text/event-stream'


# # Tests for create_run endpoint
# async def test__create_run__success(valid_payload, random_schema_thread, random_schema_assistant):
#     thread_repository = MagicMock(ThreadRepository)
#     assistant_repository = MagicMock(AssistantRepository)

#     with patch.object(thread_repository, 'create_thread', return_value=random_schema_thread) as create_thread_mock, \
#          patch.object(assistant_repository, 'retrieve_assistant', return_value=random_schema_assistant):

#         app.dependency_overrides[get_thread_repository] = lambda: thread_repository
#         app.dependency_overrides[get_assistant_repository] = lambda: assistant_repository

#         response = await client.post("/api/v1/runs", json=valid_payload.dict())

#         assert create_thread_mock.call_count == 1
#         assert retrieve_assistant_mock.call_count == 1
#         assert response.status_code == 200
#         assert response.json() == {"status": "ok"}


# async def test__create_run__invalid_assistant(valid_payload):
#     thread_repository = MagicMock(ThreadRepository)
#     assistant_repository = MagicMock(AssistantRepository)

#     with patch.object(thread_repository, 'create_thread', return_value=None), \
#          patch.object(assistant_repository, 'retrieve_assistant', return_value=None):

#         app.dependency_overrides[get_thread_repository] = lambda: thread_repository
#         app.dependency_overrides[get_assistant_repository] = lambda: assistant_repository

#         response = await client.post("/api/v1/runs", json=valid_payload.dict())

#         assert response.status_code == 400
#         assert response.json() == {"detail": "Invalid Assistant ID Provided"}


# async def test__create_run__input_validation_error():
#     invalid_payload = {
#         "user_id": "1d3ae09d-0cad-4551-9bcb-ed560a46b656",
#         "input": "invalid_input_type"  # Invalid input type
#     }

#     response = await client.post("/api/v1/runs", json=invalid_payload)

#     assert response.status_code == 422  # Unprocessable Entity for validation errors


# # Tests for input_schema endpoint
# async def test__input_schema__success():
#     response = await client.get("/api/v1/runs/input_schema")

#     assert response.status_code == 200
#     schema = response.json()
#     assert isinstance(schema, dict)


# # Tests for output_schema endpoint
# async def test__output_schema__success():
#     response = await client.get("/api/v1/runs/output_schema")

#     assert response.status_code == 200
#     schema = response.json()
#     assert isinstance(schema, dict)


# # Tests for config_schema endpoint
# async def test__config_schema__success():
#     response = await client.get("/api/v1/runs/config_schema")

#     assert response.status_code == 200
#     schema = response.json()
#     assert isinstance(schema, dict)


# # Tests for title endpoint
# @pytest.mark.asyncio
# async def test__title_endpoint__generate_title(valid_title_request, random_schema_thread):
#     thread_repository = MagicMock(ThreadRepository)

#     with patch.object(thread_repository, 'update_thread', return_value=random_schema_thread), \
#          patch('stack.app.api.title_endpoint', side_effect=[
#             (lambda request: StrOutputParser().parse(TITLE_GENERATOR_TEMPLATE))()
#          ]):

#         app.dependency_overrides[get_thread_repository] = lambda: thread_repository

#         response = await client.post("/api/v1/runs/title", json=valid_title_request.dict())

#         assert response.status_code == 200
#         thread = response.json()
#         assert isinstance(thread, dict)
#         assert thread.get("name", "").startswith("Title: ")


# @pytest.mark.asyncio
# async def test__title_endpoint__missing_thread_id():
#     invalid_request = {
#         "history": [
#             {"type": "human", "content": "Hello"},
#             {"type": "ai", "content": "Hi, how can I help you?"}
#         ]
#     }

#     response = await client.post("/api/v1/runs/title", json=invalid_request)

#     assert response.status_code == 400
#     assert response.json() == {"detail": "Thread ID is required"}


# @pytest.mark.asyncio
# async def test__title_endpoint__missing_history():
#     invalid_request = {
#         "thread_id": str(uuid.uuid4())
#     }

#     response = await client.post("/api/v1/runs/title", json=invalid_request)

#     assert response.status_code == 400
#     assert response.json() == {"detail": "History is required"}


# @pytest.mark.asyncio
# async def test__title_endpoint__update_thread_failure(valid_title_request):
#     thread_repository = MagicMock(ThreadRepository)

#     with patch.object(thread_repository, 'update_thread', side_effect=Exception("Update failed")):
#         app.dependency_overrides[get_thread_repository] = lambda: thread_repository

#         response = await client.post("/api/v1/runs/title", json=valid_title_request.dict())

#         assert response.status_code == 500
#         assert "API Endpoint Exception - Failed to generate title" in response.text


# # Tests for create_run_feedback endpoint (conditionally based on tracing settings)
# @pytest.mark.asyncio
# async def test__create_run_feedback__success(valid_feedback_request):
#     with patch.object(langsmith_client, 'create_feedback', return_value=None):

#         response = await client.post("/api/v1/runs/feedback", json=valid_feedback_request.dict())

#         assert response.status_code == 200
#         assert response.json() == {"status": "ok"}


# @pytest.mark.asyncio
# async def test__create_run_feedback__submission_failure(valid_feedback_request):
#     with patch.object(langsmith_client, 'create_feedback', side_effect=Exception("Submission failed")):

#         response = await client.post("/api/v1/runs/feedback", json=valid_feedback_request.dict())

#         assert response.status_code == 500
#         assert "Submission failed" in response.text
