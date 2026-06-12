# Company Manager — Business Management System

> A full business management system built to run your company in the background — tracking sales, purchases, expenses, loans, Vikoba savings, compliance deadlines, and upcoming tenders — all in one place.

---

## Overview

Company Manager is a full-stack web application that acts as a **silent business operator and financial controller**. It combines:

- **Smart Reminders** — TRA, loans, Vikoba, BRELA deadlines
- **Financial Tracking** — daily sales, purchases, expenses, profit & loss
- **Loan Management** — bank loans with interest calculations
- **Vikoba Management** — savings groups, hisa, penalties, dissolution
- **Tender & Project Planner** — procurement tracking for upcoming tenders

Built first for **Zimbermanne Company Limited** (Moshi, Kilimanjaro, Tanzania), then expanded as a **SaaS platform** for other Tanzanian businesses.

---

## The Problem It Solves

Running multiple businesses means juggling:

- TRA PAYE, SDL, VAT filings every month
- Bank loan repayments with interest calculations
- Vikoba hisa contributions across multiple groups
- BRELA and business name renewals
- Daily sales records across multiple shops
- Stock purchase and expense tracking
- Tender procurement planning and deadlines

Missing any of these costs money. Company Manager tracks all of it for you.

---

## Module 1 — Compliance Reminders

### Reminder Types & Intervals

| Reminder | Interval | Alert Timing |
|---|---|---|
| TRA PAYE | Monthly | 7 days and 1 day before |
| TRA SDL | Monthly | 7 days and 1 day before |
| TRA VAT Returns | Monthly | 7 days and 1 day before |
| Bank Loan Repayment | Monthly | 7 days, 1 day, and overdue |
| Vikoba Hisa | Daily / Weekly / Monthly | 1 day before |
| Vikoba Loan Repayment | Weekly or Monthly | 1 day before and overdue |
| BRELA Annual Fee | Yearly | 30, 14, 7, 1 days before |
| Business Name Renewal | Yearly | 30, 14, 7, 1 days before |
| NSSF / WCF / OSHA | Yearly | 30, 14, 7, 1 days before |

---

## Module 2 — Bank Loan Tracker

Supports **multiple simultaneous loans**, each with independent terms.

### Loan Setup

When adding a loan the user enters:
- Lender name (e.g. CRDB, NMB, NBC)
- Principal amount
- Interest type — Simple or Reducing Balance
- Interest rate (% per month or per year)
- Start date and monthly due date
- Grace period (if any)

### Interest Calculations

**Simple Interest** — fixed monthly interest on original principal:
```
Monthly Interest = (Principal × Annual Rate) / 12
Total Repayable  = Principal + (Monthly Interest × Months)
```

**Reducing Balance** — interest shrinks as balance reduces:
```
Monthly Interest = Remaining Balance × Monthly Rate
Principal Paid   = Monthly Payment - Monthly Interest
New Balance      = Remaining Balance - Principal Paid
```

### Pay-As-You-Go Tracking

No upfront schedule. Each payment logged manually, system calculates:
- Interest portion vs principal portion
- Remaining balance
- Total paid to date
- Total interest paid to date

---

## Module 3 — Vikoba Savings Management

### Group Types

| Type | Duration | End Event |
|---|---|---|
| Short-term | 1 year | Dissolves — savings divided |
| Medium-term | 2 years | Dissolves — savings divided |
| Permanent | No end | Runs indefinitely |

### What the System Tracks

- Hisa payments — date, amount, status (paid / missed)
- Automatic penalty calculation and logging on missed payments
- Member loans with interest — full repayment history
- Group running balance at all times

### Dissolution Calculator

```
Group Total = All Hisa + All Penalties + All Loan Interest Repaid

Each Member's Payout:
  + Hisa contributed
  + Penalties paid
  - Outstanding loan balance
  - Interest still owed
```
Generates a full dissolution report per member.

---

