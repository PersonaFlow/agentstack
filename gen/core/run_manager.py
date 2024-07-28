import contextvars
import uuid
import logging
from contextlib import asynccontextmanager
from typing import Any, Optional

run_id_var = contextvars.ContextVar("run_id", default=None)

class RunManager:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.run_info = {}

    def generate_run_id(self) -> uuid.UUID:
        return uuid.uuid4()

    async def set_run_info(self, pipeline_type: str):
        run_id = run_id_var.get()
        if run_id is None:
            run_id = self.generate_run_id()
            token = run_id_var.set(run_id)
            self.run_info[run_id] = {"pipeline_type": pipeline_type}
        else:
            token = run_id_var.set(run_id)
        return run_id, token

    async def get_run_info(self):
        run_id = run_id_var.get()
        return self.run_info.get(run_id, None)

    async def log_run_info(self, key: str, value: Any, is_info_log: bool = False):
        run_id = run_id_var.get()
        if run_id:
            log_message = f"Run ID: {run_id}, Key: {key}, Value: {value}"
            if is_info_log:
                self.logger.info(log_message)
            else:
                self.logger.debug(log_message)

    async def clear_run_info(self, token: contextvars.Token):
        run_id = run_id_var.get()
        run_id_var.reset(token)
        if run_id and run_id in self.run_info:
            del self.run_info[run_id]

@asynccontextmanager
async def manage_run(run_manager: RunManager, flow_type: str):
    run_id, token = await run_manager.set_run_info(flow_type)
    try:
        yield run_id
    finally:
        run_id_var.reset(token)


# Example usage:
# logging.basicConfig(level=logging.INFO)
# run_manager = RunManager()
# async with manage_run(run_manager, "example_pipeline") as run_id:
#     await run_manager.log_run_info("step", "Started processing", is_info_log=True)
#     # Your pipeline code here
#     await run_manager.log_run_info("step", "Finished processing", is_info_log=True)
