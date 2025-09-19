from sqlalchemy import (
    BigInteger, 
    Column,
    Enum, 
    Integer, 
    String, 
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import (
    datetime
    )
import pytz
from utils.database import Base
import datetime

from utils.enums.subscription import SubscriptionStatus

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
        default=lambda: datetime.datetime.now(pytz.timezone("Europe/Kiev")),
        nullable=False
        )

    order = relationship("Order", backref="subscriptions")