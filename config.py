import os

from dotenv import load_dotenv

load_dotenv()

# Load the DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
