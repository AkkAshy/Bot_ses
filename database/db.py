from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from .models import Base, UserData
from config import DB_PATH, DEBUG
from datetime import datetime, timedelta
import logging
import shutil  # Для бэкапа

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(f'sqlite:///{DB_PATH}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def save_data(data: dict) -> bool:
    with Session() as session:
        # Проверка дубликата: запись от этого user_id за последние 24 часа
        last_entry = session.query(UserData).filter(
            UserData.telegram_id == data['telegram_id'],
            UserData.created_at > datetime.utcnow() - timedelta(hours=24)
        ).first()
        
        if last_entry:
            logger.warning(f"Duplicate entry attempt for user {data['telegram_id']}")
            return False  # Не сохраняем
        
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
            longitude=data['longitude']
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