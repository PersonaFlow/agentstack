import logging
import os

# from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
from stack.app.core.auth.auth_config import (
    is_authentication_enabled,
    get_auth_strategy_endpoints,
)

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


@app.on_event("startup")
async def startup_event():
    """Retrieves all the Auth provider endpoints if authentication is
    enabled."""
    if is_authentication_enabled():
        await get_auth_strategy_endpoints()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
