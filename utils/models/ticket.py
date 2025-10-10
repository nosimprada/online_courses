from datetime import datetime

from pytz import timezone
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

from utils.database import Base
from utils.enums.ticket import TicketStatus


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), index=True)
    topic = Column(String, nullable=False)
    text = Column(String, nullable=False)
    attachments = Column(String, nullable=True)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.PENDING)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None),
        nullable=False
    )
    resolved_at = Column(DateTime, nullable=True)
    user = relationship("User", backref="tickets")
