import enum
from pydantic import BaseModel
from datetime import datetime

class SubscriptionStatus(enum.Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELED = "CANCELED"