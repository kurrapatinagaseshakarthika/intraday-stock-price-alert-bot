from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_connection
from market_status import get_market_status


app = Flask(__name__)

# Secret key used for login sessions
app.secret_key = "stock_alert_bot_secret_key"


# ============================================================
# LOGIN REQUIRED HELPER
# ============================================================

def login_required():
    return "user_id" in session


# ============================================================
# SIGN UP
# ============================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("signup.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # Check required fields
    if not name or not email or not password or not confirm_password:
        return "Please fill in all fields."

    # Check password confirmation
    if password != confirm_password:
        return "Passwords do not match."

    # Check password length
    if len(password) < 6:
        return "Password must contain at least 6 characters."

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Check whether email already exists
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return "An account with this email already exists."

        # Encrypt password
        password_hash = generate_password_hash(password)

        # Insert new user
        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (name, email, password_hash)
        )

        connection.commit()

        return redirect(url_for("login"))

    except Exception as e:
        print("SIGNUP ERROR:", e)
        return "Something went wrong while creating your account."

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        return "Please enter your email and password."

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email, password_hash
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            return "Invalid email or password."

        # Check encrypted password
        if not check_password_hash(user["password_hash"], password):
            return "Invalid email or password."

        # Create login session
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        return redirect(url_for("home"))

    except Exception as e:
        print("LOGIN ERROR:", e)
        return "Something went wrong while logging in."

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ============================================================
# HOME / DASHBOARD
# ============================================================

@app.route("/")
def home():

    if not login_required():
        return redirect(url_for("login"))

    return render_template(
        "index.html",
        user_name=session.get("user_name"),
        user_email=session.get("user_email")
    )


# ============================================================
# CREATE ALERT
# ============================================================

@app.route("/api/alerts", methods=["POST"])
def create_alert():

    if not login_required():
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400

    symbol = data.get("symbol", "").strip().upper()
    target_price = data.get("target_price")
    condition_type = data.get("condition_type")

    if not symbol or target_price is None or not condition_type:
        return jsonify({
            "success": False,
            "message": "Please fill in all alert fields."
        }), 400

    if condition_type not in [">=", "<="]:
        return jsonify({
            "success": False,
            "message": "Invalid condition type."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Check whether stock already exists
        cursor.execute(
            "SELECT id FROM stocks WHERE symbol = %s",
            (symbol,)
        )

        stock = cursor.fetchone()

        # Create stock if it does not exist
        if not stock:

            cursor.execute(
                """
                INSERT INTO stocks (symbol, company_name)
                VALUES (%s, %s)
                """,
                (symbol, symbol)
            )

            connection.commit()

            stock_id = cursor.lastrowid

        else:
            stock_id = stock["id"]

        # Insert alert
        cursor.execute(
            """
            INSERT INTO alerts
            (stock_id, target_price, condition_type, status)
            VALUES (%s, %s, %s, 'ACTIVE')
            """,
            (stock_id, target_price, condition_type)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Alert created successfully."
        })

    except Exception as e:
        print("CREATE ALERT ERROR:", e)

        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "Could not create alert."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# GET ALERTS
# ============================================================

@app.route("/api/alerts", methods=["GET"])
def get_alerts():

    if not login_required():
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

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

        # Convert database decimal values to normal numbers/strings
        for alert in alerts:

            if alert["target_price"] is not None:
                alert["target_price"] = float(alert["target_price"])

            if alert["triggered_at"] is not None:
                alert["triggered_at"] = str(alert["triggered_at"])

        return jsonify(alerts)

    except Exception as e:
        print("GET ALERTS ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Could not load alerts."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# DELETE ALERT
# ============================================================

@app.route("/api/alerts/<int:alert_id>", methods=["DELETE"])
def delete_alert(alert_id):

    if not login_required():
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM alerts WHERE id = %s",
            (alert_id,)
        )

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Alert not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Alert deleted successfully."
        })

    except Exception as e:
        print("DELETE ALERT ERROR:", e)

        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "Could not delete alert."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# GET STOCK PRICE
# ============================================================

@app.route("/api/price/<symbol>", methods=["GET"])
def get_stock_price(symbol):

    if not login_required():
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    symbol = symbol.strip().upper()

    try:

        import yfinance as yf

        ticker = yf.Ticker(symbol + ".NS")

        data = ticker.history(period="1d", interval="1m")

        if data.empty:
            return jsonify({
                "success": False,
                "message": "Could not fetch stock price."
            }), 404

        latest_price = data["Close"].iloc[-1]

        return jsonify({
            "success": True,
            "symbol": symbol,
            "price": round(float(latest_price), 2)
        })

    except Exception as e:

        print("PRICE ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Could not fetch stock price."
        }), 500


# ============================================================
# MARKET STATUS
# ============================================================

@app.route("/api/market-status", methods=["GET"])
def market_status():

    if not login_required():
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    try:

        status = get_market_status()

        return jsonify(status)

    except Exception as e:

        print("MARKET STATUS ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Could not check market status."
        }), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)