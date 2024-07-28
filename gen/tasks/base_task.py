import logging
import asyncio
import logging
import uuid
from abc import abstractmethod
from enum import Enum
from typing import Any, AsyncGenerator, Optional
from pydantic import BaseModel

from gen.core.run_manager import RunManager, manage_run
from gen.tasks.flow_state import FlowState

logger = logging.getLogger(__name__)


class TaskType(Enum):
    INGEST = "ingest"
    EVAL = "eval"
    GENERATE = "generate"
    SEARCH = "search"
    MUTATE = "mutate"
    OTHER = "other"


class BaseTask:
    """An asynchronous task for processing data with logging capabilities."""

    class TaskConfig(BaseModel):
        """Configuration for a task."""

        name: str = "default_task"
        log_level: int = logging.INFO

        class Config:
            extra = "forbid"
            arbitrary_types_allowed = True

    class Input(BaseModel):
        """Input for a task."""

        message: AsyncGenerator[Any, None]

        class Config:
            extra = "forbid"
            arbitrary_types_allowed = True

    def __init__(
        self,
        type: TaskType = TaskType.OTHER,
        config: Optional[TaskConfig] = None,
        run_manager: Optional[RunManager] = None,
    ):
        self._config = config or self.TaskConfig()
        self._type = type
        self.task_logger = self._setup_logger()
        self._run_manager = run_manager or RunManager(self.task_logger)

        logger.debug(
            f"Initialized task {self.config.name} of type {self.type}"
        )

    def _setup_logger(self):
        task_logger = logging.getLogger(f"{__name__}.{self.config.name}")
        task_logger.setLevel(self.config.log_level)
        if not task_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            task_logger.addHandler(handler)
        return task_logger

    @property
    def config(self) -> TaskConfig:
        return self._config

    @property
    def type(self) -> TaskType:
        return self._type

    async def log(self, run_id: uuid.UUID, key: str, value: str):
        log_message = f"Run ID: {run_id}, Key: {key}, Value: {value}"
        self.task_logger.info(log_message)

    def update_config(self, new_config: dict) -> None:
        """Update the task's configuration."""
        self._config = self.TaskConfig(**{**self._config.dict(), **new_config})

    async def validate_input(self, input: Input) -> bool:
        """Validate the input data for the task."""
        return True  # Implement specific validation logic in subclasses

    async def validate_output(self, output: Any) -> bool:
        """Validate the output data of the task."""
        return True  # Implement specific validation logic in subclasses


    async def run(
        self,
        input: Input,
        state: FlowState,
        run_manager: Optional[RunManager] = None,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncGenerator[Any, None]:
        """Run the task with logging capabilities."""

        run_manager = run_manager or self._run_manager

        async def wrapped_run() -> AsyncGenerator[Any, None]:
            async with manage_run(run_manager, self.config.name) as run_id:
                try:
                    async for result in self._run_task(
                        input, state, run_id=run_id, *args, **kwargs
                    ):
                        yield result
                except Exception as e:
                    self.task_logger.exception(f"Error in task {self.config.name}: {str(e)}")
                    raise


        return wrapped_run()

    @abstractmethod
    async def _run_task(
        self,
        input: Input,
        state: FlowState,
        run_id: uuid.UUID,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncGenerator[Any, None]:
        pass
