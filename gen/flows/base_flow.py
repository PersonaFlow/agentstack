"""Base flow class for running a sequence of tasks."""

import asyncio
import logging
from enum import Enum
from typing import Any, AsyncGenerator, Optional

from gen.core.run_manager import RunManager, manage_run
from gen.tasks.base_task import BaseTask
from gen.tasks.flow_state import FlowState

logger = logging.getLogger(__name__)


class FlowTypes(Enum):
    EVAL = "eval"
    INGESTION = "ingestion"
    SEARCH = "search"
    OTHER = "other"


class BaseFlow:
    """Flow class for running a sequence of tasks."""

    flow_type: str = "other"

    def __init__(
        self,
        run_manager: Optional[RunManager] = None,
    ):
        self.tasks: list[BaseTask] = []
        self.upstream_outputs: list[list[dict[str, str]]] = []
        self.run_manager = run_manager or RunManager()
        self.futures = {}
        self.level = 0

    def add_task(
        self,
        task: BaseTask,
        add_upstream_outputs: Optional[list[dict[str, str]]] = None,
        *args,
        **kwargs,
    ) -> None:
        """Add a task to the flow."""
        self.tasks.append(task)
        if not add_upstream_outputs:
            add_upstream_outputs = []
        self.upstream_outputs.append(add_upstream_outputs)

    async def run(
        self,
        input: Any,
        state: Optional[FlowState] = None,
        stream: bool = False,
        run_manager: Optional[RunManager] = None,
        log_run_info: bool = True,
        *args: Any,
        **kwargs: Any,
    ):
        """Run the flow."""
        run_manager = run_manager or self.run_manager

        try:
            FlowTypes(self.flow_type)
        except ValueError:
            raise ValueError(
                f"Invalid flow type: {self.flow_type}, must be one of {FlowTypes.__members__.keys()}"
            )

        self.state = state or FlowState()
        current_input = input
        async with manage_run(run_manager, self.flow_type):
            if log_run_info:
                logger.info(f"Flow type: {self.flow_type}")
            try:
                for task_num in range(len(self.tasks)):
                    config_name = self.tasks[task_num].config.name
                    self.futures[config_name] = asyncio.Future()

                    current_input = self._run_task(
                        task_num,
                        current_input,
                        run_manager,
                        *args,
                        **kwargs,
                    )
                    self.futures[config_name].set_result(current_input)
                if not stream:
                    final_result = await self._consume_all(current_input)
                    return final_result
                else:
                    return current_input
            except Exception as error:
                logger.error(f"Flow failed with error: {error}")
                raise error

    async def _consume_all(self, gen: AsyncGenerator) -> list[Any]:
        result = []
        async for item in gen:
            if hasattr(
                item, "__aiter__"
            ):  # Check if the item is an async generator
                sub_result = await self._consume_all(item)
                result.extend(sub_result)
            else:
                result.append(item)
        return result

    async def _run_task(
        self,
        task_num: int,
        input: Any,
        run_manager: RunManager,
        *args: Any,
        **kwargs: Any,
    ):
        # Collect inputs, waiting for the necessary futures
        task = self.tasks[task_num]
        add_upstream_outputs = self.sort_upstream_outputs(
            self.upstream_outputs[task_num]
        )
        input_dict = {"message": input}

        # Group upstream outputs by prev_task_name
        grouped_upstream_outputs = {}
        for upstream_input in add_upstream_outputs:
            upstream_task_name = upstream_input["prev_task_name"]
            if upstream_task_name not in grouped_upstream_outputs:
                grouped_upstream_outputs[upstream_task_name] = []
            grouped_upstream_outputs[upstream_task_name].append(upstream_input)

        for (
            upstream_task_name,
            upstream_inputs,
        ) in grouped_upstream_outputs.items():

            async def resolve_future_output(future):
                result = future.result()
                # consume the async generator
                return [item async for item in result]

            async def replay_items_as_async_gen(items):
                for item in items:
                    yield item

            temp_results = await resolve_future_output(
                self.futures[upstream_task_name]
            )
            if upstream_task_name == self.tasks[task_num - 1].config.name:
                input_dict["message"] = replay_items_as_async_gen(temp_results)

            for upstream_input in upstream_inputs:
                outputs = await self.state.get(upstream_task_name, "output")
                prev_output_field = upstream_input.get(
                    "prev_output_field", None
                )
                if not prev_output_field:
                    raise ValueError(
                        "`prev_output_field` must be specified in the upstream_input"
                    )
                input_dict[upstream_input["input_field"]] = outputs[
                    prev_output_field
                ]

        # Handle the task generator
        async for ele in await task.run(
            task.Input(**input_dict),
            self.state,
            run_manager,
            *args,
            **kwargs,
        ):
            yield ele

    def sort_upstream_outputs(
        self, add_upstream_outputs: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        task_name_to_index = {
            task.config.name: index for index, task in enumerate(self.tasks)
        }

        def get_task_index(upstream_output):
            return task_name_to_index[upstream_output["prev_task_name"]]

        sorted_outputs = sorted(
            add_upstream_outputs, key=get_task_index, reverse=True
        )
        return sorted_outputs

    def get_task(self, task_name: str) -> Optional[BaseTask]:
        """Get a task by its name."""
        return next((task for task in self.tasks if task.config.name == task_name), None)

    def remove_task(self, task_name: str) -> None:
        """Remove a task from the flow by its name."""
        self.tasks = [task for task in self.tasks if task.config.name != task_name]
        self.upstream_outputs = [
            outputs for task, outputs in zip(self.tasks, self.upstream_outputs)
            if task.config.name != task_name
        ]

    async def validate(self) -> bool:
        """Validate the entire flow."""
        for i, task in enumerate(self.tasks):
            if i > 0:
                prev_task = self.tasks[i-1]
                mock_input = BaseTask.Input(message=prev_task._run_task(None, None, None))
                if not await task.validate_input(mock_input):
                    return False
        return True


class EvalFlow(BaseFlow):
    """A flow for evaluation."""

    flow_type: str = "eval"

    async def run(
        self,
        input: Any,
        state: Optional[FlowState] = None,
        stream: bool = False,
        run_manager: Optional[RunManager] = None,
        *args: Any,
        **kwargs: Any,
    ):
        return await super().run(
            input, state, stream, run_manager, *args, **kwargs
        )

    def add_task(
        self,
        task: BaseTask,
        add_upstream_outputs: Optional[list[dict[str, str]]] = None,
        *args,
        **kwargs,
    ) -> None:
        logger.debug(f"Adding task {task.config.name} to the EvalFlow")
        return super().add_task(task, add_upstream_outputs, *args, **kwargs)


async def dequeue_requests(queue: asyncio.Queue) -> AsyncGenerator:
    """Create an async generator to dequeue requests."""
    while True:
        request = await queue.get()
        if request is None:
            break
        yield request
