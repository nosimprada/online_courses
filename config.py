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

API_TOKEN = "123456"

# Webhook настройки
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://yourdomain.com/webhook")
WEBHOOK_PATH = "/webhook"

SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))  # По умолчанию 8000
