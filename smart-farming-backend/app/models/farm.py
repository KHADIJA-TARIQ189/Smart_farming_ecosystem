import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="farms")
    devices = relationship("Device", back_populates="farm", cascade="all, delete-orphan")
    crops = relationship("Crop", back_populates="farm", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="farm", cascade="all, delete-orphan")
