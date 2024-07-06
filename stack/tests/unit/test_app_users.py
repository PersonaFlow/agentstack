from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient

from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings, settings
from stack.app.repositories.thread import ThreadRepository, get_thread_repository
from stack.app.repositories.user import UserRepository, get_user_repository
from stack.tests.unit.conftest import passthrough

app = create_app(Settings())
client = TestClient(app)

# Mock for default user
default_user = {
    "context": {
        "user_id": "default",
    }
}


async def test__retrieve_me__responds_correctly(random_schema_user):
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "retrieve_by_user_id", return_value=random_schema_user
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.get("/api/v1/users/me")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == random_schema_user.user_id


async def test__update_me__responds_correctly(random_schema_user):
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "update_by_user_id", return_value=random_schema_user
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.patch(
            "/api/v1/users/me",
            json={"username": "new_username"},
            headers={"User-Id": settings.DEFAULT_USER_ID},
        )

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == random_schema_user.user_id


async def test__delete_me__responds_correctly(random_schema_user):
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "delete_by_user_id", return_value=random_schema_user
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.delete(
            "/api/v1/users/me", headers={"User-Id": settings.DEFAULT_USER_ID}
        )

        # Assert
        assert method.call_count == 1
        assert response.status_code == 204


async def test__retrieve_my_threads__responds_correctly(random_model_thread):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(
        thread_repository,
        "retrieve_threads_by_user_id",
        return_value=[random_model_thread],
    ) as method:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        response = client.get(
            "/api/v1/users/me/threads", headers={"User-Id": settings.DEFAULT_USER_ID}
        )

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(random_model_thread.id)


async def test__retrieve_me__user_not_found_404():
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "retrieve_by_user_id", return_value=None
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.get("/api/v1/users/me")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test__update_me__responds_correctly(random_schema_user):
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "update_by_user_id", return_value=random_schema_user
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.patch("/api/v1/users/me", json={"username": "new_username"})

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == random_schema_user.user_id


async def test__update_me__user_not_found_404():
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "update_by_user_id", return_value=None
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.patch("/api/v1/users/me", json={"username": "new_username"})

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test__delete_me__user_not_found_404():
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "delete_by_user_id", return_value=None
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.delete("/api/v1/users/me")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test__retrieve_my_threads__grouped_responds_correctly(random_model_thread):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(
        thread_repository,
        "retrieve_threads_by_user_id",
        return_value=[random_model_thread],
    ) as method:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        response = client.get("/api/v1/users/me/threads?grouped=true")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert any(random_model_thread.id in str(threads) for threads in data.values())
