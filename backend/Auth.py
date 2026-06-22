from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from core.security import hash_password, verify_password, create_access_token
import models

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    company_name:   str
    full_name:      str
    email:          EmailStr
    password:       str
    tin:            str | None = None
    brela_number:   str | None = None
    region:         str | None = None
    district:       str | None = None
    phone:          str | None = None


class TokenResponse(BaseModel):
    access_token:   str
    token_type:     str = "bearer"
    company_id:     str
    user_id:        str
    full_name:      str


@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check email not already used
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create company
    company = models.Company(
        name=data.company_name,
        tin=data.tin,
        brela_number=data.brela_number,
        region=data.region,
        district=data.district,
        phone=data.phone,
    )
    db.add(company)
    db.flush()  # get company.id without committing

    # Create 14-day trial subscription
    from datetime import date, timedelta
    trial = models.Subscription(
        company_id=company.id,
        plan="trial",
        price_tzs=0,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=14),
    )
    db.add(trial)

    # Create user
    user = models.User(
        company_id=company.id,
        full_name=data.full_name,
        email=data.email,
        password_hash=hash_password(data.password),
        role="owner",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id})
    return TokenResponse(
        access_token=token,
        company_id=company.id,
        user_id=user.id,
        full_name=user.full_name,
    )


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    token = create_access_token({"sub": user.id})
    return TokenResponse(
        access_token=token,
        company_id=user.company_id,
        user_id=user.id,
        full_name=user.full_name,
    )