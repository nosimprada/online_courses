from aiogram import Router, F
from aiogram.types import CallbackQuery

import keyboards.admin as admin_kb
from utils.services.user import get_all_users

router = Router()


@router.callback_query(F.data == "admin:menu")
async def menu(callback: CallbackQuery) -> None:
    await callback.message.answer("Виберіть дію:", reply_markup=admin_kb.menu())
    await callback.answer()


@router.callback_query(F.data == "admin:show_users")
async def show_users(callback: CallbackQuery) -> None:
    users = await get_all_users()

    await callback.message.answer(
        f"Кількість користувачів: <code>{len(users)}</code>",
        reply_markup=admin_kb.show_users(users)
    )

    await callback.answer()
