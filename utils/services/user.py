from datetime import datetime
from typing import List, Optional

from utils.daos.user import UserDAO
from utils.database import AsyncSessionLocal
from utils.enums.order import OrderStatus
from utils.enums.subscription import SubscriptionStatus
from utils.schemas.user import (
    UserCreateSchemaDB,
    UserReadFullInfoSchemaDB,
    UserReadSchemaDB,
)
from utils.services.order import get_orders_by_tg_id
from utils.services.subscription import get_subscriptions_by_user_id


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
    if not user_data:
        return None

    orders = await get_orders_by_tg_id(tg_id) or []

    completed_order_ids: List[int] = [
        int(o.order_id)
        for o in orders
        if o.status == OrderStatus.COMPLETED and o.order_id is not None
    ]

    internal_user_id = getattr(user_data, "id", None)
    subs_user_id = internal_user_id if internal_user_id is not None else user_data.user_id

    subscriptions = await get_subscriptions_by_user_id(subs_user_id) or []

    active_subscriptions = [s for s in subscriptions if s.status == SubscriptionStatus.ACTIVE]
    expired_subscription_ids = [s.id for s in subscriptions if s.status == SubscriptionStatus.EXPIRED]

    subscription_access_to: Optional[datetime] = max(
        (s.access_to for s in active_subscriptions if s.access_to is not None),
        default=None,
    )

    is_subscribed = len(active_subscriptions) > 0

    emails: List[str] = []
    for o in orders:
        if o.email and o.email not in emails:
            emails.append(o.email)

    return UserReadFullInfoSchemaDB(
        tg_id=tg_id,
        user_id=user_data.user_id,
        username=getattr(user_data, "username", None),
        created_at=getattr(user_data, "created_at", None),
        is_subscribed=is_subscribed,
        subscription_access_to=subscription_access_to,
        emails=emails,
        completed_order_ids=completed_order_ids,
        expired_subscription_ids=expired_subscription_ids,
        leaning_progress_procent=getattr(user_data, "leaning_progress_procent", 0.0),
    )
