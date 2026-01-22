from sqlalchemy import String, Integer,Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )

    username: Mapped[str | None] = mapped_column(String(50))
    first_name: Mapped[str | None] = mapped_column(String(50))

    language: Mapped[str | None] = mapped_column(String(5))  # ro / ru

    current_index: Mapped[int] = mapped_column(Integer, default=1)

    # 🔹 DATE TEST
    test_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[int | None] = mapped_column(Integer)

    # 🏢 COMPANIE
    company_name: Mapped[str | None] = mapped_column(String(100))
    
class Intrebare(Base):
    __tablename__ = "intrebari"

    id: Mapped[int] = mapped_column(primary_key=True)
    index: Mapped[int] = mapped_column(Integer, nullable=False)

    categorie: Mapped[str] = mapped_column(String(50))
    text: Mapped[str] = mapped_column(String)
    tip: Mapped[str] = mapped_column(String(10))
    language: Mapped[str] = mapped_column(String(5))



class Raspuns(Base):
    __tablename__ = "raspunsuri"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    intrebare_id: Mapped[int] = mapped_column(ForeignKey("intrebari.id"))
    valoare: Mapped[str] = mapped_column(String(20))


class Rezultat(Base):
    __tablename__ = "rezultate"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    scor: Mapped[int]
    nivel: Mapped[str] = mapped_column(String(20))  
