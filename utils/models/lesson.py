from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import (
    datetime,
    )
import pytz
from utils.database import Base
import datetime


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
        default=lambda: datetime.datetime.now(pytz.timezone("Europe/Kiev")),
        nullable=False
        )

