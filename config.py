import os

from dotenv import load_dotenv

load_dotenv()

# Load the DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

MONOPAY_TOKEN = os.getenv("MONOPAY_TOKEN")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
"""
    Я использовал Яндекс Почту для SMTP. https://yandex.ru/support/yandex-360/business/mail/ru/mail-clients/others#smtpsetting
    SMTP_SERVER=smtp.yandex.ru
    SMTP_PORT=465 (Для SSL)
"""


WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://yourdomain.com/webhook")
WEBHOOK_PATH = "/webhook"