## Module 4 — Daily Sales, Purchases & Expenses

### Sales Recording

Sales are recorded **per item** across all businesses:

| Field | Example |
|---|---|
| Business | Zimbermanne Hardware |
| Item name | GI Pipe 1 inch |
| Quantity | 5 |
| Unit price | 8,500 TZS |
| Total | 42,500 TZS |
| Date | 11 June 2026 |

Multiple items can be added per day per business.

### Purchase Recording

Stock purchases recorded per item:

| Field | Example |
|---|---|
| Business | Electroplumbing |
| Item name | PVC Pipe 3/4 inch |
| Quantity | 50 |
| Unit cost | 3,200 TZS |
| Total cost | 160,000 TZS |
| Supplier | Moshi Hardware Suppliers |
| Date | 11 June 2026 |

### Expense Recording

Any business expense logged with:
- Category (rent, transport, utilities, salaries, etc.)
- Amount
- Description
- Business it belongs to
- Date

### Profit & Loss Summary

**Daily P&L:**
```
Daily Sales Revenue        500,000 TZS
Less: Cost of Purchases   -180,000 TZS
Less: Expenses             -45,000 TZS
─────────────────────────────────────
Daily Net Profit           275,000 TZS
```

**Monthly P&L:**
```
Total Sales Revenue      12,500,000 TZS
Less: Total Purchases    -4,800,000 TZS
Less: Total Expenses     -1,200,000 TZS
─────────────────────────────────────
Monthly Net Profit        6,500,000 TZS
```

Both views available on the dashboard, filterable by business or across all businesses combined.

---

## Module 5 — Tender & Project Procurement Planner

When you win or plan for a tender, Company Manager helps you manage everything you need to purchase before the project starts.

### Tender Setup

When adding a tender or project:
- Tender name and reference number (e.g. NeST tender ID)
- Client / issuing authority
- Total tender value
- Delivery deadline
- Procurement budget (what you need to spend to fulfill it)

### Procurement Item Tracking

For each tender, add items you need to procure:

| Field | Example |
|---|---|
| Item name | HDPE Pipe 110mm |
| Quantity needed | 200 metres |
| Estimated unit cost | 12,000 TZS |
| Supplier | Dar es Salaam Pipes Ltd |
| Status | Pending / Ordered / Delivered |
| Purchase date | 20 June 2026 |
| Actual cost paid | 11,500 TZS |

### Budget vs Actual

For each tender, the system shows:

```
Tender: SIDO Kilimanjaro — FA/2025/2026/276/TR29/G/21
─────────────────────────────────────────────────────
Tender Value:           8,500,000 TZS
Procurement Budget:     5,200,000 TZS

Items to Procure:              12
  Ordered:                      7
  Delivered:                    4
  Pending:                      1

Estimated Total Cost:   5,200,000 TZS
Actual Spent So Far:    3,150,000 TZS
Remaining Budget:       2,050,000 TZS

Projected Profit:       3,300,000 TZS
```

### Supplier Directory

A built-in supplier directory stores:
- Supplier name
- Contact number
- Location
- Items they supply
- Past purchase history with them

Reusable across tenders and regular purchases.

### Procurement Deadline Reminders

The agent sends alerts:
- When a tender delivery deadline is approaching (14, 7, 3, 1 days before)
- When a procurement item has not been marked as ordered close to the deadline
- When budget is exceeded

---

## Features Summary

### Phase 1 — Core (Zimbermanne Internal Use)
- Compliance reminders — TRA, BRELA, NSSF, WCF
- Bank loan tracker — multiple loans, simple and reducing balance interest
- Vikoba savings management — hisa, penalties, loans, dissolution
- Daily sales recording — per item, per business
- Purchase and expense tracking
- Daily and monthly Profit & Loss summary
- Tender and project procurement planner
- Supplier directory
- Budget vs actual per tender
- Push notifications to phone
- Web dashboard (PWA — installable on phone)

