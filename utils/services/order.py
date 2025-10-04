from typing import List

from utils.daos.order import OrderDAO
from utils.database import AsyncSessionLocal
from utils.enums.order import OrderStatus
from utils.random_generate import (
    generate_short_code,
    generate_token_hash
)
from utils.schemas.order import (
    OrderCreateSchemaDB,
    OrderReadSchemaDB
)
from utils.schemas.redeem_token import (
    RedeemTokenCreateSchema
)
from utils.schemas.short_code import ShortCodeCreateSchema
from utils.services.redeem_token import create_redeem_token
from utils.services.short_code import create_short_code


async def create_order(order_data: OrderCreateSchemaDB) -> OrderReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.create(session, order_data)


async def get_orders_by_tg_id(tg_id: int) -> List[OrderReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.get_by_tg_id(session, tg_id)


async def get_order_by_order_id(order_id: int) -> OrderReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.get_by_order_id(session, order_id)


async def update_order_status(order_id: int, status: OrderStatus) -> OrderReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.update_status(session, order_id, status)


async def update_user_id_by_order_id(order_id: int, user_id: int) -> OrderReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await OrderDAO.update_user_id_by_order_id(session, order_id, user_id)


# -------------------------------Кастомные сервисы-------------------------------

# Создание заказа, токена, кода с сайта.
async def create_invoice_order_token_code(order_data: OrderCreateSchemaDB) -> OrderReadSchemaDB:
    order = await create_order(order_data)
    token_hash = generate_token_hash()
    redeem_token_data = RedeemTokenCreateSchema(
        order_id=order.order_id,
        token_hash=token_hash
    )

    redeem_token = await create_redeem_token(redeem_token_data)
    print(redeem_token)

    code_hash = generate_short_code()
    short_code_data = ShortCodeCreateSchema(
        order_id=order.order_id,
        code_hash=code_hash
    )

    short_code = await create_short_code(short_code_data)
    print(short_code)
    return order
