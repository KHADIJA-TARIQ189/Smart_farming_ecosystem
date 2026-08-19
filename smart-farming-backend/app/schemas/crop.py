import datetime
from typing import Optional

from pydantic import BaseModel


class CropCreate(BaseModel):
    crop_type: str
    zone: Optional[str] = None
    planted_date: Optional[datetime.datetime] = None


class CropOut(BaseModel):
    id: int
    farm_id: int
    crop_type: str
    zone: Optional[str]
    planted_date: Optional[datetime.datetime]
    status: str

    class Config:
        from_attributes = True


class CropProfileOut(BaseModel):
    crop_type: str
    ideal_moisture_min: Optional[float]
    ideal_moisture_max: Optional[float]
    ideal_temp_min: Optional[float]
    ideal_temp_max: Optional[float]
    ideal_humidity_min: Optional[float]
    ideal_humidity_max: Optional[float]

    class Config:
        from_attributes = True
