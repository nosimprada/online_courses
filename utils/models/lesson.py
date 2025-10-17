from datetime import datetime

from pytz import timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from utils.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    module_no = Column(Integer, nullable=False)
    lesson_no = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    video_file_id = Column(String, nullable=True)
    pdf_file_id = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None),
        nullable=False
    )
