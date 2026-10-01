import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}
TELEGRAM_BOT_TOKEN = "8944880528:AAEtO7lqfq08w97McUI0vMa2Pw4hPslmHXw"
TELEGRAM_CHAT_ID = "8168353858"