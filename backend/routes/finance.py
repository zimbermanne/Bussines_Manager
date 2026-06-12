from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from pydantic import BaseModel
from datetime import date
from typing import Optional
from database import get_db
from core.security import get_current_user
import models

router = APIRouter(tags=["Finance"])


# ── Business Units ───────────────────────────────────────────

business_router = APIRouter(prefix="/business-units", tags=["Business Units"])


class BusinessUnitCreate(BaseModel):
    name: str
    type: Optional[str] = None


@business_router.get("/")
def list_business_units(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.BusinessUnit)
        .filter(
            models.BusinessUnit.company_id == current_user.company_id,
            models.BusinessUnit.is_active == True,
        )
        .order_by(models.BusinessUnit.name.asc())
        .all()
    )


@business_router.post("/")
def create_business_unit(
    data: BusinessUnitCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    unit = models.BusinessUnit(
        company_id=current_user.company_id,
        **data.model_dump(),
    )
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


# ── Schemas ──────────────────────────────────────────────────

class SaleCreate(BaseModel):
    business_unit_id:   Optional[str] = None
    sale_date:          date = date.today()
    item_name:          str
    quantity:           float
    unit_price:         float
    notes:              Optional[str] = None


class PurchaseCreate(BaseModel):
    business_unit_id:   Optional[str] = None
    supplier_id:        Optional[str] = None
    purchase_date:      date = date.today()
    item_name:          str
    quantity:           float
    unit_cost:          float
    notes:              Optional[str] = None


class ExpenseCreate(BaseModel):
    business_unit_id:   Optional[str] = None
    expense_date:       date = date.today()
    category:           str
    description:        Optional[str] = None
    amount:             float


# ── Sales ────────────────────────────────────────────────────

sales_router = APIRouter(prefix="/sales")

@sales_router.post("/")
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    sale = models.SaleEntry(
        company_id=current_user.company_id,
        total_amount=round(data.quantity * data.unit_price, 2),
        **data.model_dump()
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


@sales_router.get("/")
def list_sales(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    business_unit_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    q = db.query(models.SaleEntry).filter(
        models.SaleEntry.company_id == current_user.company_id
    )
    if start_date:
        q = q.filter(models.SaleEntry.sale_date >= start_date)
    if end_date:
        q = q.filter(models.SaleEntry.sale_date <= end_date)
    if business_unit_id:
        q = q.filter(models.SaleEntry.business_unit_id == business_unit_id)
    return q.order_by(models.SaleEntry.sale_date.desc()).all()


@sales_router.delete("/{sale_id}")
def delete_sale(
    sale_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    sale = db.query(models.SaleEntry).filter(
        models.SaleEntry.id == sale_id,
        models.SaleEntry.company_id == current_user.company_id
    ).first()
    if sale:
        db.delete(sale)
        db.commit()
    return {"message": "Deleted"}


# ── Purchases ────────────────────────────────────────────────

purchases_router = APIRouter(prefix="/purchases")

@purchases_router.post("/")
def create_purchase(
    data: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    purchase = models.Purchase(
        company_id=current_user.company_id,
        total_cost=round(data.quantity * data.unit_cost, 2),
        **data.model_dump()
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


@purchases_router.get("/")
def list_purchases(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    business_unit_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    q = db.query(models.Purchase).filter(
        models.Purchase.company_id == current_user.company_id
    )
    if start_date:
        q = q.filter(models.Purchase.purchase_date >= start_date)
    if end_date:
        q = q.filter(models.Purchase.purchase_date <= end_date)
    if business_unit_id:
        q = q.filter(models.Purchase.business_unit_id == business_unit_id)
    return q.order_by(models.Purchase.purchase_date.desc()).all()


# ── Expenses ─────────────────────────────────────────────────

expenses_router = APIRouter(prefix="/expenses")

@expenses_router.post("/")
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    expense = models.Expense(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@expenses_router.get("/")
def list_expenses(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    q = db.query(models.Expense).filter(
        models.Expense.company_id == current_user.company_id
    )
    if start_date:
        q = q.filter(models.Expense.expense_date >= start_date)
    if end_date:
        q = q.filter(models.Expense.expense_date <= end_date)
    if category:
        q = q.filter(models.Expense.category == category)
    return q.order_by(models.Expense.expense_date.desc()).all()


# ── Profit & Loss ────────────────────────────────────────────

pnl_router = APIRouter(prefix="/pnl")

@pnl_router.get("/daily")
def daily_pnl(
    target_date: date = date.today(),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    cid = current_user.company_id

    total_sales = db.query(func.coalesce(func.sum(models.SaleEntry.total_amount), 0)).filter(
        models.SaleEntry.company_id == cid,
        models.SaleEntry.sale_date == target_date
    ).scalar()

    total_purchases = db.query(func.coalesce(func.sum(models.Purchase.total_cost), 0)).filter(
        models.Purchase.company_id == cid,
        models.Purchase.purchase_date == target_date
    ).scalar()

    total_expenses = db.query(func.coalesce(func.sum(models.Expense.amount), 0)).filter(
        models.Expense.company_id == cid,
        models.Expense.expense_date == target_date
    ).scalar()

    net_profit = float(total_sales) - float(total_purchases) - float(total_expenses)

    return {
        "date": target_date,
        "total_sales": float(total_sales),
        "total_purchases": float(total_purchases),
        "total_expenses": float(total_expenses),
        "net_profit": round(net_profit, 2),
    }


@pnl_router.get("/monthly")
def monthly_pnl(
    year: int = date.today().year,
    month: int = date.today().month,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    from datetime import date as dt
    import calendar

    cid = current_user.company_id
    start = dt(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end = dt(year, month, last_day)

    total_sales = db.query(func.coalesce(func.sum(models.SaleEntry.total_amount), 0)).filter(
        models.SaleEntry.company_id == cid,
        models.SaleEntry.sale_date >= start,
        models.SaleEntry.sale_date <= end
    ).scalar()

    total_purchases = db.query(func.coalesce(func.sum(models.Purchase.total_cost), 0)).filter(
        models.Purchase.company_id == cid,
        models.Purchase.purchase_date >= start,
        models.Purchase.purchase_date <= end
    ).scalar()

    total_expenses = db.query(func.coalesce(func.sum(models.Expense.amount), 0)).filter(
        models.Expense.company_id == cid,
        models.Expense.expense_date >= start,
        models.Expense.expense_date <= end
    ).scalar()

    net_profit = float(total_sales) - float(total_purchases) - float(total_expenses)

    return {
        "year": year,
        "month": month,
        "period": f"{start.strftime('%B %Y')}",
        "total_sales": float(total_sales),
        "total_purchases": float(total_purchases),
        "total_expenses": float(total_expenses),
        "net_profit": round(net_profit, 2),
    }