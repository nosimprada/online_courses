from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreateSchemaDB(BaseModel):
    user_id: int
    username: str | None = None
    # email: str | None = None


class UserReadSchemaDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int = Field(alias="tg_id")
    username: str | None = None
    # email: str | None = None
    created_at: datetime
