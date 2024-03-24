"""
models/base.py
----------

This module provides the foundational constructs and utilities for defining ORM models in SQLAlchemy with custom behaviors, naming conventions, and schema configurations. It ensures consistent structure across all ORM models.
Functions:
---------
- `camel_to_snake_case(name: str)`: Converts a CamelCase string to a snake_case string.

Classes:
-------
- `_Base`: An internal class that provides foundational behaviors for all ORM models. Not meant to be instantiated directly.
    - `__tablename__`: Class method that returns the snake_case table name for the ORM model.
    - `alias`: Class method that returns an alias for the ORM model (usually the snake_case version of the model name).

- `Base`: The main base class for all ORM models in the system. It leverages SQLAlchemy's `declarative_base` to provide a common foundation for ORM models. All models should inherit from this class.

Key Functionalities:
-------------------
- **Automatic Table Naming**: By leveraging the `__tablename__` method in the `_Base` class, the system can automatically generate the table name in snake_case format based on the model's class name.
- **Schema Configuration**: The `Base` class is configured with the schema defined in the system's settings, ensuring that all models use the specified database schema.
- **Alias Generation**: Provides a utility to generate an alias for the model.

Note:
-----
This module centralizes the foundational logic for defining ORM models, ensuring that developers can define new models with consistent naming conventions and behaviors without repeating the same boilerplate code.

"""

import re

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, declared_attr

from app.core.configuration import settings


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
