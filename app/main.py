import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from configurare.setari import TOKEN
from bd_sqlite.scheme_bd import async_main

from bot.gestionari.start import router as start_bot
from bot.gestionari.test import router as handle_answer
from bot.gestionari.meniu import router as cabinet_router
from bot.gestionari.question import router as test_start
from bot.gestionari.raportPdf import router as raportPDF
from bot.gestionari.command import router as command_router


async def main():
    await async_main()

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage()) 

    dp.include_router(start_bot)
    dp.include_router(handle_answer)
    dp.include_router(cabinet_router)
    dp.include_router(test_start)
    dp.include_router(raportPDF)
    dp.include_router(command_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot inactiv")
