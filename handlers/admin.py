from aiogram import Router, F
from aiogram.types import Message
from config import ADMINS
from utils.exporter import export_to_excel, export_to_word
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == '/export_excel')
async def export_excel_handler(message: Message):
    if message.from_user.id not in ADMINS:
        await message.answer("Доступ запрещен. Только для админов.")
        return
    try:
        file_path = export_to_excel()
        await message.answer_document(open(file_path, 'rb'))
    except Exception as e:
        logger.error(f"Error exporting Excel: {e}")
        await message.answer("Ошибка при экспорте Excel.")

@router.message(F.text == '/export_word')
async def export_word_handler(message: Message):
    if message.from_user.id not in ADMINS:
        await message.answer("Доступ запрещен. Только для админов.")
        return
    try:
        file_path = export_to_word()
        await message.answer_document(open(file_path, 'rb'))
    except Exception as e:
        logger.error(f"Error exporting Word: {e}")
        await message.answer("Ошибка при экспорте Word.")