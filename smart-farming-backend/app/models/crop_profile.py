from sqlalchemy import Column, Integer, String, Float

from app.database import Base


class CropProfile(Base):
    __tablename__ = "crop_profiles"

    id = Column(Integer, primary_key=True, index=True)
    crop_type = Column(String, unique=True, nullable=False)  # e.g. "wheat", "tomato", "rice"
    ideal_moisture_min = Column(Float, nullable=True)
    ideal_moisture_max = Column(Float, nullable=True)
    ideal_temp_min = Column(Float, nullable=True)
    ideal_temp_max = Column(Float, nullable=True)
    ideal_humidity_min = Column(Float, nullable=True)
    ideal_humidity_max = Column(Float, nullable=True)
