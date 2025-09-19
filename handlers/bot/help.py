from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import keyboards.help as help_kb

router = Router()


class HelpStates(StatesGroup):
    choosing_topic = State()
    writing_message = State()


@router.callback_query(F.data == "help:start")
async def start_help_request(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("Виберіть тему для звернення", reply_markup=help_kb.choose_support_topic())
    await state.set_state(HelpStates.choosing_topic)
    await callback.answer()


@router.callback_query(F.data.startswith("help:support_topic_"), StateFilter(HelpStates.choosing_topic))
async def choose_support_topic(callback: CallbackQuery, state: FSMContext) -> None:
    topic_id = callback.data.split("_")[-1]
    await state.update_data(selected_topic=topic_id)

    await callback.message.answer(f"Обрано тему повідомлення {topic_id}.\nОпишіть вашу проблему якомога детальніше:")
    await state.set_state(HelpStates.writing_message)

    await callback.answer()


@router.callback_query(F.data == "help:cancel", StateFilter(HelpStates.choosing_topic))
async def cancel_help_request(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("❌ Запит до технічної підтримки скасовано.")
    await callback.answer()


@router.message(StateFilter(HelpStates.writing_message))
async def write_help_message(message: Message, state: FSMContext) -> None:
    from main import get_bot
    bot = get_bot()

    data = await state.get_data()

    selected_topic = data.get('selected_topic')
    if not selected_topic:
        await state.set_state(HelpStates.choosing_topic)
        await message.answer("Виберіть тему для звернення", reply_markup=help_kb.choose_support_topic())
        return

    # Брать следующий ID обращения из БД / чата Telegram
    help_message_id = 123

    user = message.from_user
    username = f"@{user.username}" if user.username else "Без Username"

    support_message = (
        f"🆘 <b>Нове звернення #{help_message_id} вiд {username}</b>\n\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"📋 <b>Тема:</b> {selected_topic}\n\n"
        f"💬 <b>Повідомлення:</b>\n{message.text}"
    )

    try:
        await bot.send_message(
            chat_id=-1002927033457,
            text=support_message,
            parse_mode="HTML",
            reply_markup=help_kb.choose_message_action_for_helpers(username)
        )

        await message.answer(
            f"Звернення №{help_message_id} отримано. Відповімо протягом 24 годин (10:00–18:00 за Києвом)")
    except Exception as e:
        print(f"Error sending message to support group: {e}")

    await state.clear()
