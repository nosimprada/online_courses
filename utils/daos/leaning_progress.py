from typing import List, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from utils.models.learning_progress import LearningProgress
from utils.schemas.leaning_progress import LearningProgressCreateSchemaDB, LearningProgressReadSchemaDB


class LearningProgressDAO:
    @staticmethod
    async def create(session: AsyncSession, lp_data: LearningProgressCreateSchemaDB) -> LearningProgressReadSchemaDB:
        learning_progress = LearningProgress(
            user_id=lp_data.user_id,
            lesson_id=lp_data.lesson_id
        )

        session.add(learning_progress)
        await session.commit()
        await session.refresh(learning_progress)

        return LearningProgressReadSchemaDB.model_validate(learning_progress)
    
    @staticmethod
    async def get_by_user_id(session: AsyncSession, user_id: int) -> List[LearningProgressReadSchemaDB]:
        result = await session.execute(select(LearningProgress).where(LearningProgress.user_id == user_id))
        learning_progress_list = result.scalars().all()

        if learning_progress_list:
            return [LearningProgressReadSchemaDB.model_validate(lp) for lp in learning_progress_list]

        return []
    
    @staticmethod
    async def get_lesson_progress_by_user_id_and_lesson_id(session: AsyncSession, user_id: int, lesson_id: int) -> LearningProgressReadSchemaDB | None:
        result = await session.execute(
            select(LearningProgress).where(
                (LearningProgress.user_id == user_id) & 
                (LearningProgress.lesson_id == lesson_id)
            )
        )
        learning_progress: LearningProgress | None = result.scalars().first()
        return LearningProgressReadSchemaDB.model_validate(learning_progress) if learning_progress else None