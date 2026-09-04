from services.market_data import get_stock_data

print("Starting test...")

data = get_stock_data("RELIANCE")

print(data)

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

        # Default values used by PULSE's intelligence engine
        "normal_volatility": 1.0,
        "target_price": None,
        "previous_direction": (
            "up"
            if data["change_percent"] > 0
            else "down"
            if data["change_percent"] < 0
            else "neutral"
        )
    }