from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.crop import Crop
from app.models.crop_profile import CropProfile
from app.models.farm import Farm
from app.models.user import User
from app.schemas.crop import CropCreate, CropOut, CropProfileOut

router = APIRouter(tags=["crops"])


def _get_owned_farm(farm_id: int, db: Session, current_user: User) -> Farm:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your farm")
    return farm


@router.post("/farms/{farm_id}/crops", response_model=CropOut, status_code=201)
def add_crop(
    farm_id: int,
    payload: CropCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_farm(farm_id, db, current_user)
    crop = Crop(
        farm_id=farm_id,
        crop_type=payload.crop_type,
        zone=payload.zone,
        planted_date=payload.planted_date,
    )
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


@router.get("/farms/{farm_id}/crops", response_model=List[CropOut])
def list_crops(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_farm(farm_id, db, current_user)
    return db.query(Crop).filter(Crop.farm_id == farm_id).all()


@router.get("/crop-profiles/{crop_type}", response_model=CropProfileOut)
def get_crop_profile(crop_type: str, db: Session = Depends(get_db)):
    profile = db.query(CropProfile).filter(CropProfile.crop_type == crop_type).first()
    if not profile:
        raise HTTPException(status_code=404, detail="No profile for this crop type")
    return profile
