from starlette.requests import Request
from fastapi import HTTPException
from abc import abstractmethod
from typing import Any, List
import requests
import structlog

logger = structlog.get_logger(__name__)


class BaseOAuthStrategy:
    """Base strategy for OAuth, abstract class that should be inherited from.

    Attributes:
        NAME (str): The name of the strategy.
        TOKEN_ENDPOINT (str): /token endpoint
        USERINFO_ENDPOINT (str): /userinfo endpoint
        AUTHORIZATION_ENDPOINT (str): /authorization endpoint
        PKCE_ENABLED (bool): Whether the strategy can use PKCE.
            Note: If your auth provider does not support PKCE it could break the auth flow.

        All endpoints should be fetched from the well-known endpoint
    """

    NAME = None
    TOKEN_ENDPOINT = None
    USERINFO_ENDPOINT = None
    AUTHORIZATION_ENDPOINT = None
    PKCE_ENABLED = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._post_init_check()

    def _post_init_check(self):
        if any(
            [
                self.NAME is None,
            ]
        ):
            raise ValueError(f"{self.__name__} must have NAME parameter(s) defined.")

    @abstractmethod
    def get_pkce_enabled(self, **kwargs: Any):
        """Retrieves whether the OAuth app supports PKCE and should be enabled
        during authorization."""
        ...

    @abstractmethod
    def get_client_id(self, **kwargs: Any):
        """Retrieves the OAuth app's client ID."""
        ...

    @abstractmethod
    def get_authorization_endpoint(self, **kwargs: Any):
        """Retrieves the OAuth app's authorization endpoint."""
        ...

    async def get_endpoints(self, **kwargs: Any):
        """Retrieves the /token and /userinfo endpoints."""
        try:
            response = requests.get(self.WELL_KNOWN_ENDPOINT)
            endpoints = response.json()
            self.TOKEN_ENDPOINT = endpoints["token_endpoint"]
            self.USERINFO_ENDPOINT = endpoints["userinfo_endpoint"]
            self.AUTHORIZATION_ENDPOINT = endpoints["authorization_endpoint"]
        except Exception as e:
            logger.exception(f"Error while fetching endpoints {e}")
            raise

    async def authorize(self, request: Request) -> dict | None:
        """Authorizes and fetches access token, then retrieves user info.

        Args:
            request (Request): Current request.

        Returns:
            dict: User info.
        """
        params = {
            "url": self.TOKEN_ENDPOINT,
            "authorization_response": str(request.url),
            "redirect_uri": self.REDIRECT_URI,
        }

        if self.PKCE_ENABLED:
            body = await request.json()
            code_verifier = body.get("code_verifier")

            if not code_verifier:
                raise HTTPException(
                    status_code=400,
                    detail="code_verifier not available in request body during PKCE flow.",
                )

            params["code_verifier"] = code_verifier

        try:
            token = self.client.fetch_token(**params)

            user_info = self.client.get(self.USERINFO_ENDPOINT)

            return user_info.json()
        except Exception as e:
            logger.exception(f"Error during authorization: {e}")
            return None

    async def refresh(self, request: Request) -> dict | None:
        """Uses refresh token to generate a new access token, then returns user
        info.

        Args:
            request (Request): Current request.

        Returns:
            Dict: User info.
        """
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            logger.exception("Refresh token not found in cookies.")
            return None

        try:
            token = self.client.refresh_token(
                url=self.TOKEN_ENDPOINT,
                refresh_token=refresh_token,
            )

            user_info = self.client.get(self.USERINFO_ENDPOINT)

            return user_info.json()
        except Exception as e:
            logger.exception(f"Error during token refresh: {e}")
            raise


class BaseAuthenticationStrategy:
    """Base strategy for authentication, abstract class that should be
    inherited from.

    Attributes:
        NAME (str): The name of the strategy.
    """

    NAME = "Base"

    @staticmethod
    def get_required_payload(self) -> List[str]:
        """The required /login payload for the Auth strategy."""
        ...

    @abstractmethod
    async def login(self, **kwargs: Any):
        """Check email/password credentials and return JWT token."""
        ...
