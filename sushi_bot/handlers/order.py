# order handler
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.cart import get_cart_text, get_cart_items, clear_cart
from config import DELIVERY_COST, ADMIN_ID
from handlers import admin

router = Router()

class OrderFSM(StatesGroup):
    delivery_method = State()
    address = State()
    pickup_time = State()
    name = State()
    phone = State()
    utensils = State()
    confirm = State()

@router.callback_query(F.data == "checkout")
async def choose_delivery(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderFSM.delivery_method)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚚 Доставка", callback_data="delivery"),
         InlineKeyboardButton(text="🏃 Самовывоз", callback_data="pickup")]
    ])
    await callback.message.answer("Выберите способ получения заказа:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "delivery")
async def ask_address(callback: CallbackQuery, state: FSMContext):
    await state.update_data(method="delivery")
    await state.set_state(OrderFSM.address)
    await callback.message.answer("Введите адрес доставки:")
    await callback.answer()

@router.callback_query(F.data == "pickup")
async def ask_pickup(callback: CallbackQuery, state: FSMContext):
    await state.update_data(method="pickup")
    await state.set_state(OrderFSM.pickup_time)
    await callback.message.answer("Введите дату и время самовывоза:")
    await callback.answer()

@router.message(OrderFSM.address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(OrderFSM.name)
    await message.answer("Введите ваше имя:")

@router.message(OrderFSM.pickup_time)
async def get_pickup_time(message: Message, state: FSMContext):
    await state.update_data(pickup_time=message.text)
    await state.set_state(OrderFSM.name)
    await message.answer("Введите ваше имя:")

@router.message(OrderFSM.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderFSM.phone)
    await message.answer("Введите номер телефона:")

@router.message(OrderFSM.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(OrderFSM.utensils)
    await message.answer("Сколько приборов вам понадобится?")

@router.message(OrderFSM.utensils)
async def get_utensils(message: Message, state: FSMContext):
    await state.update_data(utensils=message.text)
    await state.set_state(OrderFSM.confirm)

    data = await state.get_data()
    cart = get_cart_items(message.from_user.id)
    text = get_cart_text(message.from_user.id)
    delivery_text = ""
    total = sum(item['price'] * item['count'] for item in cart)
    if data.get("method") == "delivery":
        total += DELIVERY_COST
        delivery_text = f"\nАдрес: {data['address']}\nДоставка: {DELIVERY_COST} лв."
    else:
        delivery_text = f"\nСамовывоз: {data['pickup_time']}"

    result = (
        f"<b>Проверьте ваш заказ:</b>\n"
        f"Имя: {data['name']}\nТелефон: {data['phone']}\nПриборов: {data['utensils']}\n"
        f"{delivery_text}\n\n"
        f"<b>Состав заказа:</b>\n{text}\n\n<b>Итого: {total} лв.</b>"
    )

    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="final_confirm")],
        [InlineKeyboardButton(text="❌ Отменить заказ", callback_data="cancel_order")]
    ])

    await message.answer(result, reply_markup=confirm_kb)

@router.callback_query(F.data == "final_confirm")
async def final_submit(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = get_cart_items(callback.from_user.id)
    text = get_cart_text(callback.from_user.id)
    delivery_text = ""
    total = sum(item['price'] * item['count'] for item in cart)
    if data.get("method") == "delivery":
        total += DELIVERY_COST
        delivery_text = f"\nАдрес: {data['address']}\nДоставка: {DELIVERY_COST} лв."
    else:
        delivery_text = f"\nСамовывоз: {data['pickup_time']}"

    result = (
        f"<b>Новый заказ!</b>\n"
        f"Имя: {data['name']}\nТелефон: {data['phone']}\nПриборов: {data['utensils']}\n"
        f"{delivery_text}\n\n"
        f"<b>Состав заказа:</b>\n{text}\n<b>Итого: {total} лв.</b>"
    )

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_order"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order")
        ]
    ])

    msg = await callback.bot.send_message(ADMIN_ID, result, reply_markup=admin_kb)
    admin.admin_user_orders[msg.message_id] = callback.from_user.id

    await callback.message.answer("Ваш заказ отправлен администратору. Ожидайте подтверждение.")
    clear_cart(callback.from_user.id)
    await state.clear()
    await callback.answer()