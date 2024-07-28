import asyncio
import logging
from typing import Optional


logger = logging.getLogger(__name__)


class FlowState:
    """A state object for storing data between tasks."""

    def __init__(self):
        self.data = {}
        self.lock = asyncio.Lock()

    async def update(self, outer_key: str, values: dict):
        """Update the state with new values."""
        async with self.lock:
            if not isinstance(values, dict):
                raise ValueError("Values must be contained in a dictionary.")
            if outer_key not in self.data:
                self.data[outer_key] = {}
            for inner_key, inner_value in values.items():
                self.data[outer_key][inner_key] = inner_value

    async def get(self, outer_key: str, inner_key: str, default=None):
        """Get a value from the state."""
        async with self.lock:
            if outer_key not in self.data:
                raise ValueError(
                    f"Key {outer_key} does not exist in the state."
                )
            if inner_key not in self.data[outer_key]:
                return default or {}
            return self.data[outer_key][inner_key]

    async def delete(self, outer_key: str, inner_key: Optional[str] = None):
        """Delete a value from the state."""
        async with self.lock:
            if outer_key in self.data and not inner_key:
                del self.data[outer_key]
            else:
                if inner_key not in self.data[outer_key]:
                    raise ValueError(
                        f"Key {inner_key} does not exist in the state."
                    )
                del self.data[outer_key][inner_key]
