from datetime import datetime, timedelta, timezone
import structlog
import uuid
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError

from stack.app.core.configuration import Settings, get_settings

logger = structlog.get_logger()

settings = get_settings()


class JWTService:
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        self.secret_key = self.settings.AUTH_SECRET_KEY
        self.algorithm = self.settings.JWT_ALGORITHM
        self.expiry = self.settings.TOKEN_EXPIRY_HOURS
        self.issuer = self.settings.JWT_ISSUER

        if not self.secret_key:
            raise ValueError("Secret auth key is not set.")

    def create_and_encode_jwt(self, user: dict, strategy_name: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "iss": self.issuer,
            "iat": now,
            "exp": now + timedelta(hours=self.expiry),
            "jti": str(uuid.uuid4()),
            "strategy": strategy_name,
            "context": user,
        }

        token = jwt.encode(payload, self.secret_key, self.algorithm)

        return token

    def decode_jwt(self, token: str) -> dict:
        try:
            decoded_payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            logger.info(f"Successfully decoded token: {decoded_payload}")
            return decoded_payload
        except ExpiredSignatureError:
            logger.warning("JWT Token has expired.")
            raise ValueError("JWT Token has expired")
        except DecodeError as e:
            logger.exception(f"JWT Token is malformed: {str(e)}")
            raise ValueError("JWT Token is malformed")
        except InvalidTokenError as e:
            logger.exception(f"JWT Token is invalid: {str(e)}")
            raise ValueError(f"JWT Token is invalid: {str(e)}")
