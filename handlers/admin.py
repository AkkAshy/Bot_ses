from aiogram import Router, F
from aiogram.types import Message
from config import ADMINS
from utils.exporter import export_to_excel, export_to_word
from database.db import get_all_data
from keyboards.reply import admin_keyboard, main_menu_keyboard, back_to_admin_keyboard
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == '/start', F.from_user.id.in_(ADMINS))
async def admin_start_handler(message: Message):
    """Админ заходит — показывает админ-клавиатуру"""
    await message.answer(
        "👑 **Панель администратора СЭС**\n"
        "Выберите действие:"
    )
    await message.answer("Админ-меню:", reply_markup=admin_keyboard)

@router.message(F.text == "📊 Экспорт Excel")
async def export_excel_handler(message: Message):
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer("📊 Создаю Excel-отчет...")
    
    try:
        file_path = export_to_excel()
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                total = len(get_all_data())
                await message.answer_document(
                    file,
                    caption=f"✅ **Отчет СЭС (Excel)** | {total} учреждений\n"
                           f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                )
            os.remove(file_path)
            await message.answer("🔙 Вернуться в админ-панель?", reply_markup=back_to_admin_keyboard)
        else:
            await message.answer("❌ Нет данных для экспорта.", reply_markup=back_to_admin_keyboard)
            
    except Exception as e:
        logger.error(f"Excel export error: {e}")
        await message.answer("❌ Ошибка Excel.", reply_markup=back_to_admin_keyboard)

@router.message(F.text == "📝 Экспорт Word")
async def export_word_handler(message: Message):
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer("📝 Создаю Word-отчет...")
    
    try:
        from utils.exporter import export_to_word
        file_path = export_to_word()
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                total = len(get_all_data())
                await message.answer_document(
                    file,
                    caption=f"✅ **Отчет СЭС (Word)** | {total} учреждений\n"
                           f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                )
            os.remove(file_path)
            await message.answer("🔙 Вернуться в админ-панель?", reply_markup=back_to_admin_keyboard)
        else:
            await message.answer("❌ Нет данных для экспорта.", reply_markup=back_to_admin_keyboard)
            
    except Exception as e:
        logger.error(f"Word export error: {e}")
        await message.answer("❌ Ошибка Word.", reply_markup=back_to_admin_keyboard)

@router.message(F.text == "📈 Статистика")
async def stats_handler(message: Message):
    if message.from_user.id not in ADMINS:
        return
    
    data = get_all_data()
    total = len(data)
    
    if total == 0:
        await message.answer("📊 **Статистика**\n\n📈 Всего учреждений: 0", reply_markup=back_to_admin_keyboard)
        return
    
    # Подсчет по типам
    schools = len([d for d in data if d.institution_type == "Школа"])
    colleges = len([d for d in data if d.institution_type == "Техникум / Колледж"])
    universities = len([d for d in data if d.institution_type == "Университет"])
    
    # С фото / без
    with_photo = len([d for d in data if d.photo_path])
    
    stats_text = (
        f"📊 **Статистика СЭС**\n\n"
        f"🏫 **Всего учреждений:** {total}\n\n"
        f"📚 **По типам:**\n"
        f"• Школ: {schools}\n"
        f"• Техникумов: {colleges}\n"
        f"• Университетов: {universities}\n\n"
        f"📸 **Фото отправлено:** {with_photo} из {total}\n"
        f"💾 **Последняя запись:** {data[-1].created_at.strftime('%d.%m.%Y %H:%M') if data else '—'}"
    )
    
    await message.answer(stats_text, reply_markup=back_to_admin_keyboard)

@router.message(F.text == "🔙 В главное меню")
async def back_to_main_menu(message: Message):
    await message.answer("Переход в главное меню...", reply_markup=main_menu_keyboard)

@router.message(F.text == "🏠 Админ-панель")
async def back_to_admin(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer("👑 Панель администратора:", reply_markup=admin_keyboard)
    else:
        await message.answer("Доступ запрещен.", reply_markup=main_menu_keyboard)