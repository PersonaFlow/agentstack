import pytest
from unittest.mock import patch, MagicMock
from fastapi import Depends
import freezegun
from starlette.testclient import TestClient

from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings
from stack.app.core.auth.jwt import JWTService
from stack.app.core.auth.request_validators import validate_authorization
from stack.app.core.auth.strategies.basic import BasicAuthentication
from stack.app.core.auth.strategies.google_oauth import GoogleOAuth
from stack.app.core.auth.strategies.oidc import OpenIDConnect
from stack.app.repositories.blacklist import BlacklistRepository, get_blacklist_repository
from stack.tests.unit.conftest import passthrough

app = create_app(Settings())
client = TestClient(app)

@app.get("/test-auth")
def test_validate_authorization(token=Depends(validate_authorization)):
    return {}

freezegun.configure(extend_ignore_list=["transformers"])

@pytest.fixture
def mock_get_auth_strategy():
    with patch("stack.app.core.auth.request_validators.get_auth_strategy") as mock:
        yield mock

async def test__validate_authorization__valid_token():
    # Arrange
    user = {"user_id": "test"}
    token = JWTService().create_and_encode_jwt(user, "")

    # Act
    response = client.get("/test-auth", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert response.status_code == 200

async def test__validate_authorization__no_authorization():
    # Act
    response = client.get("/test-auth", headers={})

    # Assert
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authorization: Bearer <token> required in request headers."
    }

async def test__validate_authorization__no_bearer():
    # Act
    response = client.get("/test-auth", headers={"Authorization": "test invalid_token"})

    # Assert
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authorization: Bearer <token> required in request headers."
    }

async def test__validate_authorization__invalid_token():
    # Act
    response = client.get("/test-auth", headers={"Authorization": "Bearer invalid_token"})

    # Assert
    assert response.status_code == 401
    assert response.json() == {"detail": "Bearer token is invalid."}

async def test__validate_authorization__expired_token_strategy_dne():
    # Arrange
    user = {"user_id": "test"}
    with freezegun.freeze_time("2024-01-01 00:00:00"):
        token = JWTService().create_and_encode_jwt(user, "")

    # Act
    with freezegun.freeze_time("2024-02-01 00:00:00"):
        response = client.get("/test-auth", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Tried refreshing token, but Auth strategy is disabled or does not exist."
    }

async def test__validate_authorization__expired_token_refresh_not_implemented():
    # Arrange
    user = {"user_id": "test"}
    with freezegun.freeze_time("2024-01-01 00:00:00"):
        token = JWTService().create_and_encode_jwt(user, BasicAuthentication.NAME)

    # Act
    with freezegun.freeze_time("2024-02-01 00:00:00"):
        response = client.get("/test-auth", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Tried refreshing token, but Auth strategy Basic does not have a refresh method implemented."
    }

@pytest.mark.parametrize(
    "strategy",
    [
        GoogleOAuth.NAME,
        OpenIDConnect.NAME,
    ],
)
async def test__validate_authorization__expired_token_refreshes_token(strategy, mock_get_auth_strategy):
    # Arrange
    user = {"user_id": "test"}
    with freezegun.freeze_time("2024-01-01 00:00:00"):
        token = JWTService().create_and_encode_jwt(user, strategy)

    mock_strategy = MagicMock()
    mock_strategy.refresh.return_value = user
    mock_get_auth_strategy.return_value = mock_strategy

    # Act
    with freezegun.freeze_time("2024-02-01 00:00:00"):
        response = client.get("/test-auth", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert response.status_code == 200

async def test__validate_authorization__blacklisted_token():
    # Arrange
    user = {"user_id": "test"}
    token = JWTService().create_and_encode_jwt(user, "")
    decoded = JWTService().decode_jwt(token)

    blacklist_repository = MagicMock(BlacklistRepository)
    with patch.object(blacklist_repository, "retrieve_blacklist", return_value={"token_id": decoded["jti"]}) as method:
        app.dependency_overrides[get_blacklist_repository] = passthrough(blacklist_repository)

        # Act
        response = client.get("/test-auth", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert method.call_count == 1
    assert response.status_code == 401
    assert response.json() == {"detail": "Bearer token is blacklisted."}
