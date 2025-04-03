import asyncio
import logging
import sys

from constants import TOKEN
from routers import add_router, delete_router, edit_router, range_router, start_router

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

dp = Dispatcher()

dp.include_routers(start_router, add_router, range_router, delete_router, edit_router)


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
asyncio.run(main())
