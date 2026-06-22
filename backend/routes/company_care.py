from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from core.security import get_current_user
from database import get_db

router = APIRouter(prefix="/company-care", tags=["Company Care"])


class DebtorCreate(BaseModel):
    debtor_name: str
    debtor_phone: Optional[str] = None
    debtor_email: Optional[str] = None
    debt_date: date = date.today()
    item_or_service: Optional[str] = None
    amount_owed: float
    due_date: Optional[date] = None
    notes: Optional[str] = None


class CreditorCreate(BaseModel):
    creditor_name: str
    creditor_phone: Optional[str] = None
    creditor_email: Optional[str] = None
    credit_date: date = date.today()
    item_or_service: Optional[str] = None
    amount_owed: float
    due_date: Optional[date] = None
    notes: Optional[str] = None


class PaymentCreate(BaseModel):
    record_type: str  # debtor or creditor
    record_id: str
    payment_date: date = date.today()
    amount_paid: float
    payment_method: Optional[str] = None
    notes: Optional[str] = None


@router.get("/debtors")
def get_debtors(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    debtors = (
        db.query(models.DebtorRecord)
        .filter(models.DebtorRecord.company_id == current_user.company_id)
        .order_by(models.DebtorRecord.debt_date.desc())
        .all()
    )
    return debtors


@router.post("/debtors")
def create_debtor(
    data: DebtorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    debtor = models.DebtorRecord(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(debtor)
    db.commit()
    db.refresh(debtor)
    return debtor


@router.get("/creditors")
def get_creditors(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    creditors = (
        db.query(models.CreditorRecord)
        .filter(models.CreditorRecord.company_id == current_user.company_id)
        .order_by(models.CreditorRecord.credit_date.desc())
        .all()
    )
    return creditors


@router.post("/creditors")
def create_creditor(
    data: CreditorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    creditor = models.CreditorRecord(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(creditor)
    db.commit()
    db.refresh(creditor)
    return creditor


@router.post("/payments")
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    payment = models.DebtPayment(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(payment)
    
    # Update record
    if data.record_type == "debtor":
        record = db.query(models.DebtorRecord).filter(
            models.DebtorRecord.id == data.record_id
        ).first()
    else:
        record = db.query(models.CreditorRecord).filter(
            models.CreditorRecord.id == data.record_id
        ).first()
    
    if record:
        record.amount_paid += data.amount_paid
        if record.amount_paid >= record.amount_owed:
            record.status = "paid"
        elif record.amount_paid > 0:
            record.status = "partial"
    
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/summary")
def get_care_summary(
    period_type: str = "daily",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    total_debtors = db.query(func.coalesce(func.sum(models.DebtorRecord.balance_remaining), 0)).filter(
        models.DebtorRecord.company_id == current_user.company_id,
        models.DebtorRecord.status != "paid"
    ).scalar()
    
    total_creditors = db.query(func.coalesce(func.sum(models.CreditorRecord.balance_remaining), 0)).filter(
        models.CreditorRecord.company_id == current_user.company_id,
        models.CreditorRecord.status != "paid"
    ).scalar()
    
    net_position = float(total_debtors) - float(total_creditors)
    
    if net_position > 0:
        health_status = "healthy"
    elif net_position >= -100000:
        health_status = "watch"
    else:
        health_status = "at_risk"
    
    return {
        "total_debtors": float(total_debtors),
        "total_creditors": float(total_creditors),
        "net_position": net_position,
        "health_status": health_status
    }


@router.post("/snapshot")
def create_snapshot(
    period_type: str = "daily",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    summary = get_care_summary(period_type, db, current_user)
    
    snapshot = models.CareSnapshot(
        company_id=current_user.company_id,
        period_type=period_type,
        total_debtors=summary["total_debtors"],
        total_creditors=summary["total_creditors"],
        net_position=summary["net_position"],
        health_status=summary["health_status"]
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot