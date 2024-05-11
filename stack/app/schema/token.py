from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    # limeade_account_id: int
    # employer_id: int
    # one_tenant_id: str | None
    # limeade_one: bool = False
    # role: List[str]
    # scope: List[str]
    # status: str | None
    user_store_id: str

    # Scope is sometimes a space delimited string. Convert to list.
    # @validator("scope", pre=True)
    # def result_check(cls, v):
    #     ...
    #     return v.split(" ") if isinstance(v, str) else v

    class Config:
        from_attributes = True


class Auth0Token(TokenResponse):
    # limeade_account_id: int = Field(
    #     None, alias="https://limeade.com/limeade_account_id"
    # )
    # employer_id: int = Field(alias="https://limeade.com/employer_id")
    # one_tenant_id: str = Field(None, alias="https://limeade.com/one_tenant_id")
    # limeade_one: bool = Field(False, alias="https://limeade.com/limeade_one")
    # role: List[str] = Field(alias="https://limeade.com/role")
    user_store_id: str = Field(alias="https://limeade.com/user_store_id")
