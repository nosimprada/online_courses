from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.models.lesson import Lesson
from utils.schemas.lesson import LessonCreateSchemaDB, LessonReadSchemaDB


class LessonDAO:
    @staticmethod
    async def create(session: AsyncSession, lesson_data: LessonCreateSchemaDB) -> LessonReadSchemaDB:
        lesson = Lesson(
            module_no=lesson_data.module_number,
            lesson_no=lesson_data.lesson_number,
            title=lesson_data.title,
            video_file_id=lesson_data.video_file_id,
            pdf_file_id=lesson_data.pdf_file_id,
        )

        session.add(lesson)
        await session.commit()
        await session.refresh(lesson)

        return LessonReadSchemaDB.model_validate(lesson)

    @staticmethod
    async def get_by_id(session: AsyncSession, lesson_id: int) -> LessonReadSchemaDB | None:
        result = await session.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = result.scalars().first()

        if lesson:
            return LessonReadSchemaDB.model_validate(lesson)
        
        return None
