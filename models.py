import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Boolean, Integer, Numeric,
    Text, Date, DateTime, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


def gen_uuid():
    return str(uuid.uuid4())


# ─── AUTH & COMPANIES ────────────────────────────────────────

class Company(Base):
    __tablename__ = "companies"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name            = Column(String(255), nullable=False)
    tin             = Column(String(50))
    brela_number    = Column(String(100))
    business_name   = Column(String(255))
    address         = Column(Text)
    phone           = Column(String(30))
    email           = Column(String(255))
    region          = Column(String(100))
    district        = Column(String(100))
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users           = relationship("User", back_populates="company")
    subscriptions   = relationship("Subscription", back_populates="company")
    deadlines       = relationship("Deadline", back_populates="company")
    bank_loans      = relationship("BankLoan", back_populates="company")
    vikoba_groups   = relationship("VikobaGroup", back_populates="company")
    business_units  = relationship("BusinessUnit", back_populates="company")
    sales_entries   = relationship("SaleEntry", back_populates="company")
    purchases       = relationship("Purchase", back_populates="company")
    expenses        = relationship("Expense", back_populates="company")
    suppliers       = relationship("Supplier", back_populates="company")
    tenders         = relationship("Tender", back_populates="company")
    notifications   = relationship("NotificationLog", back_populates="company")


class User(Base):
    __tablename__ = "users"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id          = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    full_name           = Column(String(255), nullable=False)
    email               = Column(String(255), unique=True, nullable=False)
    password_hash       = Column(Text, nullable=False)
    role                = Column(String(50), default="owner")
    push_subscription   = Column(JSON)
    is_active           = Column(Boolean, default=True)
    created_at          = Column(DateTime, default=datetime.utcnow)

    company             = relationship("Company", back_populates="users")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id          = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id  = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    plan        = Column(String(50), default="trial")
    price_tzs   = Column(Integer, default=0)
    start_date  = Column(Date, default=date.today)
    end_date    = Column(Date)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    company     = relationship("Company", back_populates="subscriptions")


# ─── COMPLIANCE DEADLINES ────────────────────────────────────

class Deadline(Base):
    __tablename__ = "deadlines"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id      = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name            = Column(String(255), nullable=False)
    category        = Column(String(100), nullable=False)
    interval_type   = Column(String(50), nullable=False)
    due_day         = Column(Integer)
    due_month       = Column(Integer)
    next_due_date   = Column(Date, nullable=False)
    notes           = Column(Text)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    company         = relationship("Company", back_populates="deadlines")


# ─── BANK LOANS ──────────────────────────────────────────────

class BankLoan(Base):
    __tablename__ = "bank_loans"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id          = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    lender_name         = Column(String(255), nullable=False)
    principal_amount    = Column(Numeric(15, 2), nullable=False)
    interest_type       = Column(String(50), nullable=False)   # simple, reducing_balance
    interest_rate       = Column(Numeric(8, 4), nullable=False) # annual %
    start_date          = Column(Date, nullable=False)
    due_day             = Column(Integer, nullable=False)
    grace_period_months = Column(Integer, default=0)
    notes               = Column(Text)
    is_active           = Column(Boolean, default=True)
    created_at          = Column(DateTime, default=datetime.utcnow)

    company             = relationship("Company", back_populates="bank_loans")
    payments            = relationship("BankLoanPayment", back_populates="loan")


class BankLoanPayment(Base):
    __tablename__ = "bank_loan_payments"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    loan_id             = Column(UUID(as_uuid=False), ForeignKey("bank_loans.id", ondelete="CASCADE"), nullable=False)
    payment_date        = Column(Date, nullable=False)
    amount_paid         = Column(Numeric(15, 2), nullable=False)
    interest_portion    = Column(Numeric(15, 2), nullable=False)
    principal_portion   = Column(Numeric(15, 2), nullable=False)
    balance_after       = Column(Numeric(15, 2), nullable=False)
    notes               = Column(Text)
    created_at          = Column(DateTime, default=datetime.utcnow)

    loan                = relationship("BankLoan", back_populates="payments")


# ─── VIKOBA ──────────────────────────────────────────────────

