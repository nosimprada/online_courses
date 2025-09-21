from datetime import datetime

from pydantic import BaseModel


class LessonCreateSchemaDB(BaseModel):
    module_number: int
    lesson_number: int
    title: str
    video_file_id: str | None = None
    pdf_file_id: str | None = None


class LessonReadSchemaDB(BaseModel):
    module_number: int
    lesson_number: int
    title: str
    video_file_id: str | None = None
    pdf_file_id: str | None = None
    created_at: datetime
