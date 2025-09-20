from aiogram import Router
from aiogram.filters import StateFilter, CommandStart
from aiogram.types import Message

import keyboards.start as start_kb
from config import ADMIN_CHAT_ID

router = Router()


@router.message(CommandStart(), StateFilter(None))
async def menu(message: Message) -> None:
    is_admin = True if message.from_user.id == ADMIN_CHAT_ID else False

    await message.answer(f"Hi, {message.from_user.first_name}!", reply_markup=start_kb.menu(is_admin))
