# admin handler
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime
from config import ADMIN_ID, WORK_HOURS, save_work_hours, load_menu, save_menu

router = Router()

class CancelOrderFSM(StatesGroup):
    waiting_for_reason = State()

class WorkHoursFSM(StatesGroup):
    waiting_for_open = State()
    waiting_for_close = State()
    waiting_for_days = State()

class AddDishFSM(StatesGroup):
    name = State()
    description = State()
    price = State()
    image = State()

admin_user_orders = {}

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("У вас нет доступа к админ-панели.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Управление меню", callback_data="admin_menu")],
        [InlineKeyboardButton(text="Настройка времени работы", callback_data="admin_hours")]
    ])
    await message.answer("Добро пожаловать в админ-панель:", reply_markup=kb)

@router.callback_query(F.data == "admin_menu")
async def admin_menu(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить блюдо", callback_data="admin_add_dish")],
        [InlineKeyboardButton(text="🗑 Удалить блюдо", callback_data="admin_delete_dish")]
    ])
    await callback.message.answer("Управление меню:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "admin_add_dish")
async def start_add_dish(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddDishFSM.name)
    await callback.message.answer("Введите название блюда:")
    await callback.answer()

@router.message(AddDishFSM.name)
async def set_dish_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddDishFSM.description)
    await message.answer("Введите описание блюда:")

@router.message(AddDishFSM.description)
async def set_dish_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddDishFSM.price)
    await message.answer("Введите цену блюда (число):")

@router.message(AddDishFSM.price)
async def set_dish_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        await state.set_state(AddDishFSM.image)
        await message.answer("Теперь отправьте фото блюда (из галереи, не ссылкой):")
    except ValueError:
        await message.answer("Цена должна быть числом. Попробуйте ещё раз.")

@router.message(AddDishFSM.image, F.photo)
async def set_dish_image(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    new_dish = {
        "id": str(datetime.now().timestamp()),
        "name": data['name'],
        "description": data['description'],
        "price": data['price'],
        "image": photo_id
    }
    menu = load_menu()
    menu.append(new_dish)
    save_menu(menu)
    await message.answer(f"✅ Блюдо \"{data['name']}\" добавлено в меню.")
    await state.clear()

@router.callback_query(F.data == "admin_delete_dish")
async def delete_dish_menu(callback: CallbackQuery):
    menu = load_menu()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=dish['name'], callback_data=f"del_{dish['id']}")]
            for dish in menu
        ]
    )
    await callback.message.answer("Выберите блюдо для удаления:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("del_"))
async def delete_dish(callback: CallbackQuery):
    dish_id = callback.data.split("_")[1]
    menu = load_menu()
    menu = [dish for dish in menu if dish['id'] != dish_id]
    save_menu(menu)
    await callback.message.answer("Блюдо удалено из меню.")
    await callback.answer()

@router.callback_query(F.data == "admin_hours")
async def edit_hours(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkHoursFSM.waiting_for_open)
    await callback.message.answer("Введите время открытия (в формате ЧЧ:ММ):")
    await callback.answer()

@router.message(WorkHoursFSM.waiting_for_open)
async def set_open_time(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%H:%M")
        WORK_HOURS["open"] = message.text
        await state.set_state(WorkHoursFSM.waiting_for_close)
        await message.answer("Теперь введите время закрытия (в формате ЧЧ:ММ):")
    except ValueError:
        await message.answer("Неверный формат. Попробуйте снова (например, 10:00).")

@router.message(WorkHoursFSM.waiting_for_close)
async def set_close_time(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%H:%M")
        WORK_HOURS["close"] = message.text
        await state.set_state(WorkHoursFSM.waiting_for_days)
        await message.answer("Введите дни работы через запятую (например: Пн, Вт, Ср):")
    except ValueError:
        await message.answer("Неверный формат. Попробуйте снова (например, 22:00).")

@router.message(WorkHoursFSM.waiting_for_days)
async def set_work_days(message: Message, state: FSMContext):
    valid_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    days = [d.strip().capitalize() for d in message.text.split(",") if d.strip() in valid_days]
    if not days:
        await message.answer("Введите допустимые дни (например: Пн, Вт, Ср). Допустимые значения: Пн, Вт, Ср, Чт, Пт, Сб, Вс")
        return
    WORK_HOURS["days"] = days
    save_work_hours()
    await message.answer(f"✅ Время работы обновлено: {WORK_HOURS['open']} - {WORK_HOURS['close']}\nДни: {', '.join(WORK_HOURS['days'])}")
    await state.clear()

@router.callback_query()
async def handle_admin_callback(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    if data == "confirm_order":
        user_id = admin_user_orders.pop(callback.message.message_id, None)
        if user_id:
            await callback.bot.send_message(user_id, "✅ Ваш заказ подтверждён!")
        await callback.message.edit_reply_markup()
        await callback.answer("Заказ подтверждён.")

    elif data == "cancel_order":
        user_id = admin_user_orders.get(callback.message.message_id)
        if user_id:
            await state.set_state(CancelOrderFSM.waiting_for_reason)
            await state.update_data(client_id=user_id, msg_id=callback.message.message_id)
            await callback.message.answer("Введите причину отмены заказа:")
        await callback.message.edit_reply_markup()
        await callback.answer()

@router.message(CancelOrderFSM.waiting_for_reason)
async def process_cancel_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    reason = message.text
    client_id = data.get("client_id")
    if client_id:
        await message.bot.send_message(client_id, f"❌ Ваш заказ отменён.\nПричина: {reason}")
    admin_user_orders.pop(data.get("msg_id"), None)
    await state.clear()