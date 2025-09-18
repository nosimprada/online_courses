from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import (
    datetime, 
    )
import pytz
from utils.database import Base
import datetime

from utils.enums.order import OrderStatus

class RedeemToken(Base):
    __tablename__ = "redeem_tokens"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    token_hash = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(pytz.timezone("Europe/Kiev")),
        nullable=False
        )
    used_at = Column(DateTime, nullable=True)

    order = relationship("Order", backref="redeem_tokens")