from flask import Flask, render_template, request, jsonify

from database import get_connection
from market_status import get_market_status


app = Flask(__name__)


# ---------------------------------------
# HOME PAGE
# ---------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# ---------------------------------------
# CREATE ALERT
# ---------------------------------------

@app.route("/api/alerts", methods=["POST"])
def create_alert():

    data = request.get_json()

    symbol = data.get("symbol")
    target_price = data.get("target_price")
    condition_type = data.get("condition_type")

    if not symbol or not target_price or not condition_type:

        return jsonify({
            "success": False,
            "message": "All fields are required."
        }), 400

    symbol = symbol.upper().strip()

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        # Check whether stock already exists
        cursor.execute(
            "SELECT id FROM stocks WHERE symbol = %s",
            (symbol,)
        )

        stock = cursor.fetchone()

        # If stock doesn't exist, create it
        if stock is None:

            cursor.execute(
                "INSERT INTO stocks (symbol) VALUES (%s)",
                (symbol,)
            )

            stock_id = cursor.lastrowid

        else:

            stock_id = stock[0]

        # Insert alert
        cursor.execute(
            """
            INSERT INTO alerts
            (stock_id, condition_type, target_price, status)
            VALUES (%s, %s, %s, %s)
            """,
            (
                stock_id,
                condition_type,
                float(target_price),
                "ACTIVE"
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Alert created successfully!"
        })

    except Exception as e:

        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------
# GET ALL ALERTS
# ---------------------------------------

@app.route("/api/alerts", methods=["GET"])
def get_alerts():

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                alerts.id,
                stocks.symbol,
                alerts.target_price,
                alerts.condition_type,
                alerts.status,
                alerts.triggered_at
            FROM alerts
            INNER JOIN stocks
                ON alerts.stock_id = stocks.id
            ORDER BY alerts.id DESC
            """
        )

        alerts = cursor.fetchall()

        # ---------------------------------------
        # FORMAT TRIGGERED TIME
        # ---------------------------------------

        for alert in alerts:

            if alert["triggered_at"] is not None:

                alert["triggered_at"] = (
                    alert["triggered_at"]
                    .strftime("%d/%m/%Y, %I:%M:%S %p")
                )

        return jsonify(alerts)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------
# DELETE ALERT
# ---------------------------------------

@app.route("/api/alerts/<int:alert_id>", methods=["DELETE"])
def delete_alert(alert_id):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM alerts WHERE id = %s",
            (alert_id,)
        )

        if cursor.rowcount == 0:

            return jsonify({
                "success": False,
                "message": "Alert not found."
            }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Alert deleted successfully!"
        })

    except Exception as e:

        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------
# GET STOCK PRICE
# ---------------------------------------

@app.route("/api/price/<symbol>", methods=["GET"])
def get_stock_price_api(symbol):

    try:

        from stock_price import get_stock_price

        symbol = symbol.upper().strip()

        price = get_stock_price(symbol)

        if price is None:

            return jsonify({
                "success": False,
                "message": "Could not fetch stock price."
            }), 404

        return jsonify({
            "success": True,
            "symbol": symbol,
            "price": price
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ---------------------------------------
# GET MARKET STATUS
# ---------------------------------------

@app.route("/api/market-status", methods=["GET"])
def market_status_api():

    try:

        status = get_market_status()

        return jsonify(status)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ---------------------------------------
# START FLASK SERVER
# ---------------------------------------

if __name__ == "__main__":

    app.run(debug=True)