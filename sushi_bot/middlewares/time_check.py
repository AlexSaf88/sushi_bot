# time check middleware
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime
from config import WORK_HOURS

class TimeCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        now = datetime.now().time()
        open_time = datetime.strptime(WORK_HOURS["open"], "%H:%M").time()
        close_time = datetime.strptime(WORK_HOURS["close"], "%H:%M").time()

        if not (open_time <= now <= close_time):
            await event.answer(f"🚫 Ресторан сейчас закрыт.\nМы работаем с {WORK_HOURS['open']} до {WORK_HOURS['close']}.")
            return

        return await handler(event, data)