import yfinance as yf


def get_stock_price(symbol):

    try:
        ticker_symbol = symbol.upper().strip() + ".NS"

        ticker = yf.Ticker(ticker_symbol)

        data = ticker.history(
            period="1d",
            interval="1m"
        )

        if data.empty:
            return None

        price = data["Close"].iloc[-1]

        return float(price)

    except Exception as e:

        print("Error:", e)

        return None


if __name__ == "__main__":

    symbol = input("Enter NSE stock symbol: ")

    price = get_stock_price(symbol)

    if price is not None:

        print()
        print("Stock:", symbol.upper())
        print("Current Price: ₹", round(price, 2))

    else:

        print()
        print("Could not fetch stock price.")