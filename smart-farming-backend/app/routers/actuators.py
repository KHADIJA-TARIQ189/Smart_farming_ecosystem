from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.actuator_log import ActuatorLog
from app.models.device import Device
from app.models.user import User
from app.schemas.actuator_log import ActuatorControlIn, ActuatorLogOut

router = APIRouter(prefix="/actuators", tags=["actuators"])


@router.post("/{device_id}/control", response_model=ActuatorLogOut, status_code=201)
def control_actuator(
    device_id: int,
    payload: ActuatorControlIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # NOTE: Right now this only logs the intended action.
    # Once real hardware exists, mqtt_service.py will publish this action to
    # the device's MQTT command topic so the ESP32 actually flips the relay.
    log = ActuatorLog(
        device_id=device_id,
        actuator_type=payload.actuator_type,
        action=payload.action,
        triggered_by="user",
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/{device_id}/logs", response_model=List[ActuatorLogOut])
def actuator_logs(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ActuatorLog)
        .filter(ActuatorLog.device_id == device_id)
        .order_by(ActuatorLog.triggered_at.desc())
        .all()
    )
