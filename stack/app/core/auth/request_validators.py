import datetime
from fastapi import Depends, HTTPException, Request, Response
from typing import Annotated

from stack.app.repositories.blacklist import BlacklistRepository, get_blacklist_repository
from stack.app.repositories.user import UserRepository, get_user_repository
from stack.app.core.auth.jwt import JWTService
from stack.app.core.auth.auth_config import get_auth_strategy

UPDATE_TOKEN_HEADER = "X-Toolkit-Auth-Update"

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
    expiry_datetime = datetime.datetime.fromtimestamp(decoded_token["exp"])
    strategy_name = decoded_token["strategy"]
    now = datetime.datetime.utcnow()

    if now < expiry_datetime:
        return decoded_token

    strategy = get_auth_strategy(strategy_name)

    if not strategy:
        raise HTTPException(
            status_code=400,
            detail=f"Tried refreshing token, but Auth strategy {strategy_name} is disabled or does not exist.",
        )

    if not hasattr(strategy, "refresh"):
        raise HTTPException(
            status_code=400,
            detail=f"Tried refreshing token, but Auth strategy {strategy_name} does not have a refresh method implemented.",
        )

    try:
        userinfo = strategy.refresh(request)
        user = await user_repository.get_or_create_user(userinfo)
        token = JWTService().create_and_encode_jwt(user, strategy_name)

        # Set new token in response
        response.headers[UPDATE_TOKEN_HEADER] = token

        return token
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not create user and encode JWT token.",
        )


AuthenticatedUser = Annotated[dict, Depends(validate_authorization)]
