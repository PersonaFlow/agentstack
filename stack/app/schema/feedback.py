from datetime import datetime
from typing import Dict, Optional, Union
from uuid import UUID

from pydantic import BaseModel


class BaseFeedback(BaseModel):
    """Shared information between create requests of feedback and feedback
    objects."""

    run_id: UUID
    """The associated run ID this feedback is logged for."""

    key: str
    """The metric name, tag, or aspect to provide feedback on."""

    score: Optional[Union[float, int, bool]] = None
    """Value or score to assign the run."""

    value: Optional[Union[float, int, bool, str, Dict]] = None
    """The display value for the feedback if not a metric."""

    comment: Optional[str] = None
    """Comment or explanation for the feedback."""


class FeedbackCreateRequest(BaseFeedback):
    """Represents a request that creates feedback for an individual run."""


class Feedback(BaseFeedback):
    """Represents feedback given on an individual run."""

    id: UUID
    """The unique ID of the feedback that was created."""

    created_at: datetime
    """The time the feedback was created."""

    modified_at: datetime
    """The time the feedback was last modified."""

    correction: Optional[Dict] = None
    """Correction for the run."""
