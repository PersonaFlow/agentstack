from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request, Response
from typing import Annotated

from stack.app.repositories.blacklist import BlacklistRepository, get_blacklist_repository
from stack.app.repositories.user import UserRepository, get_user_repository
from stack.app.core.auth.jwt import JWTService
from stack.app.core.auth.auth_config import get_auth_strategy
from stack.app.core.auth.auth_config import is_authentication_enabled
from stack.app.core.configuration import settings


UPDATE_TOKEN_HEADER = "X-Toolkit-Auth-Update"

async def get_default_user():
    """
    Returns a default user when authentication is disabled.
    """
    return {
        "context": {
            "user_id": settings.DEFAULT_USER_ID,
            # Add any other default user properties here
        }
    }

def get_auth_dependency():
    """
    Returns the appropriate dependency based on whether authentication is enabled.
    """
    if is_authentication_enabled():
        return Depends(validate_authorization)
    else:
        return Depends(get_default_user)


async def validate_authorization(
    request: Request,
    response: Response,
    blacklist_repository: BlacklistRepository = Depends(get_blacklist_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> dict:
    """
    Validate that the request has the `Authorization` header, used for requests
    that require authentication.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If no `Authorization` header.

    Returns:
        dict: Decoded payload.
    """

    # 1. Check if `Authorization` header is present
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization: Bearer <token> required in request headers.",
        )

    # 2. Check if `Authorization` header is well-formed and contains a `Bearer` token.
    scheme, token = authorization.split(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Authorization: Bearer <token> required in request headers.",
        )
    try:
        decoded_token = JWTService().decode_jwt(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    if decoded_token is None or any(
        [
            "context" not in decoded_token,
            "jti" not in decoded_token,
            "exp" not in decoded_token,
            "strategy" not in decoded_token,
        ]
    ):
        raise HTTPException(status_code=401, detail="Bearer token is invalid or missing required fields.")


    # 4. Check if token is blacklisted
    blacklist = await blacklist_repository.retrieve_blacklist(token_id=decoded_token["jti"])

    if not blacklist:
        raise HTTPException(status_code=401, detail="Bearer token is blacklisted.")

     # 5. Check if token is expired - if so then try refresh logic
    expiry_datetime = datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)
    strategy_name = decoded_token["strategy"]
    now = datetime.now(timezone.utc)

    if now >= expiry_datetime:
        strategy = get_auth_strategy(strategy_name)

        if not strategy:
            raise HTTPException(
                status_code=401,
                detail=f"JWT Token has expired and Auth strategy {strategy_name} is disabled or does not exist.",
            )

        if not hasattr(strategy, "refresh"):
            raise HTTPException(
                status_code=401,
                detail=f"JWT Token has expired and Auth strategy {strategy_name} does not support token refresh.",
            )

        try:
            userinfo = await strategy.refresh(request)
            user = await user_repository.get_or_create_user(userinfo)
            new_token = JWTService().create_and_encode_jwt(user, strategy_name)
            response.headers[UPDATE_TOKEN_HEADER] = new_token
            return JWTService().decode_jwt(new_token)
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Could not refresh token: {str(e)}",
            )

    return decoded_token



AuthenticatedUser = Annotated[dict, get_auth_dependency()]
