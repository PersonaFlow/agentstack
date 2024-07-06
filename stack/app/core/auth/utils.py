from fastapi import Request
from stack.app.core.auth.auth_config import (
    is_authentication_enabled,
    ENABLED_AUTH_STRATEGY_MAPPING,
)
from stack.app.core.auth.jwt import JWTService
from stack.app.core.configuration import settings


def is_enabled_authentication_strategy(strategy_name: str) -> bool:
    """Check whether a given authentication strategy is enabled in
    auth_config.py.

    Args:
        strategy_name (str): Name the of auth strategy.

    Returns:
        bool: Whether that strategy is currently enabled
    """
    # Check the strategy is valid and enabled
    return strategy_name in ENABLED_AUTH_STRATEGY_MAPPING.keys()


def get_header_user_id(request: Request) -> str:
    """Retrieves the user_id from request headers, will work whether
    authentication is enabled or not.

    (Auth disabled): retrieves the User-Id header value
    (Auth enabled): retrieves the Authorization header, and decodes the value

    Args:
        request (Request): current Request


    Returns:
        str: User ID
    """
    default_user_id = settings.DEFAULT_USER_ID
    # Check if Auth enabled
    if is_authentication_enabled():
        # Validation already performed, so just retrieve value
        authorization = request.headers.get("Authorization")
        _, token = authorization.split(" ")
        decoded = JWTService().decode_jwt(token)

        return decoded["context"]["user_id"]
    # Auth disabled
    else:
        user_id = request.headers.get("User-Id") or default_user_id
        return user_id
