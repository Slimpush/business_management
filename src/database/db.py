from typing import AsyncGenerator
from settings import settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=True,
    future=True,
    pool_size=50,
    max_overflow=100,
)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
