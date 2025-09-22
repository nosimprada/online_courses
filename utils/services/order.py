from typing import List

from utils.daos.order import OrderDAO
from utils.database import AsyncSessionLocal
from utils.schemas.order import OrderCreateSchemaDB, OrderReadSchemaDB


async def create_order(order_data: OrderCreateSchemaDB) -> OrderReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.create(session, order_data)


async def get_orders_by_tg_id(tg_id: int) -> List[OrderReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.get_by_tg_id(session, tg_id)
