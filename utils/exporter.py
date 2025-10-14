from openpyxl import Workbook
from docx import Document
from docx.shared import Inches
from database.db import get_all_data, backup_db
import logging

logger = logging.getLogger(__name__)

def export_to_excel() -> str:
    backup_db()
    data = get_all_data()
    wb = Workbook()
    ws = wb.active
    headers = ['id', 'telegram_id', 'full_name', 'username', 'phone_number', 'institution_type', 
               'institution_name', 'address', 'landmark', 'latitude', 'longitude', 'created_at']
    ws.append(headers)
    
    for row in data:
        ws.append([row.id, row.telegram_id, row.full_name, row.username, row.phone_number, row.institution_type,
                   row.institution_name, row.address, row.landmark, row.latitude, row.longitude, row.created_at])
    
    file_path = 'data.xlsx'
    wb.save(file_path)
    logger.info("Exported to Excel")
    return file_path

def export_to_word() -> str:
    backup_db()
    data = get_all_data()
    doc = Document()
    table = doc.add_table(rows=1, cols=12)
    table.style = 'Table Grid'
    
    headers = ['ID', 'Telegram ID', 'Full Name', 'Username', 'Phone', 'Type', 'Name', 'Address', 'Landmark', 'Lat', 'Lon', 'Created']
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
    
    for row in data:
        row_cells = table.add_row().cells
        row_cells[0].text = str(row.id)
        row_cells[1].text = str(row.telegram_id)
        row_cells[2].text = row.full_name
        row_cells[3].text = row.username
        row_cells[4].text = row.phone_number
        row_cells[5].text = row.institution_type
        row_cells[6].text = row.institution_name
        row_cells[7].text = row.address
        row_cells[8].text = row.landmark
        row_cells[9].text = str(row.latitude)
        row_cells[10].text = str(row.longitude)
        row_cells[11].text = str(row.created_at)
    
    file_path = 'data.docx'
    doc.save(file_path)
    logger.info("Exported to Word")
    return file_path