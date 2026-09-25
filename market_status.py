from datetime import datetime
from zoneinfo import ZoneInfo


# -------------------------------------
# NSE 2026 HOLIDAYS
# -------------------------------------

NSE_HOLIDAYS = {

    "2026-01-15",  # Municipal Corporation Election
    "2026-01-26",  # Republic Day
    "2026-02-19",  # Chhatrapati Shivaji Maharaj Jayanti
    "2026-03-03",  # Holi
    "2026-03-19",  # Gudhi Padwa
    "2026-03-26",  # Ram Navami
    "2026-03-31",  # Mahavir Jayanti
    "2026-04-01",  # Annual Bank Closing
    "2026-04-03",  # Good Friday
    "2026-04-14",  # Dr. Babasaheb Ambedkar Jayanti
    "2026-05-01",  # Maharashtra Din / Buddha Pournima
    "2026-05-28",  # Bakri Id
    "2026-06-26",  # Muharram
    "2026-08-26",  # Id-E-Milad
    "2026-09-14",  # Ganesh Chaturthi
    "2026-10-02",  # Mahatma Gandhi Jayanti
    "2026-10-20",  # Dussehra
    "2026-11-08",  # Diwali Laxmi Pujan / Muhurat Trading
    "2026-11-10",  # Diwali (Bali Pratipada)
    "2026-11-24",  # Guru Nanak Jayanti
    "2026-12-25"   # Christmas
}


# -------------------------------------
# GET CURRENT IST TIME
# -------------------------------------

def get_current_time():

    return datetime.now(
        ZoneInfo("Asia/Kolkata")
    )


# -------------------------------------
# CHECK MARKET STATUS
# -------------------------------------

def get_market_status():

    now = get_current_time()

    today = now.strftime("%Y-%m-%d")

    current_time = now.time()


    # ---------------------------------
    # CHECK HOLIDAY
    # ---------------------------------

    if today in NSE_HOLIDAYS:

        return {
            "open": False,
            "status": "HOLIDAY",
            "message": "MARKET CLOSED - NSE HOLIDAY",
            "time": now.strftime("%I:%M:%S %p")
        }


    # ---------------------------------
    # CHECK WEEKEND
    # ---------------------------------

    if now.weekday() >= 5:

        return {
            "open": False,
            "status": "WEEKEND",
            "message": "MARKET CLOSED - WEEKEND",
            "time": now.strftime("%I:%M:%S %p")
        }


    # ---------------------------------
    # DEFINE MARKET TIMES
    # ---------------------------------

    pre_open_start = datetime.strptime(
        "09:00",
        "%H:%M"
    ).time()

    regular_market_start = datetime.strptime(
        "09:15",
        "%H:%M"
    ).time()

    regular_market_end = datetime.strptime(
        "15:30",
        "%H:%M"
    ).time()


    # ---------------------------------
    # PRE-OPEN SESSION
    # ---------------------------------

    if (
        pre_open_start
        <= current_time
        < regular_market_start
    ):

        return {
            "open": False,
            "status": "PRE_OPEN",
            "message": "PRE-OPEN SESSION",
            "time": now.strftime("%I:%M:%S %p")
        }


    # ---------------------------------
    # REGULAR MARKET
    # ---------------------------------

    if (
        regular_market_start
        <= current_time
        <= regular_market_end
    ):

        return {
            "open": True,
            "status": "OPEN",
            "message": "MARKET OPEN",
            "time": now.strftime("%I:%M:%S %p")
        }


    # ---------------------------------
    # MARKET CLOSED
    # ---------------------------------

    return {
        "open": False,
        "status": "CLOSED",
        "message": "MARKET CLOSED",
        "time": now.strftime("%I:%M:%S %p")
    }


# -------------------------------------
# CHECK IF ALERT CHECKING IS ALLOWED
# -------------------------------------

def is_market_open():

    status = get_market_status()

    return status["open"]


# -------------------------------------
# TEST
# -------------------------------------

if __name__ == "__main__":

    status = get_market_status()

    print("--------------------------------")
    print("NSE MARKET STATUS")
    print("--------------------------------")

    print(
        "Status:",
        status["status"]
    )

    print(
        "Message:",
        status["message"]
    )

    print(
        "Current IST:",
        status["time"]
    )

    print("--------------------------------")