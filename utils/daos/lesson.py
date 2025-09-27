from typing import List, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from utils.models.lesson import Lesson
from utils.schemas.lesson import LessonCreateSchemaDB, LessonReadSchemaDB, LessonUpdateSchemaDB


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

    @staticmethod
    async def get_by_module_and_lesson_number(session: AsyncSession, module: int, lesson) -> LessonReadSchemaDB | None:
        result = await session.execute(
            select(Lesson).where(Lesson.module_no == module, Lesson.lesson_no == lesson)
        )

        lesson = result.scalars().first()

        if lesson:
            return LessonReadSchemaDB.model_validate(lesson)

        return None

    @staticmethod
    async def update(session: AsyncSession, lesson_data: LessonUpdateSchemaDB) -> LessonReadSchemaDB | None:
        result = await session.execute(select(Lesson).where(
            Lesson.module_no == lesson_data.module_number,
            Lesson.lesson_no == lesson_data.lesson_number
        ))
        lesson = result.scalars().first()

        if lesson:
            if lesson_data.title is not None:
                lesson.title = lesson_data.title
            if lesson_data.video_file_id is not None:
                lesson.video_file_id = lesson_data.video_file_id
            if lesson_data.pdf_file_id is not None:
                lesson.pdf_file_id = lesson_data.pdf_file_id

            await session.commit()
            await session.refresh(lesson)

            return LessonReadSchemaDB.model_validate(lesson)

        return None

    @staticmethod
    async def delete(session: AsyncSession, lesson_id: int) -> None:
        result = await session.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = result.scalars().first()

        if lesson:
            await session.delete(lesson)
            await session.commit()

        return None

    @staticmethod
    async def get_all(session: AsyncSession) -> List[LessonReadSchemaDB]:
        result = await session.execute(select(Lesson))
        lessons = result.scalars().all()

        return [LessonReadSchemaDB.model_validate(lesson) for lesson in lessons]

    """
        Modules
    """

    @staticmethod
    async def get_modules_with_lesson_count(session: AsyncSession) -> List[Dict[str, Any]]:
        result = await session.execute(
            select(Lesson.module_no, func.count(Lesson.id).label("lesson_count"))
            .group_by(Lesson.module_no).order_by(Lesson.module_no)
        )

        modules_data = result.all()

        return [
            {
                "module_number": row.module_no,
                "lesson_count": row.lesson_count
            }
            for row in modules_data
        ]

    @staticmethod
    async def get_lessons_by_module(session: AsyncSession, module_number: int) -> List[LessonReadSchemaDB]:
        result = await session.execute(
            select(Lesson).where(Lesson.module_no == module_number).order_by(Lesson.lesson_no)
        )

        lessons = result.scalars().all()
        return [LessonReadSchemaDB.model_validate(lesson) for lesson in lessons]
