import os
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from .models import Base, UserData
from config import DB_PATH, DEBUG
from datetime import datetime, timedelta
import logging
import shutil

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

# Создаем папку для фото
PHOTOS_DIR = 'photos'
if not os.path.exists(PHOTOS_DIR):
    os.makedirs(PHOTOS_DIR)

# ✅ ПЕРЕСОЗДАЁМ БД ПРЯМО ЗДЕСЬ (ЕДИНСТВЕННЫЙ РАЗ!)
engine = create_engine(f'sqlite:///{DB_PATH}')
Base.metadata.drop_all(engine)  # Удаляем старую
Base.metadata.create_all(engine)  # Создаём новую с photo_path
print("✅ БАЗА ПЕРЕСОЗДАНА с photo_path!")  # Подтверждение
Session = sessionmaker(bind=engine)

def save_data(data: dict) -> bool:
    with Session() as session:
        last_entry = session.query(UserData).filter(
            UserData.telegram_id == data['telegram_id'],
            UserData.created_at > datetime.utcnow() - timedelta(hours=24)
        ).first()
        
        if last_entry:
            logger.warning(f"Duplicate entry attempt for user {data['telegram_id']}")
            return False
        
        new_entry = UserData(
            telegram_id=data['telegram_id'],
            full_name=data['full_name'],
            username=data['username'],
            phone_number=data['phone_number'],
            institution_type=data['institution_type'],
            institution_name=data['institution_name'],
            address=data['address'],
            landmark=data['landmark'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            photo_path=data.get('photo_path')
        )
        session.add(new_entry)
        session.commit()
        logger.info(f"Data saved for user {data['telegram_id']}")
        return True

def get_all_data() -> list:
    with Session() as session:
        return session.query(UserData).all()

def get_user_data(telegram_id: int) -> UserData:
    with Session() as session:
        return session.query(UserData).filter(UserData.telegram_id == telegram_id).order_by(UserData.created_at.desc()).first()

def backup_db():
    backup_path = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(DB_PATH, backup_path)
    logger.info(f"DB backed up to {backup_path}")

def can_add_data(telegram_id: int) -> bool:
    with Session() as session:
        last_entry = session.query(UserData).filter(
            UserData.telegram_id == telegram_id,
            UserData.created_at > datetime.utcnow() - timedelta(hours=24)
        ).first()
        return last_entry is None