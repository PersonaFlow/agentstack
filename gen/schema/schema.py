import uuid
from typing import List, Protocol

from pydantic import BaseModel


class Fact(BaseModel):
    id: uuid.UUID
    name: str
    version: str
    question: str
    answer: str
    weight: float = 1.0


class Trait(BaseModel):
    id: uuid.UUID
    name: str
    version: str
    facts: List[Fact]
    weight: float = 1.0


class Persona(BaseModel):
    id: uuid.UUID
    name: str
    traits: List[Trait]
    version: str


class Configuration(BaseModel):
    # Stub for now
    embed_settings: str = ""


class Task(Protocol):
    configuration: Configuration

    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    def __call__(self, *args, **kwargs):
        ...


class Flow(Protocol):
    configuration: Configuration
    tasks: List[Task]

    def __call__(self, *args, **kwargs):
        ...


class QAFlow(Flow):
    configuration: Configuration
    tasks: List[Task]

    def __init__(self, configuration: Configuration, tasks: List[Task]):
        self.configuration = configuration
        self.tasks = tasks

    def __call__(self, *args, **kwargs):
        pass

