import logging

import requests
from authlib.integrations.requests_client import OAuth2Session
from starlette.requests import Request

from stack.app.core.auth.strategies.base import BaseOAuthStrategy
from stack.app.core.auth.strategies.settings import AuthStrategySettings


class OIDCSettings(AuthStrategySettings):
    oidc_client_id: str
    oidc_client_secret: str
    oidc_well_known_endpoint: str
    frontend_hostname: str


class OpenIDConnect(BaseOAuthStrategy):
    """
    OpenID Connect strategy.
    """

    NAME = "OIDC"

    def __init__(self):
        try:
            self.settings = OIDCSettings()
            # TODO: switch out to proper oidc strategy name
            self.REDIRECT_URI = f"{self.settings.frontend_hostname}/auth/oidc"
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

    def get_authorization_endpoint(self):
        if hasattr(self, "AUTHORIZATION_ENDPOINT"):
            return self.AUTHORIZATION_ENDPOINT
        return None

    async def get_endpoints(self):
        response = requests.get(self.WELL_KNOWN_ENDPOINT)
        endpoints = response.json()
        try:
            self.TOKEN_ENDPOINT = endpoints["token_endpoint"]
            self.USERINFO_ENDPOINT = endpoints["userinfo_endpoint"]
            self.AUTHORIZATION_ENDPOINT = endpoints["authorization_endpoint"]
        except Exception as e:
            logging.error(
                f"Error fetching `token_endpoint` and `userinfo_endpoint` from {endpoints}."
            )
            raise

    async def authorize(self, request: Request) -> dict | None:
        """
        Authenticates the current user using their OIDC account.

        Args:
            request (Request): Current request.

        Returns:
            Access token.
        """
        token = self.client.fetch_token(
            url=self.TOKEN_ENDPOINT,
            authorization_response=str(request.url),
            redirect_uri=self.REDIRECT_URI,
        )
        user_info = self.client.get(self.USERINFO_ENDPOINT)

        return user_info.json()
