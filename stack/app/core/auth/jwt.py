from datetime import datetime, timedelta, timezone
import structlog
import uuid
import jwt
from stack.app.core.configuration import get_settings

logger = structlog.get_logger()

settings = get_settings()
class JWTService:

    def __init__(self):
        secret_key = settings.AUTH_SECRET_KEY
        algorithm = settings.JWT_ALGORITHM
        expiry = settings.TOKEN_EXPIRY_HOURS
        issuer = settings.JWT_ISSUER

        if not secret_key:
            raise ValueError("Secret auth key is not set.")

        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiry = expiry
        self.issuer = issuer

    def create_and_encode_jwt(self, user: dict) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "iss": self.issuer,
            "iat": now,
            "exp": now + timedelta(hours=self.expiry),
            "jti": str(uuid.uuid4()),
            "context": user,
        }

        token = jwt.encode(payload, self.secret_key, self.algorithm)

        return token

    def decode_jwt(self, token: str) -> dict:
        try:
            decoded_payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return decoded_payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired.")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token.")
            return None
