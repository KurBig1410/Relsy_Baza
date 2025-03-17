from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from FSM_states.user_FSM import router_user_FSM
from aiogram.filters import Command
from keyboards.users_kb import start_kb
from filters.admin_filters import IsUser

router_user_handler = Router()
router_user_handler.include_router(router_user_FSM)


# Обработчик команды /start
# Сработает, если обычный пользователь
@router_user_handler.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = "Выбери что интересует:"
    await message.answer(welcome_text, reply_markup=start_kb)
