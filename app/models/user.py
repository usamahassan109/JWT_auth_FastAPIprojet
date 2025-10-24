from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from app.config.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(100))
    is_active = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True, default=None)
    updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.now)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    def get_context_string(self, context: str):
       return f"{context}{self.password[-6]}{self.updated_at.strftime('%Y-%m-%d %H:%M:%S')}:".strip() #.strip unnecessary ha
'''

def get_context_string(self, context: str) -> str:
    """Aapke desired format mein"""
    password_last_6 = self.password[-6:] if self.password else "000000"
    updated_time = self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    return f"{context}{password_last_6}{updated_time}"

'''
