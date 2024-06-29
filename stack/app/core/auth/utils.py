import bcrypt
from fastapi import Request
from stack.app.core.auth.auth_config import is_authentication_enabled, ENABLED_AUTH_STRATEGY_MAPPING
from stack.app.core.auth.jwt import JWTService

def is_enabled_authentication_strategy(strategy_name: str) -> bool:
    """
    Check whether a given authentication strategy is enabled in config/auth.py

    Args:
        strategy_name (str): Name the of auth strategy.

    Returns:
        bool: Whether that strategy is currently enabled
    """
    # Check the strategy is valid and enabled
    if strategy_name not in ENABLED_AUTH_STRATEGY_MAPPING.keys():
        return False

    return True


def get_header_user_id(request: Request) -> str:
    """
    Retrieves the user_id from request headers, will work whether authentication is enabled or not.

    (Auth disabled): retrieves the User-Id header value
    (Auth enabled): retrieves the Authorization header, and decodes the value

    Args:
        request (Request): current Request


    Returns:
        str: User ID
    """
    # Check if Auth enabled
    if is_authentication_enabled():
        # Validation already performed, so just retrieve value
        authorization = request.headers.get("Authorization")
        _, token = authorization.split(" ")
        decoded = JWTService().decode_jwt(token)

        return decoded["context"]["id"]
    # Auth disabled
    else:
        user_id = request.headers.get("User-Id", "")
        return user_id
