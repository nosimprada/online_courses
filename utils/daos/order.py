from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.enums.order import OrderStatus
from utils.models.order import Order
from utils.schemas.order import OrderReadSchemaDB, OrderCreateSchemaDB


class OrderDAO:
    @staticmethod
    async def create(session: AsyncSession, order_data: OrderCreateSchemaDB) -> OrderReadSchemaDB:
        order = Order(
            user_id=order_data.user_id,
            amount=order_data.amount,
            status=order_data.status
        )

        session.add(order)
        await session.commit()
        await session.refresh(order)

        return OrderReadSchemaDB.model_validate(order)

    @staticmethod
    async def get_by_tg_id(session: AsyncSession, tg_id: int) -> OrderReadSchemaDB | None:
        result = await session.execute(select(Order).where(Order.user_id == tg_id))
        order = result.scalars().first()

        if order:
            return OrderReadSchemaDB.model_validate(order)

        return None

    @staticmethod
    async def close_access(session: AsyncSession, tg_id: int) -> OrderReadSchemaDB | None:
        result = await session.execute(select(Order).where(Order.user_id == tg_id))
        order = result.scalars().first()

        if order:
            order = OrderReadSchemaDB.model_validate(order)

            order.status = OrderStatus.CANCELED
            await session.commit()
            await session.refresh(order)

            return OrderReadSchemaDB.model_validate(order)

        return None
