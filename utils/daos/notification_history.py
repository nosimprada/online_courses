from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.models.notification_history import NotificationHistory
from utils.schemas.notification_history import NotificationHistoryReadSchemaDB


class NotificationHistoryDAO:
    @staticmethod
    async def create(session: AsyncSession, user_id: int, days_diff: int) -> NotificationHistoryReadSchemaDB:
        notification = NotificationHistory(
            user_id=user_id,
            days_diff=days_diff
        )

        session.add(notification)

        await session.commit()
        await session.refresh(notification)

        return NotificationHistoryReadSchemaDB.model_validate(notification)

    @staticmethod
    async def has_been_sent(session: AsyncSession, user_id: int, days_diff: int) -> bool:
        result = await session.execute(
            select(NotificationHistory).where(
                NotificationHistory.user_id == user_id,
                NotificationHistory.days_diff == days_diff
            )
        )

        return result.scalar_one_or_none() is not None
