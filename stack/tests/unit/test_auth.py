from base64 import b64encode
from datetime import datetime, timedelta, timezone
from typing import Optional
from unittest.mock import MagicMock, patch
from starlette.testclient import TestClient
import jwt

from stack.app.core.auth.handlers import AuthedUser, get_auth_handler
from stack.app.core.auth.auth_settings import (
    AuthType,
    JWTSettingsLocal,
    JWTSettingsOIDC,
)
from stack.app.core.auth.auth_settings import auth_settings
from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings

app = create_app(Settings())
client = TestClient(app)

@app.get("/me")
async def me(user: AuthedUser) -> dict:
    return user


def _create_jwt(
    key: str, alg: str, payload: dict, headers: Optional[dict] = None
) -> str:
    return jwt.encode(payload, key, algorithm=alg, headers=headers)


def test_noop():
    get_auth_handler.cache_clear()
    auth_settings.auth_type = AuthType.NOOP
    sub = "user_noop"

    response = client.get("/me", cookies={"opengpts_user_id": sub})
    assert response.status_code == 200
    assert response.json()["sub"] == sub


def test_jwt_local():
    get_auth_handler.cache_clear()
    auth_settings.auth_type = AuthType.JWT_LOCAL
    key = "key"
    auth_settings.jwt_local = JWTSettingsLocal(
        alg="HS256",
        iss="issuer",
        aud="audience",
        decode_key_b64=b64encode(key.encode("utf-8")),
    )
    sub = "user_jwt_local"

    token = _create_jwt(
        key=key,
        alg=auth_settings.jwt_local.alg,
        payload={
            "sub": sub,
            "iss": auth_settings.jwt_local.iss,
            "aud": auth_settings.jwt_local.aud,
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
        },
    )

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["sub"] == sub

    # Test invalid token
    response = client.get("/me", headers={"Authorization": "Bearer xyz"})
    assert response.status_code == 401


def test_jwt_oidc():
    get_auth_handler.cache_clear()
    auth_settings.auth_type = AuthType.JWT_OIDC
    auth_settings.jwt_oidc = JWTSettingsOIDC(iss="issuer", aud="audience")
    sub = "user_jwt_oidc"
    key = "key"
    alg = "HS256"

    token = _create_jwt(
        key=key,
        alg=alg,
        payload={
            "sub": sub,
            "iss": auth_settings.jwt_oidc.iss,
            "aud": auth_settings.jwt_oidc.aud,
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
        },
        headers={"kid": "kid", "alg": alg},
    )

    mock_jwk_client = MagicMock()
    mock_jwk_client.get_signing_key.return_value = MagicMock(key=key)

    with patch(
        "app.auth.handlers.JWTAuthOIDC._get_jwk_client", return_value=mock_jwk_client
    ):
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["sub"] == sub
