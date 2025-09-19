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
from datetime import (
    datetime
    )
import pytz
from utils.database import Base
import datetime

from utils.enums.ticket import TicketStatus

# id, user_id, topic, text, attachments[], status, created_at, resolved_at
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), index=True)
    topic = Column(String, nullable=False)
    text = Column(String, nullable=False)
    attachments = Column(String, nullable=True)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN)

    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(pytz.timezone("Europe/Kiev")),
        nullable=False
        )
    resolved_at = Column(DateTime, nullable=True)
    user = relationship("User", backref="tickets")