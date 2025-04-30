from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from database.models import AdminList


# Добавление админа
async def orm_add_admin(session: AsyncSession, data: dict):
    obj = AdminList(name=data["name"], id=data["admin_id"])
    session.add(obj)
    await session.commit()


# Изменение админа
async def orm_change_admin(session: AsyncSession, adm_id, data: dict):
    # Проверяем, существует ли запись с указанным adm_id
    existing_admin = await session.get(AdminList, adm_id)
    if not existing_admin:
        print(f"Админ с id {adm_id} не найден.")
        return 0  # Возвращаем 0, если запись не найдена
    # Дальше выполняем обновление, если запись существует
    admin_name = data["name"]
    query = update(AdminList).where(AdminList.id == int(adm_id)).values(name=admin_name)
    result = await session.execute(query)
    affected_rows = result.rowcount
    print(f"Количество обновлённых строк: {affected_rows}")
    await session.commit()
    return affected_rows


# Удаление админа по id
async def orm_delete_admins_by_id(session: AsyncSession, rem_id):
    query = delete(AdminList).where(AdminList.id == int(rem_id))
    result = await session.execute(query)
    await session.commit()
    return result.rowcount


# Получение админа по id и имени
async def orm_get_admins_by_id_and_name(admin_id, admin_name, session: AsyncSession):
    query = select(AdminList).where(
        AdminList.id == admin_id, AdminList.name == admin_name
    )
    print(f"Есть софпадение \nИмя:{admin_name}\nID{admin_id}")
    result = await session.execute(query)
    return result.scalars().all()


# Получение админа по id
async def orm_get_admins_by_id(admin_id, session: AsyncSession):
    query = select(AdminList).where(AdminList.id == admin_id)
    result = await session.execute(query)
    return result.scalars().all()


# Получение списка администраторов
async def orm_get_admins(session: AsyncSession):
    query = select(AdminList)
    result = await session.execute(query)
    return result.scalars().all()


# Удаление таблицы с админами
async def orm_delete_admins(session: AsyncSession):
    query = delete(AdminList)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount
