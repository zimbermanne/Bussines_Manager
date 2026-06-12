from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models  # noqa: F401 — register models with SQLAlchemy
from agents.agents import (
    loan_agent,
    summary_agent,
    tender_agent,
    tra_agent,
    vikoba_agent,
)
from core.config import settings
from database import Base, engine
from routes.auth import router as auth_router
from routes.bank_loans import router as loans_router
from routes.finance import (
    business_router,
    expenses_router,
    pnl_router,
    purchases_router,
    sales_router,
)
from routes.operations import deadlines_router, suppliers_router, tenders_router
from routes.vikoba import router as vikoba_router

scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(tra_agent, CronTrigger(hour=7, minute=0), id="tra_agent")
    scheduler.add_job(loan_agent, CronTrigger(hour=7, minute=30), id="loan_agent")
    scheduler.add_job(vikoba_agent, CronTrigger(hour=8, minute=0), id="vikoba_agent")
    scheduler.add_job(tender_agent, CronTrigger(hour=8, minute=30), id="tender_agent")
    scheduler.add_job(summary_agent, CronTrigger(hour=19, minute=0), id="summary_agent")
    scheduler.start()
    print("All agents started")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    scheduler.shutdown()
    print("Agents stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Business Management System for Tanzanian Companies",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(loans_router)
app.include_router(sales_router)
app.include_router(purchases_router)
app.include_router(expenses_router)
app.include_router(pnl_router)
app.include_router(business_router)
app.include_router(deadlines_router)
app.include_router(suppliers_router)
app.include_router(tenders_router)
app.include_router(vikoba_router)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "agents": [
            "tra_agent",
            "loan_agent",
            "vikoba_agent",
            "tender_agent",
            "summary_agent",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


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
