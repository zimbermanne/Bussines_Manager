from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from database import get_db
from core.security import get_current_user
import models

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ── Schemas ──────────────────────────────────────────────────

class ItemCreate(BaseModel):
    business_unit_id:   Optional[str] = None
    name:               str
    sku:                Optional[str] = None
    category:           Optional[str] = None
    unit:               Optional[str] = None
    quantity_in_stock:  float = 0
    reorder_level:      float = 0
    unit_cost:          Optional[float] = None
    unit_price:         Optional[float] = None


class ItemUpdate(BaseModel):
    name:               Optional[str] = None
    sku:                Optional[str] = None
    category:           Optional[str] = None
    unit:               Optional[str] = None
    reorder_level:      Optional[float] = None
    unit_cost:          Optional[float] = None
    unit_price:         Optional[float] = None


class StockAdjustment(BaseModel):
    quantity:   float   # positive = add stock, negative = remove
    notes:      Optional[str] = None


# ── Helper ───────────────────────────────────────────────────

def log_stock_movement(
    db: Session,
    company_id: str,
    item: models.InventoryItem,
    movement_type: str,
    quantity: float,
    reference_id: str = None,
    reference_table: str = None,
    notes: str = None,
    created_by: str = None
):
    qty_before = float(item.quantity_in_stock)
    qty_after = qty_before + quantity

    movement = models.StockMovement(
        company_id=company_id,
        item_id=item.id,
        movement_type=movement_type,
        quantity=quantity,
        quantity_before=qty_before,
        quantity_after=qty_after,
        reference_id=reference_id,
        reference_table=reference_table,
        notes=notes,
        created_by=created_by,
    )
    db.add(movement)

    item.quantity_in_stock = qty_after
    item.updated_at = datetime.utcnow()


# ── Routes ───────────────────────────────────────────────────

@router.get("/")
def list_items(
    business_unit_id: Optional[str] = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    q = db.query(models.InventoryItem).filter(
        models.InventoryItem.company_id == current_user.company_id,
        models.InventoryItem.is_active == True
    )
    if business_unit_id:
        q = q.filter(models.InventoryItem.business_unit_id == business_unit_id)
    if low_stock_only:
        q = q.filter(
            models.InventoryItem.quantity_in_stock <= models.InventoryItem.reorder_level
        )
    items = q.order_by(models.InventoryItem.name.asc()).all()

    # Annotate with low stock flag
    result = []
    for item in items:
        d = {
            "id": item.id,
            "name": item.name,
            "sku": item.sku,
            "category": item.category,
            "unit": item.unit,
            "quantity_in_stock": float(item.quantity_in_stock),
            "reorder_level": float(item.reorder_level or 0),
            "unit_cost": float(item.unit_cost) if item.unit_cost else None,
            "unit_price": float(item.unit_price) if item.unit_price else None,
            "business_unit_id": item.business_unit_id,
            "low_stock": float(item.quantity_in_stock) <= float(item.reorder_level or 0),
            "stock_value": round(float(item.quantity_in_stock) * float(item.unit_cost or 0), 2),
        }
        result.append(d)
    return result


@router.post("/")
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    item = models.InventoryItem(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(item)
    db.flush()

    # Log initial stock if any
    if data.quantity_in_stock > 0:
        log_stock_movement(
            db=db,
            company_id=current_user.company_id,
            item=item,
            movement_type="adjustment",
            quantity=data.quantity_in_stock,
            notes="Initial stock entry",
            created_by=current_user.id,
        )

    db.commit()
    db.refresh(item)

    # Activity log
    _log_activity(db, current_user, "created", "inventory_item", item.id, f"Added item: {item.name}")
    return item


@router.put("/{item_id}")
def update_item(
    item_id: str,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    item = db.query(models.InventoryItem).filter(
        models.InventoryItem.id == item_id,
        models.InventoryItem.company_id == current_user.company_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    item.updated_at = datetime.utcnow()

    db.commit()
    _log_activity(db, current_user, "updated", "inventory_item", item.id, f"Updated item: {item.name}")
    return item


@router.post("/{item_id}/adjust")
def adjust_stock(
    item_id: str,
    data: StockAdjustment,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    item = db.query(models.InventoryItem).filter(
        models.InventoryItem.id == item_id,
        models.InventoryItem.company_id == current_user.company_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    new_qty = float(item.quantity_in_stock) + data.quantity
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="Stock cannot go below zero")

    log_stock_movement(
        db=db,
        company_id=current_user.company_id,
        item=item,
        movement_type="adjustment",
        quantity=data.quantity,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.commit()

    _log_activity(db, current_user, "adjusted", "inventory_item", item.id,
                  f"Stock adjustment: {data.quantity:+.2f} units. New qty: {new_qty}")
    return {"item_id": item_id, "new_quantity": new_qty}


@router.get("/{item_id}/movements")
def get_stock_movements(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    item = db.query(models.InventoryItem).filter(
        models.InventoryItem.id == item_id,
        models.InventoryItem.company_id == current_user.company_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    movements = (
        db.query(models.StockMovement)
        .filter(models.StockMovement.item_id == item_id)
        .order_by(models.StockMovement.created_at.desc())
        .all()
    )
    return {"item": item, "movements": movements}


@router.get("/summary/value")
def stock_value_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Total inventory value and low stock count."""
    items = db.query(models.InventoryItem).filter(
        models.InventoryItem.company_id == current_user.company_id,
        models.InventoryItem.is_active == True
    ).all()

    total_value = sum(
        float(i.quantity_in_stock) * float(i.unit_cost or 0) for i in items
    )
    low_stock_count = sum(
        1 for i in items
        if float(i.quantity_in_stock) <= float(i.reorder_level or 0)
    )

    return {
        "total_items": len(items),
        "total_stock_value_tzs": round(total_value, 2),
        "low_stock_items": low_stock_count,
    }


@router.delete("/{item_id}")
def deactivate_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    item = db.query(models.InventoryItem).filter(
        models.InventoryItem.id == item_id,
        models.InventoryItem.company_id == current_user.company_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.is_active = False
    db.commit()
    _log_activity(db, current_user, "deleted", "inventory_item", item.id, f"Removed item: {item.name}")
    return {"message": "Item removed"}


# ── Activity log helper ───────────────────────────────────────

def _log_activity(db, user, action, entity_type, entity_id, description):
    log = models.ActivityLog(
        company_id=user.company_id,
        user_id=user.id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        description=description,
    )
    db.add(log)
    db.commit()