### Phase 2 — SaaS Platform (Other Companies)
- Multi-company profiles
- Company onboarding and registration
- Subscription billing (10,000 – 20,000 TZS/month)
- Admin dashboard
- 14-day free trial
- "Company Manager — Powered by Zimbermanne" branding

---

## SaaS Business Model

| Plan | Price | Features |
|---|---|---|
| Free Trial | 0 TZS | 14 days full access |
| Basic | 10,000 TZS/month | All modules, 1 company profile |
| Business | 20,000 TZS/month | All modules, multiple branches, priority support |

**Revenue potential:**
- 10 companies × 10,000 TZS = 100,000 TZS/month
- 50 companies × 10,000 TZS = 500,000 TZS/month
- 100 companies × 15,000 TZS = 1,500,000 TZS/month

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (PWA — installable on phone) |
| Backend | Python / FastAPI |
| Database | PostgreSQL |
| Background Agents | APScheduler (runs inside FastAPI) |
| Notifications | Web Push Notifications (free) |
| Backend Hosting | Railway |
| Frontend Hosting | Vercel (free tier) |

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│                React Frontend (PWA)               │
│  Dashboard · Sales · Loans · Vikoba · Tenders     │
└─────────────────────┬────────────────────────────┘
                      │ REST API
┌─────────────────────▼────────────────────────────┐
│                 FastAPI Backend                   │
│                                                   │
│  ┌──────────────┐    ┌────────────────────────┐   │
│  │  API Routes  │    │    Agent Scheduler     │   │
│  └──────────────┘    └───────────┬────────────┘   │
│                                  │                │
│        ┌─────────────────────────┼────────────┐   │
│        ▼              ▼          ▼            ▼   │
│   TRA Agent     Loan Agent  Vikoba Agent  Tender Agent
│   BRELA Agent   Summary Agent                     │
└──────────────────────────────────┬───────────────┘
                                   │
┌──────────────────────────────────▼───────────────┐
│                PostgreSQL Database                │
│                                                   │
│  companies · users · subscriptions                │
│  deadlines · bank_loans · bank_loan_payments      │
│  vikoba_groups · vikoba_members                   │
│  hisa_payments · hisa_penalties                   │
│  vikoba_loans · vikoba_loan_repayments            │
│  sales_entries · purchases · expenses             │
│  tenders · procurement_items · suppliers          │
│  notifications_log                                │
└──────────────────────────────────┬───────────────┘
                                   │
                          Push Notification
                                   │
                              Your Phone 📱
