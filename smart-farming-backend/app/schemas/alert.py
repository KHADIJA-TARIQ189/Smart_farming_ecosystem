import datetime

from pydantic import BaseModel


class AlertOut(BaseModel):
    id: int
    farm_id: int
    type: str
    message: str
    severity: str
    resolved: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True
