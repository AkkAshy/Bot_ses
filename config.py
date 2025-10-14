import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Список админ-ID, добавь свои
ADMINS = [5111968766]  # Пример, замени на реальные Telegram ID

# Путь к БД
DB_PATH = 'ses_database.db'