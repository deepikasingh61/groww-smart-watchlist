from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from watchlist_state import load_watchlist, save_watchlist
from services.change_engine import detect_meaningful_change
from services.market_data import (
    create_stock_from_market_data,
    refresh_stock_data
)
from user_state import load_user_state, save_user_state


app = FastAPI()


class StockRequest(BaseModel):
    symbol: str


# Allow React frontend to communicate with FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "PULSE backend is running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy"
    }


# ==========================================
# GET COMPLETE WATCHLIST
# ==========================================

@app.get("/api/watchlist")
def get_watchlist():
    return load_watchlist()


# ==========================================
# GET MEANINGFUL SIGNALS
# ==========================================

@app.get("/api/signals")
def get_signals():

    watchlist = load_watchlist()

    user_state = load_user_state()
    last_seen_prices = user_state.get(
        "last_seen_prices",
        {}
    )

    signals = []

    for stock in watchlist:

        # Create copy so original data isn't modified
        stock_to_check = stock.copy()

        symbol = stock["symbol"]

        # Compare against user's last seen price
        if symbol in last_seen_prices:

            last_seen_price = last_seen_prices[symbol]

            stock_to_check["previous_price"] = last_seen_price

            if last_seen_price != 0:

                change_percent = (
                    (stock["price"] - last_seen_price)
                    / last_seen_price
                ) * 100

                stock_to_check["change_percent"] = round(
                    change_percent,
                    2
                )

        result = detect_meaningful_change(stock_to_check)

        if result["meaningful"]:

            signals.append({
                **stock_to_check,
                **result
            })

    # Highest priority first
    signals.sort(
        key=lambda signal: signal["priority"],
        reverse=True
    )

    return signals


# ==========================================
# GET USER STATE
# ==========================================

@app.get("/api/state")
def get_user_state():
    return load_user_state()


# ==========================================
# MARK MARKET AS CHECKED
# ==========================================

@app.post("/api/check")
def check_market():

    watchlist = load_watchlist()

    return save_user_state(watchlist)


# ==========================================
# ADD STOCK
# ==========================================

@app.post("/api/watchlist")
def add_stock(stock_request: StockRequest):

    watchlist = load_watchlist()

    symbol = stock_request.symbol.upper().strip()

    # Check if stock already exists
    for stock in watchlist:

        if stock["symbol"] == symbol:

            raise HTTPException(
                status_code=400,
                detail="Stock already exists in your watchlist"
            )

    # Fetch real market data
    new_stock = create_stock_from_market_data(symbol)

    # Invalid stock symbol
    if not new_stock:

        raise HTTPException(
            status_code=404,
            detail=f"Could not find market data for {symbol}"
        )

    # Add stock
    watchlist.append(new_stock)

    # Save permanently
    save_watchlist(watchlist)

    return new_stock


# ==========================================
# REFRESH MARKET
# ==========================================

@app.post("/api/refresh")
def refresh_watchlist():

    watchlist = load_watchlist()

    refreshed_watchlist = []

    for stock in watchlist:

        refreshed_stock = refresh_stock_data(stock)

        refreshed_watchlist.append(
            refreshed_stock
        )

    # Save refreshed prices permanently
    save_watchlist(refreshed_watchlist)

    return refreshed_watchlist