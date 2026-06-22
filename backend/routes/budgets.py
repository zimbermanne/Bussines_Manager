from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from core.security import get_current_user
from database import get_db

router = APIRouter(prefix="/budgets", tags=["Budgets"])


class ExpenseCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class BudgetCreate(BaseModel):
    category_id: str
    business_unit_id: Optional[str] = None
    budget_month: int
    budget_year: int
    budget_amount: float


@router.get("/categories")
def get_expense_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    categories = (
        db.query(models.ExpenseCategory)
        .filter(models.ExpenseCategory.company_id == current_user.company_id)
        .filter(models.ExpenseCategory.is_active == True)
        .order_by(models.ExpenseCategory.name)
        .all()
    )
    return categories


@router.post("/categories")
def create_expense_category(
    data: ExpenseCategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    category = models.ExpenseCategory(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/")
def get_budgets(
    budget_month: Optional[int] = None,
    budget_year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.ExpenseBudget).filter(
        models.ExpenseBudget.company_id == current_user.company_id
    )
    
    if budget_month:
        query = query.filter(models.ExpenseBudget.budget_month == budget_month)
    if budget_year:
        query = query.filter(models.ExpenseBudget.budget_year == budget_year)
    
    budgets = query.order_by(
        models.ExpenseBudget.budget_year.desc(),
        models.ExpenseBudget.budget_month.desc()
    ).all()
    return budgets


@router.post("/")
def create_budget(
    data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    budget = models.ExpenseBudget(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@router.get("/summary")
def get_budget_summary(
    budget_month: int,
    budget_year: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    budgets = db.query(models.ExpenseBudget).filter(
        models.ExpenseBudget.company_id == current_user.company_id,
        models.ExpenseBudget.budget_month == budget_month,
        models.ExpenseBudget.budget_year == budget_year
    ).all()
    
    total_budget = sum(float(b.budget_amount) for b in budgets)
    total_spent = sum(float(b.actual_spent) for b in budgets)
    total_remaining = sum(float(b.remaining) for b in budgets)
    
    # Calculate actual spent from expenses
    from datetime import datetime
    start_date = datetime(budget_year, budget_month, 1).date()
    if budget_month == 12:
        end_date = datetime(budget_year + 1, 1, 1).date()
    else:
        end_date = datetime(budget_year, budget_month + 1, 1).date()
    
    actual_expenses = db.query(func.coalesce(func.sum(models.Expense.amount), 0)).filter(
        models.Expense.company_id == current_user.company_id,
        models.Expense.expense_date >= start_date,
        models.Expense.expense_date < end_date
    ).scalar()
    
    return {
        "total_budget": total_budget,
        "total_actual": float(actual_expenses),
        "total_remaining": total_budget - float(actual_expenses),
        "budgets": budgets,
        "categories_count": len(budgets)
    }