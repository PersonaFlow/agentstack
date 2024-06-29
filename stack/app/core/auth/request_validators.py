from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from stack.app.model.blacklist import Blacklist
from stack.app.repositories.blacklist import BlacklistRepository, get_blacklist_repository
from stack.app.core.auth.jwt import JWTService


async def validate_authorization(
    request: Request,
    blacklist_repository: BlacklistRepository = Depends(get_blacklist_repository),
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

    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization: Bearer <token> required in request headers.",
        )

    scheme, token = authorization.split(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Authorization: Bearer <token> required in request headers.",
        )

    decoded = JWTService().decode_jwt(token)

    if not decoded or "context" not in decoded:
        raise HTTPException(
            status_code=401, detail="Bearer token is invalid or expired."
        )

    blacklist = await blacklist_repository.retrieve_blacklist(token_id=decoded["jti"])

    # Token was blacklisted
    if blacklist is not None:
        raise HTTPException(status_code=401, detail="Bearer token is blacklisted.")

    return decoded

AuthenticatedUser = Annotated[dict, Depends(validate_authorization)]
