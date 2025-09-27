from utils.daos.short_code import ShortCodeDAO
from utils.database import AsyncSessionLocal
from utils.schemas.short_code import (
    ShortCodeCreateSchema,
    ShortCodeReadSchema
)


async def create_short_code(token_data: ShortCodeCreateSchema) -> ShortCodeReadSchema:
    async with AsyncSessionLocal() as session:
        return await ShortCodeDAO.create(session, token_data)
