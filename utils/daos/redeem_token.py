from sqlalchemy.ext.asyncio import AsyncSession

from utils.models.redeem_token import RedeemToken
from utils.schemas.redeem_token import (
    RedeemTokenCreateSchema,
    RedeemTokenReadSchema
)


class RedeemTokenDAO:
    @staticmethod
    async def create(session: AsyncSession, token_data: RedeemTokenCreateSchema) -> RedeemTokenReadSchema:
        token = RedeemToken(
            order_id=token_data.order_id,
            token_hash=token_data.token_hash
        )

        session.add(token)
        await session.commit()
        await session.refresh(token)

        return RedeemTokenReadSchema.model_validate(token)