class VikobaGroup(Base):
    __tablename__ = "vikoba_groups"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id          = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name                = Column(String(255), nullable=False)
    lifespan_type       = Column(String(50), nullable=False)   # one_year, two_years, permanent
    start_date          = Column(Date, nullable=False)
    end_date            = Column(Date)
    interval_type       = Column(String(50), nullable=False)   # daily, weekly, monthly
    hisa_amount         = Column(Numeric(15, 2), nullable=False)
    penalty_type        = Column(String(50), nullable=False)   # fixed, percentage, custom
    penalty_value       = Column(Numeric(15, 2))
    loan_interest_rate  = Column(Numeric(8, 4), default=0)
    is_dissolved        = Column(Boolean, default=False)
    dissolved_at        = Column(Date)
    notes               = Column(Text)
    created_at          = Column(DateTime, default=datetime.utcnow)

    company             = relationship("Company", back_populates="vikoba_groups")
    members             = relationship("VikobaMember", back_populates="group")
    hisa_payments       = relationship("HisaPayment", back_populates="group")
    loans               = relationship("VikobaLoan", back_populates="group")


class VikobaMember(Base):
    __tablename__ = "vikoba_members"

    id          = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    group_id    = Column(UUID(as_uuid=False), ForeignKey("vikoba_groups.id", ondelete="CASCADE"), nullable=False)
    full_name   = Column(String(255), nullable=False)
    phone       = Column(String(30))
    joined_date = Column(Date, default=date.today)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    group           = relationship("VikobaGroup", back_populates="members")
    hisa_payments   = relationship("HisaPayment", back_populates="member")
    penalties       = relationship("HisaPenalty", back_populates="member")
    loans           = relationship("VikobaLoan", back_populates="member")


class HisaPayment(Base):
    __tablename__ = "hisa_payments"

    id          = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    group_id    = Column(UUID(as_uuid=False), ForeignKey("vikoba_groups.id", ondelete="CASCADE"), nullable=False)
    member_id   = Column(UUID(as_uuid=False), ForeignKey("vikoba_members.id", ondelete="CASCADE"), nullable=False)
    due_date    = Column(Date, nullable=False)
    paid_date   = Column(Date)
    amount      = Column(Numeric(15, 2), nullable=False)
    status      = Column(String(50), default="pending")  # pending, paid, missed
    created_at  = Column(DateTime, default=datetime.utcnow)

    group       = relationship("VikobaGroup", back_populates="hisa_payments")
    member      = relationship("VikobaMember", back_populates="hisa_payments")
    penalties   = relationship("HisaPenalty", back_populates="hisa")


class HisaPenalty(Base):
    __tablename__ = "hisa_penalties"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    group_id        = Column(UUID(as_uuid=False), ForeignKey("vikoba_groups.id", ondelete="CASCADE"), nullable=False)
    member_id       = Column(UUID(as_uuid=False), ForeignKey("vikoba_members.id", ondelete="CASCADE"), nullable=False)
    hisa_id         = Column(UUID(as_uuid=False), ForeignKey("hisa_payments.id", ondelete="CASCADE"), nullable=False)
    penalty_date    = Column(Date, default=date.today)
    amount          = Column(Numeric(15, 2), nullable=False)
    status          = Column(String(50), default="unpaid")  # unpaid, paid
    paid_date       = Column(Date)
    created_at      = Column(DateTime, default=datetime.utcnow)

    member      = relationship("VikobaMember", back_populates="penalties")
    hisa        = relationship("HisaPayment", back_populates="penalties")


class VikobaLoan(Base):
    __tablename__ = "vikoba_loans"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    group_id            = Column(UUID(as_uuid=False), ForeignKey("vikoba_groups.id", ondelete="CASCADE"), nullable=False)
    member_id           = Column(UUID(as_uuid=False), ForeignKey("vikoba_members.id", ondelete="CASCADE"), nullable=False)
    loan_amount         = Column(Numeric(15, 2), nullable=False)
    interest_rate       = Column(Numeric(8, 4), nullable=False)
    issued_date         = Column(Date, nullable=False)
    repayment_interval  = Column(String(50), nullable=False)  # weekly, monthly
    due_day             = Column(Integer)
    is_fully_repaid     = Column(Boolean, default=False)
    notes               = Column(Text)
    created_at          = Column(DateTime, default=datetime.utcnow)

    group       = relationship("VikobaGroup", back_populates="loans")
    member      = relationship("VikobaMember", back_populates="loans")
    repayments  = relationship("VikobaLoanRepayment", back_populates="loan")


class VikobaLoanRepayment(Base):
    __tablename__ = "vikoba_loan_repayments"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    vikoba_loan_id      = Column(UUID(as_uuid=False), ForeignKey("vikoba_loans.id", ondelete="CASCADE"), nullable=False)
    payment_date        = Column(Date, nullable=False)
    amount_paid         = Column(Numeric(15, 2), nullable=False)
    interest_portion    = Column(Numeric(15, 2), nullable=False)
    principal_portion   = Column(Numeric(15, 2), nullable=False)
    balance_after       = Column(Numeric(15, 2), nullable=False)
    created_at          = Column(DateTime, default=datetime.utcnow)

    loan        = relationship("VikobaLoan", back_populates="repayments")


