import uuid
from datetime import datetime
from unittest.mock import patch

import pytest

from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings
from stack.app.model.thread import Thread as ModelThread
from stack.app.model.user import User as ModelUser
from stack.app.model.message import Message as MessageModel
from stack.app.schema.user import User as SchemaUser
from stack.app.schema.assistant import Assistant
from stack.app.schema.file import FileSchema
from stack.app.schema.thread import Thread as ThreadSchema

from stack.app.core.auth.auth_config import ENABLED_AUTH_STRATEGY_MAPPING

app = create_app(Settings())


def passthrough(repository):
    def wrapper():
        return repository

    return wrapper


@pytest.fixture
def random_schema_user() -> SchemaUser:
    return SchemaUser(
        user_id=str(uuid.uuid4()),
        email="test@gmail.com",
        password="abcd",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def random_model_user() -> ModelUser:
    return ModelUser(
        user_id=str(uuid.uuid4()),
        email="test@gmail.com",
        password="abcd",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def random_model_thread() -> ModelThread:
    return ModelThread(
        id=str(uuid.uuid4()),
        assistant_id=str(uuid.uuid4()),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def random_schema_thread() -> ThreadSchema:
    return ThreadSchema(
        id=str(uuid.uuid4()),
        assistant_id=str(uuid.uuid4()),
        name="Test Thread",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def random_schema_assistant() -> Assistant:
    return Assistant(
        id=str(uuid.uuid4()),
        config={
            "configurable": {
                "type": "agent",
                "type==agent/agent_type": "GPT 3.5 Turbo",
                "type==agent/retrieval_description": "Can be used to look up information",
                "type==agent/system_message": "You are a helpful assistant.",
                "type==agent/tools": [],
                "type==chat_retrieval/llm_type": "GPT 3.5 Turbo",
                "type==chat_retrieval/system_message": "You are a helpful assistant.",
                "type==chatbot/llm_type": "GPT 3.5 Turbo",
                "type==chatbot/system_message": "You are a helpful assistant.",
            }
        },
        name="My Assistant",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def random_schema_file() -> FileSchema:
    return FileSchema(
        id=uuid.uuid4(),
        purpose="assistants",
        filename="my_file.pdf",
        bytes=123,
        mime_type="application/pdf",
        source="files/my_file.pdf",
        kwargs={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def random_model_message() -> MessageModel:
    return MessageModel(
        id=str(uuid.uuid4()),
        thread_id=str(uuid.uuid4()),
        assistant_id=str(uuid.uuid4()),
        content="Test Message",
        type="AI",
        example=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture(autouse=True)
def mock_auth_secret_key_env(monkeypatch):
    monkeypatch.setenv("AUTH_SECRET_KEY", "test")


@pytest.fixture(autouse=True)
def mock_google_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test")


@pytest.fixture(autouse=True)
def mock_oidc_env(monkeypatch):
    monkeypatch.setenv("OIDC_CLIENT_ID", "test")
    monkeypatch.setenv("OIDC_CLIENT_SECRET", "test")
    monkeypatch.setenv("OIDC_CONFIG_ENDPOINT", "test")


@pytest.fixture(autouse=True)
def mock_enabled_auth(mock_google_env, mock_oidc_env):
    # Can directly use class since no external calls are made
    from stack.app.core.auth.strategies.basic import BasicAuthentication
    from stack.app.core.auth.strategies.google_oauth import GoogleOAuth
    from stack.app.core.auth.strategies.oidc import OpenIDConnect

    mocked_strategies = {
        BasicAuthentication.NAME: BasicAuthentication(),
        GoogleOAuth.NAME: GoogleOAuth(),
        OpenIDConnect.NAME: OpenIDConnect(),
    }

    with patch.dict(ENABLED_AUTH_STRATEGY_MAPPING, mocked_strategies) as mock:
        yield mock
