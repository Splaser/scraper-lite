import json
from pathlib import Path

CONFIG_FILE = Path("config.json")

with open(CONFIG_FILE, encoding="utf-8") as f:
    cfg = json.load(f)

SS_USER = cfg["SS_USER"]
SS_PASSWORD = cfg["SS_PASSWORD"]
SS_DEV_ID = cfg["SS_DEV_ID"]
SS_DEV_PASSWORD = cfg["SS_DEV_PASSWORD"]

BASE_URL = "https://api.screenscraper.fr/api2"
SOFTNAME = "scraper-lite"