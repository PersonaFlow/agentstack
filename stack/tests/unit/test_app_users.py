from unittest.mock import patch, MagicMock

from starlette.testclient import TestClient

from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings
from stack.app.repositories.thread import ThreadRepository, get_thread_repository
from stack.app.repositories.user import UserRepository, get_user_repository
from stack.tests.unit.conftest import passthrough

app = create_app(Settings())
client = TestClient(app)


async def test__retrieve_users__responds_correctly(random_schema_user):
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "retrieve_users", return_value=[random_schema_user]
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.get("/api/v1/users")

        # Assert

        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == random_schema_user.user_id


async def test__retrieve_user__responds_correctly(random_schema_user):
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "retrieve_by_user_id", return_value=random_schema_user
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.get(f"/api/v1/users/{random_schema_user.user_id}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == random_schema_user.user_id


async def test__retrieve_user__user_not_found_404():
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "retrieve_by_user_id", return_value=None
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.get(f"/api/v1/users/asdf")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test__create_user__responds_correctly(random_model_user):
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "create_user", return_value=random_model_user
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.post(
            f"/api/v1/users",
            json={"user_id": random_model_user.user_id, "email": "test@example.com"},
        )

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == random_model_user.user_id


async def test__update_user__responds_correctly(random_model_user):
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "update_by_user_id", return_value=random_model_user
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.patch(
            f"/api/v1/users/{random_model_user.user_id}", json={"user_name": "asdf"}
        )

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == random_model_user.user_id


async def test__update_user__failed_update_404():
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "update_by_user_id", return_value=None
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.patch(f"/api/v1/users/asdf", json={"user_name": "asdf"})

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test__delete_user__responds_correctly(random_model_user):
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "delete_by_user_id", return_value=random_model_user
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.delete(f"/api/v1/users/{random_model_user.user_id}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 204


async def test__delete_user__failed_update_404():
    # Arrange
    user_repository = MagicMock(UserRepository)
    with patch.object(
        user_repository, "delete_by_user_id", return_value=None
    ) as method:
        app.dependency_overrides[get_user_repository] = passthrough(user_repository)

        # Act
        response = client.delete(f"/api/v1/users/asdf")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test__retrieve_user_threads__responds_correctly(random_model_thread):
    # Arrange
    thread_repository = MagicMock(ThreadRepository)
    with patch.object(
        thread_repository,
        "retrieve_threads_by_user_id",
        return_value=[random_model_thread],
    ) as method:
        app.dependency_overrides[get_thread_repository] = passthrough(thread_repository)

        # Act
        response = client.get(f"/api/v1/users/{random_model_thread.user_id}/threads")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        assert len(response.json()) == 1
