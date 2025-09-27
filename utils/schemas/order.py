from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from utils.enums.order import OrderStatus

# class Order(Base):
#     __tablename__ = "orders"

#     id = Column(Integer, primary_key=True, index=True)
#     order_id = Column(Integer, unique=True, nullable=False, index=True)
#     invoice_id = Column(String, unique=True, nullable=False, index=True)
#     user_id = Column(BigInteger, nullable=True, index=True)
#     email = Column(String, unique=True, nullable=True, index=True)
#     amount = Column(Float, nullable=False)
#     status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
#     created_at = Column(
#         DateTime,
#         default=lambda: datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None),
#         nullable=False
#     )
#     paid_at = Column(DateTime, nullable=True)

class OrderCreateSchemaDB(BaseModel):
    user_id: Optional[int] = None
    amount: float
    email: Optional[str] = None
    invoice_id: Optional[str] = None
    order_id: Optional[int] = None
    status: OrderStatus = OrderStatus.PENDING


class OrderReadSchemaDB(BaseModel):
    id: int
    order_id: int
    invoice_id: str
    user_id: Optional[int] = None
    email: Optional[str] = None
    amount: float
    status: OrderStatus
    created_at: datetime
    paid_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)