# ─── BUSINESS UNITS, SALES, PURCHASES, EXPENSES ──────────────

class BusinessUnit(Base):
    __tablename__ = "business_units"

    id          = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id  = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name        = Column(String(255), nullable=False)
    type        = Column(String(100))
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    company     = relationship("Company", back_populates="business_units")
    sales       = relationship("SaleEntry", back_populates="business_unit")
    purchases   = relationship("Purchase", back_populates="business_unit")
    expenses    = relationship("Expense", back_populates="business_unit")


class SaleEntry(Base):
    __tablename__ = "sales_entries"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id          = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    business_unit_id    = Column(UUID(as_uuid=False), ForeignKey("business_units.id"))
    sale_date           = Column(Date, default=date.today, nullable=False)
    item_name           = Column(String(255), nullable=False)
    quantity            = Column(Numeric(10, 2), nullable=False)
    unit_price          = Column(Numeric(15, 2), nullable=False)
    total_amount        = Column(Numeric(15, 2), nullable=False)  # computed on save
    notes               = Column(Text)
    created_at          = Column(DateTime, default=datetime.utcnow)

    company             = relationship("Company", back_populates="sales_entries")
    business_unit       = relationship("BusinessUnit", back_populates="sales")


class Purchase(Base):
    __tablename__ = "purchases"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id          = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    business_unit_id    = Column(UUID(as_uuid=False), ForeignKey("business_units.id"))
    supplier_id         = Column(UUID(as_uuid=False), ForeignKey("suppliers.id", ondelete="SET NULL"))
    purchase_date       = Column(Date, default=date.today, nullable=False)
    item_name           = Column(String(255), nullable=False)
    quantity            = Column(Numeric(10, 2), nullable=False)
    unit_cost           = Column(Numeric(15, 2), nullable=False)
    total_cost          = Column(Numeric(15, 2), nullable=False)  # computed on save
    notes               = Column(Text)
    created_at          = Column(DateTime, default=datetime.utcnow)

    company             = relationship("Company", back_populates="purchases")
    business_unit       = relationship("BusinessUnit", back_populates="purchases")
    supplier            = relationship("Supplier", back_populates="purchases")


class Expense(Base):
    __tablename__ = "expenses"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id          = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    business_unit_id    = Column(UUID(as_uuid=False), ForeignKey("business_units.id"))
    expense_date        = Column(Date, default=date.today, nullable=False)
    category            = Column(String(100), nullable=False)
    description         = Column(Text)
    amount              = Column(Numeric(15, 2), nullable=False)
    created_at          = Column(DateTime, default=datetime.utcnow)

    company             = relationship("Company", back_populates="expenses")
    business_unit       = relationship("BusinessUnit", back_populates="expenses")


# ─── SUPPLIERS ───────────────────────────────────────────────

class Supplier(Base):
    __tablename__ = "suppliers"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id      = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name            = Column(String(255), nullable=False)
    contact_phone   = Column(String(30))
    contact_email   = Column(String(255))
    location        = Column(Text)
    items_supplied  = Column(Text)
    notes           = Column(Text)
    created_at      = Column(DateTime, default=datetime.utcnow)

    company         = relationship("Company", back_populates="suppliers")
    purchases       = relationship("Purchase", back_populates="supplier")
    procurement     = relationship("ProcurementItem", back_populates="supplier")


# ─── TENDERS & PROCUREMENT ───────────────────────────────────

class Tender(Base):
    __tablename__ = "tenders"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id          = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name                = Column(String(255), nullable=False)
    reference_number    = Column(String(255))
    client              = Column(String(255))
    tender_value        = Column(Numeric(15, 2))
    procurement_budget  = Column(Numeric(15, 2))
    submission_deadline = Column(Date)
    delivery_deadline   = Column(Date, nullable=False)
    status              = Column(String(50), default="planning")  # planning, won, active, completed, lost
    notes               = Column(Text)
    created_at          = Column(DateTime, default=datetime.utcnow)

    company             = relationship("Company", back_populates="tenders")
    procurement_items   = relationship("ProcurementItem", back_populates="tender")


