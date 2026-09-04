import json
import os
from datetime import datetime


STATE_FILE = "user_state.json"


def load_user_state():
    """
    Loads the user's last check information.
    """

    if not os.path.exists(STATE_FILE):
        return {
            "last_checked": None,
            "last_seen_prices": {}
        }

    with open(STATE_FILE, "r") as file:
        return json.load(file)


def save_user_state(watchlist):
    """
    Saves the current stock prices and timestamp
    when the user checks their market watchlist.
    """

    state = {
        "last_checked": datetime.now().isoformat(),
        "last_seen_prices": {
            stock["symbol"]: stock["price"]
            for stock in watchlist
        }
    }

    with open(STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)

    return state