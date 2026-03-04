from sqlalchemy import String, Integer, Boolean, ForeignKey, BigInteger  # Importa tipurile de coloane din SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column  # Importa clasa de baza declarativa si instrumentele de mapare
from sqlalchemy.ext.asyncio import AsyncAttrs  # Importa atributele asincrone pentru modelele SQLAlchemy


# =====================================================
# BAZA
# =====================================================

class Base(AsyncAttrs, DeclarativeBase):  # Defineste clasa de baza pentru toate modelele, cu suport asincron
    pass  # Clasa de baza nu contine campuri proprii, serveste doar ca parinte pentru celelalte modele


# =====================================================
# USER
# =====================================================

class User(Base):  # Defineste modelul User care mosteneste clasa de baza
    __tablename__ = "users"  # Specifica numele tabelei in baza de date

    id: Mapped[int] = mapped_column(primary_key=True)  # Coloana ID - cheia primara, se incrementeaza automat

    telegram_id: Mapped[int] = mapped_column(  # Coloana pentru ID-ul unic al utilizatorului in Telegram
        BigInteger, unique=True, nullable=False  # Tip numar mare, unic si obligatoriu
    )

    username: Mapped[str | None] = mapped_column(String(50))  # Coloana pentru numele de utilizator Telegram (optional, max 50 caractere)
    first_name: Mapped[str | None] = mapped_column(String(50))  # Coloana pentru prenumele utilizatorului (optional, max 50 caractere)

    language: Mapped[str | None] = mapped_column(String(5))  # Coloana pentru limba preferata a utilizatorului (optional, max 5 caractere)

    current_index: Mapped[int] = mapped_column(Integer, default=1)  # Coloana pentru indexul curent al intrebarii la care a ajuns utilizatorul (implicit 1)

    test_completed: Mapped[bool] = mapped_column(Boolean, default=False)  # Coloana care indica daca utilizatorul a finalizat testul (implicit False)
    score: Mapped[int | None] = mapped_column(Integer)  # Coloana pentru scorul total al utilizatorului (optional)

    company_name: Mapped[str | None] = mapped_column(String(100))  # Coloana pentru numele companiei utilizatorului (optional, max 100 caractere)
    number_company: Mapped[int | None] = mapped_column(Integer)  # Coloana pentru numarul de telefon al companiei (optional)
    email_company: Mapped[str | None] = mapped_column(String(100))  # Coloana pentru adresa de email a companiei (optional, max 100 caractere)


# =====================================================
# INTREBARI
# =====================================================

class Intrebare(Base):  # Defineste modelul Intrebare care mosteneste clasa de baza
    __tablename__ = "intrebari"  # Specifica numele tabelei in baza de date

    id: Mapped[int] = mapped_column(primary_key=True)  # Coloana ID - cheia primara, se incrementeaza automat

    # ordinea intrebarilor in test
    index: Mapped[int] = mapped_column(Integer, nullable=False)  # Coloana pentru ordinea intrebarii in test (obligatoriu)

    # bloc / categorie risc
    categorie: Mapped[str] = mapped_column(String(50))  # Coloana pentru categoria de risc careia ii apartine intrebarea

    text: Mapped[str] = mapped_column(String)  # Coloana pentru textul intrebarii
    tip: Mapped[str] = mapped_column(String(10))  # Coloana pentru tipul intrebarii (ex: da/nu, alegere multipla)
    language: Mapped[str] = mapped_column(String(5))  # Coloana pentru limba in care este scrisa intrebarea

    # 🔥 punctaj intrebare (folosit la calcul risc)
    weight: Mapped[int] = mapped_column(Integer, default=0)  # Coloana pentru punctajul intrebarii folosit la calculul riscului (implicit 0)


# =====================================================
# PRAGURI RISC (intervale)
# =====================================================

class PragRisc(Base):  # Defineste modelul PragRisc pentru intervalele de risc
    __tablename__ = "praguri_risc"  # Specifica numele tabelei in baza de date

    id: Mapped[int] = mapped_column(primary_key=True)  # Coloana ID - cheia primara, se incrementeaza automat

    categorie: Mapped[str] = mapped_column(String(50))  # Coloana pentru categoria de risc

    scor_min: Mapped[int] = mapped_column(Integer)  # Coloana pentru scorul minim al intervalului de risc
    scor_max: Mapped[int] = mapped_column(Integer)  # Coloana pentru scorul maxim al intervalului de risc

    nivel: Mapped[str] = mapped_column(String(50))  # Coloana pentru nivelul de risc (ex: scazut, mediu, ridicat)

    # ✅ Adăugat câmp pentru limbă
    language: Mapped[str] = mapped_column(String(5), default="ro")  # Coloana pentru limba pragului de risc (implicit romana)


# =====================================================
# RASPUNSURI USER
# =====================================================

class Raspuns(Base):  # Defineste modelul Raspuns pentru raspunsurile utilizatorilor
    __tablename__ = "raspunsuri"  # Specifica numele tabelei in baza de date

    id: Mapped[int] = mapped_column(primary_key=True)  # Coloana ID - cheia primara, se incrementeaza automat

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # Coloana cheie externa care leaga raspunsul de utilizator
    intrebare_id: Mapped[int] = mapped_column(ForeignKey("intrebari.id"))  # Coloana cheie externa care leaga raspunsul de intrebare

    # salvam YES / NO / IDK
    weight: Mapped[str] = mapped_column(String(20))  # Coloana pentru valoarea raspunsului (YES / NO / IDK)


# =====================================================
# REZULTATE FINALE
# =====================================================

class Rezultat(Base):  # Defineste modelul Rezultat pentru rezultatele finale ale testului
    __tablename__ = "rezultate"  # Specifica numele tabelei in baza de date

    id: Mapped[int] = mapped_column(primary_key=True)  # Coloana ID - cheia primara, se incrementeaza automat

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # Coloana cheie externa care leaga rezultatul de utilizator

    categorie: Mapped[str] = mapped_column(String(50))  # Coloana pentru categoria de risc evaluata
    scor: Mapped[int]  # Coloana pentru scorul obtinut de utilizator la aceasta categorie
    max_scor: Mapped[int | None] = mapped_column(Integer, default=None)  # Coloana pentru scorul maxim posibil la aceasta categorie (optional)
    nivel: Mapped[str] = mapped_column(String(50))  # Coloana pentru nivelul de risc rezultat (ex: scazut, mediu, ridicat)