class ProcurementItem(Base):
    __tablename__ = "procurement_items"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    tender_id           = Column(UUID(as_uuid=False), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    supplier_id         = Column(UUID(as_uuid=False), ForeignKey("suppliers.id", ondelete="SET NULL"))
    item_name           = Column(String(255), nullable=False)
    quantity_needed     = Column(Numeric(10, 2), nullable=False)
    unit                = Column(String(50))
    estimated_unit_cost = Column(Numeric(15, 2))
    actual_unit_cost    = Column(Numeric(15, 2))
    status              = Column(String(50), default="pending")  # pending, ordered, delivered
    order_date          = Column(Date)
    delivery_date       = Column(Date)
    notes               = Column(Text)
    created_at          = Column(DateTime, default=datetime.utcnow)

    tender      = relationship("Tender", back_populates="procurement_items")
    supplier    = relationship("Supplier", back_populates="procurement")


# ─── NOTIFICATIONS ───────────────────────────────────────────

class NotificationLog(Base):
    __tablename__ = "notifications_log"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id      = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id         = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))
    type            = Column(String(100), nullable=False)
    title           = Column(String(255), nullable=False)
    message         = Column(Text, nullable=False)
    reference_id    = Column(String(255))
    reference_table = Column(String(100))
    status          = Column(String(50), default="sent")
    sent_at         = Column(DateTime, default=datetime.utcnow)

    company         = relationship("Company", back_populates="notifications")


# ─── INVENTORY ───────────────────────────────────────────────

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id                  = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id          = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    business_unit_id    = Column(UUID(as_uuid=False), ForeignKey("business_units.id"))
    name                = Column(String(255), nullable=False)
    sku                 = Column(String(100))
    category            = Column(String(100))
    unit                = Column(String(50))
    quantity_in_stock   = Column(Numeric(10, 2), default=0)
    reorder_level       = Column(Numeric(10, 2), default=0)
    unit_cost           = Column(Numeric(15, 2))
    unit_price          = Column(Numeric(15, 2))
    is_active           = Column(Boolean, default=True)
    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow)

    movements           = relationship("StockMovement", back_populates="item")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id      = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    item_id         = Column(UUID(as_uuid=False), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False)
    movement_type   = Column(String(50), nullable=False)
    quantity        = Column(Numeric(10, 2), nullable=False)
    quantity_before = Column(Numeric(10, 2), nullable=False)
    quantity_after  = Column(Numeric(10, 2), nullable=False)
    reference_id    = Column(String(255))
    reference_table = Column(String(100))
    notes           = Column(Text)
    created_by      = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))
    created_at      = Column(DateTime, default=datetime.utcnow)

    item            = relationship("InventoryItem", back_populates="movements")


# ─── CONTACTS / DEBTORS / CREDITORS ─────────────────────────

class Contact(Base):
    __tablename__ = "contacts"

    id          = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id  = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name        = Column(String(255), nullable=False)
    type        = Column(String(50), nullable=False)
    phone       = Column(String(30))
    email       = Column(String(255))
    address     = Column(Text)
    notes       = Column(Text)
    created_at  = Column(DateTime, default=datetime.utcnow)

    debtor_records      = relationship("DebtorRecord", back_populates="contact")
    creditor_records    = relationship("CreditorRecord", back_populates="contact")


class DebtorRecord(Base):
    __tablename__ = "debtor_records"

    id          = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id  = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    contact_id  = Column(UUID(as_uuid=False), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    amount_owed = Column(Numeric(15, 2), nullable=False)
    amount_paid = Column(Numeric(15, 2), default=0)
    balance     = Column(Numeric(15, 2), nullable=False, default=0)  # computed on save
    due_date    = Column(Date)
    status      = Column(String(50), default="unpaid")
    created_at  = Column(DateTime, default=datetime.utcnow)

    contact     = relationship("Contact", back_populates="debtor_records")


class CreditorRecord(Base):
    __tablename__ = "creditor_records"

    id          = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id  = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    contact_id  = Column(UUID(as_uuid=False), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    amount_owed = Column(Numeric(15, 2), nullable=False)
    amount_paid = Column(Numeric(15, 2), default=0)
    balance     = Column(Numeric(15, 2), nullable=False, default=0)  # computed on save
    due_date    = Column(Date)
    status      = Column(String(50), default="unpaid")
    created_at  = Column(DateTime, default=datetime.utcnow)

    contact     = relationship("Contact", back_populates="creditor_records")


class DebtPayment(Base):
    __tablename__ = "debt_payments"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id      = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    record_id       = Column(String(255), nullable=False)
    record_type     = Column(String(50), nullable=False)
    payment_date    = Column(Date, default=date.today)
    amount          = Column(Numeric(15, 2), nullable=False)
    notes           = Column(Text)
    created_at      = Column(DateTime, default=datetime.utcnow)


# ─── ACTIVITY LOG ─────────────────────────────────────────────

class ActivityLog(Base):
    __tablename__ = "activity_log"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id      = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id         = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))
    action          = Column(String(100), nullable=False)
    entity_type     = Column(String(100))
    entity_id       = Column(String(255))
    description     = Column(Text)
    ip_address      = Column(String(50))
    created_at      = Column(DateTime, default=datetime.utcnow)
