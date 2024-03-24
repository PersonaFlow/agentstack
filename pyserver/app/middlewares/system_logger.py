"""
middlewares/system_logger.py
----------

This module provides a middleware to perform structured logging of HTTP requests and responses in a system-friendly format. It leverages the `structlog` library for structured logging and the `correlation_id` library to manage unique request identifiers.

Types:
-----
- `SystemLoggerMiddleware`: Custom middleware class that extends `BaseHTTPMiddleware` from Starlette.

Methods:
-------
- `dispatch`: Core function of the middleware. It captures the HTTP request and response details, logs them in a structured format, and then forwards the response to the next middleware or the endpoint.

Key Functionalities:
-------------------
- **Context Setup**: At the start of every request, the logger context is cleared and a new context is set up with the request's unique identifier (`request_id`).
- **Request Time Measurement**: Measures the time taken to process the request using `time.perf_counter_ns()`.
- **Structured Logging**: The middleware logs various request components like client IP and port, method, URL, HTTP version, and the processing time. These logs are structured, making them easier to analyze in a log management system.
- **Error Handling**: If an exception occurs while processing the request, it's logged under "api.error", and a generic 500 response is returned.
- **Custom Headers**: The middleware also sets a custom header (`X-Process-Time`) in the response to indicate the processing time in seconds.

Note:
-----
This middleware is especially valuable for monitoring and observability purposes. Structured logs can be easily integrated with modern log management systems for easier analysis and troubleshooting.

"""

import time

import structlog
from asgi_correlation_id.context import correlation_id
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from uvicorn.protocols.utils import get_path_with_query_string


class SystemLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        structlog.contextvars.clear_contextvars()
        # These context vars will be added to all log entries emitted during the request
        request_id = correlation_id.get()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter_ns()
        # If the call_next raises an error, we still want to return our own 500 response,
        # so we can add headers to it (process time, request ID...)
        response = Response(status_code=500)

        try:
            response = await call_next(request)
        except Exception:
            structlog.stdlib.get_logger("api.error").exception("Uncaught exception")
            raise

        finally:
            process_time = time.perf_counter_ns() - start_time
            status_code = response.status_code
            url = get_path_with_query_string(request.scope)
            client_host = request.client.host
            client_port = request.client.port
            http_method = request.method
            http_version = request.scope["http_version"]
            # Recreate the Uvicorn access log format, but add all parameters as structured information
            access_logger = structlog.stdlib.get_logger("api.access")
            await access_logger.info(
                f"""{client_host}:{client_port} - "{http_method} {url} HTTP/{http_version}" {status_code}""",
                http={
                    "url": str(request.url),
                    "status_code": status_code,
                    "method": http_method,
                    "request_id": request_id,
                    "version": http_version,
                },
                network={"client": {"ip": client_host, "port": client_port}},
                duration=process_time,
            )
            response.headers["X-Process-Time"] = str(process_time / 10**9)

        return response
