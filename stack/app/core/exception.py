"""
exception.py
----------
This module defines custom exception classes extending FastAPI's HTTPException.

These exceptions are tailored to cater to common error scenarios in the application,
enabling consistent error responses and ensuring that the response codes align with
the HTTP standard.

"""

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    def __init__(self, message: str = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=message or "Record Not Found"
        )


class UnauthorizedException(HTTPException):
    def __init__(self, message: str = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message or "Can not validate credentials",
        )
