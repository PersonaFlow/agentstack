import pytest
from unittest.mock import patch, MagicMock
from stack.app.core.auth import auth_config
from stack.app.core.auth.jwt import JWTService
from stack.app.repositories.blacklist import BlacklistRepository, get_blacklist_repository
from stack.app.repositories.user import UserRepository, get_user_repository
from stack.app.core.auth.strategies.basic import BasicAuthentication
from stack.tests.unit.conftest import passthrough
from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings
from starlette.testclient import TestClient

app = create_app(Settings())
client = TestClient(app)

# @pytest.fixture(autouse=True)
# def mock_auth_config():
#     with patch.object(auth_config, "ENABLED_AUTH_STRATEGY_MAPPING", {"Basic": BasicAuthentication()}):
#         yield

@pytest.fixture(autouse=True)
def mock_auth_config():
    with patch("stack.app.core.auth.auth_config.ENABLED_AUTH_STRATEGY_MAPPING", {"Basic": BasicAuthentication()}), \
         patch("stack.app.core.auth.auth_config.is_authentication_enabled", return_value=True), \
         patch("stack.app.core.auth.strategies.basic.BasicAuthentication.login") as mock_login:
        yield mock_login


async def test__login__success(mock_auth_config, random_schema_user):
    mock_auth_config.return_value = {"user_id": random_schema_user.user_id, "email": random_schema_user.email}

    response = client.post(
        "/api/v1/auth/login",
        json={
            "strategy": "Basic",
            "payload": {"email": "test@gmail.com", "password": "abcd"},
        },
    )

    assert response.status_code == 200
    assert response.json().get("token") is not None


async def test__login__invalid_password(mock_auth_config):
    mock_auth_config.return_value = None

    response = client.post(
        "/api/v1/auth/login",
        json={
            "strategy": "Basic",
            "payload": {"email": "test@gmail.com", "password": "test"},
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Error performing Basic authentication: Invalid credentials."
    }


async def test__login__no_user(mock_auth_config):
    mock_auth_config.return_value = None

    response = client.post(
        "/api/v1/auth/login",
        json={
            "strategy": "Basic",
            "payload": {"email": "nouser@gmail.com", "password": "test"},
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Error performing Basic authentication: Invalid credentials."
    }


async def test__login__invalid_strategy():
    response = client.post(
        "/api/v1/auth/login", json={"strategy": "test", "payload": {}}
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid Authentication strategy: test."}


async def test__login__invalid_payload(mock_auth_config):
    with patch("stack.app.core.auth.strategies.basic.BasicAuthentication.get_required_payload", return_value=["email", "password"]):
        response = client.post(
            "/api/v1/auth/login", json={"strategy": "Basic", "payload": {}}
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Missing the following keys in the payload: ['email', 'password']."
        }


async def test__login__no_strategy():
    response = client.post("/api/v1/auth/login", json={"payload": {}})

    assert response.status_code == 422


async def test__login__no_payload():
    response = client.post("/api/v1/auth/login", json={"strategy": ""})

    assert response.status_code == 422


async def test__logout__success(random_schema_user):
    user = {"user_id": random_schema_user.user_id}
    token = JWTService().create_and_encode_jwt(user, "Basic")

    blacklist_repository = MagicMock(BlacklistRepository)
    with patch.object(blacklist_repository, "create_blacklist", return_value=None) as method:
        app.dependency_overrides[get_blacklist_repository] = passthrough(blacklist_repository)

        response = client.get(
            "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
        )

        assert method.call_count == 1
        assert response.status_code == 200


