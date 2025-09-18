import enum

class SubscriptionStatus(enum.Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELED = "CANCELED"