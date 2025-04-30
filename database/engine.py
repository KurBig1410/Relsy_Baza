import os
from sqlmodel.ext.asyncio.session import AsyncSession  # ✅ ВАЖНО
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from database.models import Base
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError("Переменная окружения DB_URL не установлена или пуста.")

engine = create_async_engine(db_url, echo=True)

session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)