from aiogram import BaseMiddleware  # noqa: F401
from aiogram.types import TelegramObject  # noqa: F401
from typing import Any, Callable, Dict, Awaitable  # noqa: F401
from sqlalchemy.ext.asyncio import async_sessionmaker


class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool


    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)


