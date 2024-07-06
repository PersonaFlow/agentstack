from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    """Base model for user data."""

    username: Optional[str] = Field(
        None,
        description="(Optional) The username chosen by the user. It's a string type and does not need to be unique across the userbase.",
    )
    email: Optional[str] = Field(
        None,
        description="(Optional) The email address associated with the user's account. It's a string type and is expected to be unique across the userbase",
    )
    first_name: Optional[str] = Field(
        None, description="(Optional) The first name of the user."
    )
    last_name: Optional[str] = Field(
        None, description="(Optional) The last name of the user."
    )
    kwargs: Optional[dict] = Field(
        None, description="(Optional) Additional kwargs associated with the user."
    )

    class Config:
        from_attributes = True


class User(UserBase):
    """Model representing a registered user in the application."""

    user_id: str = Field(
        ...,
        description="Unique identifier for the user to be used across the application. Set once when the user is created and cannot be updated thereafter. Can be used for correlating local user with external systems. Autogenerates if none is provided.",
    )
    created_at: datetime = Field(..., description="Created date")
    updated_at: datetime = Field(..., description="Last updated date")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.replace(microsecond=0).isoformat(),
        }


class CreateUpdateUserSchema(UserBase):
    password: Optional[str] = Field(
        None, description="(Optional) Password for the new user account."
    )
    user_id: Optional[str] = Field(
        None,
        description="Identifier for the user to be used across the application. Can be used for correlating local user with external systems. Autogenerates if none is provided.",
    )
