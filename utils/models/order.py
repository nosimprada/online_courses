from sqlalchemy import (
    BigInteger, 
    Column, 
    Float, 
    Integer, 
    String, 
    DateTime
)
from datetime import (
    datetime, 
    timezone
    )
import pytz
from utils.database import Base
import datetime

from utils.enums.order import OrderStatus

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=True, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False, default=OrderStatus.PENDING)
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(pytz.timezone("Europe/Kiev")),
        nullable=False
        )
    paid_at = Column(DateTime, nullable=True)