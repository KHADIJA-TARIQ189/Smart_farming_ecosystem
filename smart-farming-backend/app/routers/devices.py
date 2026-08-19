from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.device import Device
from app.models.farm import Farm
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceOut

router = APIRouter(tags=["devices"])


def _get_owned_farm(farm_id: int, db: Session, current_user: User) -> Farm:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your farm")
    return farm


@router.post("/farms/{farm_id}/devices", response_model=DeviceOut, status_code=201)
def create_device(
    farm_id: int,
    payload: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_farm(farm_id, db, current_user)
    device = Device(farm_id=farm_id, name=payload.name, type=payload.type)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("/farms/{farm_id}/devices", response_model=List[DeviceOut])
def list_devices(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_farm(farm_id, db, current_user)
    return db.query(Device).filter(Device.farm_id == farm_id).all()
