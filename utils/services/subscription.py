import datetime
from typing import List

from utils.daos.subscription import SubscriptionDAO
from utils.database import AsyncSessionLocal
from utils.enums.subscription import SubscriptionStatus
from utils.schemas.subscription import SubscriptionCreateSchemaDB, SubscriptionReadSchemaDB


async def create_subscription(sub_data: SubscriptionCreateSchemaDB) -> SubscriptionReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.create(session, sub_data)


async def get_subscription_by_order_id(order_id: int) -> SubscriptionReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.get_subscription_by_order_id(session, order_id)


async def update_subscription_status(subscription_id: int,
                                     new_status: SubscriptionStatus) -> SubscriptionReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.update_status(session, subscription_id, new_status)


async def update_subscription_access_period(subscription_id: int, access_from: datetime.datetime,
                                            access_to: datetime.datetime) -> SubscriptionReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.update_access_period(session, subscription_id, access_from, access_to)


async def get_subscriptions_by_user_id(user_id: int) -> List[SubscriptionReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.get_subscriptions_by_user_id(session, user_id)


async def get_active_subscriptions_by_user_id(user_id: int) -> List[SubscriptionReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.get_active_subscriptions_by_user_id(session, user_id)


async def update_subscription_user_id_by_subscription_id(subscription_id: int,
                                                         user_id: int) -> SubscriptionReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await SubscriptionDAO.update_subscription_user_id_by_subscription_id(session, subscription_id, user_id)
