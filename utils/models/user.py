from sqlalchemy import (
    BigInteger, 
    Column, 
    Integer, 
    String, 
    DateTime
)
from datetime import (
    datetime
    )
import pytz
from utils.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(pytz.timezone("Europe/Kiev")),
        nullable=False
        )