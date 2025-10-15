from aiogram import Router, F
from aiogram.types import Message, FSInputFile  # ← ДОБАВИЛИ ИМПОРТ!
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
    await message.answer("👑 **Панель администратора СЭС**")
    await message.answer("Выберите действие:", reply_markup=admin_keyboard)

# 🔥 ИСПРАВЛЕННЫЙ ОБРАБОТЧИК EXCEL
@router.message(F.text.contains("Excel"))
async def export_excel_handler(message: Message):
    logger.info(f"🎉 EXCEL НАЖАТА: '{message.text}'!")
    await message.answer("📊 Создаю Excel-отчёт...")
    
    file_path = export_to_excel()
    
    if file_path and os.path.exists(file_path):
        # ✅ ИСПОЛЬЗУЕМ FSInputFile вместо open()
        document = FSInputFile(file_path)
        total = len(get_all_data())
        
        await message.answer_document(
            document,
            caption=f"✅ **Отчёт СЭС** | {total} учреждений"
        )
        
        # Удаляем файл после отправки
        os.remove(file_path)
        logger.info(f"Excel файл отправлен и удален: {file_path}")
    else:
        await message.answer("❌ Нет данных для экспорта")
    
    await message.answer("✅ Готово!", reply_markup=back_to_admin_keyboard)

# 📝 ОБРАБОТЧИК WORD (тоже исправляем)
@router.message(F.text.contains("Word"))
async def export_word_handler(message: Message):
    logger.info(f"📝 WORD НАЖАТА: '{message.text}'!")
    await message.answer("📝 Создаю Word-отчёт...")
    
    file_path = export_to_word()
    
    if file_path and os.path.exists(file_path):
        # ✅ ИСПОЛЬЗУЕМ FSInputFile
        document = FSInputFile(file_path)
        total = len(get_all_data())
        
        await message.answer_document(
            document,
            caption=f"✅ **Отчёт СЭС (Word)** | {total} учреждений"
        )
        
        os.remove(file_path)
        logger.info(f"Word файл отправлен и удален: {file_path}")
    else:
        await message.answer("❌ Нет данных для экспорта")
    
    await message.answer("✅ Готово!", reply_markup=back_to_admin_keyboard)

@router.message(F.text.contains("Статистика"))
async def stats_handler(message: Message):
    logger.info(f"📈 СТАТИСТИКА НАЖАТА: '{message.text}'!")
    data = get_all_data()
    total = len(data)
    
    # Подсчет по типам
    schools = sum(1 for d in data if d.institution_type == "Школа")
    colleges = sum(1 for d in data if d.institution_type == "Техникум / Колледж")
    universities = sum(1 for d in data if d.institution_type == "Университет")
    
    stats_text = (
        f"📊 **Статистика учреждений:**\n\n"
        f"🏫 Всего: {total}\n"
        f"📚 Школ: {schools}\n"
        f"🎓 Техникумов/Колледжей: {colleges}\n"
        f"🏛 Университетов: {universities}"
    )
    
    await message.answer(stats_text, reply_markup=back_to_admin_keyboard)

@router.message(F.text == "🔙 В главное меню")
async def back_to_main_menu(message: Message):
    await message.answer("Переход в главное меню...", reply_markup=main_menu_keyboard)

@router.message(F.text == "🏠 Админ-панель")
async def back_to_admin(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer("👑 Панель администратора:", reply_markup=admin_keyboard)