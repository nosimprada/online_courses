from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationHistoryCreateSchemaDB(BaseModel):
    user_id: int
    days_diff: int


class NotificationHistoryReadSchemaDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    days_diff: int
    sent_at: datetime
