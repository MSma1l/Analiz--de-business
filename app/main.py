import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from configurare.setari import TOKEN
from bd_sqlite.scheme_bd import async_main

from bot.gestionari.start import router as start_bot
from bot.gestionari.test import router as handle_answer


async def main():
    await async_main()

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage()) 

    dp.include_router(start_bot)
    dp.include_router(handle_answer)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot inactiv")
