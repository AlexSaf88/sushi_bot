# menu keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_kb(menu: list) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=item["name"], callback_data=f"dish_{item['id']}")]
        for item in menu
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_dish_kb(dish_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ В корзину", callback_data=f"add_{dish_id}"),
            InlineKeyboardButton(text="➖ Убрать", callback_data=f"remove_{dish_id}")
        ],
        [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")]
    ])