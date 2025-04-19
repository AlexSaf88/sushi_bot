from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from handlers import menu, order, admin
from middlewares.time_check import TimeCheckMiddleware
from aiogram.client.default import DefaultBotProperties

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="admin", description="Админ-панель")
    ]
    await bot.set_my_commands(commands)

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)

    dp.message.middleware(TimeCheckMiddleware())

    dp.include_routers(
        menu.router,
        order.router,
        admin.router
    )

    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
