from aiogram import Router
from aiogram import F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.admin_kb import admin_kb, admin_kb_cansel
from database.orm_query import orm_add_question, orm_add_admin, orm_add_users


router_admin_FSM = Router()


# Добавление администратора
class AddAdmins(StatesGroup):
    admin_id = State()
    name = State()

    texts = {
        "AddAdmins:admin_id": "Введи id заново",
        "AddAdmins:name": "Введи имя заново",
    }


@router_admin_FSM.message(StateFilter(AddAdmins), Command("Отмена"))
@router_admin_FSM.message(StateFilter(AddAdmins), F.text == "Отмена")
async def cancel_handler_admin(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действие отменено", reply_markup=admin_kb)


@router_admin_FSM.message(StateFilter(AddAdmins), Command("Назад"))
@router_admin_FSM.message(StateFilter(AddAdmins), F.text == "Назад")
async def back_step_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddAdmins.name:
        await message.answer(
            'Предидущего шага нет, или введите название товара или напишите "отмена"'
        )
        return
    previous = None
    for step in AddAdmins.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddAdmins.texts[previous.state]}"
            )
            return
        previous = step


@router_admin_FSM.message(F.text == "Добавить администратора")
async def add_admins(message: Message, state: FSMContext):
    await message.answer("Введи Telegram id", reply_markup=admin_kb_cansel)
    await state.set_state(AddAdmins.admin_id)


@router_admin_FSM.message(AddAdmins.admin_id, F.text)
async def add_admins_id(message: Message, state: FSMContext):
    await state.update_data(admin_id=int(message.text))
    await message.answer("Введи Имя и Фамилию", reply_markup=admin_kb_cansel)
    await state.set_state(AddAdmins.name)


@router_admin_FSM.message(AddAdmins.name, F.text)
async def add_admins_name(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(name=message.text)
    data = await state.get_data()
    try:
        await orm_add_admin(session=session, data=data)
        await message.answer(f"{data}")
        await message.answer("Ок, админ добавлен!", reply_markup=admin_kb)
        await state.clear()
    except Exception as e:
        await message.answer(f"Ошибка {str(e)}", reply_markup=admin_kb)
        await state.clear()


class AddUsers(StatesGroup):
    name = State()
    id = State()


@router_admin_FSM.message(F.text == "Добавить участников")
async def add_users_name(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отмена"),
            ],
        ],
        resize_keyboard=True,
    )
    await message.answer("Введи имя участника", reply_markup=keyboard)
    await state.set_state(AddUsers.name)


@router_admin_FSM.message(StateFilter(AddUsers), Command("Отмена"))
@router_admin_FSM.message(StateFilter(AddUsers), F.text == "Отмена")
async def cancel_handler_user(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действие отменено", reply_markup=admin_kb)


@router_admin_FSM.message(AddUsers.name, F.text)
async def add_users_id(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отмена"),
            ],
        ],
        resize_keyboard=True,
    )
    await state.update_data(name=message.text)
    await message.answer("Введи ID пользователя", reply_markup=keyboard)
    await state.set_state(AddUsers.id)


@router_admin_FSM.message(AddUsers.id, F.text)
async def save_users(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(id=message.text)
    data = await state.get_data()
    try:
        await orm_add_users(session=session, data=data)
        await state.clear()
        await message.answer("Пользователь успешно добавлен!", reply_markup=admin_kb)
    except Exception as e:
        await message.answer(f"Ошибка {str(e)}", reply_markup=admin_kb)
        await state.clear()


class AddQuestion(StatesGroup):
    id = State()
    department = State()
    category = State()
    question = State()
    answer = State()


@router_admin_FSM.message(F.text == "Добавить вопрос в FAQ")
async def add_id(message: Message, state: FSMContext):
    await message.answer("Введи id", reply_markup=admin_kb_cansel)
    await state.set_state(AddQuestion.id)


@router_admin_FSM.message(StateFilter(AddQuestion), Command("Отмена"))
@router_admin_FSM.message(StateFilter(AddQuestion), F.text == "Отмена")
async def cancel_faq(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действие отменено", reply_markup=admin_kb)


@router_admin_FSM.message(AddQuestion.id, F.text)
async def add_departament(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    await message.answer("Введи отдел", reply_markup=admin_kb_cansel)
    await state.set_state(AddQuestion.department)


@router_admin_FSM.message(AddQuestion.department, F.text)
async def add_category(message: Message, state: FSMContext):
    await state.update_data(departament=message.text)
    await message.answer("Введи категорию", reply_markup=admin_kb_cansel)
    await state.set_state(AddQuestion.category)


@router_admin_FSM.message(AddQuestion.category, F.text)
async def add_question(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Введи вопрос", reply_markup=admin_kb_cansel)
    await state.set_state(AddQuestion.question)


@router_admin_FSM.message(AddQuestion.question, F.text)
async def add_answer(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Введи ответ", reply_markup=admin_kb_cansel)
    await state.set_state(AddQuestion.answer)


@router_admin_FSM.message(AddQuestion.answer, F.text)
async def add_FAQ_save(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(answer=message.text)
    data = await state.get_data()
    try:
        await orm_add_question(session=session, data=data)
        await message.answer(f"{data}")
        await message.answer("Ок, вопрос и ответ добавлены", reply_markup=admin_kb)
        await state.clear()
    except Exception as e:
        await message.answer(f"Ошибка {str(e)}", reply_markup=admin_kb)
        await state.clear()
