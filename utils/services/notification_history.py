from utils.daos.notification_history import NotificationHistoryDAO
from utils.database import AsyncSessionLocal
from utils.schemas.notification_history import NotificationHistoryCreateSchemaDB, NotificationHistoryReadSchemaDB


async def save_notification_history(data: NotificationHistoryCreateSchemaDB) -> NotificationHistoryReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await NotificationHistoryDAO.create(session, user_id=data.user_id, days_diff=data.days_diff)


async def has_notification_been_sent(user_id: int, days_diff: int) -> bool:
    async with AsyncSessionLocal() as session:
        return await NotificationHistoryDAO.has_been_sent(session, user_id=user_id, days_diff=days_diff)