```

---

## Database Tables

### Auth & Companies
| Table | Purpose |
|---|---|
| `companies` | Company profiles |
| `users` | Login, push subscription |
| `subscriptions` | SaaS plan and billing |

### Compliance
| Table | Purpose |
|---|---|
| `deadlines` | TRA, BRELA, NSSF, WCF dates |

### Bank Loans
| Table | Purpose |
|---|---|
| `bank_loans` | Loan details — lender, principal, interest type, rate |
| `bank_loan_payments` | Each payment — date, amount, interest split, balance |

### Vikoba
| Table | Purpose |
|---|---|
| `vikoba_groups` | Group settings — interval, penalty rules, lifespan |
| `vikoba_members` | Members per group |
| `hisa_payments` | Hisa payment log — date, amount, status |
| `hisa_penalties` | Penalty log per missed payment |
| `vikoba_loans` | Member loans from the group |
| `vikoba_loan_repayments` | Repayment log with interest split |

### Sales & Finance
| Table | Purpose |
|---|---|
| `sales_entries` | Per item sales — name, qty, price, business, date |
| `purchases` | Stock purchases — item, qty, cost, supplier, date |
| `expenses` | Business expenses — category, amount, date |

### Tenders & Procurement
| Table | Purpose |
|---|---|
| `tenders` | Tender details — name, ref, client, value, deadline |
| `procurement_items` | Items to buy per tender — qty, cost, status, supplier |
| `suppliers` | Supplier directory — name, contact, location, items |

### System
| Table | Purpose |
|---|---|
| `notifications_log` | All alerts sent — type, date, status |

---

## Agent Schedule

| Agent | Schedule | Action |
|---|---|---|
| TRA Agent | Monthly | PAYE, SDL, VAT deadline alerts |
| Loan Agent | Daily | Due date alerts and overdue flags |
| Vikoba Agent | Per group interval | Missed hisa detection, penalties, alerts |
| BRELA Agent | Yearly | Renewal alerts |
| Tender Agent | Daily | Procurement deadline alerts, budget alerts |
| Summary Agent | Every evening 7:00 PM | Daily P&L snapshot notification |
| Subscription Agent | Daily | Flag expired company subscriptions |

---

## Project Structure

```
company-manager/
├── frontend/
│   ├── public/
│   │   └── manifest.json
│   └── src/
│       ├── pages/
│       │   ├── Dashboard.jsx        # P&L overview + upcoming alerts
│       │   ├── Sales.jsx            # Record and view daily sales
│       │   ├── Purchases.jsx        # Stock purchases
│       │   ├── Expenses.jsx         # Business expenses
│       │   ├── ProfitLoss.jsx       # Daily and monthly P&L
│       │   ├── BankLoans.jsx        # Loan list and payment logging
│       │   ├── LoanDetail.jsx       # Payment history + interest breakdown
│       │   ├── Vikoba.jsx           # Group list
│       │   ├── VikobaDetail.jsx     # Hisa log, loans, dissolution
│       │   ├── Tenders.jsx          # Tender list
│       │   ├── TenderDetail.jsx     # Procurement items, budget vs actual
│       │   ├── Suppliers.jsx        # Supplier directory
│       │   ├── Deadlines.jsx        # Compliance reminders
│       │   └── Settings.jsx
│       └── components/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── routes/
│   │   ├── sales.py
│   │   ├── purchases.py
│   │   ├── expenses.py
│   │   ├── bank_loans.py
│   │   ├── vikoba.py
│   │   ├── tenders.py
│   │   ├── suppliers.py
│   │   ├── deadlines.py
│   │   └── notifications.py
│   └── agents/
│       ├── tra_agent.py
│       ├── loan_agent.py
│       ├── vikoba_agent.py
│       ├── brela_agent.py
│       ├── tender_agent.py
│       └── summary_agent.py
│
├── requirements.txt
└── README.md
```

---

## Deployment

| Service | Platform | Cost |
|---|---|---|
| Backend + Agents | Railway | ~$3–5/month |
| PostgreSQL | Railway | ~$0–5/month |
| Frontend | Vercel | Free |
| Push Notifications | Web Push API | Free |
| **Total** | | **~$3–10/month** |

---

## Development Phases

- [x] Project scoped and designed
- [x] README written
- [ ] Database schema (SQL)
- [ ] FastAPI backend + models
- [ ] Sales, purchases, expenses routes
- [ ] Profit & Loss calculation engine
- [ ] Bank loan tracker with interest calculation
- [ ] Vikoba savings management
- [ ] Tender procurement planner
- [ ] Supplier directory
- [ ] Agent scheduler (APScheduler)
- [ ] Push notification service
- [ ] React dashboard — Phase 1 (Zimbermanne internal)
- [ ] Testing and refinement
- [ ] Multi-company SaaS profiles — Phase 2
- [ ] Subscription billing
- [ ] Public launch

---

## Business Context — Phase 1 User

**Zimbermanne Company Limited** (TIN: 202-013-449) — Moshi, Kilimanjaro, Tanzania

- Electroplumbing / Zimbermanne Hardware
- Clothes & Garments Shop
- Regal Elixir Co. (cocktail brand — 3-person partnership)

---

*Company Manager — Built in Tanzania, for Tanzanian businesses.*
