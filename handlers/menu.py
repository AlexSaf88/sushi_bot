# menu handler
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.menu import get_main_menu_kb, get_dish_kb
import json
from pathlib import Path
from services.cart import add_to_cart, remove_from_cart, get_cart_text

router = Router()
MENU_PATH = Path("data/menu.json")

@router.message(F.text == "/start")
async def start_cmd(message: Message):
    with open(MENU_PATH, "r", encoding="utf-8") as f:
        menu = json.load(f)

    text = "<b>Меню:</b>\nВыберите блюдо для подробностей."
    kb = get_main_menu_kb(menu)
    await message.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("dish_"))
async def show_dish(callback: CallbackQuery):
    dish_id = callback.data.split("_")[1]
    with open(MENU_PATH, "r", encoding="utf-8") as f:
        menu = json.load(f)
    dish = next((d for d in menu if d["id"] == dish_id), None)

    if dish:
        caption = f"<b>{dish['name']}</b>\n{dish['description']}\nЦена: {dish['price']} лв."
        kb = get_dish_kb(dish_id)
        await callback.message.answer_photo(photo=dish['image'], caption=caption, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("add_"))
async def add_item(callback: CallbackQuery):
    dish_id = callback.data.split("_")[1]
    add_to_cart(callback.from_user.id, dish_id)
    text = get_cart_text(callback.from_user.id)
    await callback.message.answer(f"<b>Обновлённая корзина:</b>\n{text}")
    await callback.answer("Добавлено в корзину")

@router.callback_query(F.data.startswith("remove_"))
async def remove_item(callback: CallbackQuery):
    dish_id = callback.data.split("_")[1]
    remove_from_cart(callback.from_user.id, dish_id)
    text = get_cart_text(callback.from_user.id)
    await callback.message.answer(f"<b>Обновлённая корзина:</b>\n{text}")
    await callback.answer("Удалено из корзины")

from aiogram.types import Message

#@router.message(F.photo)
#async def get_photo_id(message: Message):
#    file_id = message.photo[-1].file_id
#    await message.answer(f"<b>file_id:</b> <code>{file_id}</code>")