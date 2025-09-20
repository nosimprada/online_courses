from utils.daos.user import UserDAO
from utils.database import AsyncSessionLocal
from utils.schemas.user import (
    UserCreateSchemaDB,
    UserReadSchemaDB,
)


async def create_user(user_data: UserCreateSchemaDB) -> UserReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await UserDAO.create(session, user_data)


async def get_user_by_tg_id(tg_id: int) -> UserReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await UserDAO.get_by_tg_id(session, tg_id)


async def get_user_by_email(email: str) -> UserReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await UserDAO.get_user_by_email(session, email)


async def get_all_users() -> UserReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await UserDAO.get_all_users(session)
