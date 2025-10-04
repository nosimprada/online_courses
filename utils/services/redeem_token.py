from utils.daos.redeem_token import RedeemTokenDAO
from utils.database import AsyncSessionLocal
from utils.schemas.redeem_token import (
    RedeemTokenCreateSchema,
    RedeemTokenReadSchema
)


async def create_redeem_token(token_data: RedeemTokenCreateSchema) -> RedeemTokenReadSchema:
    async with AsyncSessionLocal() as session:
        return await RedeemTokenDAO.create(session, token_data)

async def get_redeem_token_by_order_id(order_id: int) -> RedeemTokenReadSchema | None:
    async with AsyncSessionLocal() as session:
        return await RedeemTokenDAO.get_redeem_token_by_order_id(session, order_id)
    
async def get_redeem_token_by_token_hash(token_hash: str) -> RedeemTokenReadSchema | None:
    async with AsyncSessionLocal() as session:
        return await RedeemTokenDAO.get_redeem_token_by_token_hash(session, token_hash)
    