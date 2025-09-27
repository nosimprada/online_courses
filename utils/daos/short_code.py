from typing import List

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