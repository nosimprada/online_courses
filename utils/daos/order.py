from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.models.order import Order
from utils.schemas.order import OrderCreateSchemaDB, OrderReadSchemaDB


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
    async def get_by_tg_id(session: AsyncSession, tg_id: int) -> List[OrderReadSchemaDB]:
        result = await session.execute(select(Order).where((Order.user_id == tg_id)))
        orders = result.scalars().all()

        if orders:
            return [OrderReadSchemaDB.model_validate(order) for order in orders]

        return None
