import json
from pathlib import Path

MENU_PATH = Path("data/menu.json")

# Словарь для хранения корзин пользователей
user_carts = {}

def add_to_cart(user_id: int, dish_id: str):
    cart = user_carts.setdefault(user_id, {})
    cart[dish_id] = cart.get(dish_id, 0) + 1

def remove_from_cart(user_id: int, dish_id: str):
    cart = user_carts.get(user_id, {})
    if dish_id in cart:
        cart[dish_id] -= 1
        if cart[dish_id] <= 0:
            del cart[dish_id]

def get_cart_items(user_id: int):
    cart = user_carts.get(user_id, {})
    with open(MENU_PATH, "r", encoding="utf-8") as f:
        menu = json.load(f)

    result = []
    for dish_id, count in cart.items():
        dish = next((d for d in menu if d['id'] == dish_id), None)
        if dish:
            result.append({
                "name": dish['name'],
                "count": count,
                "price": dish['price']
            })
    return result

def get_cart_text(user_id: int):
    items = get_cart_items(user_id)
    if not items:
        return "Корзина пуста."
    return "\n".join([
        f"{item['name']} x{item['count']} — {item['count'] * item['price']} лв."
        for item in items
    ])

def clear_cart(user_id: int):
    user_carts.pop(user_id, None)