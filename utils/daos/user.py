from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils.models.user import User
from utils.schemas.user import UserCreateSchema, UserReadSchema

class UserDAO:
    @staticmethod
    async def create(session: AsyncSession, user_data: UserCreateSchema) -> UserReadSchema:
        user = User(
            tg_id=user_data.tg_id,
            username=user_data.username,
            email=user_data.email,
            current_subscription_until=user_data.current_subscription_until
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return UserReadSchema.model_validate(user)
