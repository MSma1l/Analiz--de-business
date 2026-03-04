import os  # Importa modulul os pentru lucrul cu caile de fisiere
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker  # Importa motorul asincron si generatorul de sesiuni din SQLAlchemy
from sqlalchemy import event  # Importa modulul event pentru a intercepta evenimentele motorului de baza de date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Obtine calea absoluta a directorului radacina al proiectului (doua nivele mai sus)
DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'data', 'telegram_bot.db')}"  # Construieste URL-ul de conectare la baza de date SQLite din folderul data


engine = create_async_engine(  # Creeaza motorul asincron pentru conectarea la baza de date
    DATABASE_URL,  # Specifica URL-ul bazei de date
    echo=False,  # Dezactiveaza afisarea comenzilor SQL in consola (seteaza True pentru depanare)
    connect_args={"timeout": 30},  # Seteaza timeout-ul de asteptare la 30 secunde cand baza de date e blocata
)


# ==================== OPTIMIZARE PERFORMANTA SQLite ====================
@event.listens_for(engine.sync_engine, "connect")  # Interceptam fiecare conexiune noua la baza de date
def _set_sqlite_pragma(dbapi_connection, connection_record):  # Functia care seteaza pragmele SQLite pentru performanta
    cursor = dbapi_connection.cursor()  # Obtinem un cursor pentru executarea comenzilor SQL
    cursor.execute("PRAGMA journal_mode=WAL")  # Activam WAL (Write-Ahead Logging) — permite citiri si scrieri simultane fara blocare
    cursor.execute("PRAGMA synchronous=NORMAL")  # Setam sincronizarea la NORMAL — mai rapid decat FULL, sigur cu WAL
    cursor.execute("PRAGMA cache_size=-8000")  # Setam cache-ul la 8MB (valoare negativa = kilobytes) pentru acces mai rapid la date
    cursor.execute("PRAGMA busy_timeout=30000")  # Setam timeout-ul de asteptare la 30 secunde la nivel SQLite (backup pentru connect_args)
    cursor.close()  # Inchidem cursorul dupa setarea pragmelor


async_session = async_sessionmaker(  # Creeaza fabricul de sesiuni asincrone pentru interogari
    engine,  # Specifica motorul de baza de date care va fi folosit
    expire_on_commit=False  # Dezactiveaza expirarea obiectelor dupa comitere pentru a le putea folosi in continuare
)
