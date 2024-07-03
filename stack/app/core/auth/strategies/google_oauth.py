import logging

import requests
from authlib.integrations.requests_client import OAuth2Session
from starlette.requests import Request

from stack.app.core.auth.strategies.base import BaseOAuthStrategy
from stack.app.core.auth.strategies.settings import AuthStrategySettings


class GoogleOAuthSettings(AuthStrategySettings):
    google_client_id: str
    google_client_secret: str
    frontend_hostname: str


class GoogleOAuth(BaseOAuthStrategy):
    """
    Google OAuth2.0 strategy.
    """

    NAME = "Google"
    WELL_KNOWN_ENDPOINT = "https://accounts.google.com/.well-known/openid-configuration"

    def __init__(self):
        try:
            self.settings = GoogleOAuthSettings()
            self.REDIRECT_URI = (
                f"{self.settings.frontend_hostname}/auth/{self.NAME.lower()}"
            )
            self.client = OAuth2Session(
                client_id=self.settings.google_client_id,
                client_secret=self.settings.google_client_secret,
            )
        except Exception as e:
            logging.error(f"Error during initializing of GoogleOAuth class: {str(e)}")
            raise

    def get_client_id(self):
        return self.settings.google_client_id

    def get_pkce_enabled(self):
        return self.PKCE_ENABLED if hasattr(self, "PKCE_ENABLED") else False

    def get_authorization_endpoint(self):
        return self.AUTHORIZATION_ENDPOINT if hasattr(self, "AUTHORIZATION_ENDPOINT") else None

    # async def authorize(self, request: Request) -> dict | None:
    #     """
    #     Authenticates the current user using their Google account.

    #     Args:
    #         request (Request): Current request.

    #     Returns:
    #         Access token.
    #     """
    #     token = self.client.fetch_token(
    #         url=self.TOKEN_ENDPOINT,
    #         authorization_response=str(request.url),
    #         redirect_uri=self.REDIRECT_URI,
    #     )
    #     user_info = self.client.get(self.USERINFO_ENDPOINT)

    #     return user_info.json()
