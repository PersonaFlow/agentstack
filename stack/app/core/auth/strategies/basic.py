import bcrypt
from typing import List

from stack.app.model.user import User
from stack.app.core.auth.strategies.base import BaseAuthenticationStrategy
from stack.app.repositories.user import UserRepository


class BasicAuthentication(BaseAuthenticationStrategy):
    """
    Basic email/password strategy.
    """

    NAME = "Basic"

    @staticmethod
    def get_required_payload() -> List[str]:
        """
        Retrieves the required /login payload for the Auth strategy.

        Returns:
            List[str]: List of required variables.
        """
        return ["email", "password"]

    def check_password(self, plain_text_password: str, hashed_password: bytes) -> bool:
        """
        Checks that the input plain text password corresponds to a hashed password.

        Args:
            plain_text_password (str): Password to check.
            hashed_password (bytes): Password to check against.

        Returns:
            bool: Whether the plain-text password matches the given hashed password.
        """
        return bcrypt.checkpw(plain_text_password.encode("utf-8"), hashed_password)


    async def login(self, user_repository: UserRepository, payload: dict[str, str]) -> dict | None:
        """
        Logs user in, checking if the hashed input password corresponds to the
        one stored in the DB.

        Args:
            user_repository (UserRepository): UserRepository
            payload (dict[str, str]): Login payload

        Returns:
            dict | None: Returns the user as dict to set the app session, or None.
        """

        payload_email = payload.get("email", "")
        payload_password = payload.get("password", "")
        user: User = await user_repository.retrieve_user_by_email(payload_email)

        if not user:
            return None

        if self.check_password(payload_password, user.hashed_password):
            return {
                "user_id": user.user_id,
                "email": user.email,
            }

        return None
