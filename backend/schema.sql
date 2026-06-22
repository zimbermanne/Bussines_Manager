-- ============================================================
-- COMPANY MANAGER — Database Schema
-- PostgreSQL
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- SECTION 1: AUTH & COMPANIES
-- ============================================================

CREATE TABLE companies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    tin             VARCHAR(50),                        -- TRA Tax ID
    brela_number    VARCHAR(100),                       -- BRELA registration
    business_name   VARCHAR(255),                       -- Registered business name
    address         TEXT,
    phone           VARCHAR(30),
    email           VARCHAR(255),
    region          VARCHAR(100),                       -- e.g. Kilimanjaro
    district        VARCHAR(100),                       -- e.g. Moshi
    profile_type    VARCHAR(50) DEFAULT 'company',     -- solo, company
    bank_name       VARCHAR(255),                       -- For payments
    bank_account_number VARCHAR(50),                    -- For payments
    logo_url        TEXT,                               -- Company logo for PDFs
    base_currency   VARCHAR(3) DEFAULT 'TZS',           -- TZS, USD, KES, EUR, GBP
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    full_name           VARCHAR(255) NOT NULL,
    email               VARCHAR(255) UNIQUE NOT NULL,
    password_hash       TEXT NOT NULL,
    role                VARCHAR(50) DEFAULT 'owner',   -- owner, staff, accountant
    push_subscription   JSONB,                         -- Web Push subscription object
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_businesses (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    is_primary          BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, company_id)
);

CREATE TABLE subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    plan            VARCHAR(50) DEFAULT 'trial',       -- trial, basic, business
    price_tzs       INTEGER DEFAULT 0,
    start_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date        DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 2: COMPLIANCE DEADLINES
-- ============================================================

