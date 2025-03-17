from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import File


# Добавление файла в базу данных из полученного списка файлов с Яндекс.Диска
async def orm_add_file(session: AsyncSession, data: dict):
    # Проверяем, существует ли запись с таким же name и download_path
    query = select(File).where(
        File.name == data["name"],
        File.download_path == data["download_path"]
    )

    result = await session.execute(query)
    existing_file = result.scalars().first()

    if existing_file:
        return False
    
    # Если запись не найдена, добавляем её
    obj = File(name=data["name"], download_path=data["download_path"], img=data["img"])
    session.add(obj)
    await session.commit()


async def orm_change_file(session: AsyncSession, us_id, data: dict):
    user_name = data["name"]
    query = update(File).where(File.id == int(us_id)).values(name=user_name)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount


# Получение файла по имени с учётом нечувствительности к регистру и частичного совпадения
async def orm_get_file_by_name(name, session: AsyncSession):
    # Формируем запрос с использованием оператора ILIKE для поиска по подстроке, игнорируя регистр
    query = select(File).where(File.name.ilike(f"%{name}%"))
    result = await session.execute(query)
    return result.scalars().all()


# Удаление пользователя по id
async def orm_delete_file_by_id(session: AsyncSession, us_id):
    query = delete(File).where(File.id == int(us_id))
    result = await session.execute(query)
    await session.commit()
    return result.rowcount


# Получение списка участников
async def orm_get_file(session: AsyncSession):
    query = select(File)
    result = await session.execute(query)
    return result.scalars().all()


# Удаление таблицы с участниками
async def orm_delete_file(session: AsyncSession):
    query = delete(File)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount
