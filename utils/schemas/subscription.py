from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from utils.enums.subscription import SubscriptionStatus


class SubscriptionCreateSchemaDB(BaseModel):
    order_id: int


class SubscriptionReadSchemaDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    order_id: int
    access_from: Optional[datetime]
    access_to: Optional[datetime]
    status: SubscriptionStatus
    created_at: Optional[datetime]
