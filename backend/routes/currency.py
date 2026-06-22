from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from core.security import get_current_user
from database import get_db

router = APIRouter(prefix="/currency", tags=["Currency"])


class ExchangeRateCreate(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    effective_date: date = date.today()


@router.get("/rates")
def get_exchange_rates(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    rates = (
        db.query(models.ExchangeRate)
        .order_by(models.ExchangeRate.effective_date.desc())
        .limit(50)
        .all()
    )
    return rates


@router.post("/rates")
def create_exchange_rate(
    data: ExchangeRateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    rate = models.ExchangeRate(**data.model_dump())
    db.add(rate)
    db.commit()
    db.refresh(rate)
    return rate


@router.get("/convert")
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    db: Session = Depends(get_db)
):
    if from_currency == to_currency:
        return {"converted_amount": amount, "rate": 1.0}
    
    # Find latest exchange rate
    rate = db.query(models.ExchangeRate).filter(
        models.ExchangeRate.from_currency == from_currency,
        models.ExchangeRate.to_currency == to_currency
    ).order_by(models.ExchangeRate.effective_date.desc()).first()
    
    if not rate:
        return {"error": "Exchange rate not found"}
    
    converted_amount = amount * float(rate.rate)
    return {"converted_amount": converted_amount, "rate": float(rate.rate)}