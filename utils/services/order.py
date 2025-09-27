from typing import List

from utils.daos.order import OrderDAO
from utils.database import AsyncSessionLocal
from utils.schemas.order import (
    OrderCreateSchemaDB, 
    OrderReadSchemaDB
)
from utils.schemas.redeem_token import (
    RedeemTokenCreateSchema
)


async def create_order(order_data: OrderCreateSchemaDB) -> OrderReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.create(session, order_data)


async def get_orders_by_tg_id(tg_id: int) -> List[OrderReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.get_by_tg_id(session, tg_id)


#-------------------------------Кастомные сервисы-------------------------------

#Создание заказа, токена, кода с сайта. 
async def create_invoice_order_token_code(order_data: OrderCreateSchemaDB) -> OrderReadSchemaDB:
    order = await create_order(order_data)
    redeem_token_data = RedeemTokenCreateSchema(
        order_id=order.order_id,
        token_hash=generate_token_hash()  # Предполагается, что эта функция определ
