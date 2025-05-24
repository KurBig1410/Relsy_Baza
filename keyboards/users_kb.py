from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            # KeyboardButton(text="Поиск файлов в Яндекс диске"),
            # KeyboardButton(text="Поиск папок в Яндекс диске"),
            KeyboardButton(text="Часто задаваемые вопросы"),
            KeyboardButton(text="Рейтинг сети студий"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вас интересует?",
)
department_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Развитие"),
            KeyboardButton(text="Запуск"),
        ]
    ],
)
del_kb = ReplyKeyboardRemove()