import uuid
from datetime import datetime
import pytest
from unittest.mock import patch, MagicMock

from starlette.testclient import TestClient
from fastapi import HTTPException

from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings
from stack.app.repositories.thread import ThreadRepository, get_thread_repository
from stack.app.repositories.message import MessageRepository, get_message_repository
from stack.app.repositories.user import UserRepository, get_user_repository
from stack.app.repositories.assistant import (
    AssistantRepository,
    get_assistant_repository,
)
from stack.tests.unit.conftest import passthrough

app = create_app(Settings())
client = TestClient(app)


@pytest.fixture
def random_updated_thread(random_schema_thread):
    # Ensuring the UUID strings are the same
    return {
        "id": str(random_schema_thread.id),
        "user_id": random_schema_thread.user_id,
        "assistant_id": random_schema_thread.assistant_id,
        "name": "Updated Thread",
        "created_at": random_schema_thread.created_at.isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


async def test__create_thread_responds__correctly(
    random_model_thread, random_model_user, random_schema_assistant
):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    assistant_repository = MagicMock(AssistantRepository)
    user_repository = MagicMock(UserRepository)

    # Ensure the random_model_thread, random_model_user, and random_schema_assistant return dicts with stringified UUIDs
    random_model_thread.id = str(random_model_thread.id)
    random_model_user.user_id = str(random_model_user.user_id)
    random_schema_assistant.id = str(random_schema_assistant.id)

    with patch.object(
        assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
    ), patch.object(
        user_repository, "retrieve_by_user_id", return_value=random_model_user
    ), patch.object(
        thread_repository, "create_thread", return_value=random_model_thread
    ) as method:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.post(
            "/api/v1/threads",
            json={
                "assistant_id": random_schema_assistant.id,
                "user_id": random_model_user.user_id,
                "name": random_model_thread.name,
            },
        )

        # Assert
        assert method.call_count == 1
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == random_model_thread.id


async def test__retrieve_threads__responds_correctly(random_schema_thread):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(
        thread_repository, "retrieve_threads", return_value=[random_schema_thread]
    ) as method:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        response = client.get("/api/v1/threads")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(random_schema_thread.id)


async def test__retrieve_thread__responds_correctly(random_schema_thread):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(
        thread_repository, "retrieve_thread", return_value=random_schema_thread
    ) as method:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        response = client.get(f"/api/v1/threads/{random_schema_thread.id}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(random_schema_thread.id)


async def test__update_thread__responds_correctly(
    random_schema_thread, random_updated_thread
):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(
        thread_repository, "update_thread", return_value=random_updated_thread
    ) as method:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        response = client.patch(
            f"/api/v1/threads/{str(random_schema_thread.id)}",
            json={"name": "Updated Thread"},
        )

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == random_updated_thread["id"]
        assert data["name"] == "Updated Thread"


async def test__delete_thread__responds_correctly(random_schema_thread):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(thread_repository, "delete_thread", return_value=None) as method:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        response = client.delete(f"/api/v1/threads/{random_schema_thread.id}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 204


async def test__retrieve_checkpoint_messages_for_thread__responds_correctly(
    random_model_thread,
):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    checkpoints = [{"checkpoint_id": "123", "content": "Test checkpoint message"}]
    with patch.object(
        thread_repository, "get_thread_checkpoints", return_value=checkpoints
    ) as method:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        response = client.get(f"/api/v1/threads/{random_model_thread.id}/checkpoints")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["checkpoint_id"] == "123"


async def test_retrieve_thread_responds_404():
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(
        thread_repository, "retrieve_thread", return_value=None
    ) as method:
        app.dependency_overrides[get_thread_repository] = lambda: thread_repository

        # Act
        non_existent_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/threads/{non_existent_id}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test_update_thread_responds_404():
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(thread_repository, "update_thread", return_value=None) as method:
        app.dependency_overrides[get_thread_repository] = lambda: thread_repository

        # Act
        non_existent_id = str(uuid.uuid4())
        response = client.patch(
            f"/api/v1/threads/{non_existent_id}", json={"name": "Updated Thread"}
        )

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test_delete_thread_responds_404():
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(
        thread_repository,
        "delete_thread",
        side_effect=HTTPException(status_code=404, detail="Thread not found"),
    ) as method:
        app.dependency_overrides[get_thread_repository] = lambda: thread_repository

        # Act
        non_existent_id = str(uuid.uuid4())
        response = client.delete(f"/api/v1/threads/{non_existent_id}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test_retrieve_messages_by_thread_id_responds_404():
    message_repository = MagicMock(MessageRepository)
    with patch.object(
        message_repository,
        "retrieve_messages_by_thread_id",
        side_effect=HTTPException(status_code=404, detail="Thread not found"),
    ) as method:
        app.dependency_overrides[get_message_repository] = lambda: message_repository

        # Act
        non_existent_thread_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/threads/{non_existent_thread_id}/messages")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test_retrieve_checkpoint_messages_for_thread_responds_404():
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(
        thread_repository,
        "get_thread_checkpoints",
        side_effect=HTTPException(status_code=404, detail="Thread not found"),
    ) as method:
        app.dependency_overrides[get_thread_repository] = lambda: thread_repository

        # Act
        non_existent_thread_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/threads/{non_existent_thread_id}/checkpoints")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404
