from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User


# Добавление пользователя
async def orm_add_users(session: AsyncSession, data: dict):
    obj = User(id=data["id"], name=data["name"])
    session.add(obj)
    await session.commit()


# Изменение пользователя
async def orm_change_user(session: AsyncSession, us_id, data: dict):
    user_name = data["name"]
    query = update(User).where(User.id == int(us_id)).values(name=user_name)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount


# Получение пользователей по имени
async def orm_get_users_by_name(name, session: AsyncSession):
    query = select(User).where(User.name == name)
    result = await session.execute(query)
    return result.scalars().all()


# Получение пользователей по ID
async def orm_get_users_by_id(id, session: AsyncSession):
    query = select(User).where(User.id == id)
    result = await session.execute(query)
    return result.scalars().all()


# Удаление пользователя по id
async def orm_delete_users_by_id(session: AsyncSession, us_id):
    query = delete(User).where(User.id == int(us_id))
    result = await session.execute(query)
    await session.commit()
    return result.rowcount


# Получение списка пользователей
async def orm_get_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()


# Удаление таблицы с пользователями
async def orm_delete_users(session: AsyncSession):
    query = delete(User)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount
