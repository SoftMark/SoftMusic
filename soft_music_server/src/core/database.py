from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

ENGINE = create_async_engine("sql_path", echo=True)
SESSION_MAKER = async_sessionmaker(ENGINE, expire_on_commit=False)


async def get_session():
    async with SESSION_MAKER() as session:
        yield session


class Base(DeclarativeBase):
    pass