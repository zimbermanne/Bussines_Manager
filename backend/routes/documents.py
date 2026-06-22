from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from core.security import get_current_user
from database import get_db

router = APIRouter(prefix="/documents", tags=["Documents"])


class DocumentItemCreate(BaseModel):
    description: str
    quantity: float
    unit: Optional[str] = None
    unit_price: float


class DocumentCreate(BaseModel):
    document_type: str  # QUO, PRO, INV, RCP, CRN, DBN, DLN
    receiver_company_id: str
    issue_date: date = date.today()
    due_date: Optional[date] = None
    currency: str = "TZS"
    exchange_rate: float = 1
    vat_rate: float = 18
    notes: Optional[str] = None
    client_name: str
    client_address: str
    client_tin: Optional[str] = None
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    items: list[DocumentItemCreate]


@router.get("/inbox")
def get_inbox(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    documents = (
        db.query(models.BusinessDocument)
        .filter(models.BusinessDocument.receiver_company_id == current_user.company_id)
        .order_by(models.BusinessDocument.created_at.desc())
        .all()
    )
    return documents


@router.get("/outbox")
def get_outbox(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    documents = (
        db.query(models.BusinessDocument)
        .filter(models.BusinessDocument.sender_company_id == current_user.company_id)
        .order_by(models.BusinessDocument.created_at.desc())
        .all()
    )
    return documents


@router.post("/")
def create_document(
    data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify receiver company exists
    receiver = db.query(models.Company).filter(models.Company.id == data.receiver_company_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver company not found")

    # Generate document number
    import uuid
    doc_number = f"{data.document_type}-{date.today().year}-{str(uuid.uuid4())[:8].upper()}"

    # Create document
    document = models.BusinessDocument(
        company_id=current_user.company_id,
        sender_company_id=current_user.company_id,
        receiver_company_id=data.receiver_company_id,
        document_type=data.document_type,
        document_number=doc_number,
        issue_date=data.issue_date,
        due_date=data.due_date,
        currency=data.currency,
        exchange_rate=data.exchange_rate,
        vat_rate=data.vat_rate,
        notes=data.notes,
        client_name=data.client_name,
        client_address=data.client_address,
        client_tin=data.client_tin,
        client_phone=data.client_phone,
        client_email=data.client_email,
        status="sent"
    )
    db.add(document)
    db.flush()

    # Add items
    subtotal = 0
    for item_data in data.items:
        item_total = item_data.quantity * item_data.unit_price
        subtotal += item_total
        
        item = models.DocumentItem(
            document_id=document.id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit=item_data.unit,
            unit_price=item_data.unit_price,
            total=item_total
        )
        db.add(item)

    # Calculate totals
    vat_amount = subtotal * (data.vat_rate / 100)
    grand_total = subtotal + vat_amount

    document.subtotal = subtotal
    document.vat_amount = vat_amount
    document.grand_total = grand_total

    # Create sent event
    event = models.DocumentEvent(
        document_id=document.id,
        status="sent",
        changed_by_user_id=current_user.id
    )
    db.add(event)

    db.commit()
    db.refresh(document)
    return document


@router.post("/{document_id}/confirm")
def confirm_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    document = db.query(models.BusinessDocument).filter(
        models.BusinessDocument.id == document_id,
        models.BusinessDocument.receiver_company_id == current_user.company_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = "confirmed"
    
    event = models.DocumentEvent(
        document_id=document_id,
        status="confirmed",
        changed_by_user_id=current_user.id
    )
    db.add(event)
    
    db.commit()
    return {"message": "Document confirmed"}


@router.post("/{document_id}/reject")
def reject_document(
    document_id: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    document = db.query(models.BusinessDocument).filter(
        models.BusinessDocument.id == document_id,
        models.BusinessDocument.receiver_company_id == current_user.company_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = "rejected"
    document.rejection_reason = reason
    
    event = models.DocumentEvent(
        document_id=document_id,
        status="rejected",
        changed_by_user_id=current_user.id,
        notes=reason
    )
    db.add(event)
    
    db.commit()
    return {"message": "Document rejected"}


@router.get("/{document_id}")
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    document = db.query(models.BusinessDocument).filter(
        models.BusinessDocument.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check access
    if document.sender_company_id != current_user.company_id and document.receiver_company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    items = db.query(models.DocumentItem).filter(
        models.DocumentItem.document_id == document_id
    ).all()
    
    events = db.query(models.DocumentEvent).filter(
        models.DocumentEvent.document_id == document_id
    ).order_by(models.DocumentEvent.created_at).all()
    
    return {
        "document": document,
        "items": items,
        "events": events
    }