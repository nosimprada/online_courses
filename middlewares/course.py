from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User, Message, CallbackQuery

from config import ADMIN_CHAT_ID
from utils.enums.subscription import SubscriptionStatus
from utils.services.subscription import get_subscriptions_by_tg_id


class CourseMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        callback_data = str(getattr(event, "data", None))

        if callback_data and callback_data.startswith("course:"):
            user: User = data.get("event_from_user")

            if user:
                if user.id == ADMIN_CHAT_ID:
                    return await handler(event, data)

                try:
                    subscriptions = await get_subscriptions_by_tg_id(user.id)

                    has_active_subscription = any(
                        subscription.status == SubscriptionStatus.ACTIVE
                        for subscription in subscriptions
                    ) if subscriptions else False

                    if has_active_subscription:
                        return await handler(event, data)
                    else:
                        if isinstance(event, Message):
                            await event.answer("⛔️ У вас немає активної підписки на цей курс.")
                        elif isinstance(event, CallbackQuery):
                            await event.answer("⛔️ У вас немає активної підписки на цей курс.", show_alert=True)
                        return None

                except Exception as e:
                    print(f"Error checking subscription for user {user.id}: {e}")
                    if isinstance(event, CallbackQuery):
                        await event.answer("⛔️ Помилка перевірки підписки. Спробуйте пізніше.", show_alert=True)
                    return None

        return await handler(event, data)
