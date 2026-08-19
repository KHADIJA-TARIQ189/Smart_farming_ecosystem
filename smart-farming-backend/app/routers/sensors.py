import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.device import Device
from app.models.sensor_reading import SensorReading
from app.models.user import User
from app.schemas.sensor_reading import SensorReadingIn, SensorReadingOut
from app.services.irrigation_logic import evaluate_reading_for_alerts

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.post("/ingest", response_model=SensorReadingOut, status_code=201)
def ingest_reading(payload: SensorReadingIn, db: Session = Depends(get_db)):
    """
    Devices call this endpoint directly using their own api_key (no user JWT needed).
    This is what your ESP32 will POST to, and what you can fake with curl/Postman
    before hardware exists.
    """
    device = db.query(Device).filter(Device.api_key == payload.api_key).first()
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device api_key")

    reading = SensorReading(
        device_id=device.id,
        sensor_type=payload.sensor_type,
        value=payload.value,
        unit=payload.unit,
    )
    db.add(reading)

    device.status = "online"
    device.last_seen = datetime.datetime.utcnow()

    db.commit()
    db.refresh(reading)

    # Baseline threshold alerting (Section 2 of the proposal: "if-then" automation)
    evaluate_reading_for_alerts(db, device, reading)

    return reading


@router.get("/{device_id}/latest", response_model=List[SensorReadingOut])
def latest_readings(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Latest reading per sensor_type for a device."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    sensor_types = (
        db.query(SensorReading.sensor_type)
        .filter(SensorReading.device_id == device_id)
        .distinct()
        .all()
    )
    results = []
    for (sensor_type,) in sensor_types:
        latest = (
            db.query(SensorReading)
            .filter(SensorReading.device_id == device_id, SensorReading.sensor_type == sensor_type)
            .order_by(SensorReading.recorded_at.desc())
            .first()
        )
        if latest:
            results.append(latest)
    return results


@router.get("/{device_id}/history", response_model=List[SensorReadingOut])
def sensor_history(
    device_id: int,
    sensor_type: Optional[str] = Query(default=None),
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(SensorReading).filter(SensorReading.device_id == device_id)
    if sensor_type:
        query = query.filter(SensorReading.sensor_type == sensor_type)
    return query.order_by(SensorReading.recorded_at.desc()).limit(limit).all()
