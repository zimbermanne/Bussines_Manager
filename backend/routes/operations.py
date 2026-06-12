from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from typing import Optional
from database import get_db
from core.security import get_current_user
import models

# ── Deadlines ────────────────────────────────────────────────

deadlines_router = APIRouter(prefix="/deadlines", tags=["Deadlines"])


class DeadlineCreate(BaseModel):
    name:           str
    category:       str
    interval_type:  str
    due_day:        Optional[int] = None
    due_month:      Optional[int] = None
    next_due_date:  date
    notes:          Optional[str] = None


@deadlines_router.get("/")
def list_deadlines(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return (
        db.query(models.Deadline)
        .filter(
            models.Deadline.company_id == current_user.company_id,
            models.Deadline.is_active == True
        )
        .order_by(models.Deadline.next_due_date.asc())
        .all()
    )


@deadlines_router.post("/")
def create_deadline(
    data: DeadlineCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    deadline = models.Deadline(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(deadline)
    db.commit()
    db.refresh(deadline)
    return deadline


@deadlines_router.put("/{deadline_id}/update-due-date")
def update_due_date(
    deadline_id: str,
    next_due_date: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    deadline = db.query(models.Deadline).filter(
        models.Deadline.id == deadline_id,
        models.Deadline.company_id == current_user.company_id
    ).first()
    if not deadline:
        raise HTTPException(status_code=404, detail="Deadline not found")
    deadline.next_due_date = next_due_date
    db.commit()
    return deadline


@deadlines_router.delete("/{deadline_id}")
def delete_deadline(
    deadline_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    deadline = db.query(models.Deadline).filter(
        models.Deadline.id == deadline_id,
        models.Deadline.company_id == current_user.company_id
    ).first()
    if deadline:
        deadline.is_active = False
        db.commit()
    return {"message": "Deleted"}


# ── Suppliers ────────────────────────────────────────────────

suppliers_router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


class SupplierCreate(BaseModel):
    name:           str
    contact_phone:  Optional[str] = None
    contact_email:  Optional[str] = None
    location:       Optional[str] = None
    items_supplied: Optional[str] = None
    notes:          Optional[str] = None


@suppliers_router.get("/")
def list_suppliers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return (
        db.query(models.Supplier)
        .filter(models.Supplier.company_id == current_user.company_id)
        .order_by(models.Supplier.name.asc())
        .all()
    )


@suppliers_router.post("/")
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    supplier = models.Supplier(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@suppliers_router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    supplier = db.query(models.Supplier).filter(
        models.Supplier.id == supplier_id,
        models.Supplier.company_id == current_user.company_id
    ).first()
    if supplier:
        db.delete(supplier)
        db.commit()
    return {"message": "Deleted"}


# ── Tenders ──────────────────────────────────────────────────

tenders_router = APIRouter(prefix="/tenders", tags=["Tenders"])


class TenderCreate(BaseModel):
    name:                   str
    reference_number:       Optional[str] = None
    client:                 Optional[str] = None
    tender_value:           Optional[float] = None
    procurement_budget:     Optional[float] = None
    submission_deadline:    Optional[date] = None
    delivery_deadline:      date
    status:                 str = "planning"
    notes:                  Optional[str] = None


class ProcurementItemCreate(BaseModel):
    supplier_id:            Optional[str] = None
    item_name:              str
    quantity_needed:        float
    unit:                   Optional[str] = None
    estimated_unit_cost:    Optional[float] = None
    actual_unit_cost:       Optional[float] = None
    status:                 str = "pending"
    order_date:             Optional[date] = None
    delivery_date:          Optional[date] = None
    notes:                  Optional[str] = None


@tenders_router.get("/")
def list_tenders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return (
        db.query(models.Tender)
        .filter(models.Tender.company_id == current_user.company_id)
        .order_by(models.Tender.delivery_deadline.asc())
        .all()
    )


@tenders_router.post("/")
def create_tender(
    data: TenderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    tender = models.Tender(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(tender)
    db.commit()
    db.refresh(tender)
    return tender


@tenders_router.get("/{tender_id}")
def get_tender(
    tender_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    tender = db.query(models.Tender).filter(
        models.Tender.id == tender_id,
        models.Tender.company_id == current_user.company_id
    ).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    items = db.query(models.ProcurementItem).filter(
        models.ProcurementItem.tender_id == tender_id
    ).all()

    total_estimated = sum(
        (i.quantity_needed * i.estimated_unit_cost)
        for i in items if i.estimated_unit_cost
    )
    total_actual = sum(
        (i.quantity_needed * i.actual_unit_cost)
        for i in items if i.actual_unit_cost
    )

    budget = float(tender.procurement_budget or 0)
    projected_profit = float(tender.tender_value or 0) - total_actual if total_actual else None

    return {
        "tender": tender,
        "procurement_items": items,
        "summary": {
            "total_items": len(items),
            "pending": sum(1 for i in items if i.status == "pending"),
            "ordered": sum(1 for i in items if i.status == "ordered"),
            "delivered": sum(1 for i in items if i.status == "delivered"),
            "total_estimated_cost": round(total_estimated, 2),
            "total_actual_cost": round(total_actual, 2),
            "budget_remaining": round(budget - total_actual, 2) if budget else None,
            "projected_profit": round(projected_profit, 2) if projected_profit else None,
        }
    }


@tenders_router.post("/{tender_id}/items")
def add_procurement_item(
    tender_id: str,
    data: ProcurementItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    tender = db.query(models.Tender).filter(
        models.Tender.id == tender_id,
        models.Tender.company_id == current_user.company_id
    ).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    item = models.ProcurementItem(tender_id=tender_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@tenders_router.put("/{tender_id}/items/{item_id}")
def update_procurement_item(
    tender_id: str,
    item_id: str,
    data: ProcurementItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    item = db.query(models.ProcurementItem).filter(
        models.ProcurementItem.id == item_id,
        models.ProcurementItem.tender_id == tender_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in data.model_dump().items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@tenders_router.put("/{tender_id}/status")
def update_tender_status(
    tender_id: str,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    tender = db.query(models.Tender).filter(
        models.Tender.id == tender_id,
        models.Tender.company_id == current_user.company_id
    ).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    tender.status = status
    db.commit()
    return tender