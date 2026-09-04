import yfinance as yf
import math


def get_stock_data(symbol: str):
    """
    Fetch real stock market data from Yahoo Finance.
    Assumes NSE-listed stocks.
    """

    try:
        symbol = symbol.upper().strip()
        ticker_symbol = f"{symbol}.NS"

        stock = yf.Ticker(ticker_symbol)

        # Get recent historical data
        history = stock.history(period="5d")

        if history.empty or len(history) < 2:
            return None

        current_price = float(history["Close"].iloc[-1])
        previous_close = float(history["Close"].iloc[-2])

        # Prevent NaN / invalid values
        if (
            not math.isfinite(current_price)
            or not math.isfinite(previous_close)
            or previous_close == 0
        ):
            return None

        current_price = round(current_price, 2)
        previous_close = round(previous_close, 2)

        # Calculate percentage change
        change_percent = round(
            ((current_price - previous_close) / previous_close) * 100,
            2
        )

        # Default company name
        company_name = symbol

        # Try to fetch company information separately
        # Failure here should NOT stop the stock from being added
        try:
            info = stock.info
            company_name = info.get("longName", symbol)
        except Exception as error:
            print(
                f"Could not fetch company name for {symbol}: {error}"
            )

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
    Create a complete PULSE stock object using real market data.
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
    # keep the existing stock unchanged
    if not real_data:
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