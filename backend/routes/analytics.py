from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from core.security import get_current_user
from database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    company_id = current_user.company_id
    
    # Sales analytics
    today_sales = db.query(func.coalesce(func.sum(models.SaleEntry.total_amount), 0)).filter(
        models.SaleEntry.company_id == company_id,
        models.SaleEntry.sale_date == date.today()
    ).scalar()
    
    month_start = date.today().replace(day=1)
    month_sales = db.query(func.coalesce(func.sum(models.SaleEntry.total_amount), 0)).filter(
        models.SaleEntry.company_id == company_id,
        models.SaleEntry.sale_date >= month_start
    ).scalar()
    
    # Expenses analytics
    today_expenses = db.query(func.coalesce(func.sum(models.Expense.amount), 0)).filter(
        models.Expense.company_id == company_id,
        models.Expense.expense_date == date.today()
    ).scalar()
    
    month_expenses = db.query(func.coalesce(func.sum(models.Expense.amount), 0)).filter(
        models.Expense.company_id == company_id,
        models.Expense.expense_date >= month_start
    ).scalar()
    
    # Debt/Credit analytics
    total_debtors = db.query(func.coalesce(func.sum(models.DebtorRecord.balance_remaining), 0)).filter(
        models.DebtorRecord.company_id == company_id,
        models.DebtorRecord.status != "paid"
    ).scalar()
    
    total_creditors = db.query(func.coalesce(func.sum(models.CreditorRecord.balance_remaining), 0)).filter(
        models.CreditorRecord.company_id == company_id,
        models.CreditorRecord.status != "paid"
    ).scalar()
    
    # Loan analytics
    active_loans = db.query(func.count(models.BankLoan.id)).filter(
        models.BankLoan.company_id == company_id,
        models.BankLoan.is_active == True
    ).scalar()
    
    # Vikoba analytics
    active_vikoba = db.query(func.count(models.VikobaGroup.id)).filter(
        models.VikobaGroup.company_id == company_id,
        models.VikobaGroup.is_dissolved == False
    ).scalar()
    
    return {
        "today_revenue": float(today_sales),
        "month_revenue": float(month_sales),
        "today_expenses": float(today_expenses),
        "month_expenses": float(month_expenses),
        "month_profit": float(month_sales) - float(month_expenses),
        "total_debtors": float(total_debtors),
        "total_creditors": float(total_creditors),
        "net_cash_position": float(total_debtors) - float(total_creditors),
        "active_loans": active_loans,
        "active_vikoba": active_vikoba
    }


@router.get("/sales-trend")
def get_sales_trend(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    start_date = date.today() - timedelta(days=days)
    
    sales = db.query(
        models.SaleEntry.sale_date,
        func.sum(models.SaleEntry.total_amount).label("total")
    ).filter(
        models.SaleEntry.company_id == current_user.company_id,
        models.SaleEntry.sale_date >= start_date
    ).group_by(models.SaleEntry.sale_date).order_by(models.SaleEntry.sale_date).all()
    
    return [
        {"date": str(s.sale_date), "total": float(s.total)}
        for s in sales
    ]


@router.get("/top-items")
def get_top_items(
    days: int = 30,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    start_date = date.today() - timedelta(days=days)
    
    items = db.query(
        models.SaleEntry.item_name,
        func.sum(models.SaleEntry.quantity).label("total_qty"),
        func.sum(models.SaleEntry.total_amount).label("total_revenue")
    ).filter(
        models.SaleEntry.company_id == current_user.company_id,
        models.SaleEntry.sale_date >= start_date
    ).group_by(models.SaleEntry.item_name).order_by(
        func.sum(models.SaleEntry.total_revenue).desc()
    ).limit(limit).all()
    
    return [
        {"item": i.item_name, "quantity": float(i.total_qty), "revenue": float(i.total_revenue)}
        for i in items
    ]


@router.get("/expense-breakdown")
def get_expense_breakdown(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    start_date = date.today() - timedelta(days=days)
    
    expenses = db.query(
        models.Expense.category,
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.company_id == current_user.company_id,
        models.Expense.expense_date >= start_date
    ).group_by(models.Expense.category).order_by(
        func.sum(models.Expense.amount).desc()
    ).all()
    
    return [
        {"category": e.category, "amount": float(e.total)}
        for e in expenses
    ]