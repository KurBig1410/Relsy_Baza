from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from database.models import File, Folder

# Удаление таблицы с файлами и папками
async def orm_delete_file_and_folders(session: AsyncSession):
    # Удаляем файлы
    result_file = await session.execute(delete(File))
    # Удаляем папки
    result_folder = await session.execute(delete(Folder))
    # Сохраняем изменения
    await session.commit()

    # Возвращаем общее количество удаленных строк
    return result_file.rowcount + result_folder.rowcount
