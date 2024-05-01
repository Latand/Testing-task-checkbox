from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import Config, load_config


from database.repo.requests import RequestsRepo


@lru_cache
def get_config() -> Config:
    return load_config()


@lru_cache
def get_session_pool():
    config = get_config()
    engine = create_async_engine(config.db.get_connection_string())
    session_pool = async_sessionmaker(engine, expire_on_commit=False)
    return session_pool


async def get_repository(session_pool: async_sessionmaker = Depends(get_session_pool)):
    async with session_pool() as session:
        yield RequestsRepo(session)
