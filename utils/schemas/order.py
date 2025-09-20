from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrderCreateSchemaDB(BaseModel):
    user_id: Optional[int] = None
    amount: float
    status: Optional[str] = None


class OrderReadSchemaDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    amount: float
    status: str
    created_at: datetime
    paid_at: Optional[datetime] = None
