import uuid
from datetime import datetime
import pytest
from unittest.mock import patch, MagicMock
from stack.app.schema.thread import UpdateThreadSchema
from starlette.testclient import TestClient
from fastapi import HTTPException
from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings, settings
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


async def test__update_thread__responds_correctly(random_schema_thread, random_updated_thread):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    update_data = UpdateThreadSchema(name="Updated Thread")

    with patch.object(
        thread_repository, "retrieve_thread", return_value=random_schema_thread
    ) as retrieve_method, patch.object(
        thread_repository, "update_thread", return_value=random_updated_thread
    ) as update_method, patch(
        "stack.app.api.v1.threads.get_header_user_id", return_value=settings.DEFAULT_USER_ID
    ) as mock_get_user_id:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        response = client.patch(
            f"/api/v1/threads/{str(random_schema_thread.id)}",
            json=update_data.model_dump(),
            headers={"User-Id": settings.DEFAULT_USER_ID}
        )

        # Assert
        assert retrieve_method.call_count == 1
        assert update_method.call_count == 1
        assert mock_get_user_id.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == random_updated_thread["id"]
        assert data["name"] == "Updated Thread"

        # Verify the calls
        retrieve_method.assert_called_once_with(thread_id=str(random_schema_thread.id))
        update_method.assert_called_once_with(thread_id=str(random_schema_thread.id), data=update_data.model_dump())


async def test__delete_thread__responds_correctly(random_schema_thread):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)

    with patch.object(
        thread_repository, "retrieve_thread", return_value=random_schema_thread
    ) as retrieve_method, patch.object(
        thread_repository, "delete_thread", return_value=None
    ) as delete_method, patch(
        "stack.app.api.v1.threads.get_header_user_id", return_value=settings.DEFAULT_USER_ID
    ) as mock_get_user_id:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        response = client.delete(
            f"/api/v1/threads/{random_schema_thread.id}",
            headers={"User-Id": settings.DEFAULT_USER_ID}
        )

        # Assert
        assert retrieve_method.call_count == 1
        assert delete_method.call_count == 1
        assert mock_get_user_id.call_count == 1
        assert response.status_code == 204

        # Verify the calls
        retrieve_method.assert_called_once_with(thread_id=str(random_schema_thread.id))
        delete_method.assert_called_once_with(thread_id=str(random_schema_thread.id))


async def test_retrieve_thread_responds_404():
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(
        thread_repository, "retrieve_thread", return_value=None
    ) as retrieve_method, patch(
        "stack.app.api.v1.threads.get_header_user_id", return_value=settings.DEFAULT_USER_ID
    ) as mock_get_user_id:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        non_existent_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/threads/{non_existent_id}",
            headers={"User-Id": settings.DEFAULT_USER_ID}
        )

        # Assert
        assert retrieve_method.call_count == 1
        assert mock_get_user_id.call_count == 1
        assert response.status_code == 404
        assert response.json() == {"detail": "Thread not found"}

        # Verify the call
        retrieve_method.assert_called_once_with(thread_id=non_existent_id)


async def test_retrieve_thread_state_responds_correctly(
    random_schema_thread, random_schema_assistant
):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    assistant_repository = MagicMock(AssistantRepository)
    expected_state = {"key": "value"}

    # Ensure random_schema_thread has the necessary attributes
    random_schema_thread.user_id = settings.DEFAULT_USER_ID
    random_schema_thread.assistant_id = random_schema_assistant.id

    with patch.object(
        thread_repository, "retrieve_thread", return_value=random_schema_thread
    ) as retrieve_thread_mock, patch.object(
        assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
    ) as retrieve_assistant_mock, patch.object(
        thread_repository, "get_thread_state", return_value=expected_state
    ) as get_thread_state_mock, patch(
        "stack.app.api.v1.threads.get_header_user_id", return_value=settings.DEFAULT_USER_ID
    ) as mock_get_user_id:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)
        app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)

        # Act
        response = client.get(
            f"/api/v1/threads/{random_schema_thread.id}/state",
            headers={"User-Id": settings.DEFAULT_USER_ID}
        )

        # Assert
        assert retrieve_thread_mock.call_count == 1
        assert retrieve_assistant_mock.call_count == 1
        assert get_thread_state_mock.call_count == 1
        assert mock_get_user_id.call_count == 1
        assert response.status_code == 200
        assert response.json() == expected_state

        # Verify the calls
        retrieve_thread_mock.assert_called_once_with(thread_id=str(random_schema_thread.id))
        retrieve_assistant_mock.assert_called_once_with(assistant_id=random_schema_thread.assistant_id)
        get_thread_state_mock.assert_called_once_with(thread_id=str(random_schema_thread.id), assistant=random_schema_assistant)


async def test_retrieve_thread_state_responds_404_when_thread_not_found():
    # Arrange
    thread_repository = MagicMock(ThreadRepository)

    with patch.object(thread_repository, "retrieve_thread", return_value=None):
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        non_existent_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/threads/{non_existent_id}/state")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Thread not found"


async def test_add_thread_state_responds_correctly(
    random_schema_thread, random_schema_assistant
):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    assistant_repository = MagicMock(AssistantRepository)
    expected_state = {"key": "new_value"}
    payload = {
        "config": {"configurable": {"thread_id": str(random_schema_thread.id)}},
        "values": {"key": "new_value"},
    }

    with patch.object(
        thread_repository, "retrieve_thread", return_value=random_schema_thread
    ), patch.object(
        assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
    ), patch.object(
        thread_repository, "update_thread_state", return_value=expected_state
    ):
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )

        # Act
        response = client.post(
            f"/api/v1/threads/{random_schema_thread.id}/state", json=payload
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == expected_state


async def test_add_thread_state_responds_404_when_thread_not_found():
    # Arrange
    thread_repository = MagicMock(ThreadRepository)

    with patch.object(thread_repository, "retrieve_thread", return_value=None):
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        non_existent_id = str(uuid.uuid4())
        payload = {
            "config": {"configurable": {"thread_id": non_existent_id}},
            "values": {"key": "value"},
        }
        response = client.post(f"/api/v1/threads/{non_existent_id}/state", json=payload)

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Thread not found"


async def test_get_thread_history_responds_correctly(
    random_schema_thread, random_schema_assistant
):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    assistant_repository = MagicMock(AssistantRepository)
    expected_history = [{"message": "Hello"}, {"message": "Hi there"}]

    with patch.object(
        thread_repository, "retrieve_thread", return_value=random_schema_thread
    ), patch.object(
        assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
    ), patch.object(
        thread_repository, "get_thread_history", return_value=expected_history
    ):
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )

        # Act
        response = client.get(f"/api/v1/threads/{random_schema_thread.id}/history")

        # Assert
        assert response.status_code == 200
        assert response.json() == expected_history


async def test_get_thread_history_responds_404_when_thread_not_found():
    # Arrange
    thread_repository = MagicMock(ThreadRepository)

    with patch.object(thread_repository, "retrieve_thread", return_value=None):
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        non_existent_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/threads/{non_existent_id}/history")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Thread not found"
