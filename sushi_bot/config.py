import json
from pathlib import Path

TOKEN = '7040262724:AAHCRLBB7Zexob_BrPtLb-Gc9ddiBM-5PVo'
ADMIN_ID = 157080971
DELIVERY_COST = 10

CONFIG_PATH = Path("data/work_hours.json")
MENU_PATH = Path("data/menu.json")

if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        WORK_HOURS = json.load(f)
else:
    WORK_HOURS = {"open": "10:00", "close": "22:00"}
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(WORK_HOURS, f)

def save_work_hours():
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(WORK_HOURS, f)

def load_menu():
    with open(MENU_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_menu(menu):
    with open(MENU_PATH, "w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=2)
