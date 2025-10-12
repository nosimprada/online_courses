from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserCreateSchemaDB(BaseModel):
    tg_id: int
    username: str | None = None


class UserReadSchemaDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tg_id: int
    username: str | None = None
    created_at: datetime


class UserReadFullInfoSchemaDB(UserReadSchemaDB):
    is_subscribed: bool = False
    subscription_access_to: datetime | None = None
    emails: list[str] = []
    completed_order_ids: list[int] = []
    expired_subscription_ids: list[int] = []
    leaning_progress_procent: float = 0.0
