from pydantic import BaseModel
from sqlalchemy import DateTime

class UserCreateSchemaDB(BaseModel):
    user_id: int
    username: str | None = None
    email: str | None = None

class UserReadSchemaDB(BaseModel):
    user_id: int
    username: str | None = None
    email: str | None = None
    created_at: DateTime
