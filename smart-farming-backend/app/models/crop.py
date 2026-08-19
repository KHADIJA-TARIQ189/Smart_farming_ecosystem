import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    crop_type = Column(String, nullable=False)  # must match a CropProfile.crop_type
    zone = Column(String, nullable=True)
    planted_date = Column(DateTime, nullable=True)
    status = Column(String, default="growing")  # growing, harvested

    farm = relationship("Farm", back_populates="crops")
