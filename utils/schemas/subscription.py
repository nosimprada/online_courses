from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from utils.enums.subscription import SubscriptionStatus


class SubscriptionCreateSchemaDB(BaseModel):
    order_id: int



class SubscriptionReadSchemaDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    order_id: int
    access_from: datetime | None
    access_to: datetime | None
    status: SubscriptionStatus
    created_at: datetime | None
