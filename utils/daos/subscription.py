import datetime
from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.enums.subscription import SubscriptionStatus
from utils.models.subscription import Subscription
from utils.schemas.subscription import SubscriptionCreateSchemaDB, SubscriptionReadSchemaDB


class SubscriptionDAO:
    @staticmethod
    async def create(session: AsyncSession, sub_data: SubscriptionCreateSchemaDB) -> SubscriptionReadSchemaDB:
        subscription = Subscription(
            order_id=sub_data.order_id
        )

        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)

        return SubscriptionReadSchemaDB.model_validate(subscription)

    @staticmethod
    async def get_subscription_by_order_id(session: AsyncSession, order_id: int) -> SubscriptionReadSchemaDB | None:
        result = await session.execute(
            select(Subscription).where(Subscription.order_id == order_id)
        )
        subscription: Subscription | None = result.scalars().first()
        return SubscriptionReadSchemaDB.model_validate(subscription) if subscription else None

    @staticmethod
    async def update_status(session: AsyncSession, subscription_id: int,
                            new_status: SubscriptionStatus) -> SubscriptionReadSchemaDB | None:
        result = await session.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription: Subscription | None = result.scalars().first()
        if subscription:
            subscription.status = new_status
            await session.commit()
            await session.refresh(subscription)
            return SubscriptionReadSchemaDB.model_validate(subscription)
        return None

    @staticmethod
    async def update_access_period(session: AsyncSession, subscription_id: int, access_from: datetime,
                                   access_to: datetime) -> SubscriptionReadSchemaDB | None:
        result = await session.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription: Subscription | None = result.scalars().first()
        if subscription:
            subscription.access_from = access_from
            subscription.access_to = access_to
            await session.commit()
            await session.refresh(subscription)
            return SubscriptionReadSchemaDB.model_validate(subscription)
        return None

    @staticmethod
    async def get_subscriptions_by_user_id(session: AsyncSession, user_id: int) -> List[SubscriptionReadSchemaDB]:
        result = await session.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscriptions: Sequence[Subscription] = result.scalars().all()
        return [SubscriptionReadSchemaDB.model_validate(sub) for sub in subscriptions]

    @staticmethod
    async def get_active_subscriptions_by_user_id(session: AsyncSession, user_id: int) -> List[
        SubscriptionReadSchemaDB]:
        result = await session.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
        subscriptions: Sequence[Subscription] = result.scalars().all()
        return [SubscriptionReadSchemaDB.model_validate(sub) for sub in subscriptions]

    @staticmethod
    async def update_subscription_user_id_by_subscription_id(session: AsyncSession, subscription_id: int,
                                                             user_id: int) -> SubscriptionReadSchemaDB | None:
        result = await session.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription: Subscription | None = result.scalars().first()
        if subscription:
            subscription.user_id = user_id
            await session.commit()
            await session.refresh(subscription)
            return SubscriptionReadSchemaDB.model_validate(subscription)
        return None
