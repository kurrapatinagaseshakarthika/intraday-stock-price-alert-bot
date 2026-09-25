import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    response = requests.post(
        url,
        data=data,
        timeout=10
    )

    print("Telegram API response:")
    print(response.text)

    if response.ok:
        print()
        print("✅ Telegram message sent successfully!")
        return True

    print()
    print("❌ Telegram message failed!")
    return False


if __name__ == "__main__":

    print("================================")
    print("TELEGRAM BOT TEST")
    print("================================")

    message = """
🔔 Intraday Stock Alert Bot

Telegram connection test successful! ✅

Your bot is connected successfully.
"""

    send_telegram_message(message)