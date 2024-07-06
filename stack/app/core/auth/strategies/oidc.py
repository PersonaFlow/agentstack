import logging
from authlib.integrations.requests_client import OAuth2Session

from stack.app.core.auth.strategies.base import BaseOAuthStrategy
from stack.app.core.auth.strategies.settings import AuthStrategySettings


class OIDCSettings(AuthStrategySettings):
    oidc_client_id: str
    oidc_client_secret: str
    oidc_well_known_endpoint: str
    frontend_hostname: str


class OpenIDConnect(BaseOAuthStrategy):
    """OpenID Connect strategy."""

    NAME = "OIDC"
    PKCE_ENABLED = True

    def __init__(self):
        try:
            self.settings = OIDCSettings()
            self.REDIRECT_URI = (
                f"{self.settings.frontend_hostname}/auth/{self.NAME.lower()}"
            )
            self.WELL_KNOWN_ENDPOINT = self.settings.oidc_well_known_endpoint
            self.client = OAuth2Session(
                client_id=self.settings.oidc_client_id,
                client_secret=self.settings.oidc_client_secret,
            )
        except Exception as e:
            logging.error(f"Error during initializing of OpenIDConnect class: {str(e)}")
            raise

    def get_client_id(self):
        return self.settings.oidc_client_id

    def get_pkce_enabled(self):
        return self.PKCE_ENABLED if hasattr(self, "PKCE_ENABLED") else False

    def get_authorization_endpoint(self):
        return (
            self.AUTHORIZATION_ENDPOINT
            if hasattr(self, "AUTHORIZATION_ENDPOINT")
            else None
        )
