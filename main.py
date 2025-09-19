import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from handlers import routers

bot = Bot(token="8324688063:AAFZSq2D1PNi-cnWDMEmOIP3JKmP0AyQ_I0")


async def main() -> None:
    dp = Dispatcher()

    dp.include_routers(*routers)
    await dp.start_polling(bot)


def get_bot() -> Bot:
    return bot


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
