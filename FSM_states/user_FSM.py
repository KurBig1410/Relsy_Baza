from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, ReplyKeyboardMarkup

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_file_by_name, orm_get_folder_by_name
from database.orm_query_template.orm_query_admin.orm_adm_FAQ import orm_get_category_by_department, orm_get_question, orm_get_question_by_category
from keyboards.inline import get_callback_btns
from keyboards.users_kb import department_kb


router_user_FSM = Router()
user_answers = {}  # user_id: message_id
del_kb = ReplyKeyboardMarkup()
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


# Машина состояний для поиска файлов
class FAQ(StatesGroup):
    department = State()
    category = State()
    name = State()


@router_user_FSM.message(F.text == "Часто задаваемые вопросы")
async def faq_start(message: Message, state: FSMContext):
    await message.answer("Выбери отдел", reply_markup=department_kb)
    await state.set_state(FAQ.department)


@router_user_FSM.message(FAQ.department, F.text)
async def faq_search_department(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer("Выбери категорию", reply_markup=del_kb)
    department=message.text
    faq_category = await orm_get_category_by_department(department=department, session=session)
    for faq in faq_category:
        await message.answer(
            text=f"❓ {faq.category}",
            reply_markup=get_callback_btns(
                btns={"Вопросы по категории": f"faq_{faq.category}"}  # Лучше передавать ID, не сам ответ
            ),
        )
    await state.set_state(FAQ.category)


@router_user_FSM.callback_query(F.data.startswith("faq"))
async def show_faq(callback: CallbackQuery, session: AsyncSession):
    category = callback.data.split("_")[-1]
    faq_list = await orm_get_question_by_category(category=category, session=session)
    for faq in faq_list:
        await callback.message.answer(
            text=f"❓ {faq.question}",
            reply_markup=get_callback_btns(
                btns={"Ответ": f"answer_{faq.id}"}  # Лучше передавать ID, не сам ответ
            ),
        )
    user_id = callback.from_user.id
    if user_id in user_answers:
        try:
            await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=user_answers[user_id])
        except Exception as e:
            print(f"Ошибка при удалении предыдущего сообщения: {e}")
