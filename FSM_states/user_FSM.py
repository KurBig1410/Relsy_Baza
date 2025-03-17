from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from database.orm_query import orm_get_file_by_name, orm_get_folder_by_name
from sqlalchemy.ext.asyncio import AsyncSession

router_user_FSM = Router()


# Машина состояний для поиска файлов
class GetFile(StatesGroup):
    name = State()


@router_user_FSM.message(F.text == "Поиск файлов в Яндекс диске")
async def search_files(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer("Окей, введи название файла")
    await state.set_state(GetFile.name)


@router_user_FSM.message(GetFile.name, F.text)
async def get_name_files(message: Message, state: FSMContext, session: AsyncSession):
    search_query = message.text.strip()
    await message.answer(f"Окей, ищу файл с названием {search_query}")

    try:
        # Выполняем поиск файлов
        found_files = await orm_get_file_by_name(name=search_query, session=session)

        # Если файлы не найдены
        if not found_files:
            await message.answer("Файлы с таким названием не найдены на ЯндексДиске.")
        else:
            # Если файлы найдены, отправляем их пользователю
            for file in found_files:
                file_name = file.name
                download_path = file.download_path
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="Скачать файл", url=download_path)]
                    ]
                )
                await message.answer_photo(
                    photo=file.img,
                    caption=f"Файл найден: {file_name}\nДля скачивания нажмите на кнопку ниже.",
                    reply_markup=keyboard,
                )
    except Exception as e:
        # Обрабатываем ошибки
        await message.answer(f"Ссылка на файл:\n{file.img}")
        await message.answer(f"Произошла ошибка при поиске файла:\n{e}")
    finally:
        # Очистка состояния в любом случае
        await state.clear()


# Машина состояний для поиска папок
class SearchFolder(StatesGroup):
    name = State()


@router_user_FSM.message(F.text == "Поиск папок в Яндекс диске")
async def search_folders(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer("Окей, введи название папки")
    await state.set_state(SearchFolder.name)


@router_user_FSM.message(SearchFolder.name, F.text)
async def get_name_folders(message: Message, state: FSMContext, session: AsyncSession):
    search_query = message.text.strip()
    await message.answer(f"Окей, ищу папку с названием {search_query}")

    try:
        for folder in await orm_get_folder_by_name(name=search_query, session=session):
            folder_name = folder.name
            path = folder.path
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Перейти к папке", url=path)]
                ]
            )
            await message.answer_photo(
                photo=folder.img,
                caption=f"Папка найдена: {folder_name}\nДля перехода нажмите на кнопку ниже.",
                reply_markup=keyboard,
            )
    except Exception as e:
        await message.answer(
            f"Папка с таким названием не найдена на Яндекс.Диске.\nОшибка: {e}"
        )
    await state.clear()
