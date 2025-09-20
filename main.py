import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import routers

bot = Bot(token=BOT_TOKEN)


async def main() -> None:
    dp = Dispatcher()

    dp.include_routers(*routers)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
