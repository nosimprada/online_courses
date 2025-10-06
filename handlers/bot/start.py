from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import ADMIN_CHAT_ID
from outboxes.admin import menu as admin_menu
from outboxes.start import registration_func, start_menu
from utils.services.user import get_user_by_tg_id

router = Router()


@router.message(CommandStart())
async def start_command_handler(message: Message):
    if message.from_user.id == ADMIN_CHAT_ID:
        await admin_menu(message)
        return

    command_args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    print(f"COMMAND ARGS====================================: {command_args}")

    user_data = await get_user_by_tg_id(message.from_user.id)

    if not user_data:
        if command_args:
            ref_code = command_args[0]
            print(f"РЕФЕРАЛЬНЫЙ КОД: {ref_code}")

            await registration_func(message, ref_code)
            print('Сработала регистрация')

        else:
            await message.answer("Welcome! Use the menu below to navigate.")

    else:
        await start_menu(message)


@router.message(F.text == "🔁 На головну")
async def handle_back_to_start(message: Message) -> None:
    await start_menu(message)
