import datetime

from pydantic import BaseModel


class ActuatorControlIn(BaseModel):
    actuator_type: str  # pump, fan, light
    action: str  # on, off


class ActuatorLogOut(BaseModel):
    id: int
    device_id: int
    actuator_type: str
    action: str
    triggered_by: str
    triggered_at: datetime.datetime

    class Config:
        from_attributes = True
