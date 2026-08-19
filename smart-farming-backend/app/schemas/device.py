import datetime
from typing import Optional

from pydantic import BaseModel


class DeviceCreate(BaseModel):
    name: str
    type: str = "esp32"


class DeviceOut(BaseModel):
    id: int
    farm_id: int
    name: str
    type: str
    api_key: str
    status: str
    last_seen: Optional[datetime.datetime]
    created_at: datetime.datetime

    class Config:
        from_attributes = True
