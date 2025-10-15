from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для контакта
contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Отправить номер телефона", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Клавиатура для типа учреждения
institution_type_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Школа")],
        [KeyboardButton(text="Техникум / Колледж")],
        [KeyboardButton(text="Университет")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Клавиатура для геолокации
location_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Клавиатура для подтверждения
confirmation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Подтвердить"), KeyboardButton(text="🔄 Изменить")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)


main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Добавить учреждение")],
        [KeyboardButton(text="👁 Посмотреть мои данные")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False  # Постоянное меню
)


# АДМИН-КЛАВИАТУРА
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Экспорт Excel")],
        [KeyboardButton(text="📝  Word")],
        [KeyboardButton(text="📈 Статистика")],
        [KeyboardButton(text="🔙 В главное меню")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Кнопка возврата в админ-панель
back_to_admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 Админ-панель")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Клавиатура для фото (БЫЛА ПРОПУЩЕНА!)
photo_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏭ Пропустить")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)