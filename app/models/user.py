from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func, ForeignKey
from app.config.database import Base
from sqlalchemy.orm import mapped_column, relationship


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

    tokens = relationship("UserToken", back_populates="user")

    def get_context_string(self, context: str):
        password_last_6 = self.password[-6:] if self.password else "000000"
        updated_time = (
            self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            if self.updated_at else datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        )
        return f"{context}{password_last_6}{updated_time}"


class UserToken(Base):
    __tablename__ = 'user_token'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(ForeignKey("users.id"))
    access_key = Column(String(250), index=True, nullable=True, default=None)
    refresh_key = Column(String(250), index=True, nullable=True, default=None)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="tokens")
