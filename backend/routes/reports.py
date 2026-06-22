from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from core.security import get_current_user
from database import get_db
import csv
from io import StringIO

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/generate")
def generate_report(
    report_type: str,
    report_format: str = "csv",
    period_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    company_id = current_user.company_id
    
    # Get data based on report type
    if report_type == "sales":
        data = db.query(models.SaleEntry).filter(
            models.SaleEntry.company_id == company_id
        )
        if start_date:
            data = data.filter(models.SaleEntry.sale_date >= start_date)
        if end_date:
            data = data.filter(models.SaleEntry.sale_date <= end_date)
        data = data.all()
        
    elif report_type == "purchases":
        data = db.query(models.Purchase).filter(
            models.Purchase.company_id == company_id
        )
        if start_date:
            data = data.filter(models.Purchase.purchase_date >= start_date)
        if end_date:
            data = data.filter(models.Purchase.purchase_date <= end_date)
        data = data.all()
        
    elif report_type == "expenses":
        data = db.query(models.Expense).filter(
            models.Expense.company_id == company_id
        )
        if start_date:
            data = data.filter(models.Expense.expense_date >= start_date)
        if end_date:
            data = data.filter(models.Expense.expense_date <= end_date)
        data = data.all()
        
    else:
        raise HTTPException(status_code=400, detail="Unsupported report type")
    
    # Generate report based on format
    if report_format == "csv":
        csv_file = StringIO()
        writer = csv.writer(csv_file)
        
        # Write header
        if report_type == "sales":
            writer.writerow(["Date", "Item", "Quantity", "Unit Price", "Total"])
            for item in data:
                writer.writerow([item.sale_date, item.item_name, item.quantity, item.unit_price, item.total_amount])
        elif report_type == "purchases":
            writer.writerow(["Date", "Item", "Quantity", "Unit Cost", "Total"])
            for item in data:
                writer.writerow([item.purchase_date, item.item_name, item.quantity, item.unit_cost, item.total_cost])
        elif report_type == "expenses":
            writer.writerow(["Date", "Category", "Description", "Amount"])
            for item in data:
                writer.writerow([item.expense_date, item.category, item.description, item.amount])
        
        csv_file.seek(0)
        return {
            "data": csv_file.getvalue(),
            "format": "csv",
            "report_type": report_type
        }
    
    return {"error": "Unsupported format"}


@router.get("/history")
def get_report_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    history = (
        db.query(models.ReportHistory)
        .filter(models.ReportHistory.company_id == current_user.company_id)
        .order_by(models.ReportHistory.generated_at.desc())
        .limit(20)
        .all()
    )
    return history