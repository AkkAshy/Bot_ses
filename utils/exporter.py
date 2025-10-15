from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from database.db import get_all_data, backup_db
from database.models import UserData
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

def export_to_excel() -> str:
    """Создает красиво оформленный Excel-файл и возвращает путь"""
    backup_db()
    data = get_all_data()
    
    if not data:
        logger.warning("No data to export")
        return None
    
    # Создаем книгу и лист
    wb = Workbook()
    ws = wb.active
    ws.title = "Данные учреждений"
    
    # Русские заголовки (как в ТЗ)
    headers = [
        'ID', 'Telegram ID', 'ФИО', 'Username', 'Телефон', 'Тип', 
        'Название', 'Адрес', 'Ориентир', 'Широта', 'Долгота', 
        'Фото', 'Дата создания'
    ]
    
    # Добавляем заголовки
    ws.append(headers)
    
    # Стили для заголовков
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="3673A5", end_color="3673A5", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    
    # Форматируем заголовки
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.value = headers[col-1]
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border
    
    # Заполняем данными
    for row_idx, record in enumerate(data, start=2):
        ws.append([
            record.id,
            record.telegram_id,
            record.full_name or '',
            record.username or '',
            record.phone_number or '',
            record.institution_type or '',
            record.institution_name or '',
            record.address or '',
            record.landmark or '',
            f"{record.latitude:.4f}" if record.latitude else '',
            f"{record.longitude:.4f}" if record.longitude else '',
            os.path.basename(record.photo_path) if record.photo_path else 'Нет',
            record.created_at.strftime('%d.%m.%Y %H:%M') if record.created_at else ''
        ])
        
        # Форматируем строку данных
        for col in range(1, 14):
            cell = ws.cell(row=row_idx, column=col)
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            cell.border = border
    
    # Автоподгонка ширины колонок
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 20)  # Макс 20 символов
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Высота строк
    for row in ws.rows:
        ws.row_dimensions[row[0].row].height = 20
    
    # Имя файла с датой
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    file_path = f'data_{timestamp}.xlsx'
    wb.save(file_path)
    
    logger.info(f"Exported {len(data)} records to {file_path}")
    return file_path

def export_to_word() -> str:
    """Экспорт в Word (оставляем как было, но с photo_path)"""
    backup_db()
    data = get_all_data()
    if not data:
        return None
        
    from docx import Document
    from docx.shared import Inches
    
    doc = Document()
    table = doc.add_table(rows=1, cols=13)
    table.style = 'Table Grid'
    
    headers = ['ID', 'Telegram ID', 'ФИО', 'Username', 'Телефон', 'Тип', 'Название', 
               'Адрес', 'Ориентир', 'Широта', 'Долгота', 'Фото', 'Дата']
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
    
    for row in data:
        row_cells = table.add_row().cells
        row_cells[0].text = str(row.id)
        row_cells[1].text = str(row.telegram_id)
        row_cells[2].text = row.full_name or ''
        row_cells[3].text = row.username or ''
        row_cells[4].text = row.phone_number or ''
        row_cells[5].text = row.institution_type or ''
        row_cells[6].text = row.institution_name or ''
        row_cells[7].text = row.address or ''
        row_cells[8].text = row.landmark or ''
        row_cells[9].text = str(row.latitude) if row.latitude else ''
        row_cells[10].text = str(row.longitude) if row.longitude else ''
        row_cells[11].text = os.path.basename(row.photo_path) if row.photo_path else 'Нет'
        row_cells[12].text = row.created_at.strftime('%d.%m.%Y %H:%M') if row.created_at else ''
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    file_path = f'data_word_{timestamp}.docx'
    doc.save(file_path)
    logger.info(f"Exported {len(data)} records to Word")
    return file_path