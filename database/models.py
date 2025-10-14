from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserData(Base):
    __tablename__ = 'user_data'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    full_name = Column(String)
    username = Column(String)
    phone_number = Column(String)
    institution_type = Column(String)
    institution_name = Column(String)
    address = Column(String)
    landmark = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)