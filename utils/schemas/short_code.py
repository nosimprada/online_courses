from typing import Optional

from pydantic import BaseModel

from datetime import datetime

# class ShortCode(Base):
#     __tablename__ = "short_codes"

#     id = Column(Integer, primary_key=True, index=True)
#     order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
#     code_hash = Column(String, unique=True, nullable=False, index=True)
#     created_at = Column(
#         DateTime,
#         default=lambda: datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None),
#         nullable=False
#     )
#     used_at = Column(DateTime, nullable=True)

#     order = relationship("Order", backref="short_codes")

class ShortCodeCreateSchema(BaseModel):
    order_id: int
    code_hash: str

class ShortCodeReadSchema(BaseModel):
    id: int
    order_id: int
    code_hash: str
    created_at: datetime
    used_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True