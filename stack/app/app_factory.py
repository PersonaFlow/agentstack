from typing import Callable
from contextlib import asynccontextmanager
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request, status
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.openapi.utils import get_openapi

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from stack.app.core.auth.auth_config import is_authentication_enabled
from stack.app.api.v1 import api_router
from stack.app.core.configuration import Settings
from stack.app.core.logger import init_logging
from stack.app.core.struct_logger import init_structlogger
from stack.app.middlewares.system_logger import SystemLoggerMiddleware
from stack.app.utils.exceptions import UniqueConstraintViolationError
from stack.app.core.auth.auth_config import get_auth_strategy_endpoints


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


def get_custom_openapi(app: FastAPI, settings: Settings):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        routes=app.routes,
    )

    # Add SecurityScheme for JWT
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Add security to all operations
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"Bearer Auth": []}]

    openapi_schema["info"]["x-logo"] = {
        "url": "../../../assets/PersonaFlowIcon-512.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


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

    if is_authentication_enabled():
        # Required to save temporary OAuth state in session
        _app.add_middleware(SessionMiddleware, secret_key=settings.AUTH_SECRET_KEY)

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

    @_app.exception_handler(UniqueConstraintViolationError)
    async def unique_constraint_exception_handler(
        request: Request, exc: UniqueConstraintViolationError
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    _app.settings = settings
    _app.include_router(api_router, prefix="/api/v1")
    _app.openapi = lambda: get_custom_openapi(_app, settings)

    @_app.on_event("startup")
    async def startup_event():
        if is_authentication_enabled():
            await get_auth_strategy_endpoints()

    return _app
