import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    type = Column(String, nullable=False)  # low_moisture, high_temp, device_offline, ...
    message = Column(String, nullable=False)
    severity = Column(String, default="info")  # info, warning, critical
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farm = relationship("Farm", back_populates="alerts")
