from utils.daos.redeem_token import RedeemTokenDAO
from utils.database import AsyncSessionLocal
from utils.schemas.redeem_token import (
    RedeemTokenCreateSchema,
    RedeemTokenReadSchema
)


async def create_redeem_token(token_data: RedeemTokenCreateSchema) -> RedeemTokenReadSchema:
    async with AsyncSessionLocal() as session:
        return await RedeemTokenDAO.create(session, token_data)
