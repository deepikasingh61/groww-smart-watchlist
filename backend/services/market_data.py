import math
import yfinance as yf


def is_valid_number(value):
    """
    Check if a value is a valid finite number.
    Rejects NaN and infinity.
    """
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def get_stock_data(symbol: str):
    """
    Fetch latest stock market data from Yahoo Finance.
    Assumes NSE-listed stocks.
    """

    try:
        ticker_symbol = f"{symbol}.NS"

        stock = yf.Ticker(ticker_symbol)

        # Get recent historical data
        history = stock.history(period="5d")

        # Need at least 2 valid data points
        if history.empty or len(history) < 2:
            return None

        current_raw = history["Close"].iloc[-1]
        previous_raw = history["Close"].iloc[-2]

        # Prevent NaN from entering the application
        if not is_valid_number(current_raw):
            print(f"Invalid current price received for {symbol}")
            return None

        if not is_valid_number(previous_raw):
            print(f"Invalid previous price received for {symbol}")
            return None

        current_price = round(float(current_raw), 2)
        previous_close = round(float(previous_raw), 2)

        # Prevent division by zero
        if previous_close == 0:
            return None

        # Calculate percentage change
        change_percent = round(
            ((current_price - previous_close) / previous_close) * 100,
            2
        )

        # Final validation
        if not is_valid_number(change_percent):
            return None

        # Get company information safely
        try:
            info = stock.info
            company_name = info.get("longName", symbol)
        except Exception:
            company_name = symbol

        return {
            "symbol": symbol,
            "name": company_name,
            "price": current_price,
            "previous_price": previous_close,
            "change_percent": change_percent,
        }

    except Exception as error:
        print(f"Error fetching {symbol}: {error}")
        return None


def create_stock_from_market_data(symbol: str):
    """
    Create a complete PULSE stock object using market data.
    """

    data = get_stock_data(symbol)

    if not data:
        return None

    return {
        "symbol": data["symbol"],
        "name": data["name"],
        "price": data["price"],
        "previous_price": data["previous_price"],
        "change_percent": data["change_percent"],
        "normal_volatility": 1.0,
        "target_price": None,
        "previous_direction": (
            "up"
            if data["change_percent"] > 0
            else "down"
            if data["change_percent"] < 0
            else "neutral"
        ),
    }


def refresh_stock_data(stock):
    """
    Fetch latest market data and update an existing stock.
    """

    symbol = stock["symbol"]

    real_data = get_stock_data(symbol)

    # If market data couldn't be fetched,
    # OR invalid data was returned,
    # keep the existing stock unchanged
    if not real_data:
        print(f"Keeping existing data for {symbol}")
        return stock

    return {
        **stock,

        "name": real_data["name"],
        "price": real_data["price"],
        "previous_price": real_data["previous_price"],
        "change_percent": real_data["change_percent"],

        "previous_direction": (
            "up"
            if real_data["change_percent"] > 0
            else "down"
            if real_data["change_percent"] < 0
            else "neutral"
        ),
    }