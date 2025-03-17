from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Поиск файлов в Яндекс диске"),
            KeyboardButton(text="Поиск папок в Яндекс диске")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вас интересует?",
)

del_kb = ReplyKeyboardRemove()