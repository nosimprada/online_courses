from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# class RedeemToken(Base):
#     __tablename__ = "redeem_tokens"

#     id = Column(Integer, primary_key=True, index=True)
#     order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
#     token_hash = Column(String, unique=True, nullable=False, index=True)
#     created_at = Column(
#         DateTime,
#         default=lambda: datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None),
#         nullable=False
#     )
#     used_at = Column(DateTime, nullable=True)

#     order = relationship("Order", backref="redeem_tokens")


class RedeemTokenCreateSchema(BaseModel):
    order_id: int
    token_hash: str


class RedeemTokenReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    token_hash: str
    created_at: datetime
    used_at: Optional[datetime] = None
