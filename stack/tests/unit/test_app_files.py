import datetime
import io
import uuid
from unittest.mock import MagicMock, patch

# from stack.app.utils import file_helpers
import logging
import pytest
from starlette.testclient import TestClient

from stack.app.app_factory import create_app
from stack.app.core import configuration
from stack.app.core.configuration import Settings
from stack.app.model.file import File
from stack.app.repositories.file import FileRepository, get_file_repository
from stack.tests.unit.conftest import passthrough

app = create_app(Settings())
client = TestClient(app)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def random_file():
    return File(
        id=uuid.uuid4(),
        user_id="asdf",
        purpose="rag",
        filename="asdf.txt",
        bytes="100",
        mime_type="asdf",
        source="asdf.txt",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        kwargs={},
    )


async def test__retrieve_files__responds_correctly(random_file):
    # Arrange
    file_repository = MagicMock(FileRepository)
    with patch.object(
        file_repository, "retrieve_files", return_value=[random_file]
    ) as method:
        app.dependency_overrides[get_file_repository] = passthrough(file_repository)

        # Act
        response = client.get("/api/v1/files", params={"user_id": "asdf"})
        data = response.json()
        print(data)

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        assert len(data) == 1


async def test__retrieve_file__responds_correctly(random_file):
    # Arrange
    file_repository = MagicMock(FileRepository)
    with patch.object(
        file_repository, "retrieve_file", return_value=random_file
    ) as method:
        app.dependency_overrides[get_file_repository] = lambda: file_repository

        # Act
        response = client.get(f"/api/v1/files/{random_file.id}")
        data = response.json()
        print(data)

        # Assert
        assert method.call_count == 1
        assert response.status_code == 200
        assert data["id"] == str(random_file.id)


