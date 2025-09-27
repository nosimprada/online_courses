from typing import List, Dict, Any

from utils.daos.lesson import LessonDAO
from utils.database import AsyncSessionLocal
from utils.schemas.lesson import LessonCreateSchemaDB, LessonReadSchemaDB, LessonUpdateSchemaDB


async def create_lesson(lesson_data: LessonCreateSchemaDB) -> LessonReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await LessonDAO.create(session, lesson_data)


async def get_lesson_by_id(lesson_id: int) -> LessonReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await LessonDAO.get_by_id(session, lesson_id)


async def update_lesson(lesson_data: LessonUpdateSchemaDB) -> LessonReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await LessonDAO.update(session, lesson_data)


async def delete_lesson(lesson_id: int) -> None:
    async with AsyncSessionLocal() as session:
        return await LessonDAO.delete(session, lesson_id)


async def get_all_lessons() -> List[LessonReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await LessonDAO.get_all(session)


async def get_all_modules_with_lesson_count() -> List[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        return await LessonDAO.get_modules_with_lesson_count(session)


async def get_lessons_by_module(module_number: int) -> List[LessonReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await LessonDAO.get_lessons_by_module(session, module_number)


async def get_lesson_by_module_and_lesson_number(module: int, lesson) -> LessonReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await LessonDAO.get_by_module_and_lesson_number(session, module, lesson)
