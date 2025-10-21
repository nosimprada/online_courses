from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from config import ADMIN_CHAT_ID
from keyboards.renewal import renewal_menu_keyboard
from outboxes.admin import menu as admin_menu
from outboxes.start import register_ref_code_handler, registration_func, start_menu, subscription_renewal
from utils.services.user import get_user_by_tg_id
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.states import RefCode, RenewalRefCode

router = Router()

@router.message(F.text == "Продовити доступ 🔄")
async def renew_subscription(message: Message, state: FSMContext):
    text = """
Перейдіть на сторінку оплати, щоб продовжити доступ до курсу.
Якщо у вас є оплачена підписка, введіть код підтвердження, який ви отримали після оплати.
"""
    await message.answer(text, reply_markup=await renewal_menu_keyboard())

@router.callback_query(F.data == "renewal:enter_code")
async def enter_renewal_code(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RenewalRefCode.get_ref_code)
    await callback.message.answer("Введіть код підтвердження, який ви отримали після оплати.")
    await callback.answer()

@router.message(StateFilter(RenewalRefCode.get_ref_code))
async def process_renewal_ref_code(message: Message, state: FSMContext):
    ref_code = message.text.strip()
    print(f"РЕФЕРАЛЬНЫЙ КОД ДЛЯ ПРОДЛЕНИЯ: {ref_code}")

    await subscription_renewal(message, short_code=ref_code)
    await state.clear()