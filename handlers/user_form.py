from aiogram import Router, F
from aiogram.types import Message, Contact, Location, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.form import Form  # ← ГЛАВНОЕ! СОСТОЯНИЯ FSM
from keyboards.reply import (
    contact_keyboard, institution_type_keyboard, location_keyboard, 
    confirmation_keyboard, photo_keyboard, main_menu_keyboard,
    admin_keyboard, back_to_admin_keyboard
)
from database.db import save_data, get_user_data, can_add_data
from database.models import UserData
from datetime import timedelta, datetime
import logging
import os

logger = logging.getLogger(__name__)
router = Router()

from config import ADMINS

@router.message(F.text == '/start', F.from_user.id.in_(ADMINS))
async def admin_start_handler(message: Message):
    """Админ заходит — показывает админ-клавиатуру"""
    await message.answer(
        "👑 **Панель администратора СЭС**\n"
        "Выберите действие:"
    )
    await message.answer("Админ-меню:", reply_markup=admin_keyboard)

@router.message(F.text == "📝 Добавить учреждение")
async def add_institution_handler(message: Message, state: FSMContext):
    # Проверяем, можно ли добавлять
    if not can_add_data(message.from_user.id):
        await message.answer("Вы уже отправляли данные недавно. Подождите 24 часа перед добавлением новых.")
        await message.answer("Вернитесь в меню:", reply_markup=main_menu_keyboard)
        return
    
    # Если можно — запускаем процесс
    await message.answer("Давайте добавим учреждение. Сначала поделитесь номером телефона.", reply_markup=contact_keyboard)
    await state.set_state(Form.waiting_for_contact)

@router.message(F.text == "👁 Посмотреть мои данные")
async def view_my_data_message(message: Message):
    user_data = get_user_data(message.from_user.id)
    if user_data:
        summary = (
            f"Ваши данные:\n"
            f"Тип: {user_data.institution_type}\n"
            f"Название: {user_data.institution_name}\n"
            f"Адрес: {user_data.address}\n"
            f"Ориентир: {user_data.landmark}\n"
            f"Координаты: {user_data.latitude}, {user_data.longitude}\n"
            f"Номер: {user_data.phone_number}\n"
            f"Фото: {'отправлено' if user_data.photo_path else 'не отправлено'}\n"
            f"Дата: {user_data.created_at}"
        )
        await message.answer(summary, reply_markup=main_menu_keyboard)
        # Отправляем фото, если есть (bot автоматически доступен в message)
        if user_data.photo_path and os.path.exists(user_data.photo_path):
            await message.answer_photo(FSInputFile(user_data.photo_path))
    else:
        await message.answer("Данные не найдены. Добавьте их сначала.", reply_markup=main_menu_keyboard)

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
    await message.answer("Введите название учреждения (например, 'Школа №12').", reply_markup=None)
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
    await message.answer("Можете отправить фото местоположения (необязательно) или пропустить.", reply_markup=photo_keyboard)
    await state.set_state(Form.waiting_for_photo)

@router.message(Form.waiting_for_photo, F.text == "⏭ Пропустить")
async def skip_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    summary = (
        "Проверьте, верно ли всё указано:\n"
        f"Тип: {data['institution_type']}\n"
        f"Название: {data['institution_name']}\n"
        f"Адрес: {data['address']}\n"
        f"Ориентир: {data['landmark']}\n"
        f"Координаты: {data['latitude']}, {data['longitude']}\n"
        f"Номер: {data['phone_number']}\n"
        f"Фото: не отправлено"
    )
    await message.answer(summary, reply_markup=confirmation_keyboard)
    await state.set_state(Form.confirmation)

@router.message(Form.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    try:
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_path = f"photos/{message.from_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        await message.bot.download_file(file_info.file_path, file_path)
        
        data = await state.get_data()
        data['photo_path'] = file_path
        await state.set_data(data)
        
        summary = (
            "Проверьте, верно ли всё указано:\n"
            f"Тип: {data['institution_type']}\n"
            f"Название: {data['institution_name']}\n"
            f"Адрес: {data['address']}\n"
            f"Ориентир: {data['landmark']}\n"
            f"Координаты: {data['latitude']}, {data['longitude']}\n"
            f"Номер: {data['phone_number']}\n"
            f"Фото: отправлено"
        )
        await message.answer(summary, reply_markup=confirmation_keyboard)
        await state.set_state(Form.confirmation)
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await message.answer("Ошибка при загрузке фото. Попробуйте еще раз или пропустите.")
        await message.answer("Отправьте фото или пропустите.", reply_markup=photo_keyboard)

@router.message(Form.confirmation, F.text == "✅ Подтвердить")
async def confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    if save_data(data):
        await message.answer("Спасибо! Ваши данные успешно отправлены.")
        # Inline для быстрого просмотра
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👁  данные", callback_data="view_my_data")]
        ])
        await message.answer("Если хотите убедиться, нажмите ниже.", reply_markup=inline_kb)
        # Главное меню
        await message.answer("Что дальше?", reply_markup=main_menu_keyboard)
    else:
        await message.answer("Данные не сохранены: вы уже отправляли недавно. Подождите 24 часа.")
        await message.answer("Вернитесь в меню:", reply_markup=main_menu_keyboard)
    await state.clear()

@router.message(Form.confirmation, F.text == "🔄 Изменить")
async def change(message: Message, state: FSMContext):
    await message.answer("Давайте начнем заново с типа учреждения.", reply_markup=institution_type_keyboard)
    await state.set_state(Form.waiting_for_institution_type)

@router.callback_query(F.data == "view_my_data")
async def view_my_data_callback(callback_query: CallbackQuery):
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
            f"Фото: {'отправлено' if user_data.photo_path else 'не отправлено'}\n"
            f"Дата: {user_data.created_at}"
        )
        await callback_query.message.answer(summary)
        if user_data.photo_path and os.path.exists(user_data.photo_path):
            await callback_query.message.answer_photo(FSInputFile(user_data.photo_path))
    else:
        await callback_query.message.answer("Данные не найдены.")
    await callback_query.answer()
    # После просмотра — главное меню
    await callback_query.message.answer("Вернитесь в меню:", reply_markup=main_menu_keyboard)

# Обработка ошибок
@router.message()
async def error_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        logger.error(f"Error in state {current_state}: {message.text}")
        await message.answer("Произошла ошибка. Давайте начнем заново.")
        await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard)


# Админ может вернуться в панель из главного меню
@router.message(F.text == "🏠 Админ-панель")
async def user_to_admin(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer("👑 Панель администратора:", reply_markup=admin_keyboard)
    else:
        await message.answer("❌ Доступ только для админов.", reply_markup=main_menu_keyboard)