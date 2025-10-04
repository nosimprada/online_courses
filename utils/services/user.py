from typing import List

from utils.daos.user import UserDAO
from utils.database import AsyncSessionLocal
from utils.enums.order import OrderStatus
from utils.enums.subscription import SubscriptionStatus
from utils.schemas.user import (
    UserCreateSchemaDB,
    UserReadFullInfoSchemaDB,
    UserReadSchemaDB,
)
from utils.services.leaning_progress import get_learning_progress_by_user_id
from utils.services.lesson import get_all_lessons
from utils.services.order import get_orders_by_tg_id
from utils.services.subscription import get_subscription_by_order_id, get_subscriptions_by_user_id


async def create_user(user_data: UserCreateSchemaDB) -> UserReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await UserDAO.create(session, user_data)


async def get_user_by_tg_id(tg_id: int) -> UserReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await UserDAO.get_by_tg_id(session, tg_id)


# async def get_user_by_email(email: str) -> UserReadSchemaDB | None:
#     async with AsyncSessionLocal() as session:
#         return await UserDAO.get_user_by_email(session, email)


async def get_all_users() -> List[UserReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await UserDAO.get_all_users(session)

# async def set_user_email(tg_id: int, email: str) -> UserReadSchemaDB | None:
#     async with AsyncSessionLocal() as session:
#         return await UserDAO.set_user_email(session, tg_id, email)

# class UserReadFullInfoSchemaDB(UserReadSchemaDB):
#     is_subscribed: bool = False
#     created_at: datetime | None = None
#     subscription_access_to: datetime | None = None
#     user_id: int | None = None
#     emails: list[str] = []
#     completed_order_ids: list[int] = []
#     expired_subscription_ids: list[int] = []
#     leaning_progress_procent: float = 0.0


async def get_user_full_info_by_tg_id(tg_id: int) -> UserReadFullInfoSchemaDB | None:
    user_data = await get_user_by_tg_id(tg_id)
    if user_data is None:
        return None
    orders = await get_orders_by_tg_id(tg_id)
    completed_order_ids = [order.order_id for order in orders if order.status == OrderStatus.COMPLETED]
    subscriptions = await get_subscriptions_by_user_id(user_data.user_id)
    active_subscriptions = [sub for sub in subscriptions if sub.status == SubscriptionStatus.ACTIVE]
    is_subscribed = len(active_subscriptions) > 0
    expired_subscription_ids = [sub.id for sub in subscriptions if sub.status == SubscriptionStatus.EXPIRED]
    subscription_access_to = max((sub.access_to for sub in active_subscriptions), default=None)
    all_lessons = await get_all_lessons()
    learning_progress = await get_learning_progress_by_user_id(user_data.user_id)
    completed_lesson_ids = {lp.lesson_id for lp in learning_progress}
    leaning_progress_procent = (len(completed_lesson_ids) / len(all_lessons) * 100) if all_lessons else 0.0
    emails = []
    for order in orders:
        if order.email and order.email not in emails:
            emails.append(order.email)

    return UserReadFullInfoSchemaDB(
        user_id=user_data.user_id,
        emails=emails,
        is_subscribed=is_subscribed,
        created_at=user_data.created_at,
        subscription_access_to=subscription_access_to,
        completed_order_ids=completed_order_ids,
        expired_subscription_ids=expired_subscription_ids,
        leaning_progress_procent=leaning_progress_procent,
    )
