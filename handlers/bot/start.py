from aiogram import Router
from aiogram.filters import StateFilter, CommandStart
from aiogram.types import Message

import keyboards.start as start_kb
from config import ADMIN_CHAT_ID
from utils.schemas.user import UserCreateSchemaDB
from utils.services.user import create_user

router = Router()


@router.message(CommandStart(), StateFilter(None))
async def menu(message: Message) -> None:
    is_admin = True if message.from_user.id == ADMIN_CHAT_ID else False

    # TODO: Пользователь добавляется сразу, а не после подтверждения почтой или токеном
    await create_user(UserCreateSchemaDB(
        user_id=message.from_user.id,
        username=message.from_user.username,
        email="admin@test.com"
    ))

    await message.answer(f"Hi, {message.from_user.first_name}!", reply_markup=start_kb.menu(is_admin))
