from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from stack.app.core.auth.auth_config import ENABLED_AUTH_STRATEGY_MAPPING, get_auth_strategy
from stack.app.repositories.blacklist import get_blacklist_repository, BlacklistRepository
from stack.app.model.blacklist import Blacklist
from stack.app.schema.auth import JWTResponse, ListAuthStrategy, Login, Logout
from stack.app.core.auth.jwt import JWTService
from stack.app.core.auth.request_validators import validate_authorization
from stack.app.core.auth.utils import is_enabled_authentication_strategy
from stack.app.repositories.user import get_user_repository, UserRepository

router = APIRouter()
DEFAULT_TAG = "Authentication"


@router.get(
    "/auth_strategies",
    tags=[DEFAULT_TAG],
    response_model=list[ListAuthStrategy],
    operation_id="get_auth_strategies",
    summary="Get enabled authentication strategies",
    description="Returns a list of enabled authentication strategies.",
)
def get_strategies() -> list[ListAuthStrategy]:
    strategies = []
    for strategy_name, strategy_instance in ENABLED_AUTH_STRATEGY_MAPPING.items():
        strategies.append(
            {
                "strategy": strategy_name,
                "client_id": (
                    strategy_instance.get_client_id()
                    if hasattr(strategy_instance, "get_client_id")
                    else None
                ),
                "authorization_endpoint": (
                    strategy_instance.get_authorization_endpoint()
                    if hasattr(strategy_instance, "get_authorization_endpoint")
                    else None
                ),
                 "pkce_enabled": (
                    strategy_instance.get_pkce_enabled()
                    if hasattr(strategy_instance, "get_pkce_enabled")
                    else False
                ),
                "refresh_token_params": (
                    strategy_instance.get_refresh_token_params()
                    if hasattr(strategy_instance, "get_refresh_token_params")
                    else None
                ),
            }
        )

    return strategies


@router.post(
    "/login",
    tags=[DEFAULT_TAG],
    response_model=Union[JWTResponse, None],
    operation_id="login",
    summary="Login",
    description="Logs user in, performing auth according to auth strategy.",
)
async def login(
    request: Request,
    login: Login,
    user_repository: UserRepository = Depends(get_user_repository),
):
    strategy_name = login.strategy
    payload = login.payload

    strategy = get_auth_strategy(strategy_name)
    if not strategy:
        raise HTTPException(
            status_code=422, detail=f"Invalid Authentication strategy: {strategy_name}."
        )


    strategy_payload = strategy.get_required_payload()
    if not set(strategy_payload).issubset(payload.keys()):
        missing_keys = [key for key in strategy_payload if key not in payload.keys()]
        raise HTTPException(
            status_code=422,
            detail=f"Missing the following keys in the payload: {missing_keys}.",
        )

    user = await strategy.login(user_repository, payload)
    if not user:
        raise HTTPException(
            status_code=401,
            detail=f"Error performing {strategy_name} authentication with payload: {payload}.",
        )

    token = JWTService().create_and_encode_jwt(user, strategy_name)

    return {"token": token}

@router.post(
    "/{strategy}/auth",
    response_model=JWTResponse,
    operation_id="authorize",
    summary="Authorize",
    description="Callback authorization endpoint used for OAuth providers after authenticating on the provider's login screen.",
)
async def authorize(
    strategy: str,
    request: Request,
    user_repository: UserRepository = Depends(get_user_repository),
):
    strategy_name = None
    for enabled_strategy_name in ENABLED_AUTH_STRATEGY_MAPPING.keys():
        if enabled_strategy_name.lower() == strategy.lower():
            strategy_name = enabled_strategy_name

    if not strategy_name:
        raise HTTPException(
            status_code=400,
            detail=f"Error calling /auth with invalid strategy name: {strategy_name}.",
        )
    if not is_enabled_authentication_strategy(strategy_name):
        raise HTTPException(
            status_code=404, detail=f"Invalid Authentication strategy: {strategy_name}."
        )

    strategy = ENABLED_AUTH_STRATEGY_MAPPING[strategy_name]

    try:
        userinfo = await strategy.authorize(request)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not fetch access token from provider, failed with error: {str(e)}",
        )

    if not userinfo:
        raise HTTPException(
            status_code=401, detail=f"Could not get user from auth token: {token}."
        )

    # Get or create user, then set session user
    user = user_repository.get_or_create_user(userinfo)

    token = JWTService().create_and_encode_jwt(user)

    return {"token": token}


@router.get(
    "/logout",
    tags=[DEFAULT_TAG],
    response_model=Logout,
    operation_id="logout",
    summary="Logout",
    description="Logs user out, adding the given JWT token to the blacklist.",
)
async def logout(
    request: Request,
    blacklist_repository: BlacklistRepository = Depends(get_blacklist_repository),
    token: dict | None = Depends(validate_authorization),
):
    if token is not None:
        db_blacklist = Blacklist(token_id=token["jti"])
        blacklist_repository.create_blacklist(db_blacklist)

    return {}

