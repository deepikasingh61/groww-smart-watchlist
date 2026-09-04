import json
import os

from data import WATCHLIST


STATE_FILE = "watchlist.json"


def load_watchlist():
    if not os.path.exists(STATE_FILE):
        save_watchlist(WATCHLIST)
        return WATCHLIST.copy()

    with open(STATE_FILE, "r") as file:
        return json.load(file)


def save_watchlist(watchlist):
    with open(STATE_FILE, "w") as file:
        json.dump(watchlist, file, indent=4)