from datetime import datetime

from pytz import timezone
from sqlalchemy import (
    BigInteger,
    Column,
    Enum,
    Float,
    Integer,
    DateTime,
    String
)

from utils.database import Base
from utils.enums.order import OrderStatus


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True, nullable=True, index=True)
    invoice_id = Column(String, unique=True, nullable=True, index=True)
    user_id = Column(BigInteger, nullable=True, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None),
        nullable=False
    )
    paid_at = Column(DateTime, nullable=True)
