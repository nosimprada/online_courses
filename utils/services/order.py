from utils.daos.order import OrderDAO
from utils.database import AsyncSessionLocal
from utils.schemas.order import OrderReadSchemaDB, OrderCreateSchemaDB


async def create_order(order_data: OrderCreateSchemaDB) -> OrderReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.create(session, order_data)


async def get_order_by_tg_id(tg_id: int) -> OrderReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.get_by_tg_id(session, tg_id)


async def close_order_access(tg_id: int) -> OrderReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.close_access(session, tg_id)
