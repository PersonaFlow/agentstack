"""
middlewares/request_logger.py
----------

This module provides a middleware that logs the HTTP request and response details into a PostgreSQL database. It's especially useful for tracking, debugging, and maintaining an audit trail of HTTP interactions.

Methods:
-------
- `set_body`: Utility to set the request body to be retrievable multiple times.
- `dispatch`: Core function of the middleware that captures, logs, and forwards the HTTP request. This function also captures the HTTP response after the request is processed.

Key Functionalities:
-------------------
- **Exclude Logging**: The middleware provides a way to exclude logging for certain endpoints defined in `settings.EXCLUDE_REQUEST_LOG_ENDPOINTS`.
- **Request Component Logging**: It captures various request components like endpoint, host, method, headers, query parameters, request body, and request ID (correlation ID).
- **Response Component Logging**: It captures response components like status code and response body.
- **Database Commit**: The middleware commits the logged request and response details into a PostgreSQL database.

Note:
-----
The middleware modifies the behavior of body retrieval to make it readable multiple times. This is necessary for logging the body while not consuming it for the actual request processing.

"""

import json

from asgi_correlation_id import correlation_id
from fastapi import Request, Response
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from pyserver.app.core.configuration import Settings

# from pyserver.app.core.pg_database import get_postgresql_session
from app.models.request_log import RequestLog


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    @staticmethod
    async def set_body(request: Request):
        _receive = await request._receive()  # noqa

        async def receive():
            return _receive

        request._receive = receive

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        settings: Settings = request.app.settings
        # session = get_postgresql_session(settings=settings, container=request)

        if request.url.path in settings.EXCLUDE_REQUEST_LOG_ENDPOINTS:
            return await call_next(request)

        await self.set_body(request)
        response = await call_next(request)

        # Request Component
        endpoint = request.url.path
        host = request.client.host
        method = request.method
        headers = dict(request.headers)
        query_parameters = dict(request.query_params)
        request_body = await request.body()
        request_body = {} if not request_body else json.loads(request_body.decode())
        request_id = correlation_id.get()

        # Response Component
        # https://stackoverflow.com/a/71883126
        status_code = response.status_code
        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))
        response_body = b"".join(response_body)
        response_body = {} if not response_body else json.loads(response_body.decode())

        async with session() as session:
            request_log = RequestLog(
                request_id=request_id,
                endpoint=endpoint,
                host=host,
                method=method,
                headers=headers,
                query_parameters=query_parameters,
                request_body=request_body,
                response_body=response_body,
                status_code=status_code,
            )

            session.add(request_log)
            await session.commit()

        return response
