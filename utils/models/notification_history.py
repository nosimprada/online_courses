from datetime import datetime

from pytz import timezone
from sqlalchemy import Column, Integer, BigInteger, DateTime

from utils.database import Base


class NotificationHistory(Base):
    __tablename__ = "notification_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    days_diff = Column(Integer, nullable=False)
    sent_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None),
        nullable=False
    )
