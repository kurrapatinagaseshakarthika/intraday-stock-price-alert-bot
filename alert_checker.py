import time

from database import get_connection
from stock_price import get_stock_price
from telegram_bot import send_telegram_message
from market_status import is_market_open



def check_alerts():

    print()
    print("================================")
    print("CHECKING STOCK ALERTS")
    print("================================")

    # Check whether NSE market is open
    if not is_market_open():

        print("🔴 NSE MARKET IS CLOSED")
        print("Skipping stock price check.")

        return
    print()
    print("================================")
    print("CHECKING STOCK ALERTS")
    print("================================")

    connection = get_connection()

    if connection is None:
        print("DATABASE CONNECTION FAILED!")
        return

    print("DATABASE CONNECTED SUCCESSFULLY!")

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            alerts.id,
            alerts.stock_id,
            alerts.target_price,
            alerts.condition_type,
            alerts.status,
            stocks.symbol
        FROM alerts
        JOIN stocks
            ON alerts.stock_id = stocks.id
        WHERE alerts.status = 'ACTIVE'
    """

    cursor.execute(query)
    alerts = cursor.fetchall()

    print("Active alerts found:", len(alerts))
    print("--------------------------------")

    for alert in alerts:

        alert_id = alert["id"]
        symbol = alert["symbol"]
        target_price = float(alert["target_price"])
        condition = alert["condition_type"]

        print("Alert ID:", alert_id)
        print("Stock:", symbol)
        print("Target Price: ₹", target_price)
        print("Condition:", condition)

        current_price = get_stock_price(symbol)

        if current_price is None:
            print("Could not fetch current price.")
            print("--------------------------------")
            continue

        print("Current Price: ₹", round(current_price, 2))

        triggered = False

        if condition == ">=":

            if current_price >= target_price:
                triggered = True

        elif condition == "<=":

            if current_price <= target_price:
                triggered = True

        if triggered:

            print("🔔 ALERT TRIGGERED!")

            update_query = """
                UPDATE alerts
                SET status = 'TRIGGERED',
                    triggered_at = NOW()
                WHERE id = %s
            """

            cursor.execute(update_query, (alert_id,))
            connection.commit()

            print("Alert status changed to TRIGGERED.")

            message = f"""
🔔 STOCK PRICE ALERT

Stock: {symbol}
Current Price: ₹{current_price:.2f}
Target Price: ₹{target_price:.2f}
Condition: {condition}

⚡ Alert triggered!
"""

            send_telegram_message(message)

            print("Telegram notification sent.")

        else:

            print("Alert condition not reached.")

        print("--------------------------------")

    cursor.close()
    connection.close()

    print("Check completed.")


if __name__ == "__main__":

    print("================================")
    print("INTRADAY STOCK ALERT BOT")
    print("================================")
    print("Automatic checking: EVERY 60 SECONDS")
    print("Press CTRL + C to stop.")
    print("================================")

    while True:

        try:

            check_alerts()

            print()
            print("Waiting 10 seconds for next check...")

            time.sleep(10)

        except KeyboardInterrupt:

            print()
            print("Stock alert bot stopped.")
            break

        except Exception as e:

            print("Error:", e)
            print("Retrying after 60 seconds...")

            time.sleep(10)