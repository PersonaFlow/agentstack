from unittest.mock import patch, MagicMock

from starlette.testclient import TestClient

from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings
from stack.app.core.auth.auth_config import ENABLED_AUTH_STRATEGY_MAPPING
from stack.tests.unit.conftest import passthrough

app = create_app(Settings())
client = TestClient(app)


async def test__list_auth_strategies__responds_correctly():
    # Arrange
    mock_strategies = {
        "Basic": MagicMock(
            get_client_id=lambda: None,
            get_authorization_endpoint=lambda: None,
            get_pkce_enabled=lambda: False,
        ),
        "Google": MagicMock(
            get_client_id=lambda: "google_client_id",
            get_authorization_endpoint=lambda: "https://accounts.google.com/o/oauth2/v2/auth",
            get_pkce_enabled=lambda: True,
        ),
        "OIDC": MagicMock(
            get_client_id=lambda: "oidc_client_id",
            get_authorization_endpoint=lambda: "https://example.com/auth",
            get_pkce_enabled=lambda: True,
        ),
    }

    with patch.dict(ENABLED_AUTH_STRATEGY_MAPPING, mock_strategies):
        # Act
        response = client.get("/api/v1/auth/auth_strategies")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    expected_strategies = ["Basic", "Google", "OIDC"]
    for strategy in data:
        assert strategy["strategy"] in expected_strategies
        assert "client_id" in strategy
        assert "authorization_endpoint" in strategy
        assert "pkce_enabled" in strategy

    basic_strategy = next(s for s in data if s["strategy"] == "Basic")
    assert basic_strategy["client_id"] is None
    assert basic_strategy["authorization_endpoint"] is None
    assert basic_strategy["pkce_enabled"] is False

    google_strategy = next(s for s in data if s["strategy"] == "Google")
    assert google_strategy["client_id"] == "google_client_id"
    assert (
        google_strategy["authorization_endpoint"]
        == "https://accounts.google.com/o/oauth2/v2/auth"
    )
    assert google_strategy["pkce_enabled"] is True

    oidc_strategy = next(s for s in data if s["strategy"] == "OIDC")
    assert oidc_strategy["client_id"] == "oidc_client_id"
    assert oidc_strategy["authorization_endpoint"] == "https://example.com/auth"
    assert oidc_strategy["pkce_enabled"] is True


async def test__list_auth_strategies__no_strategies():
    # Arrange
    with patch.dict(ENABLED_AUTH_STRATEGY_MAPPING, {}, clear=True):
        # Act
        response = client.get("/api/v1/auth/auth_strategies")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
