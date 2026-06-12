from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import date
from typing import Optional
from database import get_db
from core.security import get_current_user
import models

router = APIRouter(prefix="/loans", tags=["Bank Loans"])


class LoanCreate(BaseModel):
    lender_name:            str
    principal_amount:       float
    interest_type:          str     # simple, reducing_balance
    interest_rate:          float   # annual %
    start_date:             date
    due_day:                int
    grace_period_months:    int = 0
    notes:                  Optional[str] = None


class PaymentCreate(BaseModel):
    payment_date:   date
    amount_paid:    float
    notes:          Optional[str] = None


def calculate_interest_split(loan: models.BankLoan, amount_paid: float, current_balance: float):
    """
    Calculate interest and principal split for a payment.
    Returns (interest_portion, principal_portion, balance_after)
    """
    monthly_rate = float(loan.interest_rate) / 100 / 12

    if loan.interest_type == "simple":
        # Interest is fixed based on original principal
        monthly_interest = float(loan.principal_amount) * monthly_rate
    else:
        # Reducing balance — interest based on remaining balance
        monthly_interest = current_balance * monthly_rate

    monthly_interest = round(monthly_interest, 2)

    # If payment is less than interest, all goes to interest
    if amount_paid <= monthly_interest:
        interest_portion = amount_paid
        principal_portion = 0.0
    else:
        interest_portion = monthly_interest
        principal_portion = round(amount_paid - monthly_interest, 2)

    balance_after = round(max(0, current_balance - principal_portion), 2)

    return interest_portion, principal_portion, balance_after


def get_loan_balance(loan_id: str, db: Session) -> float:
    """Get current remaining balance for a loan."""
    loan = db.query(models.BankLoan).filter(models.BankLoan.id == loan_id).first()
    if not loan:
        return 0.0

    last_payment = (
        db.query(models.BankLoanPayment)
        .filter(models.BankLoanPayment.loan_id == loan_id)
        .order_by(models.BankLoanPayment.created_at.desc())
        .first()
    )

    if last_payment:
        return float(last_payment.balance_after)
    return float(loan.principal_amount)


# ── Routes ───────────────────────────────────────────────────

@router.post("/")
def create_loan(
    data: LoanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    loan = models.BankLoan(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@router.get("/")
def list_loans(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    loans = (
        db.query(models.BankLoan)
        .filter(
            models.BankLoan.company_id == current_user.company_id,
            models.BankLoan.is_active == True
        )
        .all()
    )

    result = []
    for loan in loans:
        balance = get_loan_balance(loan.id, db)
        total_paid = float(loan.principal_amount) - balance

        payments = db.query(models.BankLoanPayment).filter(
            models.BankLoanPayment.loan_id == loan.id
        ).all()

        total_interest_paid = sum(float(p.interest_portion) for p in payments)
        total_principal_paid = sum(float(p.principal_portion) for p in payments)

        result.append({
            "id": loan.id,
            "lender_name": loan.lender_name,
            "principal_amount": float(loan.principal_amount),
            "interest_type": loan.interest_type,
            "interest_rate": float(loan.interest_rate),
            "start_date": loan.start_date,
            "due_day": loan.due_day,
            "balance_remaining": balance,
            "total_paid": round(total_paid + total_interest_paid, 2),
            "total_interest_paid": round(total_interest_paid, 2),
            "total_principal_paid": round(total_principal_paid, 2),
            "payment_count": len(payments),
        })

    return result


@router.get("/{loan_id}")
def get_loan_detail(
    loan_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    loan = db.query(models.BankLoan).filter(
        models.BankLoan.id == loan_id,
        models.BankLoan.company_id == current_user.company_id
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    payments = (
        db.query(models.BankLoanPayment)
        .filter(models.BankLoanPayment.loan_id == loan_id)
        .order_by(models.BankLoanPayment.payment_date.asc())
        .all()
    )

    balance = get_loan_balance(loan_id, db)

    return {
        "loan": loan,
        "payments": payments,
        "balance_remaining": balance,
        "total_interest_paid": sum(float(p.interest_portion) for p in payments),
        "total_principal_paid": sum(float(p.principal_portion) for p in payments),
    }


@router.post("/{loan_id}/payments")
def log_payment(
    loan_id: str,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    loan = db.query(models.BankLoan).filter(
        models.BankLoan.id == loan_id,
        models.BankLoan.company_id == current_user.company_id
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    current_balance = get_loan_balance(loan_id, db)

    if current_balance <= 0:
        raise HTTPException(status_code=400, detail="Loan is already fully repaid")

    interest_portion, principal_portion, balance_after = calculate_interest_split(
        loan, data.amount_paid, current_balance
    )

    payment = models.BankLoanPayment(
        loan_id=loan_id,
        payment_date=data.payment_date,
        amount_paid=data.amount_paid,
        interest_portion=interest_portion,
        principal_portion=principal_portion,
        balance_after=balance_after,
        notes=data.notes,
    )
    db.add(payment)

    # Mark loan as inactive if fully repaid
    if balance_after <= 0:
        loan.is_active = False

    db.commit()
    db.refresh(payment)

    return {
        "payment": payment,
        "interest_portion": interest_portion,
        "principal_portion": principal_portion,
        "balance_after": balance_after,
        "message": "Loan fully repaid!" if balance_after <= 0 else f"Balance remaining: {balance_after:,.2f} TZS"
    }


@router.delete("/{loan_id}")
def delete_loan(
    loan_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    loan = db.query(models.BankLoan).filter(
        models.BankLoan.id == loan_id,
        models.BankLoan.company_id == current_user.company_id
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    loan.is_active = False
    db.commit()
    return {"message": "Loan removed"}