from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LessonCreateSchemaDB(BaseModel):
    module_number: int
    lesson_number: int
    title: str
    video_file_id: str | None = None
    pdf_file_id: str | None = None


class LessonReadSchemaDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    module_number: int = Field(alias="module_no")
    lesson_number: int = Field(alias="lesson_no")
    title: str
    video_file_id: str | None = None
    pdf_file_id: str | None = None
    created_at: datetime


class LessonUpdateSchemaDB(BaseModel):
    module_number: int = Field(alias="module_no")
    lesson_number: int = Field(alias="lesson_no")
    title: str | None = None
    video_file_id: str | None = None
    pdf_file_id: str | None = None
