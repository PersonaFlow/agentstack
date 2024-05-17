import logging
import os
from dotenv import load_dotenv
# from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi.openapi.utils import get_openapi

# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# If we have the `ENVIRONMENT`variable already, we are running in Docker or Kubernetes
# and do not need to load the .env file
environment = os.getenv("ENVIRONMENT")
if not environment:
    env_path = ".env"
    load_dotenv(env_path)

from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings

settings = Settings()

"""
Application Insights configuration
Set the logging level for all azure-* libraries
(Disabled if APPLICATIONINSIGHTS_CONNECTION_STRING is not set)
"""
logging.getLogger("azure").setLevel(logging.WARN)
logging.getLogger("httpcore").setLevel(logging.WARN)
logging.getLogger("urllib3").setLevel(logging.WARN)
logging.getLogger("opentelemetry").setLevel(logging.WARN)
AI_CONN_STR_ENV_NAME = "APPLICATIONINSIGHTS_CONNECTION_STRING"
AI_CONN_STR = os.getenv(AI_CONN_STR_ENV_NAME)
# if AI_CONN_STR and AI_CONN_STR != "":
#     configure_azure_monitor(
#         connection_string=os.getenv(AI_CONN_STR_ENV_NAME),
#         logger_name="personaflow",
#         logging_level=os.getenv("INFO"),
#     )

if settings.ENABLE_LANGSMITH_TRACING:
    from langsmith import Client

    client = Client()

app = create_app(settings)
# FastAPIInstrumentor.instrument_app(app)


def get_custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "../../assets/PersonaFlowIcon-512.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
