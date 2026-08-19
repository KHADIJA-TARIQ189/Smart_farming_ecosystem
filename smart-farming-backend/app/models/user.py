import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="farmer")  # farmer, admin
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farms = relationship("Farm", back_populates="owner", cascade="all, delete-orphan")
