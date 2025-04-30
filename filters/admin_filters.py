from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_get_admins_by_id, orm_get_users_by_id


class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        is_admin = await orm_get_admins_by_id(
            admin_id=message.from_user.id, session=session
        )
        if is_admin:
            return True
        else:
            return False


class IsUser(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        is_user = await orm_get_users_by_id(
            id=message.from_user.id, session=session
        )
        if is_user:
            return True
        else:
            return False