from unittest.mock import patch, MagicMock
from uuid import uuid4

from starlette.testclient import TestClient

from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings
from stack.app.repositories.assistant import AssistantRepository, get_assistant_repository
from stack.app.repositories.file import FileRepository, get_file_repository
from stack.tests.unit.conftest import passthrough
from stack.app.schema.assistant import CreateAssistantSchema, UpdateAssistantSchema

app = create_app(Settings())
client = TestClient(app)


async def test__create_assistant__responds_correctly(random_schema_assistant):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    create_data = CreateAssistantSchema(name="Assistant 1", config={"type": "chatbot"})
    with patch.object(
        assistant_repository, "create_assistant", return_value=random_schema_assistant
    ) as method:
        app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)

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
        assistant_repository, "retrieve_assistants", return_value=[random_schema_assistant]
    ) as method:
        app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)

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
        app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)

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
        app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)

        # Act
        response = client.get(f"/api/v1/assistants/{uuid4()}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test__update_assistant__responds_correctly(random_schema_assistant):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    update_data = UpdateAssistantSchema(name="Updated Assistant")
    with patch.object(
        assistant_repository, "update_assistant", return_value=random_schema_assistant
    ) as method:
        app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)

        # Act
        response = client.patch(f"/api/v1/assistants/{random_schema_assistant.id}", json=update_data.model_dump())

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(random_schema_assistant.id)


async def test__update_assistant__assistant_not_found_404():
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    with patch.object(
        assistant_repository, "update_assistant", return_value=None
    ) as method:
        app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)

        # Act
        response = client.patch(f"/api/v1/assistants/{uuid4()}", json={"name": "Updated Assistant"})

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404


async def test__delete_assistant__responds_correctly(random_schema_assistant):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    with patch.object(
        assistant_repository, "delete_assistant", return_value=random_schema_assistant
    ) as method:
        app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)

        # Act
        response = client.delete(f"/api/v1/assistants/{random_schema_assistant.id}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 204

# TODO: Need to spend some more time with this one
# async def test__create_assistant_file__responds_correctly(random_schema_file, random_schema_assistant):
#     # Arrange
#     assistant_repository = MagicMock(AssistantRepository)
#     file_repository = MagicMock(FileRepository)
#     create_data = {"file_id": str(random_schema_file.id)}
#     with patch.object(
#         assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
#     ) as method_a, patch.object(
#         file_repository, "retrieve_file", return_value=random_schema_file
#     ) as method_f, patch('stack.app.api.v1.assistants.get_vector_service') as mock_get_vector_service:
#         # Mock the vector service's upsert method
#         mock_service = MagicMock()
#         mock_service.upsert = MagicMock(return_value=random_schema_file)
#         mock_get_vector_service.return_value = mock_service

#         app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)
#         app.dependency_overrides[get_file_repository] = passthrough(file_repository)

#         # Act
#         response = client.post(f"/api/v1/assistants/{random_schema_assistant.id}/files", json=create_data)

#         # Assert
#         assert method_a.call_count == 1
#         assert method_f.call_count == 1
#         assert mock_get_vector_service.call_count == 1
#         assert mock_service.upsert.call_count == 1
#         assert response.status_code == 200
#         data = response.json()
#         assert data["file_id"] == str(random_schema_file.id)


async def test__create_assistant_file__assistant_not_found_404(random_schema_file):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    file_repository = MagicMock(FileRepository)
    create_data = {"file_id": str(random_schema_file.id)}
    with patch.object(
        assistant_repository, "retrieve_assistant", return_value=None
    ) as method_a:
        app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)

        # Act
        response = client.post(f"/api/v1/assistants/{uuid4()}/files", json=create_data)

        # Assert
        assert method_a.call_count == 1
        assert response.status_code == 404

# TODO: Need to spend some more time with this one
# async def test__delete_assistant_file__responds_correctly(random_schema_file, random_schema_assistant):
#     # Arrange
#     assistant_repository = MagicMock(AssistantRepository)
#     with patch.object(
#         assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
#     ) as method_a, patch.object(
#         assistant_repository, "remove_file_reference_from_assistant", return_value=random_schema_assistant
#     ) as method_d, patch('stack.app.api.v1.assistants.get_vector_service') as mock_get_vector_service:
#         # Mock the vector service's delete method
#         mock_service = MagicMock()
#         mock_service.delete = MagicMock(return_value=10)
#         mock_get_vector_service.return_value = mock_service

#         app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)

#         # Act
#         response = client.delete(f"/api/v1/assistants/{random_schema_assistant.id}/files/{random_schema_file.id}")

#         # Assert
#         assert method_a.call_count == 1
#         assert method_d.call_count == 1
#         assert mock_get_vector_service.call_count == 1
#         assert mock_service.delete.call_count == 1
#         assert response.status_code == 200
#         data = response.json()
#         assert data["id"] == str(random_schema_assistant.id)



async def test__retrieve_assistant_files__responds_correctly(random_schema_file, random_schema_assistant):
    # Arrange
    assistant_repository = MagicMock(AssistantRepository)
    file_repository = MagicMock(FileRepository)
    with patch.object(
        assistant_repository, "retrieve_assistant", return_value=random_schema_assistant
    ) as method_a, patch.object(
        file_repository, "retrieve_files_by_ids", return_value=[random_schema_file]
    ) as method_f:
        app.dependency_overrides[get_assistant_repository] = passthrough(assistant_repository)
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
