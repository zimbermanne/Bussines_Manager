from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from core.security import get_current_user
from database import get_db

router = APIRouter(prefix="/customers", tags=["Customers"])


class CustomerCreate(BaseModel):
    full_name: str
    business_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    physical_address: Optional[str] = None
    customer_type: str = "individual"
    tin: Optional[str] = None
    notes: Optional[str] = None


@router.get("/")
def get_customers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    customers = (
        db.query(models.Customer)
        .filter(models.Customer.company_id == current_user.company_id)
        .filter(models.Customer.is_active == True)
        .order_by(models.Customer.full_name)
        .all()
    )
    return customers


@router.post("/")
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    customer = models.Customer(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}")
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.company_id == current_user.company_id
    ).first()
    
    if not customer:
        return None
    
    # Get customer sales history
    sales = db.query(models.CustomerSale).filter(
        models.CustomerSale.customer_id == customer_id
    ).order_by(models.CustomerSale.sale_date.desc()).limit(20).all()
    
    total_purchased = sum(float(s.amount) for s in sales)
    
    return {
        "customer": customer,
        "sales_history": sales,
        "total_purchased": total_purchased,
        "last_purchase_date": sales[0].sale_date if sales else None
    }