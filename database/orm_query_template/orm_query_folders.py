from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Folder


# Добавление файла в базу данных из полученного списка файлов с Яндекс.Диска
async def orm_add_folder(session: AsyncSession, data: dict):
    # Проверяем, существует ли запись с таким же name и path
    query = select(Folder).where(
        Folder.name == data["name"], Folder.path == data["path"]
    )

    result = await session.execute(query)
    existing_file = result.scalars().first()

    if existing_file:
        return False

    # Если запись не найдена, добавляем её
    obj = Folder(name=data["name"], path=data["path"], img=data["img"])
    session.add(obj)
    await session.commit()


# Получение папки по имени
async def orm_get_folder_by_name(name, session: AsyncSession):
    query = select(Folder).where(Folder.name.ilike(f"%{name}%"))
    result = await session.execute(query)
    return result.scalars().all()


# Получение списка участников
async def orm_get_folder(session: AsyncSession):
    query = select(Folder)
    result = await session.execute(query)
    return result.scalars().all()


# Удаление таблицы с участниками
async def orm_delete_folder(session: AsyncSession):
    query = delete(Folder)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount
