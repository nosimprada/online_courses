from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import ADMIN_CHAT_ID
from outboxes.admin import menu as admin_menu
from outboxes.start import register_ref_code_handler, registration_func, start_menu, subscription_renewal
from utils.services.user import get_user_by_tg_id
from utils.states import RefCode

router = Router()



@router.message(CommandStart())
async def start_command_handler(message: Message, state: FSMContext):
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

            await registration_func(message, ref_code, state)
            print('Сработала регистрация')

        else:
            await message.answer(
                "Активних підписок немає. Введіть будь ласка код, який був надісланий вам на електронну пошту.")
            print(f'Сработал запрос кода подтверждения, + устарновилось состояние FSM')
            await state.set_state(RefCode.get_ref_code)

    else:
        if command_args:
            ref_code = command_args[0]
            print(f"РЕФЕРАЛЬНЫЙ КОД: {ref_code}")
            await subscription_renewal(message, ref_code)
        await start_menu(message)

@router.message(StateFilter(RefCode.get_ref_code))
async def process_ref_code(message: Message, state: FSMContext):
    ref_code = message.text.strip()
    print(f"РЕФЕРАЛЬНЫЙ КОД: {ref_code}")

    await register_ref_code_handler(ref_code, message)
    await state.clear()


@router.message(F.text == "🔁 На головну")
async def handle_back_to_menu_message(message: Message) -> None:
    await start_menu(message)


@router.callback_query(F.data == "back_to_menu")
async def handle_back_to_menu_callback(callback: CallbackQuery) -> None:
    await start_menu(callback)
