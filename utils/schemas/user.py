from pydantic import BaseModel

class UserCreateSchemaDB(BaseModel):
    tg_id: int
    username: str | None = None
    email: str
