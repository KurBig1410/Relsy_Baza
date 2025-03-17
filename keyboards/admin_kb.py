from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Поиск файлов в Яндекс диске"),
            KeyboardButton(text="Поиск папок в Яндекс диске"),
            KeyboardButton(text="Сканирование ЯндексДиска"),
            KeyboardButton(text="Сбросить базу"),
        ],
        [
            KeyboardButton(text="Список пользователей"),
            KeyboardButton(text="Добавить пользователей"),
            KeyboardButton(text="Очистить базу пользователей"),
        ],
        [
            KeyboardButton(text="Список администраторов"),
            KeyboardButton(text="Добавить администратора"),
            KeyboardButton(text="Очистить базу администраторов"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вас интересует?",
)

del_kb = ReplyKeyboardRemove()


admin_kb_cansel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Назад"),
            KeyboardButton(text="Отмена"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вас интересует?",
)
