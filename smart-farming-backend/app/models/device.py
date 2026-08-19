import datetime
import secrets

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def generate_api_key():
    return secrets.token_hex(16)


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, default="esp32")  # esp32, esp32-cam, gateway
    api_key = Column(String, unique=True, default=generate_api_key)
    status = Column(String, default="offline")  # online, offline
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farm = relationship("Farm", back_populates="devices")
    readings = relationship("SensorReading", back_populates="device", cascade="all, delete-orphan")
    actuator_logs = relationship("ActuatorLog", back_populates="device", cascade="all, delete-orphan")
