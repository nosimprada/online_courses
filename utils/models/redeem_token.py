from datetime import datetime

from pytz import timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from utils.database import Base


class RedeemToken(Base):
    __tablename__ = "redeem_tokens"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False, index=True)
    token_hash = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None),
        nullable=False
    )
    used_at = Column(DateTime, nullable=True)

    order = relationship("Order", backref="redeem_tokens")
