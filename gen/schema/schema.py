import uuid
from typing import List

from pydantic import BaseModel


class Trait(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    question: str
    answer: str


class Persona(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    name: str
    traits: List[Trait]


class Configuration(BaseModel):
    # Stub for now
    embed_settings: str = ""
