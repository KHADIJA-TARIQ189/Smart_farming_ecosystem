import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    sensor_type = Column(String, nullable=False)  # moisture, temperature, humidity, npk_n, npk_p, npk_k, light, ph
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    device = relationship("Device", back_populates="readings")
