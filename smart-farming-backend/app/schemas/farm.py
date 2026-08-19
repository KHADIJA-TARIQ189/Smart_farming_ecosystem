import datetime
from typing import Optional

from pydantic import BaseModel


class FarmCreate(BaseModel):
    name: str
    location: Optional[str] = None


class FarmOut(BaseModel):
    id: int
    owner_id: int
    name: str
    location: Optional[str]
    created_at: datetime.datetime

    class Config:
        from_attributes = True
