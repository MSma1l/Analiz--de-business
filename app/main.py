import asyncio  # Importa modulul asyncio pentru programare asincrona
from aiogram import Bot, Dispatcher  # Importa clasele Bot si Dispatcher din biblioteca aiogram
from aiogram.fsm.storage.memory import MemoryStorage  # Importa MemoryStorage pentru stocarea starilor FSM in memorie
from configurare.setari import TOKEN  # Importa token-ul botului din fisierul de configurare
from bd_sqlite.schema_bd import async_main  # Importa functia de creare a bazei de date

from bot.gestionari.pornire import router as start_bot  # Importa router-ul pentru comanda de pornire a botului
from bot.gestionari.raspuns import router as handle_answer  # Importa router-ul pentru gestionarea raspunsurilor
from bot.gestionari.meniu import router as cabinet_router  # Importa router-ul pentru meniul cabinetului personal
from bot.gestionari.intrebare import router as test_start  # Importa router-ul pentru inceperea testului cu intrebari
from bot.gestionari.comenzi import router as command_router  # Importa router-ul pentru comenzile botului


async def main():  # Defineste functia principala asincrona
    await async_main()  # Asteapta crearea tabelelor in baza de date

    bot = Bot(token=TOKEN)  # Creeaza instanta botului Telegram folosind token-ul
    dp = Dispatcher(storage=MemoryStorage())  # Creeaza dispatcher-ul cu stocare in memorie pentru starile FSM

    dp.include_router(start_bot)  # Inregistreaza router-ul de pornire in dispatcher
    dp.include_router(handle_answer)  # Inregistreaza router-ul de raspunsuri in dispatcher
    dp.include_router(cabinet_router)  # Inregistreaza router-ul meniului in dispatcher
    dp.include_router(test_start)  # Inregistreaza router-ul de intrebari in dispatcher
    dp.include_router(command_router)  # Inregistreaza router-ul de comenzi in dispatcher

    await dp.start_polling(bot)  # Porneste ascultarea mesajelor de la Telegram prin metoda polling


if __name__ == "__main__":  # Verifica daca fisierul este rulat direct (nu importat ca modul)
    try:  # Incearca sa execute blocul de cod
        asyncio.run(main())  # Lanseaza functia principala asincrona
    except KeyboardInterrupt:  # Prinde intreruperea de la tastatura (Ctrl+C)
        print("Bot inactiv")  # Afiseaza mesajul ca botul a fost oprit
