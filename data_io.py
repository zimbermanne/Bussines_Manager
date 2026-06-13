from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from core.security import get_current_user
import models
import csv
import io

router = APIRouter(prefix="/data", tags=["Import & Export"])


# ── CSV Export ───────────────────────────────────────────────

def make_csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    if not rows:
        raise HTTPException(status_code=404, detail="No data to export")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/sales")
def export_sales(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    sales = db.query(models.SaleEntry).filter(
        models.SaleEntry.company_id == current_user.company_id
    ).order_by(models.SaleEntry.sale_date.desc()).all()

    rows = [
        {
            "date": s.sale_date,
            "item_name": s.item_name,
            "quantity": float(s.quantity),
            "unit_price": float(s.unit_price),
            "total_amount": float(s.total_amount),
            "notes": s.notes or "",
        }
        for s in sales
    ]
    return make_csv_response(rows, f"sales_{date.today()}.csv")


@router.get("/export/purchases")
def export_purchases(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    purchases = db.query(models.Purchase).filter(
        models.Purchase.company_id == current_user.company_id
    ).order_by(models.Purchase.purchase_date.desc()).all()

    rows = [
        {
            "date": p.purchase_date,
            "item_name": p.item_name,
            "quantity": float(p.quantity),
            "unit_cost": float(p.unit_cost),
            "total_cost": float(p.total_cost),
            "notes": p.notes or "",
        }
        for p in purchases
    ]
    return make_csv_response(rows, f"purchases_{date.today()}.csv")


@router.get("/export/expenses")
def export_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    expenses = db.query(models.Expense).filter(
        models.Expense.company_id == current_user.company_id
    ).order_by(models.Expense.expense_date.desc()).all()

    rows = [
        {
            "date": e.expense_date,
            "category": e.category,
            "description": e.description or "",
            "amount": float(e.amount),
        }
        for e in expenses
    ]
    return make_csv_response(rows, f"expenses_{date.today()}.csv")


@router.get("/export/inventory")
def export_inventory(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    items = db.query(models.InventoryItem).filter(
        models.InventoryItem.company_id == current_user.company_id,
        models.InventoryItem.is_active == True
    ).all()

    rows = [
        {
            "name": i.name,
            "sku": i.sku or "",
            "category": i.category or "",
            "unit": i.unit or "",
            "quantity_in_stock": float(i.quantity_in_stock),
            "reorder_level": float(i.reorder_level or 0),
            "unit_cost": float(i.unit_cost) if i.unit_cost else "",
            "unit_price": float(i.unit_price) if i.unit_price else "",
        }
        for i in items
    ]
    return make_csv_response(rows, f"inventory_{date.today()}.csv")


@router.get("/export/debtors")
def export_debtors(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    records = db.query(models.DebtorRecord).filter(
        models.DebtorRecord.company_id == current_user.company_id
    ).all()

    rows = []
    for r in records:
        contact = db.query(models.Contact).filter(models.Contact.id == r.contact_id).first()
        rows.append({
            "contact_name": contact.name if contact else "",
            "contact_phone": contact.phone if contact else "",
            "description": r.description,
            "amount_owed": float(r.amount_owed),
            "amount_paid": float(r.amount_paid),
            "balance": float(r.balance),
            "due_date": r.due_date or "",
            "status": r.status,
        })
    return make_csv_response(rows, f"debtors_{date.today()}.csv")


@router.get("/export/all")
def export_full_backup(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Export all data as a single ZIP file.
    Each module becomes a separate CSV inside the ZIP.
    """
    import zipfile

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:

        def write_csv(name, rows):
            if not rows:
                return
            out = io.StringIO()
            writer = csv.DictWriter(out, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            zf.writestr(name, out.getvalue())

        # Sales
        sales = db.query(models.SaleEntry).filter(
            models.SaleEntry.company_id == current_user.company_id
        ).all()
        write_csv("sales.csv", [
            {"date": s.sale_date, "item": s.item_name, "qty": float(s.quantity),
             "unit_price": float(s.unit_price), "total": float(s.total_amount)}
            for s in sales
        ])

        # Purchases
        purchases = db.query(models.Purchase).filter(
            models.Purchase.company_id == current_user.company_id
        ).all()
        write_csv("purchases.csv", [
            {"date": p.purchase_date, "item": p.item_name, "qty": float(p.quantity),
             "unit_cost": float(p.unit_cost), "total": float(p.total_cost)}
            for p in purchases
        ])

        # Expenses
        expenses = db.query(models.Expense).filter(
            models.Expense.company_id == current_user.company_id
        ).all()
        write_csv("expenses.csv", [
            {"date": e.expense_date, "category": e.category,
             "description": e.description, "amount": float(e.amount)}
            for e in expenses
        ])

        # Inventory
        items = db.query(models.InventoryItem).filter(
            models.InventoryItem.company_id == current_user.company_id
        ).all()
        write_csv("inventory.csv", [
            {"name": i.name, "sku": i.sku, "category": i.category,
             "qty": float(i.quantity_in_stock), "unit_cost": float(i.unit_cost or 0)}
            for i in items
        ])

        # Debtors
        debtors = db.query(models.DebtorRecord).filter(
            models.DebtorRecord.company_id == current_user.company_id
        ).all()
        write_csv("debtors.csv", [
            {"description": r.description, "amount_owed": float(r.amount_owed),
             "balance": float(r.balance), "status": r.status}
            for r in debtors
        ])

    buffer.seek(0)
    filename = f"company_manager_backup_{date.today()}.zip"
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ── CSV Import ───────────────────────────────────────────────

@router.post("/import/sales")
async def import_sales(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Import sales from CSV.
    Required columns: date, item_name, quantity, unit_price
    Optional: notes
    """
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    imported = 0
    errors = []

    for i, row in enumerate(reader, start=2):
        try:
            qty = float(row["quantity"])
            price = float(row["unit_price"])
            sale = models.SaleEntry(
                company_id=current_user.company_id,
                sale_date=row["date"],
                item_name=row["item_name"].strip(),
                quantity=qty,
                unit_price=price,
                total_amount=round(qty * price, 2),
                notes=row.get("notes", ""),
            )
            db.add(sale)
            imported += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    db.commit()

    # Log activity
    log = models.ActivityLog(
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="import",
        entity_type="sales",
        description=f"Imported {imported} sales from CSV. Errors: {len(errors)}"
    )
    db.add(log)
    db.commit()

    return {
        "imported": imported,
        "errors": errors,
        "message": f"Successfully imported {imported} sales records."
    }


@router.post("/import/purchases")
async def import_purchases(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Import purchases from CSV.
    Required columns: date, item_name, quantity, unit_cost
    Optional: notes
    """
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    imported = 0
    errors = []

    for i, row in enumerate(reader, start=2):
        try:
            qty = float(row["quantity"])
            cost = float(row["unit_cost"])
            purchase = models.Purchase(
                company_id=current_user.company_id,
                purchase_date=row["date"],
                item_name=row["item_name"].strip(),
                quantity=qty,
                unit_cost=cost,
                total_cost=round(qty * cost, 2),
                notes=row.get("notes", ""),
            )
            db.add(purchase)
            imported += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    db.commit()

    log = models.ActivityLog(
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="import",
        entity_type="purchases",
        description=f"Imported {imported} purchases from CSV. Errors: {len(errors)}"
    )
    db.add(log)
    db.commit()

    return {
        "imported": imported,
        "errors": errors,
        "message": f"Successfully imported {imported} purchase records."
    }
