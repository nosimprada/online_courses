from aiogram import Router
from aiogram.filters import StateFilter, CommandStart
from aiogram.types import Message

import keyboards.start as start_kb

router = Router()


@router.message(CommandStart(), StateFilter(None))
async def menu(message: Message) -> None:
    await message.answer(f"Hi, {message.from_user.first_name}!", reply_markup=start_kb.menu())
