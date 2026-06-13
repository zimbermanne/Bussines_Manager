from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager

from core.config import settings
from database import engine, Base

# Import all models so SQLAlchemy creates tables
import models  # noqa

# Import routes
from routes.auth         import router as auth_router
from routes.bank_loans   import router as loans_router
from routes.finance      import sales_router, purchases_router, expenses_router, pnl_router
from routes.operations   import deadlines_router, suppliers_router, tenders_router
from routes.inventory    import router as inventory_router
from routes.contacts     import router as contacts_router, debtors_router, creditors_router
from routes.data_io      import router as data_io_router
from routes.activity     import router as activity_router

# Import agents
from agents.agents import (
    tra_agent,
    loan_agent,
    vikoba_agent,
    tender_agent,
    summary_agent,
)

# ─── Scheduler setup ─────────────────────────────────────────

scheduler = BackgroundScheduler()


def start_scheduler():
    # TRA / Compliance agent — runs every morning at 7:00 AM
    scheduler.add_job(tra_agent, CronTrigger(hour=7, minute=0), id="tra_agent")

    # Loan agent — runs every morning at 7:30 AM
    scheduler.add_job(loan_agent, CronTrigger(hour=7, minute=30), id="loan_agent")

    # Vikoba agent — runs every morning at 8:00 AM
    scheduler.add_job(vikoba_agent, CronTrigger(hour=8, minute=0), id="vikoba_agent")

    # Tender agent — runs every morning at 8:30 AM
    scheduler.add_job(tender_agent, CronTrigger(hour=8, minute=30), id="tender_agent")

    # Daily summary — runs every evening at 7:00 PM
    scheduler.add_job(summary_agent, CronTrigger(hour=19, minute=0), id="summary_agent")

    scheduler.start()
    print("✅ All agents started")


# ─── App lifecycle ───────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables
    Base.metadata.create_all(bind=engine)
    # Start agents
    start_scheduler()
    yield
    # Shutdown
    scheduler.shutdown()
    print("Agents stopped")


# ─── App init ────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Business Management System for Tanzanian Companies",
    lifespan=lifespan,
)

# CORS — allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register routes ─────────────────────────────────────────

app.include_router(auth_router)
app.include_router(loans_router)
app.include_router(sales_router)
app.include_router(purchases_router)
app.include_router(expenses_router)
app.include_router(pnl_router)
app.include_router(deadlines_router)
app.include_router(suppliers_router)
app.include_router(tenders_router)
app.include_router(inventory_router)
app.include_router(contacts_router)
app.include_router(debtors_router)
app.include_router(creditors_router)
app.include_router(data_io_router)
app.include_router(activity_router)


# ─── Health check ────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "agents": ["tra_agent", "loan_agent", "vikoba_agent", "tender_agent", "summary_agent"]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ─── Manual agent trigger endpoints (for testing) ───────────

@app.post("/admin/run/tra-agent")
def run_tra_agent():
    tra_agent()
    return {"message": "TRA agent executed"}

@app.post("/admin/run/loan-agent")
def run_loan_agent():
    loan_agent()
    return {"message": "Loan agent executed"}

@app.post("/admin/run/vikoba-agent")
def run_vikoba_agent():
    vikoba_agent()
    return {"message": "Vikoba agent executed"}

@app.post("/admin/run/summary-agent")
def run_summary_agent():
    summary_agent()
    return {"message": "Summary agent executed"}
