from aiogram import Router, F
from aiogram.filters import StateFilter, CommandStart
from aiogram.types import Message, CallbackQuery

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


@router.callback_query(F.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery) -> None:
    is_admin = True if callback.from_user.id == ADMIN_CHAT_ID else False
    await callback.message.edit_text(f"Hi, {callback.from_user.first_name}!", reply_markup=start_kb.menu(is_admin))
