from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

from starlette.testclient import TestClient

from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings
from stack.app.repositories.assistant import (
    AssistantRepository,
    get_assistant_repository,
)
from stack.app.schema.assistant import Assistant
from stack.app.repositories.file import FileRepository, get_file_repository
from stack.tests.unit.conftest import passthrough
from stack.app.schema.assistant import CreateAssistantSchema, UpdateAssistantSchema
from stack.app.core.configuration import settings
from stack.app.schema.assistant import CreateAssistantFileSchema


app = create_app(Settings())
client = TestClient(app)


async def test__create_assistant__responds_correctly(random_schema_assistant):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    create_data = CreateAssistantSchema(name="Assistant 1", config={"type": "chatbot"})
    with patch.object(
        assistant_repository, "create_assistant", return_value=random_schema_assistant
    ) as method:
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )

        # Act
        response = client.post("/api/v1/assistants", json=create_data.model_dump())

        # Assert
        assert method.call_count == 1
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(random_schema_assistant.id)


async def test__retrieve_assistants__responds_correctly(random_schema_assistant):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    with patch.object(
        assistant_repository,
        "retrieve_assistants",
        return_value=[random_schema_assistant],
    ) as method:
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )

        # Act
        response = client.get("/api/v1/assistants")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(random_schema_assistant.id)


async def test__retrieve_assistant__responds_correctly(random_schema_assistant):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    with patch.object(
        assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
    ) as method:
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )

        # Act
        response = client.get(f"/api/v1/assistants/{random_schema_assistant.id}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(random_schema_assistant.id)


async def test__retrieve_assistant__assistant_not_found_404():
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    with patch.object(
        assistant_repository, "retrieve_assistant", return_value=None
    ) as method:
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )

        # Act
        response = client.get(f"/api/v1/assistants/{uuid4()}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test__update_assistant__responds_correctly(random_schema_assistant):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    update_data = UpdateAssistantSchema(name="Updated Assistant")
    update_data = UpdateAssistantSchema(name="Updated Assistant")

    # Create an updated version of the assistant
    updated_assistant = Assistant(
        **{**random_schema_assistant.model_dump(), "name": "Updated Assistant"}
    )

    with patch.object(
        assistant_repository, "update_assistant", return_value=updated_assistant
    ) as update_method, patch.object(
        assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
    ) as retrieve_method, patch(
        "stack.app.api.v1.assistants.get_header_user_id",
        return_value=settings.DEFAULT_USER_ID,
    ) as mock_get_user_id:
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )

        # Act
        response = client.patch(
            f"/api/v1/assistants/{random_schema_assistant.id}",
            json=update_data.model_dump(),
            headers={"User-Id": settings.DEFAULT_USER_ID},
        )

        # Assert
        assert retrieve_method.call_count == 1
        assert update_method.call_count == 1
        assert mock_get_user_id.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(random_schema_assistant.id)
        assert data["name"] == "Updated Assistant"


async def test__update_assistant__assistant_not_found_404():
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    update_data = UpdateAssistantSchema(name="Updated Assistant")
    non_existent_id = str(uuid4())

    with patch.object(
        assistant_repository, "retrieve_assistant", return_value=None
    ) as retrieve_method, patch(
        "stack.app.api.v1.assistants.get_header_user_id",
        return_value=settings.DEFAULT_USER_ID,
    ) as mock_get_user_id:
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )

        # Act
        response = client.patch(
            f"/api/v1/assistants/{non_existent_id}",
            json=update_data.model_dump(),
            headers={"User-Id": settings.DEFAULT_USER_ID},
        )

        # Assert
        assert retrieve_method.call_count == 1
        assert mock_get_user_id.call_count == 1
        assert response.status_code == 404
        assert response.json() == {"detail": "Assistant not found"}


async def test__delete_assistant__responds_correctly(random_schema_assistant):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)

    with patch.object(
        assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
    ) as retrieve_method, patch.object(
        assistant_repository, "delete_assistant", return_value=None
    ) as delete_method, patch(
        "stack.app.api.v1.assistants.get_header_user_id",
        return_value=settings.DEFAULT_USER_ID,
    ) as mock_get_user_id:
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )

        # Act
        response = client.delete(
            f"/api/v1/assistants/{random_schema_assistant.id}",
            headers={"User-Id": settings.DEFAULT_USER_ID},
        )

        # Assert
        assert retrieve_method.call_count == 1
        assert delete_method.call_count == 1
        assert mock_get_user_id.call_count == 1
        assert response.status_code == 204
        assert response.content == b""  # No content for successful delete


# Assistant Files


