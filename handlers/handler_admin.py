from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession
from yandex_disk import scan_and_notify
from database.engine import drop_db

from filters.admin_filters import IsAdmin

from keyboards.admin_kb import admin_kb
from keyboards.users_kb import start_kb
from keyboards.inline import get_callback_btns

from FSM_states.admin_FSM import router_admin_FSM

from database.orm_query import (
    orm_get_admins,
    orm_delete_admins,
    orm_delete_file_and_folders,
    orm_get_users,
    orm_delete_users,
    orm_delete_admins_by_id,
    orm_get_question,
    orm_delete_faqs_by_id

)

import asyncio


router_admin_handler = Router()
router_admin_handler.message.filter(IsAdmin())  # Фильтр проверяет наличие админа в базе
router_admin_handler.include_router(router_admin_FSM)


# Обработчик команды /start. (Входит в админ панель, если админ)
@router_admin_handler.message(Command("start"))
@router_admin_handler.message(Command("admin"))
async def cmd_start_admin(message: Message):
    welcome_text = "Вы вошли как Админ.\nВыбери что интересует:"
    await message.answer(welcome_text, reply_markup=admin_kb)


@router_admin_handler.callback_query(F.data.startswith("delete-admin"))
async def delete_admin(callback: CallbackQuery, session: AsyncSession):
    admin_id = callback.data.split("_")[-1]
    await orm_delete_admins_by_id(session=session, rem_id=admin_id)
    await callback.message.delete()
    await callback.message.answer("Администратор удален!")


@router_admin_handler.callback_query(F.data.startswith("delete-faqs"))
async def delete_faq(callback: CallbackQuery, session: AsyncSession):
    faq_id = callback.data.split("_")[-1]
    await orm_delete_faqs_by_id(session=session, faq_id=faq_id)
    await callback.message.delete()
    await callback.message.answer("Вопрос удален!")


# Обработчик команды /user (Выходит из админ панели)
@router_admin_handler.message(Command("user"))
async def cmd_start_user(message: Message):
    welcome_text = "Вы вышли из панели администратора.\nВыбери что интересует:"
    await message.answer(welcome_text, reply_markup=start_kb)


# Выводит список админов
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


# Выводит список админов
@router_admin_handler.message(F.text == "Обновить статистику")
async def run_yc_data(message: Message, session: AsyncSession):
    try:
        command = ["xvfb-run", "-a", "python3", "run.py"]
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            await message.answer(f'"output": {stdout.decode()}')
            return {"status": "success", "output": stdout.decode()}
        else:
            print(f'Ошибка:\n{stdout.decode()}')
            # raise HTTPException(status_code=500, detail=stderr.decode())
    except Exception as e:
        await message.answer(f'Ошибка:\n{e}')
        print(f'Ошибка:\n{e}')





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


@router_admin_handler.message(F.text == "Список вопросов")
async def get_FAQ(message: Message, session: AsyncSession):
    for faq in await orm_get_question(session=session):
        await message.answer(
            text=f"Вопрос: {faq.question}\n\nОтвет: {faq.answer}",
            reply_markup=get_callback_btns(
                btns={
                    "Удалить": f"delete-faqs_{faq.id}",
                    "Изменить": f"change-faqs_{faq.id}",
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
