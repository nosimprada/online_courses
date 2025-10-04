from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LearningProgressCreateSchemaDB(BaseModel):
    user_id: int
    lesson_id: int


class LearningProgressReadSchemaDB(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    progress: int
    created_at: datetime