from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from outboxes.start import registration_func, start_menu
from utils.services.user import get_user_by_tg_id

router = Router()


@router.message(CommandStart())
async def start_command_handler(message: Message):
    command_args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    print(f"COMMAND ARGS====================================: {command_args}")
    user_data = await get_user_by_tg_id(message.from_user.id)
    if user_data is None:
        if command_args:
            ref_code = command_args[0]
            print(f"РЕФЕРАЛЬНЫЙ КОД: {ref_code}")
            print('Сработала регистрация')
            await registration_func(message, ref_code)

        else:
            await message.answer("Welcome! Use the menu below to navigate.")
    else:
        await start_menu(message)
