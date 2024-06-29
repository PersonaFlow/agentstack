from stack.app.core.auth.strategies.basic import BasicAuthentication
from stack.app.core.auth.strategies.google_oauth import GoogleOAuth
from stack.app.core.auth.strategies.oidc import OpenIDConnect

# Add Auth strategy classes here to enable them
# Ex: [BasicAuthentication]
ENABLED_AUTH_STRATEGIES = [
    BasicAuthentication,
    # GoogleOAuth,
    # OpenIDConnect,
]

# Define the mapping from Auth strategy name to class obj - does not need to be manually modified.
# During runtime, this will create an instance of each enabled strategy class.
# Ex: {"Basic": BasicAuthentication()}
ENABLED_AUTH_STRATEGY_MAPPING = {cls.NAME: cls() for cls in ENABLED_AUTH_STRATEGIES}
