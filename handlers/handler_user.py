from aiogram.fsm.state import StatesGroup, State # noqa: F401
from aiogram import F, Router
from aiogram.fsm.context import FSMContext  # noqa: F401
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, WebAppInfo # noqa: F401
from FSM_states.user_FSM import router_user_FSM
from aiogram.filters import Command
from keyboards.users_kb import start_kb
from filters.admin_filters import IsUser # noqa: F401
from keyboards.inline import get_callback_btns
from database.orm_query import orm_get_question
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import FAQ


router_user_handler = Router()
router_user_handler.include_router(router_user_FSM)
user_answers = {}  # user_id: message_id

# Обработчик команды /start
# Сработает, если обычный пользователь
@router_user_handler.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = "Выбери что интересует:"
    await message.answer(welcome_text, reply_markup=start_kb)

@router_user_handler.message(F.text == "Рейтинг сети студий")
# async def cmd_static(message: Message):
#     welcome_text = "https://kurbig1410.github.io/filial-stats-vue/"
#     await message.answer(welcome_text)


async def send_stats(message: Message):
    kb = InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Открыть статистику", 
                    web_app=WebAppInfo(url="https://kurbig1410.github.io/filial-stats-vue/")
                )
            ]
        ],
    )
    await message.answer(
        "Нажми кнопку ниже, чтобы открыть статистику:", reply_markup=kb
    )



@router_user_handler.message(F.text == "Часто задаваемые вопросы")
async def show_faq(message: Message, session: AsyncSession):
    faq_list = await orm_get_question(session=session)
    for faq in faq_list:
        await message.answer(
            text=f"❓ {faq.question}",
            reply_markup=get_callback_btns(
                btns={
                    "Ответ": f"answer_{faq.id}"  # Лучше передавать ID, не сам ответ
                }
            ),
        )





@router_user_handler.callback_query(F.data.startswith("answer"))
async def show_answer(callback: CallbackQuery, session: AsyncSession):
    faq_id = callback.data.split("_")[-1]
    query = select(FAQ).where(FAQ.id == faq_id)
    result = await session.execute(query)
    faq = result.scalar_one_or_none()
    # await callback.message.answer(f'{query}\n\n\n{result}\n\n\n{faq.answer}\n\n\n{faq.question}')
    if not faq:
        await callback.message.answer("Ответ не найден 😕")
        return await callback.answer()

    user_id = callback.from_user.id

    # Удаляем старый ответ, если он был
    if user_id in user_answers:
        try:
            await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=user_answers[user_id])
        except Exception as e:
            print(f"Ошибка при удалении предыдущего сообщения: {e}")

    # Отправляем новый ответ
    sent = await callback.message.answer(f"📌 Ответ:\n{faq.answer}")

    # Сохраняем ID нового сообщения
    user_answers[user_id] = sent.message_id

    await callback.answer()
