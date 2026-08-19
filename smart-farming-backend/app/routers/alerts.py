from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.alert import Alert
from app.models.user import User
from app.schemas.alert import AlertOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertOut])
def list_alerts(
    farm_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Alert)
    if farm_id:
        query = query.filter(Alert.farm_id == farm_id)
    return query.order_by(Alert.created_at.desc()).all()


@router.patch("/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.resolved = True
    db.commit()
    db.refresh(alert)
    return alert
