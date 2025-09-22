from typing import List

from utils.daos.subscription import SubscriptionDAO
from utils.database import AsyncSessionLocal
from utils.enums.subscription import SubscriptionStatus
from utils.schemas.subscription import SubscriptionCreateSchemaDB, SubscriptionReadSchemaDB


async def create_subscription(sub_data: SubscriptionCreateSchemaDB) -> SubscriptionReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.create(session, sub_data)


async def get_subscriptions_by_tg_id(tg_id: int) -> List[SubscriptionReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.get_by_tg_id(session, tg_id)


async def get_active_subscriptions() -> List[SubscriptionReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.get_active_subscriptions(session)


async def open_subscriptions_access(tg_id: int) -> List[SubscriptionReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.update_status(session, tg_id, SubscriptionStatus.ACTIVE)


async def close_subscriptions_access(tg_id: int) -> List[SubscriptionReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.update_status(session, tg_id, SubscriptionStatus.CANCELED)
