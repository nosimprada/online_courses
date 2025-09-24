from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.models.user import User
from utils.schemas.user import UserCreateSchemaDB, UserReadSchemaDB


class UserDAO:
    @staticmethod
    async def create(session: AsyncSession, user_data: UserCreateSchemaDB) -> UserReadSchemaDB:
        existing_user = await UserDAO.get_by_tg_id(session, user_data.user_id)
        if existing_user:
            return existing_user

        if user_data.email:
            existing_email_user = await UserDAO.get_user_by_email(session, user_data.email)
            if existing_email_user:
                return existing_email_user

        user = User(
            tg_id=user_data.user_id,
            username=user_data.username,
            email=user_data.email
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return UserReadSchemaDB.model_validate(user)

    @staticmethod
    async def get_by_tg_id(session: AsyncSession, tg_id: int) -> UserReadSchemaDB | None:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()
        if user:
            return UserReadSchemaDB.model_validate(user)
        return None

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> UserReadSchemaDB | None:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user:
            return UserReadSchemaDB.model_validate(user)
        return None

    @staticmethod
    async def get_all_users(session: AsyncSession) -> List[UserReadSchemaDB]:
        result = await session.execute(select(User))

        users: Sequence[User] = result.scalars().all()
        return [UserReadSchemaDB.model_validate(user) for user in users]
