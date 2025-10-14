from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для контакта
contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Отправить номер телефона", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Клавиатура для типа учреждения
institution_type_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Школа")],
        [KeyboardButton(text="Техникум / Колледж")],
        [KeyboardButton(text="Университет")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Клавиатура для геолокации
location_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Клавиатура для подтверждения
confirmation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Подтвердить"), KeyboardButton(text="🔄 Изменить")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)