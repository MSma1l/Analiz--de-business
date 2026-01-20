import aiogram 
import asyncio
from aiogram import Bot, Dispatcher
from configurare.setari import TOKEN
from bot.gestionari.start import router
from bd_sqlite.scheme_bd import async_main

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    await async_main(router)
    dp.include_router(router)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot Inactiv")