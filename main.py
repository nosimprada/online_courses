import asyncio
import logging
import sys

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update
from fastapi import FastAPI, Request

from api.routes import orders
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, SERVER_PORT
from handlers import routers
from utils.notificator import setup as setup_notifications_scheduler

logging.basicConfig(level=logging.DEBUG)

dp = Dispatcher()
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp.include_routers(*routers)

app = FastAPI(title="Online Courses API", version="1.0.0")

# Подключаем API роутеры
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])


# Основные эндпоинты
@app.get("/")
async def root():
    return {"message": "Online Courses API", "bot_status": "active"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# Telegram Webhook
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        update_data = await request.json()

        update = Update(**update_data)
        await dp.feed_update(bot, update)

        return {"ok": True}

    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return {"ok": False, "error": str(e)}


async def main() -> None:
    logging.info("Setting up webhook...")

    await bot.set_webhook(
        url=WEBHOOK_URL,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )

    setup_notifications_scheduler(bot)

    logging.info(f"Webhook set to {WEBHOOK_URL}.")
    # logging.info("Sending test email...")
    # success, error = await send_course_access_email(
    #     to="avd.bots.project@gmail.com",
    #     access_code="123456",
    #     bot_link="https://t.me/lagidna_disciplinabot"
    # )

    # if success:
    #     logging.info("Test email sent successfully!")
    # else:
    #     logging.error(f"Failed to send test email: {error}")

    # Запускаем FastAPI сервер
    config = uvicorn.Config(app, host="0.0.0.0", port=SERVER_PORT)
    server = uvicorn.Server(config)

    await server.serve()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
