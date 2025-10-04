from typing import List

from utils.daos.leaning_progress import LearningProgressDAO
from utils.database import AsyncSessionLocal
from utils.schemas.leaning_progress import LearningProgressCreateSchemaDB, LearningProgressReadSchemaDB


async def create_learning_progress(lp_data: LearningProgressCreateSchemaDB) -> LearningProgressReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await LearningProgressDAO.create(session, lp_data)


async def get_learning_progress_by_user_id(user_id: int) -> List[LearningProgressReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await LearningProgressDAO.get_by_user_id(session, user_id)


async def get_lesson_progress_by_user_id_and_lesson_id(user_id: int,
                                                       lesson_id: int) -> LearningProgressReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await LearningProgressDAO.get_lesson_progress_by_user_id_and_lesson_id(session, user_id, lesson_id)
