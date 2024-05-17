import uuid
from typing import List

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
