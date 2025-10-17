from datetime import date, datetime
from typing import Dict, List

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

import utils.notifications.keyboards as kb
from utils.services.subscription import get_all_active_subscriptions

MESSAGES: Dict[str, str] = {
    "paid": "✅ Оплата успішно отримана!\nДоступ буде діяти до {date}.\nПочати з уроку 1?",
    "will_expire": "⚠️ Доступ закінчиться через {in_days} днів ({date})!\nПродовжити на 90 днів?",
    "expired": "⛔ Дні доступу до курсу закінчилися.\nМожна продовжити ще на 90 днів?",
    "maybe_extend": "ℹ️ Вже минув тиждень з моменту закінчення доступу.\nБажаєте продовжити?"
}


def setup(bot: Bot) -> None:
    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")

    async def check_users():
        try:
            subscriptions = await get_all_active_subscriptions()
            sent_for_users: Dict[int, List[int]] = {}

            for sub in subscriptions:
                user_id = sub.user_id

                if user_id not in sent_for_users:
                    sent_for_users[user_id] = []

                days_diff = _days_diff(sub.access_from)

                if days_diff in [75, 85] and days_diff not in sent_for_users[user_id]:
                    await bot.send_message(
                        user_id,
                        MESSAGES["will_expire"].format(in_days=90 - days_diff, date=_format_date(sub.access_to.date())),
                        reply_markup=await kb.extend_subscription()
                    )

                    sent_for_users[user_id].append(days_diff)

                elif days_diff == 90 and 90 not in sent_for_users[user_id]:
                    await bot.send_message(
                        user_id,
                        MESSAGES["expired"],
                        reply_markup=await kb.extend_subscription()
                    )

                    sent_for_users[user_id].append(90)

                elif days_diff == 97 and 97 not in sent_for_users[user_id]:
                    await bot.send_message(
                        user_id,
                        MESSAGES["maybe_extend"],
                        reply_markup=await kb.extend_subscription()
                    )

                    sent_for_users[user_id].append(97)

        except Exception as e:
            print(f"Scheduler: Error in check_users: {e}")

    scheduler.add_job(check_users, trigger="cron", second=5)
    scheduler.start()


def _days_diff(start_date: date) -> int:
    as_date = start_date.date() if isinstance(start_date, datetime) else start_date
    return (_now_kiev().date() - as_date).days


def _format_date(d: date) -> str:
    return d.strftime('%d.%m.%Y')


def _now_kiev() -> datetime:
    return datetime.now(timezone("Europe/Kyiv"))
