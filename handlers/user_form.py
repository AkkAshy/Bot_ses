from aiogram import Router, F
from aiogram.types import Message, Contact, Location, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.form import Form
from keyboards.reply import contact_keyboard, institution_type_keyboard, location_keyboard, confirmation_keyboard
from database.db import save_data, get_user_data
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == '/start')
async def start_handler(message: Message, state: FSMContext):
    await message.answer(
        "Здравствуйте! Этот бот собирает данные об образовательных учреждениях для СЭС.\n"
        "Пожалуйста, ответьте на несколько вопросов."
    )
    await message.answer("Сначала поделитесь номером телефона.", reply_markup=contact_keyboard)
    await state.set_state(Form.waiting_for_contact)

@router.message(Form.waiting_for_contact, F.contact)
async def process_contact(message: Message, state: FSMContext):
    contact: Contact = message.contact
    user = message.from_user
    data = {
        'telegram_id': user.id,
        'full_name': f"{user.first_name} {user.last_name or ''}".strip(),
        'username': f"@{user.username}" if user.username else None,
        'phone_number': contact.phone_number
    }
    await state.set_data(data)
    await message.answer("Спасибо! Теперь укажите тип учреждения.", reply_markup=institution_type_keyboard)
    await state.set_state(Form.waiting_for_institution_type)

@router.message(Form.waiting_for_institution_type, F.text.in_({"Школа", "Техникум / Колледж", "Университет"}))
async def process_institution_type(message: Message, state: FSMContext):
    data = await state.get_data()
    data['institution_type'] = message.text
    await state.set_data(data)
    await message.answer("Введите название учреждения.", reply_markup=None)  # Убираем клавиатуру
    await state.set_state(Form.waiting_for_institution_name)

@router.message(Form.waiting_for_institution_name, F.text)
async def process_institution_name(message: Message, state: FSMContext):
    data = await state.get_data()
    data['institution_name'] = message.text
    await state.set_data(data)
    await message.answer("Введите адрес учреждения (улица, дом, район и т.д.).")
    await state.set_state(Form.waiting_for_address)

@router.message(Form.waiting_for_address, F.text)
async def process_address(message: Message, state: FSMContext):
    data = await state.get_data()
    data['address'] = message.text
    await state.set_data(data)
    await message.answer("Введите ориентир (например, 'рядом с рынком').")
    await state.set_state(Form.waiting_for_landmark)

@router.message(Form.waiting_for_landmark, F.text)
async def process_landmark(message: Message, state: FSMContext):
    data = await state.get_data()
    data['landmark'] = message.text
    await state.set_data(data)
    await message.answer("Теперь отправьте геолокацию.", reply_markup=location_keyboard)
    await state.set_state(Form.waiting_for_location)

@router.message(Form.waiting_for_location, F.location)
async def process_location(message: Message, state: FSMContext):
    location: Location = message.location
    data = await state.get_data()
    data['latitude'] = location.latitude
    data['longitude'] = location.longitude
    await state.set_data(data)
    
    # Резюме
    summary = (
        "Проверьте, верно ли всё указано:\n"
        f"Тип: {data['institution_type']}\n"
        f"Название: {data['institution_name']}\n"
        f"Адрес: {data['address']}\n"
        f"Ориентир: {data['landmark']}\n"
        f"Координаты: {data['latitude']}, {data['longitude']}\n"
        f"Номер: {data['phone_number']}"
    )
    await message.answer(summary, reply_markup=confirmation_keyboard)
    await state.set_state(Form.confirmation)

@router.message(Form.confirmation, F.text == "✅ Подтвердить")
async def confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    if save_data(data):
        await message.answer("Спасибо! Ваши данные успешно отправлены.")
        
        # Инлайн-кнопка для просмотра
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Посмотреть мои данные", callback_data="view_my_data")]
        ])
        await message.answer("Если хотите убедиться, нажмите ниже.", reply_markup=inline_kb)
    else:
        await message.answer("Данные не сохранены: вы уже отправляли недавно. Подождите 24 часа.")
    await state.clear()

@router.message(Form.confirmation, F.text == "🔄 Изменить")
async def change(message: Message, state: FSMContext):
    await message.answer("Давайте начнем заново с типа учреждения.", reply_markup=institution_type_keyboard)
    await state.set_state(Form.waiting_for_institution_type)

@router.callback_query(F.data == "view_my_data")
async def view_my_data(callback_query):
    user_data = get_user_data(callback_query.from_user.id)
    if user_data:
        summary = (
            f"Ваши данные:\n"
            f"Тип: {user_data.institution_type}\n"
            f"Название: {user_data.institution_name}\n"
            f"Адрес: {user_data.address}\n"
            f"Ориентир: {user_data.landmark}\n"
            f"Координаты: {user_data.latitude}, {user_data.longitude}\n"
            f"Номер: {user_data.phone_number}\n"
            f"Дата: {user_data.created_at}"
        )
        await callback_query.message.answer(summary)
    else:
        await callback_query.message.answer("Данные не найдены.")
    await callback_query.answer()

# Обработка ошибок: если что-то сломалось, сброс
@router.message()
async def error_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        logger.error(f"Error in state {current_state}: {message.text}")
        await message.answer("Произошла ошибка. Давайте начнем заново.")
        await state.clear()
        await start_handler(message, state)