CREATE TABLE deadlines (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,              -- e.g. TRA PAYE, BRELA Annual Fee
    category        VARCHAR(100) NOT NULL,              -- tra, brela, nssf, wcf, osha, custom
    interval_type   VARCHAR(50) NOT NULL,               -- monthly, yearly, custom
    due_day         INTEGER,                            -- day of month (e.g. 7 for 7th)
    due_month       INTEGER,                            -- month of year for yearly deadlines
    next_due_date   DATE NOT NULL,
    notes           TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 3: BANK LOANS
-- ============================================================

CREATE TABLE bank_loans (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    lender_name         VARCHAR(255) NOT NULL,          -- e.g. CRDB, NMB, NBC
    principal_amount    NUMERIC(15,2) NOT NULL,
    interest_type       VARCHAR(50) NOT NULL,           -- simple, reducing_balance
    interest_rate       NUMERIC(8,4) NOT NULL,          -- annual rate e.g. 18.00
    start_date          DATE NOT NULL,
    due_day             INTEGER NOT NULL,               -- day of month repayment is due
    grace_period_months INTEGER DEFAULT 0,
    notes               TEXT,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bank_loan_payments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id             UUID NOT NULL REFERENCES bank_loans(id) ON DELETE CASCADE,
    payment_date        DATE NOT NULL,
    amount_paid         NUMERIC(15,2) NOT NULL,
    interest_portion    NUMERIC(15,2) NOT NULL,         -- calculated by backend
    principal_portion   NUMERIC(15,2) NOT NULL,         -- calculated by backend
    balance_after       NUMERIC(15,2) NOT NULL,         -- calculated by backend
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 4: VIKOBA SAVINGS GROUPS
-- ============================================================

CREATE TABLE vikoba_groups (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name                VARCHAR(255) NOT NULL,
    lifespan_type       VARCHAR(50) NOT NULL,           -- one_year, two_years, permanent
    start_date          DATE NOT NULL,
    end_date            DATE,                           -- NULL if permanent
    interval_type       VARCHAR(50) NOT NULL,           -- daily, weekly, monthly
    hisa_amount         NUMERIC(15,2) NOT NULL,         -- fixed contribution amount
    penalty_type        VARCHAR(50) NOT NULL,           -- fixed, percentage, custom
    penalty_value       NUMERIC(15,2),                  -- amount or percentage
    loan_interest_rate  NUMERIC(8,4) DEFAULT 0,        -- % per month on group loans
    is_dissolved        BOOLEAN DEFAULT FALSE,
    dissolved_at        DATE,
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE vikoba_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id        UUID NOT NULL REFERENCES vikoba_groups(id) ON DELETE CASCADE,
    full_name       VARCHAR(255) NOT NULL,
    phone           VARCHAR(30),
    joined_date     DATE NOT NULL DEFAULT CURRENT_DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE hisa_payments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id        UUID NOT NULL REFERENCES vikoba_groups(id) ON DELETE CASCADE,
    member_id       UUID NOT NULL REFERENCES vikoba_members(id) ON DELETE CASCADE,
    due_date        DATE NOT NULL,
    paid_date       DATE,                               -- NULL if not yet paid
    amount          NUMERIC(15,2) NOT NULL,
    status          VARCHAR(50) DEFAULT 'pending',      -- pending, paid, missed
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE hisa_penalties (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id        UUID NOT NULL REFERENCES vikoba_groups(id) ON DELETE CASCADE,
    member_id       UUID NOT NULL REFERENCES vikoba_members(id) ON DELETE CASCADE,
    hisa_id         UUID NOT NULL REFERENCES hisa_payments(id) ON DELETE CASCADE,
    penalty_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    amount          NUMERIC(15,2) NOT NULL,
    status          VARCHAR(50) DEFAULT 'unpaid',       -- unpaid, paid
    paid_date       DATE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE vikoba_loans (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id            UUID NOT NULL REFERENCES vikoba_groups(id) ON DELETE CASCADE,
    member_id           UUID NOT NULL REFERENCES vikoba_members(id) ON DELETE CASCADE,
    loan_amount         NUMERIC(15,2) NOT NULL,
    interest_rate       NUMERIC(8,4) NOT NULL,          -- % per month
    issued_date         DATE NOT NULL,
    repayment_interval  VARCHAR(50) NOT NULL,           -- weekly, monthly
    due_day             INTEGER,                        -- day of week (1-7) or day of month
    is_fully_repaid     BOOLEAN DEFAULT FALSE,
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE vikoba_loan_repayments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vikoba_loan_id      UUID NOT NULL REFERENCES vikoba_loans(id) ON DELETE CASCADE,
    payment_date        DATE NOT NULL,
    amount_paid         NUMERIC(15,2) NOT NULL,
    interest_portion    NUMERIC(15,2) NOT NULL,
    principal_portion   NUMERIC(15,2) NOT NULL,
    balance_after       NUMERIC(15,2) NOT NULL,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 5: SALES, PURCHASES & EXPENSES
-- ============================================================

CREATE TABLE business_units (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,              -- e.g. Hardware Shop, Garments, Regal Elixir
    type            VARCHAR(100),                       -- retail, wholesale, production
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sales_entries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    business_unit_id UUID REFERENCES business_units(id),
    sale_date       DATE NOT NULL DEFAULT CURRENT_DATE,
    item_name       VARCHAR(255) NOT NULL,
    quantity        NUMERIC(10,2) NOT NULL,
    unit_price      NUMERIC(15,2) NOT NULL,
    total_amount    NUMERIC(15,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE purchases (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    business_unit_id    UUID REFERENCES business_units(id),
    supplier_id         UUID,                           -- FK added after suppliers table
    purchase_date       DATE NOT NULL DEFAULT CURRENT_DATE,
    item_name           VARCHAR(255) NOT NULL,
    quantity            NUMERIC(10,2) NOT NULL,
    unit_cost           NUMERIC(15,2) NOT NULL,
    total_cost          NUMERIC(15,2) GENERATED ALWAYS AS (quantity * unit_cost) STORED,
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE expenses (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    business_unit_id    UUID REFERENCES business_units(id),
    expense_date        DATE NOT NULL DEFAULT CURRENT_DATE,
    category            VARCHAR(100) NOT NULL,          -- rent, transport, utilities, salary, etc.
    description         TEXT,
    amount              NUMERIC(15,2) NOT NULL,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 6: SUPPLIERS
-- ============================================================

CREATE TABLE suppliers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    contact_phone   VARCHAR(30),
    contact_email   VARCHAR(255),
    location        TEXT,
    items_supplied  TEXT,                               -- free text description
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Add supplier FK to purchases now that table exists
ALTER TABLE purchases
    ADD CONSTRAINT fk_purchases_supplier
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL;

-- ============================================================
-- SECTION 7: TENDERS & PROCUREMENT
-- ============================================================

CREATE TABLE tenders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name                VARCHAR(255) NOT NULL,
    reference_number    VARCHAR(255),                   -- e.g. NeST tender ref
    client              VARCHAR(255),                   -- issuing authority
    tender_value        NUMERIC(15,2),                  -- total value of tender
    procurement_budget  NUMERIC(15,2),                  -- budget to fulfill tender
    submission_deadline DATE,
    delivery_deadline   DATE NOT NULL,
    status              VARCHAR(50) DEFAULT 'planning', -- planning, won, active, completed, lost
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE procurement_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tender_id           UUID NOT NULL REFERENCES tenders(id) ON DELETE CASCADE,
    supplier_id         UUID REFERENCES suppliers(id) ON DELETE SET NULL,
    item_name           VARCHAR(255) NOT NULL,
    quantity_needed     NUMERIC(10,2) NOT NULL,
    unit               VARCHAR(50),                     -- metres, pieces, kg, etc.
    estimated_unit_cost NUMERIC(15,2),
    actual_unit_cost    NUMERIC(15,2),
    total_estimated     NUMERIC(15,2) GENERATED ALWAYS AS (quantity_needed * estimated_unit_cost) STORED,
    status              VARCHAR(50) DEFAULT 'pending',  -- pending, ordered, delivered
    order_date          DATE,
    delivery_date       DATE,
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 8: NOTIFICATIONS LOG
-- ============================================================

CREATE TABLE notifications_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    type            VARCHAR(100) NOT NULL,              -- tra_paye, loan_due, vikoba_missed, etc.
    title           VARCHAR(255) NOT NULL,
    message         TEXT NOT NULL,
    reference_id    UUID,                               -- ID of related record
    reference_table VARCHAR(100),                       -- which table the reference_id points to
    status          VARCHAR(50) DEFAULT 'sent',         -- sent, failed, read
    sent_at         TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 9: BUSINESS DOCUMENTS EXCHANGE
-- ============================================================

CREATE TABLE business_documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    sender_company_id   UUID NOT NULL REFERENCES companies(id),
    receiver_company_id UUID NOT NULL REFERENCES companies(id),
    document_type       VARCHAR(10) NOT NULL,           -- QUO, PRO, INV, RCP, CRN, DBN, DLN
    document_number     VARCHAR(50) NOT NULL,
    issue_date          DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date            DATE,
    status              VARCHAR(20) DEFAULT 'draft',     -- draft, sent, delivered, confirmed, rejected
    subtotal            NUMERIC(15,2) DEFAULT 0,
    vat_amount          NUMERIC(15,2) DEFAULT 0,
    vat_rate            NUMERIC(5,2) DEFAULT 18,
    grand_total         NUMERIC(15,2) DEFAULT 0,
    currency            VARCHAR(3) DEFAULT 'TZS',
    exchange_rate       NUMERIC(10,6) DEFAULT 1,
    notes               TEXT,
    client_name         VARCHAR(255) NOT NULL,
    client_address      TEXT NOT NULL,
    client_tin          VARCHAR(50),
    client_phone        VARCHAR(30),
    client_email        VARCHAR(255),
    rejection_reason    TEXT,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE document_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id         UUID NOT NULL REFERENCES business_documents(id) ON DELETE CASCADE,
    description         VARCHAR(255) NOT NULL,
    quantity            NUMERIC(10,2) NOT NULL,
    unit                VARCHAR(50),
    unit_price          NUMERIC(15,2) NOT NULL,
    total               NUMERIC(15,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE document_events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id         UUID NOT NULL REFERENCES business_documents(id) ON DELETE CASCADE,
    status              VARCHAR(20) NOT NULL,
    changed_by_user_id  UUID REFERENCES users(id),
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 10: COMPANY CARE — DEBTORS & CREDITORS
-- ============================================================

CREATE TABLE debtor_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    customer_id         UUID REFERENCES customers(id) ON DELETE SET NULL,
    debtor_name         VARCHAR(255) NOT NULL,
    debtor_phone        VARCHAR(30),
    debtor_email        VARCHAR(255),
    debt_date           DATE NOT NULL DEFAULT CURRENT_DATE,
    item_or_service     VARCHAR(255),
    amount_owed         NUMERIC(15,2) NOT NULL,
    amount_paid         NUMERIC(15,2) DEFAULT 0,
    balance_remaining   NUMERIC(15,2) GENERATED ALWAYS AS (amount_owed - amount_paid) STORED,
    status              VARCHAR(20) DEFAULT 'unpaid',    -- unpaid, partial, paid
    due_date            DATE,
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE creditor_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    supplier_id         UUID REFERENCES suppliers(id) ON DELETE SET NULL,
    creditor_name       VARCHAR(255) NOT NULL,
    creditor_phone      VARCHAR(30),
    creditor_email      VARCHAR(255),
    credit_date         DATE NOT NULL DEFAULT CURRENT_DATE,
    item_or_service     VARCHAR(255),
    amount_owed         NUMERIC(15,2) NOT NULL,
    amount_paid         NUMERIC(15,2) DEFAULT 0,
    balance_remaining   NUMERIC(15,2) GENERATED ALWAYS AS (amount_owed - amount_paid) STORED,
    status              VARCHAR(20) DEFAULT 'unpaid',    -- unpaid, partial, paid
    due_date            DATE,
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE debt_payments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    record_type         VARCHAR(10) NOT NULL,            -- debtor, creditor
    record_id           UUID NOT NULL,                   -- FK to debtor_records or creditor_records
    payment_date        DATE NOT NULL DEFAULT CURRENT_DATE,
    amount_paid         NUMERIC(15,2) NOT NULL,
    payment_method      VARCHAR(50),
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE care_snapshots (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    snapshot_date       DATE NOT NULL DEFAULT CURRENT_DATE,
    period_type         VARCHAR(10) NOT NULL,            -- daily, monthly, quarterly, yearly
    total_debtors       NUMERIC(15,2) DEFAULT 0,
    total_creditors     NUMERIC(15,2) DEFAULT 0,
    net_position        NUMERIC(15,2) GENERATED ALWAYS AS (total_debtors - total_creditors) STORED,
    health_status       VARCHAR(20),                     -- healthy, watch, at_risk
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 11: STAFF & PAYROLL MANAGEMENT
-- ============================================================

CREATE TABLE employees (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    business_unit_id    UUID REFERENCES business_units(id) ON DELETE SET NULL,
    full_name           VARCHAR(255) NOT NULL,
    phone               VARCHAR(30),
    email               VARCHAR(255),
    national_id         VARCHAR(50),
    position            VARCHAR(100),
    department          VARCHAR(100),
    employment_type     VARCHAR(50),                     -- permanent, contract, casual
    employment_date      DATE NOT NULL,
    basic_salary        NUMERIC(15,2),
    bank_name           VARCHAR(255),
    bank_account_number VARCHAR(50),
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payroll_runs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    business_unit_id    UUID REFERENCES business_units(id) ON DELETE SET NULL,
    run_date            DATE NOT NULL DEFAULT CURRENT_DATE,
    period_month        INTEGER NOT NULL,
    period_year         INTEGER NOT NULL,
    total_gross_pay     NUMERIC(15,2) DEFAULT 0,
    total_deductions    NUMERIC(15,2) DEFAULT 0,
    total_net_pay       NUMERIC(15,2) DEFAULT 0,
    status              VARCHAR(20) DEFAULT 'draft',     -- draft, finalized, paid
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payroll_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payroll_run_id      UUID NOT NULL REFERENCES payroll_runs(id) ON DELETE CASCADE,
    employee_id         UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    basic_salary        NUMERIC(15,2) NOT NULL,
    gross_pay           NUMERIC(15,2) NOT NULL,
    total_deductions    NUMERIC(15,2) DEFAULT 0,
    net_pay             NUMERIC(15,2) NOT NULL,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payroll_deductions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payroll_item_id     UUID NOT NULL REFERENCES payroll_items(id) ON DELETE CASCADE,
    deduction_type      VARCHAR(50) NOT NULL,            -- nssf, paye, loan, advance, other
    deduction_name      VARCHAR(100),
    amount              NUMERIC(15,2) NOT NULL,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payroll_allowances (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payroll_item_id     UUID NOT NULL REFERENCES payroll_items(id) ON DELETE CASCADE,
    allowance_type      VARCHAR(50) NOT NULL,            -- transport, housing, meal, other
    allowance_name      VARCHAR(100),
    amount              NUMERIC(15,2) NOT NULL,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 12: INVENTORY & STOCK MANAGEMENT
-- ============================================================

CREATE TABLE inventory_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    business_unit_id    UUID REFERENCES business_units(id) ON DELETE SET NULL,
    item_name           VARCHAR(255) NOT NULL,
    sku                 VARCHAR(50),
    unit                VARCHAR(50),                     -- pieces, kg, metres, etc.
    current_quantity    NUMERIC(10,2) DEFAULT 0,
    reorder_level       NUMERIC(10,2) DEFAULT 0,
    reorder_quantity    NUMERIC(10,2) DEFAULT 0,
    preferred_supplier_id UUID REFERENCES suppliers(id) ON DELETE SET NULL,
    unit_cost           NUMERIC(15,2),
    unit_price          NUMERIC(15,2),
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE reorder_alerts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    inventory_item_id   UUID NOT NULL REFERENCES inventory_items(id) ON DELETE CASCADE,
    alert_date          DATE NOT NULL DEFAULT CURRENT_DATE,
    current_quantity    NUMERIC(10,2) NOT NULL,
    reorder_level       NUMERIC(10,2) NOT NULL,
    status              VARCHAR(20) DEFAULT 'triggered', -- triggered, ordered, resolved
    purchase_order_id   UUID REFERENCES business_documents(id) ON DELETE SET NULL,
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 13: LOAN APPLICATIONS
-- ============================================================

CREATE TABLE loan_applications (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    lender_name         VARCHAR(255) NOT NULL,          -- NMB, CRDB, SIDO, Government
    loan_type           VARCHAR(50) NOT NULL,           -- business, government, emergency
    amount_applied      NUMERIC(15,2) NOT NULL,
    application_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_disbursement_date DATE,
    purpose             TEXT,
    collateral          TEXT,
    status              VARCHAR(30) DEFAULT 'applied',  -- applied, under_review, approved, rejected, disbursed
    follow_up_date      DATE,
    rejection_reason    TEXT,
    disbursement_amount NUMERIC(15,2),
    disbursement_date   DATE,
    converted_to_loan_id UUID REFERENCES bank_loans(id) ON DELETE SET NULL,
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE loan_application_events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id      UUID NOT NULL REFERENCES loan_applications(id) ON DELETE CASCADE,
    status              VARCHAR(30) NOT NULL,
    changed_by_user_id  UUID REFERENCES users(id),
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 14: CUSTOMER MANAGEMENT (CRM)
-- ============================================================

CREATE TABLE customers (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    full_name           VARCHAR(255) NOT NULL,
    business_name       VARCHAR(255),
    phone               VARCHAR(30),
    email               VARCHAR(255),
    physical_address     TEXT,
    customer_type       VARCHAR(20) DEFAULT 'individual', -- individual, business
    tin                 VARCHAR(50),
    date_added          DATE NOT NULL DEFAULT CURRENT_DATE,
    notes               TEXT,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE customer_sales (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    customer_id         UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    sale_id             UUID REFERENCES sales_entries(id) ON DELETE SET NULL,
    sale_date           DATE NOT NULL DEFAULT CURRENT_DATE,
    amount              NUMERIC(15,2) NOT NULL,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE customer_documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    customer_id         UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    document_id         UUID NOT NULL REFERENCES business_documents(id) ON DELETE CASCADE,
    sent_date           DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 15: MULTI-CURRENCY SUPPORT
-- ============================================================

CREATE TABLE currencies (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code                VARCHAR(3) UNIQUE NOT NULL,     -- TZS, USD, KES, EUR, GBP
    name                VARCHAR(50) NOT NULL,
    symbol              VARCHAR(5) NOT NULL,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE exchange_rates (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_currency       VARCHAR(3) NOT NULL,             -- USD
    to_currency         VARCHAR(3) NOT NULL,             -- TZS
    rate                NUMERIC(10,6) NOT NULL,
    effective_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at          TIMESTAMP DEFAULT NOW(),
    UNIQUE(from_currency, to_currency, effective_date)
);

-- ============================================================
-- SECTION 16: EXPENSE CATEGORIES & BUDGET
-- ============================================================

CREATE TABLE expense_categories (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name                VARCHAR(100) NOT NULL,
    description         TEXT,
    is_default          BOOLEAN DEFAULT FALSE,          -- Default categories
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE expense_budgets (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    category_id         UUID NOT NULL REFERENCES expense_categories(id) ON DELETE CASCADE,
    business_unit_id    UUID REFERENCES business_units(id) ON DELETE SET NULL,
    budget_month        INTEGER NOT NULL,
    budget_year         INTEGER NOT NULL,
    budget_amount       NUMERIC(15,2) NOT NULL,
    actual_spent        NUMERIC(15,2) DEFAULT 0,
    remaining           NUMERIC(15,2) GENERATED ALWAYS AS (budget_amount - actual_spent) STORED,
    created_at          TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, category_id, business_unit_id, budget_month, budget_year)
);

-- ============================================================
-- SECTION 17: REPORT GENERATION
-- ============================================================

CREATE TABLE report_history (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id             UUID REFERENCES users(id) ON DELETE SET NULL,
    report_type         VARCHAR(50) NOT NULL,            -- sales, purchases, expenses, pnl, payroll, etc.
    report_format       VARCHAR(10) NOT NULL,            -- pdf, csv
    period_type         VARCHAR(20),                     -- daily, monthly, quarterly, yearly
    start_date          DATE,
    end_date            DATE,
    file_path           TEXT,
    generated_at        TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SECTION 18: ANALYTICS CACHE
-- ============================================================

CREATE TABLE analytics_cache (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    cache_key           VARCHAR(100) NOT NULL,
    cache_data          JSONB NOT NULL,
    cache_date          DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at          TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, cache_key, cache_date)
);

-- ============================================================
-- SECTION 9: INDEXES
-- ============================================================

-- Companies & Users
CREATE INDEX idx_users_company ON users(company_id);

-- Deadlines
CREATE INDEX idx_deadlines_company ON deadlines(company_id);
CREATE INDEX idx_deadlines_next_due ON deadlines(next_due_date);

-- Bank Loans
CREATE INDEX idx_bank_loans_company ON bank_loans(company_id);
CREATE INDEX idx_bank_loan_payments_loan ON bank_loan_payments(loan_id);

-- Vikoba
CREATE INDEX idx_vikoba_groups_company ON vikoba_groups(company_id);
CREATE INDEX idx_vikoba_members_group ON vikoba_members(group_id);
CREATE INDEX idx_hisa_payments_group ON hisa_payments(group_id);
CREATE INDEX idx_hisa_payments_member ON hisa_payments(member_id);
CREATE INDEX idx_hisa_payments_due_date ON hisa_payments(due_date);
CREATE INDEX idx_hisa_penalties_member ON hisa_penalties(member_id);
CREATE INDEX idx_vikoba_loans_group ON vikoba_loans(group_id);
CREATE INDEX idx_vikoba_loans_member ON vikoba_loans(member_id);
CREATE INDEX idx_vikoba_loan_repayments_loan ON vikoba_loan_repayments(vikoba_loan_id);

-- Sales, Purchases, Expenses
CREATE INDEX idx_sales_company ON sales_entries(company_id);
CREATE INDEX idx_sales_date ON sales_entries(sale_date);
CREATE INDEX idx_sales_business_unit ON sales_entries(business_unit_id);
CREATE INDEX idx_purchases_company ON purchases(company_id);
CREATE INDEX idx_purchases_date ON purchases(purchase_date);
CREATE INDEX idx_expenses_company ON expenses(company_id);
CREATE INDEX idx_expenses_date ON expenses(expense_date);

-- Tenders
CREATE INDEX idx_tenders_company ON tenders(company_id);
CREATE INDEX idx_tenders_delivery ON tenders(delivery_deadline);
CREATE INDEX idx_procurement_tender ON procurement_items(tender_id);

-- Notifications
CREATE INDEX idx_notifications_company ON notifications_log(company_id);
CREATE INDEX idx_notifications_sent_at ON notifications_log(sent_at);

-- ============================================================
-- SECTION 10: SEED DATA — Zimbermanne Company Limited
-- ============================================================

-- Insert the company
INSERT INTO companies (id, name, tin, brela_number, address, region, district)
VALUES (
    'a1b2c3d4-0000-0000-0000-000000000001',
    'Zimbermanne Company Limited',
    '202-013-449',
    'BRELA-ZCL-001',
    'Kiusa Line, Moshi Town',
    'Kilimanjaro',
    'Moshi'
);

-- Insert business units
INSERT INTO business_units (company_id, name, type) VALUES
    ('a1b2c3d4-0000-0000-0000-000000000001', 'Electroplumbing / Zimbermanne Hardware', 'retail'),
    ('a1b2c3d4-0000-0000-0000-000000000001', 'Clothes & Garments Shop', 'retail'),
    ('a1b2c3d4-0000-0000-0000-000000000001', 'Regal Elixir Co.', 'production');

-- Insert compliance deadlines
INSERT INTO deadlines (company_id, name, category, interval_type, due_day, next_due_date) VALUES
    ('a1b2c3d4-0000-0000-0000-000000000001', 'TRA PAYE', 'tra', 'monthly', 7, DATE_TRUNC('month', NOW()) + INTERVAL '7 days'),
    ('a1b2c3d4-0000-0000-0000-000000000001', 'TRA SDL', 'tra', 'monthly', 7, DATE_TRUNC('month', NOW()) + INTERVAL '7 days'),
    ('a1b2c3d4-0000-0000-0000-000000000001', 'TRA VAT Returns', 'tra', 'monthly', 20, DATE_TRUNC('month', NOW()) + INTERVAL '20 days'),
    ('a1b2c3d4-0000-0000-0000-000000000001', 'BRELA Annual Fee', 'brela', 'yearly', NULL, '2027-01-01'),
    ('a1b2c3d4-0000-0000-0000-000000000001', 'Business Name Renewal', 'brela', 'yearly', NULL, '2027-01-01'),
    ('a1b2c3d4-0000-0000-0000-000000000001', 'NSSF Registration Renewal', 'nssf', 'yearly', NULL, '2027-01-01'),
    ('a1b2c3d4-0000-0000-0000-000000000001', 'WCF Renewal', 'wcf', 'yearly', NULL, '2027-01-01'),
    ('a1b2c3d4-0000-0000-0000-000000000001', 'OSHA Renewal', 'osha', 'yearly', NULL, '2027-01-01');