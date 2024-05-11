from typing import Callable
from contextlib import asynccontextmanager
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request, status
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from pyserver.app.core import init_logging, init_structlogger
from pyserver.app.api.v1 import api_router
from pyserver.app.core.configuration import Settings
from pyserver.app.middlewares import SystemLoggerMiddleware


def create_async_engine_with_settings(settings: Settings) -> AsyncEngine:
    return create_async_engine(settings.INTERNAL_DATABASE_URI, echo=True)


def get_lifespan(settings: Settings) -> Callable:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.async_engine = create_async_engine_with_settings(settings)
        try:
            yield
        finally:
            await app.state.async_engine.dispose()

    return lifespan


def create_app(settings: Settings):
    init_structlogger(settings)
    init_logging()

    middleware = [
        Middleware(CorrelationIdMiddleware),
        Middleware(SystemLoggerMiddleware),
        # Request logger needs to be refactored to use db session
        # Middleware(RequestLoggerMiddleware),
    ]
    _app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        lifespan=get_lifespan(settings),
        middleware=middleware,
        openapi_url="/api/v1/openapi.json",
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @_app.exception_handler(ValueError)
    async def value_error_exception_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": [{"loc": None, "msg": str(exc), "type": "value_error"}]},
        )

    @_app.exception_handler(Exception)
    async def universal_exception_handler(request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred."},
        )

    @_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @_app.exception_handler(ResponseValidationError)
    async def response_validation_exception_handler(
        request, exc: ResponseValidationError
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @_app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    _app.settings = settings
    _app.include_router(api_router, prefix="/api/v1")

    return _app
