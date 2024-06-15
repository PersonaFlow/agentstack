import re

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, declared_attr

from stack.app.core.configuration import settings


def camel_to_snake_case(name: str):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class _Base:
    @declared_attr
    def __tablename__(cls):
        return camel_to_snake_case(cls.__name__)

    @declared_attr
    def alias(cls):
        return camel_to_snake_case(cls.__name__)


Base = declarative_base(
    cls=_Base, metadata=MetaData(schema=settings.INTERNAL_DATABASE_SCHEMA)
)
