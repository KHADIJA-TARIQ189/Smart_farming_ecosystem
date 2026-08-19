import datetime
from typing import Optional

from pydantic import BaseModel


class SensorReadingIn(BaseModel):
    api_key: str  # device authenticates with its own api_key, not a user JWT
    sensor_type: str
    value: float
    unit: Optional[str] = None


class SensorReadingOut(BaseModel):
    id: int
    device_id: int
    sensor_type: str
    value: float
    unit: Optional[str]
    recorded_at: datetime.datetime

    class Config:
        from_attributes = True
