from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from config import ADMIN_CHAT_ID
from utils.services.user import get_user_full_info_by_tg_id


class IsSubscribedMiddleware(BaseMiddleware):
    """
    Middleware для проверки подписки пользователя.
    Проверяет есть ли у пользователя активная подписка.
    """

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        user_tg_id: int = 0

        # Получаем tg_id пользователя
        if isinstance(event, Message):
            user_tg_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_tg_id = event.from_user.id

        user_data = await get_user_full_info_by_tg_id(user_tg_id)

        if user_data.user_id != ADMIN_CHAT_ID and not user_data.is_subscribed:
            return None

        return await handler(event, data)
