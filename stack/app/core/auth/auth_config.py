from stack.app.core.auth.strategies.base import (
    BaseAuthenticationStrategy,
    BaseOAuthStrategy,
)
from stack.app.core.auth.strategies.basic import BasicAuthentication
from stack.app.core.auth.strategies.google_oauth import GoogleOAuth
from stack.app.core.auth.strategies.oidc import OpenIDConnect

# Add Auth strategy classes here to enable them
# Ex: [BasicAuthentication]
ENABLED_AUTH_STRATEGIES = [
    # BasicAuthentication,
    # GoogleOAuth,
    # OpenIDConnect,
]

# Define the mapping from Auth strategy name to class obj - does not need to be manually modified.
# During runtime, this will create an instance of each enabled strategy class.
# Ex: {"Basic": BasicAuthentication()}
ENABLED_AUTH_STRATEGY_MAPPING = {cls.NAME: cls() for cls in ENABLED_AUTH_STRATEGIES}


def is_authentication_enabled() -> bool:
    """Check whether any form of authentication was enabled.

    Returns:
        bool: Whether authentication is enabled.
    """
    return bool(ENABLED_AUTH_STRATEGY_MAPPING)


def get_auth_strategy(
    strategy_name: str,
) -> BaseAuthenticationStrategy | BaseOAuthStrategy | None:
    return ENABLED_AUTH_STRATEGY_MAPPING.get(strategy_name)


async def get_auth_strategy_endpoints() -> None:
    """Fetches the endpoints for each enabled strategy."""
    for strategy in ENABLED_AUTH_STRATEGY_MAPPING.values():
        if hasattr(strategy, "get_endpoints"):
            await strategy.get_endpoints()
