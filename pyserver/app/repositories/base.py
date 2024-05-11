"""
repositories/base.py
----------

This module provides a generic base repository class to interface with the database for CRUD operations. It abstracts away the common patterns in data access so that the higher-level application layers remain free from low-level database operations.
This base repository can be extended to add more specific methods or override the existing ones based on requirements.

Classes:
-------
- `BaseRepository`: A foundational repository class that provides generic CRUD operations.
    - `create`: Adds a new record to the database.
    - `retrieve_one`: Fetches a single record from the database based on a given query and ID.
    - `retrieve_all`: Retrieves all records based on a given query.
    - `retrieve_by_field`: Fetches a single record from the database based on a given field and value.
    - `update`: Modifies an existing record in the database based on its UUID.
    - `update_by_field`: Updates a record based on a specified field.
    - `delete`: Removes a record from the database based on its UUID.
    - `delete_by_field`: Removes a record based on a specified field.

"""

import uuid
from typing import Type

from sqlalchemy import delete, select, update, cast, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from typing import Optional, Dict, Any


class BaseRepository:
    def __init__(self, postgresql_session: AsyncSession):
        """Initializes the repository with a given PostgreSQL session.

        :param postgresql_session: The SQLAlchemy asynchronous session.
        """
        self.postgresql_session = postgresql_session

    async def create(self, model, values: dict):
        """Creates a new record in the database for the given model.

        :param model: The SQLAlchemy model class.
        :param values: A dictionary of values to set for the new record.
        :return: The newly created record.
        """
        record = model(**values)
        self.postgresql_session.add(record)
        return record

    async def retrieve_one(self, query: Select, object_id: uuid.UUID):
        """Retrieves a single record by its UUID.

        :param query: The base SQLAlchemy select query.
        :param object_id: The unique identifier of the record.
        :return: The record if found, otherwise None.
        """
        table_cte = query.cte("record")
        query = select(table_cte.columns)
        query = query.where(table_cte.columns.id == object_id)
        result = await self.postgresql_session.execute(query)
        record = result.fetchone()
        return record

    async def retrieve_by_field(self, model: Type[Any], field: Any, field_value: Any):
        """Retrieves a record in the database based on a specified field.

        :param model: The SQLAlchemy model class.
        :param field: The field to be used for the WHERE clause.
        :param field_value: The value of the field to match.
        :return: The record if found, otherwise None.
        """
        query = select(model).where(field == field_value)
        result = await self.postgresql_session.execute(query)
        record = result.scalars().first()
        return record

    async def retrieve_all(
        self, model: Type[Any], filters: Optional[Dict[str, Any]] = None
    ):
        """Retrieves all records that match the given filters. It is made to
        handle advanced filtering scenarios like array containment.

        :param model: The SQLAlchemy model class to query.
        :param filters: A dictionary of filters to apply.
        :return: A list of records that match the filters.
        """
        query = select(model)

        if filters:
            conditions = []
            for key, value in filters.items():
                if not hasattr(model, key):
                    continue

                if not isinstance(value, dict):
                    conditions.append(getattr(model, key) == value)
                    continue

                for op, op_value in value.items():
                    if op != "contains":
                        raise ValueError(f"Unsupported operator: {op}")

                    conditions.append(
                        cast(getattr(model, key), ARRAY(String)).contains(op_value)
                    )

            query = query.filter(*conditions)

        result = await self.postgresql_session.execute(query)
        records = result.scalars().all() or []
        return records

    async def update(self, model, values: dict, object_id: uuid.UUID):
        """Updates an existing record by its ID.

        :param model: The SQLAlchemy model class.
        :param values: A dictionary of values to update.
        :param object_id: The unique identifier of the record to update.
        :return: The updated record.
        """
        query = (
            update(model).values(**values).where(model.id == object_id).returning(model)
        )
        result = await self.postgresql_session.execute(query)
        record = result.scalars().one()
        return record

    async def update_by_field(
        self, model: Type[Any], values: dict, field: Any, field_value: Any
    ):
        """Updates a record in the database based on a specified field.

        :param model: The SQLAlchemy model class.
        :param values: A dictionary of values to update.
        :param field: The field to be used for the WHERE clause.
        :param field_value: The value of the field to match.
        :return: The updated record.
        """
        query = (
            update(model).values(**values).where(field == field_value).returning(model)
        )
        result = await self.postgresql_session.execute(query)
        record = result.scalars().one()
        return record

    async def delete(self, model, object_id: uuid.UUID):
        """Deletes a record by its ID.

        :param model: The SQLAlchemy model class.
        :param object_id: The unique identifier of the record to delete.
        :return: The deleted record, or None if no record was found.
        """
        query = delete(model).where(model.id == object_id).returning(model)
        result = await self.postgresql_session.execute(query)
        record = result.scalars().one()
        return record

    async def delete_by_field(self, model: Type[Any], field: Any, field_value: Any):
        """Deletes a record in the database based on a specified field.

        :param model: The SQLAlchemy model class.
        :param field: The field to be used for the WHERE clause.
        :param field_value: The value of the field to match.
        :return: The deleted record, or None if no record was found.
        """
        query = delete(model).where(field == field_value).returning(model)
        result = await self.postgresql_session.execute(query)
        record = result.scalars().one()
        return record
