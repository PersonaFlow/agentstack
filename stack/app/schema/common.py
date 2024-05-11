from typing import Any
from pydantic import BaseModel
from typing import List
from stack.app.schema.user import User


class Result(BaseModel):
    Ok: Any = None
    Err: Any = None


class StartupResult(BaseModel):
    user: User
    isFirstLogin: bool
    assistants: List[str]
