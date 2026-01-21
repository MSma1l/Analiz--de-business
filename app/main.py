import asyncio
from aiogram import Bot, Dispatcher

from configurare.setari import TOKEN
from bot.gestionari.start import router
from bd_sqlite.scheme_bd import async_main


async def main():
    # creează tabelele DB (o singură dată)
    await async_main()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot inactiv")
