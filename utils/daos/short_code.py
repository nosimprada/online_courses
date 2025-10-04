from sqlalchemy import select 
from sqlalchemy.ext.asyncio import AsyncSession

from utils.models.short_code import ShortCode
from utils.schemas.short_code import (
    ShortCodeCreateSchema,
    ShortCodeReadSchema
)


class ShortCodeDAO:
    @staticmethod
    async def create(session: AsyncSession, code_data: ShortCodeCreateSchema) -> ShortCodeReadSchema:
        code = ShortCode(
            order_id=code_data.order_id,
            code_hash=code_data.code_hash
        )

        session.add(code)
        await session.commit()
        await session.refresh(code)

        return ShortCodeReadSchema.model_validate(code)

    @staticmethod
    async def get_short_code_by_order_id(session: AsyncSession, order_id: int) -> ShortCodeReadSchema | None:
        result = await session.execute(
            select(ShortCode).where(ShortCode.order_id == order_id)
        )
        code: ShortCode | None = result.scalars().first()
        if code:
            return ShortCodeReadSchema.model_validate(code)
        return None