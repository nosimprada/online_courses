from sqlalchemy import (
    Column,
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

class ShortCode(Base):
    __tablename__ = "short_codes"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    code_hash = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(pytz.timezone("Europe/Kiev")),
        nullable=False
        )
    used_at = Column(DateTime, nullable=True)

    order = relationship("Order", backref="short_codes")