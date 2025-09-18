import enum
from pydantic import BaseModel
from datetime import datetime

class TicketStatus(enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"