async def test__retrieve_file__file_not_found(random_file):
    # Arrange
    file_repository = MagicMock(FileRepository)
    with patch.object(file_repository, "retrieve_file", return_value=None) as method:
        app.dependency_overrides[get_file_repository] = lambda: file_repository
        non_existent_file_id = uuid.uuid4()

        # Act
        response = client.get(f"/api/v1/files/{non_existent_file_id}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 404
        assert response.json() == {"detail": "File not found"}


async def test__retrieve_file__server_error(random_file):
    # Arrange
    file_repository = MagicMock(FileRepository)
    with patch.object(
        file_repository, "retrieve_file", side_effect=Exception("Test Exception")
    ) as method:
        app.dependency_overrides[get_file_repository] = lambda: file_repository

        # Act
        response = client.get(f"/api/v1/files/{random_file.id}")

        # Assert
        assert method.call_count == 1
        assert response.status_code == 500
        assert response.json() == {
            "detail": "An error occurred while retrieving the file."
        }


@pytest.fixture
def upload_file():
    f = io.BytesIO(b"test file content 123123123123")
    return ("test.txt", f, "text/plain")


async def test__upload_file__responds_correctly(random_file, upload_file):
    # Arrange
    file_repository = MagicMock(FileRepository)
    with patch.object(
        file_repository, "create_file", return_value=random_file
    ) as method:
        app.dependency_overrides[get_file_repository] = lambda: file_repository

        # Act
        response = client.post(
            "/api/v1/files",
            files={"file": upload_file},
            data={"purpose": "rag", "user_id": "asdf", "filename": "test.txt"},
        )
        data = response.json()
        print(data)

        # Assert
        assert method.call_count == 1
        assert response.status_code == 201
        assert data["id"] == str(random_file.id)


async def test__upload_file__file_required(upload_file):
    # Arrange
    file_repository = MagicMock(FileRepository)
    app.dependency_overrides[get_file_repository] = lambda: file_repository

    # Act
    response = client.post(
        "/api/v1/files",
        files={},
        data={"purpose": "rag", "user_id": "asdf", "filename": "test.txt"},
    )

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"


# TODO: Fix this test

# async def test__upload_file__unsupported_file_type(random_file):
#     # Arrange
#     f = io.BytesIO(b"test file content")
#     upload_file = ("test.anything", f, "application/i_dont_know")
#     file_repository = MagicMock(FileRepository)

#     with (
#         patch.object(
#             file_repository, "create_file", return_value=random_file
#         ) as method,
#     ):
#         app.dependency_overrides[get_file_repository] = lambda: file_repository
#         # Act
#         response = client.post(
#             "/api/v1/files",
#             files={"file": upload_file},
#             data={"purpose": "rag", "user_id": "asdf", "filename": "test.random"},
#         )

#     # Assert
#     assert method.call_count == 0
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Unsupported file type."}


# async def test__upload_file__unsupported_file_type():
#     # Arrange
#     f = io.BytesIO(b"test file content")
#     upload_file = ("test.anything", f, "application/i_dont_know")
#     file_repository = MagicMock(FileRepository)

#     def mock_guess_mime_type(filename, file_bytes):
#         print(f"Mock guess_mime_type called with filename: {filename}")
#         return "application/i_dont_know"

#     def mock_is_mime_type_supported(mime_type):
#         print(f"Mock is_mime_type_supported called with mime_type: {mime_type}")
#         return False

#     with (
#         patch.object(file_repository, "create_file", return_value=random_file) as method,
#         patch('stack.app.utils.file_helpers.guess_mime_type', side_effect=mock_guess_mime_type),
#         patch('stack.app.utils.file_helpers.is_mime_type_supported', side_effect=mock_is_mime_type_supported)
#     ):
#         app.dependency_overrides[get_file_repository] = lambda: file_repository
#         # Act
#         print("Sending POST request")
#         response = client.post(
#             "/api/v1/files",
#             files={"file": upload_file},
#             data={"purpose": "rag", "user_id": "asdf", "filename": "test.random"},
#         )
#         print(f"Response status code: {response.status_code}")
#         print(f"Response content: {response.content}")

#     # Assert
#     print(f"create_file call count: {method.call_count}")
#     assert method.call_count == 0
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Unsupported file type."}

# async def test__upload_file__unsupported_file_type(random_file):
#     # Arrange
#     f = io.BytesIO(b"test file content")
#     upload_file = ("test.anything", f, "application/i_dont_know")
#     file_repository = MagicMock(FileRepository)

#     with (
#         patch.object(file_repository, "create_file", return_value=random_file) as method,
#         patch('stack.app.utils.file_helpers.guess_mime_type', return_value="application/i_dont_know")
#     ):
#         app.dependency_overrides[get_file_repository] = lambda: file_repository
#         # Act
#         response = client.post(
#             "/api/v1/files",
#             files={"file": upload_file},
#             data={"purpose": "rag", "user_id": "asdf", "filename": "test.random"},
#         )


# # Assert
# assert method.call_count == 0
# assert response.status_code == 400
# assert response.json() == {"detail": "Unsupported file type."}
#
async def test__upload_file__file_size_exceeds_limit(upload_file, random_file):
    # Arrange
    file_repository = MagicMock(FileRepository)
    app.dependency_overrides[get_file_repository] = lambda: file_repository

    # Act
    with patch.object(
        file_repository, "create_file", return_value=random_file
    ) as method, patch.object(configuration.settings, "MAX_FILE_UPLOAD_SIZE", 1):
        response = client.post(
            "/api/v1/files",
            files={"file": upload_file},
            data={"purpose": "rag", "user_id": "asdf", "filename": "test.txt"},
        )

    # Assert
    assert method.call_count == 0
    assert response.status_code == 400
    assert response.json() == {"detail": "File size exceeds the maximum allowed size."}


async def test__upload_file__server_error(upload_file):
    # Arrange
    file_repository = MagicMock(FileRepository)
    with patch.object(
        file_repository, "create_file", side_effect=Exception("Test Exception")
    ) as method:
        app.dependency_overrides[get_file_repository] = lambda: file_repository

        # Act
        response = client.post(
            "/api/v1/files",
            files={"file": upload_file},
            data={"purpose": "rag", "user_id": "asdf", "filename": "test.txt"},
        )

        # Assert
        assert method.call_count == 1
        assert response.status_code == 500
        assert response.json() == {
            "detail": "An error occurred while uploading the file."
        }
