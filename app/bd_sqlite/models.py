from sqlalchemy import String, Integer, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


# =====================================================
# BAZA
# =====================================================

class Base(AsyncAttrs, DeclarativeBase):
    pass


# =====================================================
# USER
# =====================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )

    username: Mapped[str | None] = mapped_column(String(50))
    first_name: Mapped[str | None] = mapped_column(String(50))

    language: Mapped[str | None] = mapped_column(String(5))

    current_index: Mapped[int] = mapped_column(Integer, default=1)

    test_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[int | None] = mapped_column(Integer)

    company_name: Mapped[str | None] = mapped_column(String(100))
    number_company: Mapped[int | None] = mapped_column(Integer)
    email_company: Mapped[str | None] = mapped_column(String(100))


# =====================================================
# INTREBARI
# =====================================================

class Intrebare(Base):
    __tablename__ = "intrebari"

    id: Mapped[int] = mapped_column(primary_key=True)

    # ordinea intrebarilor in test
    index: Mapped[int] = mapped_column(Integer, nullable=False)

    # bloc / categorie risc
    categorie: Mapped[str] = mapped_column(String(50))

    text: Mapped[str] = mapped_column(String)
    tip: Mapped[str] = mapped_column(String(10))
    language: Mapped[str] = mapped_column(String(5))

    # 🔥 punctaj intrebare (folosit la calcul risc)
    weight: Mapped[int] = mapped_column(Integer, default=0)


# =====================================================
# PRAGURI RISC (intervale)
# =====================================================

class PragRisc(Base):
    __tablename__ = "praguri_risc"

    id: Mapped[int] = mapped_column(primary_key=True)

    categorie: Mapped[str] = mapped_column(String(50))

    scor_min: Mapped[int] = mapped_column(Integer)
    scor_max: Mapped[int] = mapped_column(Integer)

    nivel: Mapped[str] = mapped_column(String(50))


# =====================================================
# RASPUNSURI USER
# =====================================================

class Raspuns(Base):
    __tablename__ = "raspunsuri"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    intrebare_id: Mapped[int] = mapped_column(ForeignKey("intrebari.id"))

    # salvam YES / NO / IDK
    weight: Mapped[str] = mapped_column(String(20))


# =====================================================
# REZULTATE FINALE
# =====================================================

class Rezultat(Base):
    __tablename__ = "rezultate"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    categorie: Mapped[str] = mapped_column(String(50))
    scor: Mapped[int]
    nivel: Mapped[str] = mapped_column(String(50))
