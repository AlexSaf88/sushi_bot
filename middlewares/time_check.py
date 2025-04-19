# time check middleware
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime
from config import WORK_HOURS, ADMIN_ID

WEEKDAYS_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

class TimeCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        now = datetime.now()
        weekday = WEEKDAYS_RU[now.weekday()]
        time = now.time()

        if (event.from_user.id != ADMIN_ID and
            (weekday not in WORK_HOURS.get("days", []) or
             not (datetime.strptime(WORK_HOURS["open"], "%H:%M").time() <= time <= datetime.strptime(WORK_HOURS["close"], "%H:%M").time()))):

            days_str = ", ".join(WORK_HOURS.get("days", []))
            await event.answer(
                f"🚫 Ресторан сейчас закрыт.\n"
                f"Мы работаем с {WORK_HOURS['open']} до {WORK_HOURS['close']}\n"
                f"Дни работы: {days_str}"
            )
            return

        return await handler(event, data)