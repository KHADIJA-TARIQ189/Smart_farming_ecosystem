import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ActuatorLog(Base):
    __tablename__ = "actuator_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    actuator_type = Column(String, nullable=False)  # pump, fan, light
    action = Column(String, nullable=False)  # on, off
    triggered_by = Column(String, default="user")  # user, system
    triggered_at = Column(DateTime, default=datetime.datetime.utcnow)

    device = relationship("Device", back_populates="actuator_logs")
