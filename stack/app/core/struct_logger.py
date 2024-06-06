"""
logger.py
----------

Logger Configuration for the Application.

This module sets up the structured logging for the application using `structlog`.
The logger is configured to produce logs in either a human-readable format for local
development or as structured JSON for other environments, like production. This
structured logging aids in observability and debugging, especially when the application
is deployed in cloud environments or containerized setups.

Functions:
---------
- `drop_color_message_key`: Removes the `color_message` key from the event dict. Uvicorn
  logs the message a second time in the `color_message` field, which is unnecessary for
  our purposes.
- `init_logger`: The main function that sets up the logger for the application. It configures
  processors, handlers, formatters, and other logging settings.
- `handle_validation_error`: Processes ValidationError instances in the logs, ensuring they
  are properly serialized.
- `handle_exception`: Global uncaught exception handler that logs exceptions instead of just
  letting Python print them. Ensures even unhandled exceptions are logged in our desired format.

Notes:
-----
Two gists were used as references to create this logger configuration:
- https://gist.github.com/nymous/f138c7f06062b7c43c060bf03759c29e
- https://gist.github.com/nkhitrov/38adbb314f0d35371eba4ffb8f27078f

Usage:
-----
Typically, this module is imported and used in the main application entry point to
initialize logging at the start of the application.

Example:
    ```python
    from stack.app.logger import init_logger
    from stack.app.core.configuration import Settings

    settings = Settings()
    init_logger(settings)
    ```

"""

import logging
import sys
from pydantic import ValidationError
import structlog
from structlog.types import EventDict, Processor

from stack.app.core.configuration import EnvironmentEnum, Settings


def drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    """Uvicorn logs the message a second time in the extra `color_message`, but
    we don't need it.

    This processor drops the key from the event dict if it exists.
    """
    event_dict.pop("color_message", None)
    return event_dict


def init_structlogger(settings: Settings):
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    def handle_validation_error(_, __, event_dict: EventDict) -> EventDict:
        error = event_dict.get("error")
        if isinstance(error, ValidationError):
            event_dict["error"] = error.json()
        return event_dict

    shared_processors: list[Processor] = [
        timestamper,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.contextvars.merge_contextvars,
        structlog.processors.CallsiteParameterAdder(
            {
                # structlog.processors.CallsiteParameter.PATHNAME,
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.THREAD,
                # structlog.processors.CallsiteParameter.THREAD_NAME,
                # structlog.processors.CallsiteParameter.PROCESS,
                structlog.processors.CallsiteParameter.PROCESS_NAME,
            }
        ),
        structlog.stdlib.ExtraAdder(),
        handle_validation_error,
        drop_color_message_key,
    ]

    # structlog.configure(
    #     processors=shared_processors
    #     + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
    #     logger_factory=structlog.stdlib.LoggerFactory(),
    #     # call log with await syntax in thread pool executor
    #     wrapper_class=structlog.stdlib.AsyncBoundLogger,
    #     cache_logger_on_first_use=True,
    # )

    # Use this configuration instead when refactoring the logs to remove async requirement
    structlog.configure(
        processors=shared_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_renderer: structlog.types.Processor

    if settings.ENVIRONMENT != EnvironmentEnum.LOCAL:
        log_renderer = structlog.dev.ConsoleRenderer()
    else:
        log_renderer = structlog.processors.JSONRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within
        # structlog.
        foreign_pre_chain=shared_processors,
        # These run on ALL entries after the pre_chain is done.
        processors=[
            # Remove _record & _from_structlog.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
    )

    handler = logging.StreamHandler()
    # Use OUR `ProcessorFormatter` to format all `logging` entries.
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOG_LEVEL.value)

    for _log in ["uvicorn", "uvicorn.error"]:
        # Clear the log handlers for uvicorn loggers, and enable propagation
        # so the messages are caught by our root logger and formatted correctly
        # by structlog
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True

    # Since we re-create the access logs ourselves, to add all information
    # in the structured log (see the `logging_middleware` in main.py), we clear
    # the handlers and prevent the logs to propagate to a logger higher up in the
    # hierarchy (effectively rendering them silent).
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False

    def handle_exception(exc_type, exc_value, exc_traceback):
        """Log any uncaught exception instead of letting it be printed by
        Python (but leave KeyboardInterrupt untouched to allow users to Ctrl+C
        to stop) See https://stackoverflow.com/a/16993115/3641865."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        root_logger.error(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception
