from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.farm import Farm
from app.models.user import User
from app.schemas.farm import FarmCreate, FarmOut

router = APIRouter(prefix="/farms", tags=["farms"])


@router.post("", response_model=FarmOut, status_code=201)
def create_farm(
    payload: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = Farm(owner_id=current_user.id, name=payload.name, location=payload.location)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get("", response_model=List[FarmOut])
def list_my_farms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Farm).filter(Farm.owner_id == current_user.id).all()


@router.get("/{farm_id}", response_model=FarmOut)
def get_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = _get_owned_farm(farm_id, db, current_user)
    return farm


def _get_owned_farm(farm_id: int, db: Session, current_user: User) -> Farm:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your farm")
    return farm
