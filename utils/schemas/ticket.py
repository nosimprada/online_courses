from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from utils.enums.ticket import TicketStatus


class TicketCreateSchemaDB(BaseModel):
    user_id: int
    topic: str
    text: str
    attachments: Optional[str] = None
    status: TicketStatus = TicketStatus.PENDING


class TicketReadSchemaDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    topic: str
    text: str
    attachments: Optional[str] = None
    status: TicketStatus

    created_at: datetime
    resolved_at: Optional[datetime] = None
