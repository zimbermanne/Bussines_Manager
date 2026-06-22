from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from core.security import get_current_user
from database import get_db

router = APIRouter(prefix="/staff", tags=["Staff & Payroll"])


class EmployeeCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    national_id: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[str] = None
    employment_date: date
    basic_salary: Optional[float] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None


@router.get("/employees")
def get_employees(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    employees = (
        db.query(models.Employee)
        .filter(models.Employee.company_id == current_user.company_id)
        .filter(models.Employee.is_active == True)
        .order_by(models.Employee.full_name)
        .all()
    )
    return employees


@router.post("/employees")
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    employee = models.Employee(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("/payroll-runs")
def get_payroll_runs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    runs = (
        db.query(models.PayrollRun)
        .filter(models.PayrollRun.company_id == current_user.company_id)
        .order_by(models.PayrollRun.run_date.desc())
        .all()
    )
    return runs


@router.post("/payroll-runs")
def create_payroll_run(
    period_month: int,
    period_year: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Get all active employees
    employees = (
        db.query(models.Employee)
        .filter(models.Employee.company_id == current_user.company_id)
        .filter(models.Employee.is_active == True)
        .all()
    )
    
    # Create payroll run
    payroll_run = models.PayrollRun(
        company_id=current_user.company_id,
        period_month=period_month,
        period_year=period_year,
        status="draft"
    )
    db.add(payroll_run)
    db.flush()
    
    total_gross = 0
    total_deductions = 0
    total_net = 0
    
    # Create payroll items for each employee
    for employee in employees:
        basic_salary = float(employee.basic_salary or 0)
        gross_pay = basic_salary
        
        # Calculate NSSF (5% employee contribution)
        nssf = gross_pay * 0.05
        
        # Calculate PAYE (simplified tax brackets)
        if gross_pay <= 170000:
            paye = 0
        elif gross_pay <= 360000:
            paye = (gross_pay - 170000) * 0.09
        elif gross_pay <= 540000:
            paye = 17100 + (gross_pay - 360000) * 0.20
        else:
            paye = 53100 + (gross_pay - 540000) * 0.25
        
        total_deductions_emp = nssf + paye
        net_pay = gross_pay - total_deductions_emp
        
        payroll_item = models.PayrollItem(
            payroll_run_id=payroll_run.id,
            employee_id=employee.id,
            basic_salary=basic_salary,
            gross_pay=gross_pay,
            total_deductions=total_deductions_emp,
            net_pay=net_pay
        )
        db.add(payroll_item)
        
        # Add NSSF deduction
        nssf_deduction = models.PayrollDeduction(
            payroll_item_id=payroll_item.id,
            deduction_type="nssf",
            deduction_name="NSSF Employee Contribution",
            amount=nssf
        )
        db.add(nssf_deduction)
        
        # Add PAYE deduction
        paye_deduction = models.PayrollDeduction(
            payroll_item_id=payroll_item.id,
            deduction_type="paye",
            deduction_name="PAYE Tax",
            amount=paye
        )
        db.add(paye_deduction)
        
        total_gross += gross_pay
        total_deductions += total_deductions_emp
        total_net += net_pay
    
    payroll_run.total_gross_pay = total_gross
    payroll_run.total_deductions = total_deductions
    payroll_run.total_net_pay = total_net
    
    db.commit()
    db.refresh(payroll_run)
    return payroll_run


@router.get("/payroll-runs/{run_id}")
def get_payroll_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    payroll_run = db.query(models.PayrollRun).filter(
        models.PayrollRun.id == run_id,
        models.PayrollRun.company_id == current_user.company_id
    ).first()
    
    if not payroll_run:
        return None
    
    items = db.query(models.PayrollItem).filter(
        models.PayrollItem.payroll_run_id == run_id
    ).all()
    
    return {
        "payroll_run": payroll_run,
        "items": items
    }