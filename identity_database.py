import json
import os
from pathlib import Path

DATABASE_PATH = Path("people.json")
DEFAULT_SCENTS = [
    "Fresh Bread Dough",
    "Barry's Tea",
    "Lyons Tea",
    "Fresh Hay",
    "Freshly Baked Cookies",
    "Wood Fire Smoke",
    "Rose Garden",
]

identity_map = {}


def load_people():
    global identity_map

    if not DATABASE_PATH.exists():
        identity_map = {}
        return identity_map

    try:
        with DATABASE_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        identity_map = {}
        return identity_map

    if isinstance(data, dict):
        identity_map = data
    else:
        identity_map = {}

    return identity_map


def save_people():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATABASE_PATH.open("w", encoding="utf-8") as file:
        json.dump(identity_map, file, indent=4)

    return DATABASE_PATH


load_people()