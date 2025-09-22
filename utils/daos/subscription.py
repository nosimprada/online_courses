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
            user_id=sub_data.user_id,
            order_id=sub_data.order_id,
            access_from=sub_data.access_from,
            access_to=sub_data.access_to,
            status=sub_data.status
        )

        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)

        return SubscriptionReadSchemaDB.model_validate(subscription)

    @staticmethod
    async def get_by_tg_id(session: AsyncSession, tg_id: int) -> List[SubscriptionReadSchemaDB]:
        result = await session.execute(
            select(Subscription)
            .where(Subscription.user_id == tg_id)
            .order_by(Subscription.created_at.desc())
        )

        subscriptions: Sequence[Subscription] = result.scalars().all()
        return _subscriptions_list_as_schemas(subscriptions)

    @staticmethod
    async def update_status(session: AsyncSession, tg_id: int, status: SubscriptionStatus
                            ) -> List[SubscriptionReadSchemaDB]:
        result = await session.execute(select(Subscription).where((Subscription.user_id == tg_id)))
        subscriptions: Sequence[Subscription] = result.scalars().all()

        if not subscriptions:
            return []

        updated = []
        for subscription in subscriptions:
            subscription.status = status
            updated.append(subscription)

        await session.commit()

        for subscription in updated:
            await session.refresh(subscription)

        return _subscriptions_list_as_schemas(subscriptions)

    @staticmethod
    async def get_active_subscriptions(session: AsyncSession) -> List[SubscriptionReadSchemaDB]:
        result = await session.execute(
            select(Subscription)
            .where(Subscription.status == SubscriptionStatus.ACTIVE)
            .order_by(Subscription.created_at.desc())
        )

        subscriptions: Sequence[Subscription] = result.scalars().all()
        return _subscriptions_list_as_schemas(subscriptions)


def _subscriptions_list_as_schemas(subscriptions: Sequence[Subscription]) -> List[SubscriptionReadSchemaDB] | None:
    return [SubscriptionReadSchemaDB.model_validate(subscription) for subscription in subscriptions]
