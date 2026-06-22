from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from core.security import get_current_user
from database import get_db

router = APIRouter(prefix="/inventory", tags=["Inventory"])


class InventoryItemCreate(BaseModel):
    item_name: str
    sku: Optional[str] = None
    unit: Optional[str] = None
    current_quantity: float = 0
    reorder_level: float = 0
    reorder_quantity: float = 0
    preferred_supplier_id: Optional[str] = None
    unit_cost: Optional[float] = None
    unit_price: Optional[float] = None


@router.get("/items")
def get_inventory_items(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    items = (
        db.query(models.InventoryItem)
        .filter(models.InventoryItem.company_id == current_user.company_id)
        .filter(models.InventoryItem.is_active == True)
        .order_by(models.InventoryItem.item_name)
        .all()
    )
    return items


@router.post("/items")
def create_inventory_item(
    data: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    item = models.InventoryItem(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(item)
    
    # Check if reorder level is already reached
    if data.current_quantity <= data.reorder_level:
        alert = models.ReorderAlert(
            company_id=current_user.company_id,
            inventory_item_id=item.id,
            current_quantity=data.current_quantity,
            reorder_level=data.reorder_level,
            status="triggered"
        )
        db.add(alert)
    
    db.commit()
    db.refresh(item)
    return item


@router.put("/items/{item_id}")
def update_inventory_item(
    item_id: str,
    current_quantity: float,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    item = db.query(models.InventoryItem).filter(
        models.InventoryItem.id == item_id,
        models.InventoryItem.company_id == current_user.company_id
    ).first()
    
    if not item:
        return None
    
    old_quantity = item.current_quantity
    item.current_quantity = current_quantity
    
    # Check if reorder level is reached
    if current_quantity <= item.reorder_level and old_quantity > item.reorder_level:
        alert = models.ReorderAlert(
            company_id=current_user.company_id,
            inventory_item_id=item.id,
            current_quantity=current_quantity,
            reorder_level=item.reorder_level,
            status="triggered"
        )
        db.add(alert)
    
    # Check if reorder alert is resolved
    if current_quantity > item.reorder_level:
        existing_alert = db.query(models.ReorderAlert).filter(
            models.ReorderAlert.inventory_item_id == item_id,
            models.ReorderAlert.status == "triggered"
        ).first()
        if existing_alert:
            existing_alert.status = "resolved"
    
    db.commit()
    db.refresh(item)
    return item


@router.get("/alerts")
def get_reorder_alerts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    alerts = (
        db.query(models.ReorderAlert)
        .filter(models.ReorderAlert.company_id == current_user.company_id)
        .filter(models.ReorderAlert.status == "triggered")
        .order_by(models.ReorderAlert.alert_date.desc())
        .all()
    )
    return alerts


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    alert = db.query(models.ReorderAlert).filter(
        models.ReorderAlert.id == alert_id,
        models.ReorderAlert.company_id == current_user.company_id
    ).first()
    
    if alert:
        alert.status = "resolved"
        db.commit()
    
    return {"message": "Alert resolved"}