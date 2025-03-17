from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession
from yandex_disk import scan_and_notify
from database.engine import drop_db

from filters.admin_filters import IsAdmin

from keyboards.admin_kb import admin_kb
from keyboards.inline import get_callback_btns

from FSM_states.admin_FSM import router_admin_FSM

from database.orm_query_template.orm_query_admin import (
    orm_get_admins,
    orm_delete_admins,
    orm_delete_file_and_folders
)
from database.orm_query_template.orm_query_user import (
    orm_get_users,
    orm_delete_users,
)


router_admin_handler = Router()
router_admin_handler.message.filter(IsAdmin())  # Фильтр проверяет наличие админа в базе
router_admin_handler.include_router(router_admin_FSM)


# Обработчик команды /start
# Сработает, если админ
@router_admin_handler.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = "Выбери что интересует:"
    await message.answer(welcome_text, reply_markup=admin_kb)


@router_admin_handler.message(F.text == "Список администраторов")
async def get_admins(message: Message, session: AsyncSession):
    for admin in await orm_get_admins(session=session):
        await message.answer(
            text=f"{admin.name}",
            reply_markup=get_callback_btns(
                btns={
                    "Удалить": f"delete-admin_{message.message_id}_{admin.id}",
                    "Изменить": f"change-admin_{admin.id}_{admin.id}",
                }
            ),
        )


@router_admin_handler.message(F.text == "Список пользователей")
async def get_user(message: Message, session: AsyncSession):
    for user in await orm_get_users(session=session):
        await message.answer(
            text=f"Имя: {user.name}",
            reply_markup=get_callback_btns(
                btns={
                    "Удалить": f"delete-user_{user.id}",
                    "Изменить": f"change-user_{user.id}",
                }
            ),
        )


# Удаление базы участников
@router_admin_handler.message(F.text == "Очистить базу пользователей")
async def delete_users(message: Message, session: AsyncSession):
    await orm_delete_users(session=session)
    try:
        await message.answer("База удалена")
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=admin_kb)


# Удаление базы админов
@router_admin_handler.message(F.text == "Очистить базу администраторов")
async def delete_admins(message: Message, session: AsyncSession):
    await orm_delete_admins(session=session)
    try:
        await message.answer("База удалена")
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=admin_kb)


@router_admin_handler.message(F.text == "Сканирование ЯндексДиска")
async def search_files(message: Message, session: AsyncSession):
    await message.answer("Окей, произвожу сканирование ЯндексДиска")
    try:
        await scan_and_notify(session=session)
        await message.answer("Сканирование завершено")
    except Exception as e:
        await message.answer(f"Ошибка сканирования: {e}")


@router_admin_handler.message(F.text == "Сбросить базу")
async def drop_database(message: Message, session: AsyncSession):
    await message.answer("Окей, сбрасываю базу данных")
    try:
        await orm_delete_file_and_folders(session=session)
        # await drop_db()
        await message.answer("База сброшена")
    except Exception as e:
        await message.answer(f"Ошибка сброса: {e}")