async def test__create_assistant_file__assistant_not_found_404(random_schema_file):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    file_repository = MagicMock(FileRepository)
    non_existent_assistant_id = str(uuid4())
    create_data = CreateAssistantFileSchema(file_id=str(random_schema_file.id))

    with patch.object(
        assistant_repository, "retrieve_assistant", return_value=None
    ) as retrieve_assistant_method, patch.object(
        file_repository, "retrieve_file", return_value=random_schema_file
    ) as retrieve_file_method, patch(
        "stack.app.api.v1.assistants.get_header_user_id",
        return_value=settings.DEFAULT_USER_ID,
    ) as mock_get_user_id, patch(
        "stack.app.api.v1.assistants.get_ingest_tasks_from_config", return_value=[]
    ) as mock_get_ingest_tasks, patch(
        "asyncio.gather", new_callable=AsyncMock
    ) as mock_gather:
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )
        app.dependency_overrides[get_file_repository] = passthrough(file_repository)

        # Act
        response = client.post(
            f"/api/v1/assistants/{non_existent_assistant_id}/files",
            json=create_data.model_dump(),
            headers={"User-Id": settings.DEFAULT_USER_ID},
        )

        # Assert
        assert retrieve_assistant_method.call_count == 1
        assert retrieve_file_method.call_count == 1
        assert mock_get_user_id.call_count == 1
        assert mock_get_ingest_tasks.call_count == 0
        assert mock_gather.call_count == 0
        assert response.status_code == 404
        assert response.json() == {"detail": "Assistant not found"}


async def test__retrieve_assistant_files__responds_correctly(
    random_schema_file, random_schema_assistant
):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    file_repository = MagicMock(FileRepository)
    with patch.object(
        assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
    ) as method_a, patch.object(
        file_repository, "retrieve_files_by_ids", return_value=[random_schema_file]
    ) as method_f:
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )
        app.dependency_overrides[get_file_repository] = passthrough(file_repository)

        # Act
        response = client.get(f"/api/v1/assistants/{random_schema_assistant.id}/files")

        # Assert
        assert method_a.call_count == 1
        assert method_f.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(random_schema_file.id)


async def test__create_assistant_file__responds_correctly(
    random_schema_file, random_schema_assistant
):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    file_repository = MagicMock(FileRepository)
    create_data = CreateAssistantFileSchema(file_id=str(random_schema_file.id))

    # Ensure random_schema_assistant has file_ids attribute
    random_schema_assistant.file_ids = []

    with patch.object(
        assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
    ) as retrieve_assistant_method, patch.object(
        file_repository, "retrieve_file", return_value=random_schema_file
    ) as retrieve_file_method, patch(
        "stack.app.api.v1.assistants.get_header_user_id",
        return_value=settings.DEFAULT_USER_ID,
    ) as mock_get_user_id, patch(
        "stack.app.api.v1.assistants.get_ingest_tasks_from_config",
        return_value=[AsyncMock()],
    ) as mock_get_ingest_tasks, patch(
        "asyncio.gather", new_callable=AsyncMock
    ) as mock_gather, patch.object(
        assistant_repository,
        "add_file_to_assistant",
        return_value=random_schema_assistant,
    ) as add_file_method:
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )
        app.dependency_overrides[get_file_repository] = passthrough(file_repository)

        # Act
        response = client.post(
            f"/api/v1/assistants/{random_schema_assistant.id}/files",
            json=create_data.model_dump(),
            headers={"User-Id": settings.DEFAULT_USER_ID},
        )

        # Assert
        assert retrieve_assistant_method.call_count == 1
        assert retrieve_file_method.call_count == 1
        assert mock_get_user_id.call_count == 1
        assert mock_get_ingest_tasks.call_count == 1
        assert mock_gather.call_count == 1
        assert add_file_method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["file_id"] == str(random_schema_file.id)
        assert data["assistant_id"] == str(random_schema_assistant.id)


async def test__delete_assistant_file__responds_correctly(
    random_schema_file, random_schema_assistant
):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)

    # Ensure random_schema_assistant has file_ids attribute
    random_schema_assistant.file_ids = [str(random_schema_file.id)]
    random_schema_assistant.user_id = settings.DEFAULT_USER_ID

    mock_service = AsyncMock()
    mock_service.delete = AsyncMock(return_value=10)

    with patch.object(
        assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
    ) as retrieve_method, patch.object(
        assistant_repository,
        "remove_file_reference_from_assistant",
        return_value=random_schema_assistant,
    ) as remove_file_method, patch(
        "stack.app.api.v1.assistants.get_vector_service", return_value=mock_service
    ) as mock_get_vector_service, patch(
        "stack.app.api.v1.assistants.get_header_user_id",
        return_value=settings.DEFAULT_USER_ID,
    ) as mock_get_user_id:
        app.dependency_overrides[get_assistant_repository] = passthrough(
            assistant_repository
        )

        # Act
        response = client.delete(
            f"/api/v1/assistants/{random_schema_assistant.id}/files/{random_schema_file.id}",
            headers={"User-Id": settings.DEFAULT_USER_ID},
        )

        # Assert
        assert retrieve_method.call_count == 1
        assert remove_file_method.call_count == 1
        assert mock_get_vector_service.call_count == 1
        assert mock_service.delete.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(random_schema_assistant.id)

        # Verify the call to vector service delete method
        mock_service.delete.assert_called_once_with(
            str(random_schema_file.id), str(random_schema_assistant.id)
        )
