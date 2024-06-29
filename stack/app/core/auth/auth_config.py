from stack.app.core.auth.constants import ENABLED_AUTH_STRATEGY_MAPPING
from stack.app.core.auth.strategies.base import BaseAuthenticationStrategy, BaseOAuthStrategy

def is_authentication_enabled() -> bool:
    """
    Check whether any form of authentication was enabled.

    Returns:
        bool: Whether authentication is enabled.
    """
    return bool(ENABLED_AUTH_STRATEGY_MAPPING)

def get_auth_strategy(
    strategy_name: str,
) -> BaseAuthenticationStrategy | BaseOAuthStrategy | None:
    return ENABLED_AUTH_STRATEGY_MAPPING.get(strategy_name)

async def get_auth_strategy_endpoints() -> None:
    """
    Fetches the endpoints for each enabled strategy.
    """
    for strategy in ENABLED_AUTH_STRATEGY_MAPPING.values():
        if hasattr(strategy, "get_endpoints"):
            await strategy.get_endpoints()
