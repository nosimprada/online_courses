from datetime import datetime

from pytz import timezone
from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    Integer,
    DateTime,
)
from sqlalchemy.orm import relationship

from utils.database import Base


class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    progress = Column(Integer, nullable=False, default=0)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None),
        nullable=False
    )

    lesson = relationship("Lesson", back_populates="learning_progress")
