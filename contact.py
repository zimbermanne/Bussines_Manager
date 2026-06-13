from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from typing import Optional
from database import get_db
from core.security import get_current_user
import models

router = APIRouter(prefix="/contacts", tags=["Debtors & Creditors"])


# ── Schemas ──────────────────────────────────────────────────

class ContactCreate(BaseModel):
    name:       str
    type:       str             # debtor, creditor, both
    phone:      Optional[str] = None
    email:      Optional[str] = None
    address:    Optional[str] = None
    notes:      Optional[str] = None


class DebtCreate(BaseModel):
    contact_id:     str
    description:    str
    amount_owed:    float
    due_date:       Optional[date] = None


class PaymentCreate(BaseModel):
    amount:         float
    payment_date:   date = date.today()
    notes:          Optional[str] = None


# ── Contacts ─────────────────────────────────────────────────

@router.get("/")
def list_contacts(
    contact_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    q = db.query(models.Contact).filter(
        models.Contact.company_id == current_user.company_id
    )
    if contact_type:
        q = q.filter(models.Contact.type == contact_type)
    return q.order_by(models.Contact.name.asc()).all()


@router.post("/")
def create_contact(
    data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    contact = models.Contact(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


# ── Debtors ──────────────────────────────────────────────────

debtors_router = APIRouter(prefix="/debtors", tags=["Debtors"])


@debtors_router.get("/")
def list_debtors(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    q = db.query(models.DebtorRecord).filter(
        models.DebtorRecord.company_id == current_user.company_id
    )
    if status:
        q = q.filter(models.DebtorRecord.status == status)

    records = q.order_by(models.DebtorRecord.created_at.desc()).all()

    total_outstanding = sum(float(r.balance) for r in records if r.status != "paid")

    return {
        "records": records,
        "total_outstanding_tzs": round(total_outstanding, 2),
    }


@debtors_router.post("/")
def create_debtor_record(
    data: DebtCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify contact belongs to company
    contact = db.query(models.Contact).filter(
        models.Contact.id == data.contact_id,
        models.Contact.company_id == current_user.company_id
    ).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    record = models.DebtorRecord(
        company_id=current_user.company_id,
        balance=data.amount_owed,  # balance starts equal to amount_owed
        **data.model_dump()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@debtors_router.post("/{record_id}/pay")
def record_debtor_payment(
    record_id: str,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    record = db.query(models.DebtorRecord).filter(
        models.DebtorRecord.id == record_id,
        models.DebtorRecord.company_id == current_user.company_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    new_paid = float(record.amount_paid) + data.amount
    if new_paid > float(record.amount_owed):
        raise HTTPException(status_code=400, detail="Payment exceeds amount owed")

    # Log payment
    payment = models.DebtPayment(
        company_id=current_user.company_id,
        record_id=record_id,
        record_type="debtor",
        payment_date=data.payment_date,
        amount=data.amount,
        notes=data.notes,
    )
    db.add(payment)

    record.amount_paid = new_paid
    record.balance = float(record.amount_owed) - new_paid
    record.status = "paid" if new_paid >= float(record.amount_owed) else "partial"

    db.commit()
    return {
        "record_id": record_id,
        "amount_paid_this_time": data.amount,
        "total_paid": new_paid,
        "balance_remaining": float(record.amount_owed) - new_paid,
        "status": record.status,
    }


# ── Creditors ─────────────────────────────────────────────────

creditors_router = APIRouter(prefix="/creditors", tags=["Creditors"])


@creditors_router.get("/")
def list_creditors(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    q = db.query(models.CreditorRecord).filter(
        models.CreditorRecord.company_id == current_user.company_id
    )
    if status:
        q = q.filter(models.CreditorRecord.status == status)

    records = q.order_by(models.CreditorRecord.created_at.desc()).all()
    total_owed = sum(float(r.balance) for r in records if r.status != "paid")

    return {
        "records": records,
        "total_owed_tzs": round(total_owed, 2),
    }


@creditors_router.post("/")
def create_creditor_record(
    data: DebtCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    contact = db.query(models.Contact).filter(
        models.Contact.id == data.contact_id,
        models.Contact.company_id == current_user.company_id
    ).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    record = models.CreditorRecord(
        company_id=current_user.company_id,
        balance=data.amount_owed,  # balance starts equal to amount_owed
        **data.model_dump()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@creditors_router.post("/{record_id}/pay")
def record_creditor_payment(
    record_id: str,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    record = db.query(models.CreditorRecord).filter(
        models.CreditorRecord.id == record_id,
        models.CreditorRecord.company_id == current_user.company_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    new_paid = float(record.amount_paid) + data.amount
    if new_paid > float(record.amount_owed):
        raise HTTPException(status_code=400, detail="Payment exceeds amount owed")

    payment = models.DebtPayment(
        company_id=current_user.company_id,
        record_id=record_id,
        record_type="creditor",
        payment_date=data.payment_date,
        amount=data.amount,
        notes=data.notes,
    )
    db.add(payment)

    record.amount_paid = new_paid
    record.balance = float(record.amount_owed) - new_paid
    record.status = "paid" if new_paid >= float(record.amount_owed) else "partial"

    db.commit()
    return {
        "record_id": record_id,
        "amount_paid_this_time": data.amount,
        "total_paid": new_paid,
        "balance_remaining": float(record.amount_owed) - new_paid,
        "status": record.status,
    }
