from datetime import datetime

from pytz import timezone
from sqlalchemy import (
    BigInteger,
    Column,
    Enum,
    Integer,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship, Mapped

from utils.database import Base
from utils.enums.subscription import SubscriptionStatus
from utils.models.order import Order


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    access_from = Column(DateTime, nullable=False)
    access_to = Column(DateTime, nullable=False)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.CREATED)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None),
        nullable=False
    )

    order: Mapped["Order"] = relationship("Order", backref="subscriptions")
