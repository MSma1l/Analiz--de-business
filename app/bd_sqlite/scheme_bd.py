import sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
import asyncio
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, ForeignKey,BigInteger

engine = create_async_engine(utl='sqlite+aiosqlite:///Bazadedate.sqlite3')
async_session = async_sessionmaker(engine)

class Base (AsyncAttrs,DeclarativeBase):
    pass

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print ("Create cu succes tabelele")
    
if __name___ == '__main__':
    asyncio.run(async_main())