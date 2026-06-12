from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from core.security import get_current_user
from database import get_db

router = APIRouter(prefix="/vikoba", tags=["Vikoba"])


class GroupCreate(BaseModel):
    name: str
    lifespan_type: str
    start_date: date
    end_date: Optional[date] = None
    interval_type: str
    hisa_amount: float
    penalty_type: str
    penalty_value: Optional[float] = None
    loan_interest_rate: float = 0
    notes: Optional[str] = None


class MemberCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    joined_date: date = date.today()


class HisaPaymentCreate(BaseModel):
    member_id: str
    due_date: date
    amount: float
    paid_date: Optional[date] = None
    status: str = "pending"


class HisaPayRequest(BaseModel):
    paid_date: date = date.today()


@router.get("/")
def list_groups(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    groups = (
        db.query(models.VikobaGroup)
        .filter(
            models.VikobaGroup.company_id == current_user.company_id,
            models.VikobaGroup.is_dissolved == False,
        )
        .all()
    )
    result = []
    for group in groups:
        member_count = (
            db.query(models.VikobaMember)
            .filter(
                models.VikobaMember.group_id == group.id,
                models.VikobaMember.is_active == True,
            )
            .count()
        )
        result.append(
            {
                "id": group.id,
                "name": group.name,
                "lifespan_type": group.lifespan_type,
                "interval_type": group.interval_type,
                "hisa_amount": float(group.hisa_amount),
                "member_count": member_count,
                "start_date": group.start_date,
                "end_date": group.end_date,
            }
        )
    return result


@router.post("/")
def create_group(
    data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = models.VikobaGroup(
        company_id=current_user.company_id,
        **data.model_dump(),
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.get("/{group_id}")
def get_group(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = db.query(models.VikobaGroup).filter(
        models.VikobaGroup.id == group_id,
        models.VikobaGroup.company_id == current_user.company_id,
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    members = (
        db.query(models.VikobaMember)
        .filter(models.VikobaMember.group_id == group_id)
        .all()
    )
    hisa_payments = (
        db.query(models.HisaPayment)
        .filter(models.HisaPayment.group_id == group_id)
        .order_by(models.HisaPayment.due_date.desc())
        .limit(50)
        .all()
    )
    penalties = (
        db.query(models.HisaPenalty)
        .filter(models.HisaPenalty.group_id == group_id)
        .all()
    )
    loans = (
        db.query(models.VikobaLoan)
        .filter(models.VikobaLoan.group_id == group_id)
        .all()
    )

    total_hisa = sum(
        float(h.amount) for h in hisa_payments if h.status == "paid"
    )
    total_penalties = sum(float(p.amount) for p in penalties)

    return {
        "group": group,
        "members": members,
        "hisa_payments": hisa_payments,
        "penalties": penalties,
        "loans": loans,
        "summary": {
            "total_hisa_collected": round(total_hisa, 2),
            "total_penalties": round(total_penalties, 2),
            "member_count": len(members),
        },
    }


@router.post("/{group_id}/members")
def add_member(
    group_id: str,
    data: MemberCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = db.query(models.VikobaGroup).filter(
        models.VikobaGroup.id == group_id,
        models.VikobaGroup.company_id == current_user.company_id,
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    member = models.VikobaMember(group_id=group_id, **data.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.post("/{group_id}/hisa")
def create_hisa(
    group_id: str,
    data: HisaPaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = db.query(models.VikobaGroup).filter(
        models.VikobaGroup.id == group_id,
        models.VikobaGroup.company_id == current_user.company_id,
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    hisa = models.HisaPayment(group_id=group_id, **data.model_dump())
    db.add(hisa)
    db.commit()
    db.refresh(hisa)
    return hisa


@router.post("/{group_id}/hisa/{hisa_id}/pay")
def mark_hisa_paid(
    group_id: str,
    hisa_id: str,
    data: HisaPayRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    hisa = db.query(models.HisaPayment).filter(
        models.HisaPayment.id == hisa_id,
        models.HisaPayment.group_id == group_id,
    ).first()
    if not hisa:
        raise HTTPException(status_code=404, detail="Hisa payment not found")

    hisa.status = "paid"
    hisa.paid_date = data.paid_date
    db.commit()
    db.refresh(hisa)
    return hisa
