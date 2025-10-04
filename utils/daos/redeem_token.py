from sqlalchemy import select
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

    @staticmethod
    async def get_redeem_token_by_order_id(session: AsyncSession, order_id: int) -> RedeemTokenReadSchema | None:
        result = await session.execute(
            select(RedeemToken).where(RedeemToken.order_id == order_id)
        )
        token: RedeemToken | None = result.scalars().first()
        if token:
            return RedeemTokenReadSchema.model_validate(token)
        return None

    @staticmethod
    async def get_redeem_token_by_token_hash(session: AsyncSession, token_hash: str) -> RedeemTokenReadSchema | None:
        result = await session.execute(
            select(RedeemToken).where(RedeemToken.token_hash == token_hash)
        )
        token: RedeemToken | None = result.scalars().first()
        if token:
            return RedeemTokenReadSchema.model_validate(token)
        return None
