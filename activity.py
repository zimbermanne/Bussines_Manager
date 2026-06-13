from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from core.security import get_current_user
import models

router = APIRouter(prefix="/activity", tags=["Activity Log"])


@router.get("/")
def get_activity_log(
    limit:          int = 50,
    entity_type:    Optional[str] = None,
    user_id:        Optional[str] = None,
    db:             Session = Depends(get_db),
    current_user:   models.User = Depends(get_current_user)
):
    q = db.query(models.ActivityLog).filter(
        models.ActivityLog.company_id == current_user.company_id
    )
    if entity_type:
        q = q.filter(models.ActivityLog.entity_type == entity_type)
    if user_id:
        q = q.filter(models.ActivityLog.user_id == user_id)

    logs = q.order_by(models.ActivityLog.created_at.desc()).limit(limit).all()

    # Enrich with user names
    result = []
    for log in logs:
        user = db.query(models.User).filter(models.User.id == log.user_id).first()
        result.append({
            "id": log.id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "performed_by": user.full_name if user else "System",
            "created_at": log.created_at,
        })

    return result
