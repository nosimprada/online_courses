from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SubscriptionCreateSchemaDB(BaseModel):
    user_id: Optional[int] = None
    order_id: int
    access_from: datetime
    access_to: datetime
    status: Optional[str] = None


class SubscriptionReadSchemaDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    order_id: int
    access_from: datetime
    access_to: datetime
    status: str
    created_at: datetime
