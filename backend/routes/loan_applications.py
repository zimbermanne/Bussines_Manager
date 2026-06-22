from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from core.security import get_current_user
from database import get_db

router = APIRouter(prefix="/loan-applications", tags=["Loan Applications"])


class LoanApplicationCreate(BaseModel):
    lender_name: str
    loan_type: str  # business, government, emergency
    amount_applied: float
    expected_disbursement_date: Optional[date] = None
    purpose: Optional[str] = None
    collateral: Optional[str] = None
    follow_up_date: Optional[date] = None
    notes: Optional[str] = None


@router.get("/")
def get_loan_applications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    applications = (
        db.query(models.LoanApplication)
        .filter(models.LoanApplication.company_id == current_user.company_id)
        .order_by(models.LoanApplication.application_date.desc())
        .all()
    )
    return applications


@router.post("/")
def create_loan_application(
    data: LoanApplicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    application = models.LoanApplication(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(application)
    
    # Create applied event
    event = models.LoanApplicationEvent(
        application_id=application.id,
        status="applied",
        changed_by_user_id=current_user.id
    )
    db.add(event)
    
    db.commit()
    db.refresh(application)
    return application


@router.put("/{application_id}/status")
def update_application_status(
    application_id: str,
    status: str,
    rejection_reason: Optional[str] = None,
    disbursement_amount: Optional[float] = None,
    disbursement_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    application = db.query(models.LoanApplication).filter(
        models.LoanApplication.id == application_id,
        models.LoanApplication.company_id == current_user.company_id
    ).first()
    
    if not application:
        return None
    
    application.status = status
    if rejection_reason:
        application.rejection_reason = rejection_reason
    if disbursement_amount:
        application.disbursement_amount = disbursement_amount
    if disbursement_date:
        application.disbursement_date = disbursement_date
    
    # Create status change event
    event = models.LoanApplicationEvent(
        application_id=application_id,
        status=status,
        changed_by_user_id=current_user.id,
        notes=rejection_reason
    )
    db.add(event)
    
    db.commit()
    db.refresh(application)
    return application


@router.post("/{application_id}/convert-to-loan")
def convert_to_loan(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    application = db.query(models.LoanApplication).filter(
        models.LoanApplication.id == application_id,
        models.LoanApplication.company_id == current_user.company_id
    ).first()
    
    if not application or application.status != "disbursed":
        return None
    
    # Create bank loan from application
    loan = models.BankLoan(
        company_id=current_user.company_id,
        lender_name=application.lender_name,
        principal_amount=application.disbursement_amount or application.amount_applied,
        interest_type="simple",
        interest_rate=18.0,
        start_date=application.disbursement_date or date.today(),
        due_day=1,
        notes=f"Created from loan application: {application.purpose}"
    )
    db.add(loan)
    
    application.converted_to_loan_id = loan.id
    
    db.commit()
    db.refresh(application)
    return {"message": "Converted to bank loan", "loan_id": loan.id}