from pydantic import BaseModel
from sqlalchemy import DateTime


    # user_id = Column(BigInteger, nullable=True, index=True)
    # amount = Column(Float, nullable=False)
    # status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
class OrderCreateSchemaDB(BaseModel):
    amount: float
    status: str | None = None

class OrderReadSchemaDB(OrderCreateSchemaDB):
    id: int