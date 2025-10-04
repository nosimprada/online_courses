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

class UserReadFullInfoSchemaDB(UserReadSchemaDB):
    is_subscribed: bool = False
    created_at: datetime | None = None
    subscription_access_to: datetime | None = None
    user_id: int | None = None
    emails: list[str] = []
    completed_order_ids: list[int] = []
    expired_subscription_ids: list[int] = []
    leaning_progress_procent: float = 0.0
    