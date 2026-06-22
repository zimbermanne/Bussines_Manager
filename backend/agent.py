"""
Company Manager — Background Agents
Runs on APScheduler. Each agent checks its domain and fires
push notifications when action is needed.
"""

from datetime import date, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
import models


# ─── Notification helper ─────────────────────────────────────

def send_push(db: Session, company_id: str, notif_type: str, title: str, message: str, reference_id: str = None, reference_table: str = None):
    """Log notification and send Web Push to all company users."""
    users = db.query(models.User).filter(
        models.User.company_id == company_id,
        models.User.is_active == True
    ).all()

    for user in users:
        # Log it
        log = models.NotificationLog(
            company_id=company_id,
            user_id=user.id,
            type=notif_type,
            title=title,
            message=message,
            reference_id=reference_id,
            reference_table=reference_table,
        )
        db.add(log)

        # Send Web Push if subscription exists
        if user.push_subscription:
            try:
                from pywebpush import webpush, WebPushException
                from core.config import settings
                import json

                webpush(
                    subscription_info=user.push_subscription,
                    data=json.dumps({"title": title, "body": message}),
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": f"mailto:{settings.VAPID_CLAIM_EMAIL}"},
                )
            except Exception as e:
                print(f"Push failed for user {user.id}: {e}")

    db.commit()


def days_until(target: date) -> int:
    return (target - date.today()).days


# ─── Agent 1: TRA Deadlines ──────────────────────────────────

def tra_agent():
    """Check TRA and all compliance deadlines. Alert at 7 days and 1 day before."""
    db = SessionLocal()
    try:
        deadlines = db.query(models.Deadline).filter(
            models.Deadline.is_active == True
        ).all()

        for dl in deadlines:
            days_left = days_until(dl.next_due_date)

            if days_left in [7, 3, 1, 0]:
                if days_left == 0:
                    title = f"⚠️ DUE TODAY: {dl.name}"
                    message = f"{dl.name} is due today. File immediately to avoid penalties."
                elif days_left == 1:
                    title = f"🔔 Tomorrow: {dl.name}"
                    message = f"{dl.name} is due tomorrow ({dl.next_due_date}). Prepare now."
                else:
                    title = f"📅 Reminder: {dl.name}"
                    message = f"{dl.name} is due in {days_left} days on {dl.next_due_date}."

                send_push(
                    db=db,
                    company_id=dl.company_id,
                    notif_type=f"deadline_{dl.category}",
                    title=title,
                    message=message,
                    reference_id=dl.id,
                    reference_table="deadlines"
                )

                # Advance monthly deadlines after they pass
                if days_left == 0 and dl.interval_type == "monthly":
                    dl.next_due_date = dl.next_due_date + timedelta(days=30)
                elif days_left == 0 and dl.interval_type == "yearly":
                    from dateutil.relativedelta import relativedelta
                    dl.next_due_date = dl.next_due_date + relativedelta(years=1)

        db.commit()
        print(f"[TRA Agent] Checked {len(deadlines)} deadlines")
    finally:
        db.close()


# ─── Agent 2: Bank Loan Agent ────────────────────────────────

def loan_agent():
    """Check bank loan due dates. Alert 7 days, 1 day before, and if overdue."""
    db = SessionLocal()
    try:
        loans = db.query(models.BankLoan).filter(
            models.BankLoan.is_active == True
        ).all()

        today = date.today()

        for loan in loans:
            # Find this month's due date
            try:
                due_date = date(today.year, today.month, loan.due_day)
            except ValueError:
                # Handle months with fewer days (e.g. due_day=31 in April)
                import calendar
                last_day = calendar.monthrange(today.year, today.month)[1]
                due_date = date(today.year, today.month, last_day)

            days_left = days_until(due_date)

            # Check if already paid this month
            paid_this_month = db.query(models.BankLoanPayment).filter(
                models.BankLoanPayment.loan_id == loan.id,
                models.BankLoanPayment.payment_date >= date(today.year, today.month, 1),
                models.BankLoanPayment.payment_date <= due_date
            ).first()

            if paid_this_month:
                continue

            # Get current balance
            last_payment = (
                db.query(models.BankLoanPayment)
                .filter(models.BankLoanPayment.loan_id == loan.id)
                .order_by(models.BankLoanPayment.created_at.desc())
                .first()
            )
            balance = float(last_payment.balance_after) if last_payment else float(loan.principal_amount)

            if days_left in [7, 1, 0] or days_left < 0:
                if days_left < 0:
                    title = f"🚨 OVERDUE: {loan.lender_name} Loan"
                    message = f"Your {loan.lender_name} loan payment is {abs(days_left)} days overdue. Balance: {balance:,.0f} TZS."
                elif days_left == 0:
                    title = f"⚠️ DUE TODAY: {loan.lender_name} Loan"
                    message = f"Your {loan.lender_name} loan payment is due today. Balance remaining: {balance:,.0f} TZS."
                else:
                    title = f"🏦 Loan Reminder: {loan.lender_name}"
                    message = f"Loan payment to {loan.lender_name} due in {days_left} day(s) on {due_date}. Balance: {balance:,.0f} TZS."

                send_push(
                    db=db,
                    company_id=loan.company_id,
                    notif_type="loan_due",
                    title=title,
                    message=message,
                    reference_id=loan.id,
                    reference_table="bank_loans"
                )

        print(f"[Loan Agent] Checked {len(loans)} loans")
    finally:
        db.close()


# ─── Agent 3: Vikoba Agent ───────────────────────────────────

def vikoba_agent():
    """
    Check Vikoba hisa due dates.
    Flag missed payments and apply penalties automatically.
    """
    db = SessionLocal()
    try:
        today = date.today()

        # Find all pending hisa payments that are now overdue
        overdue_hisa = db.query(models.HisaPayment).filter(
            models.HisaPayment.status == "pending",
            models.HisaPayment.due_date < today
        ).all()

        for hisa in overdue_hisa:
            # Mark as missed
            hisa.status = "missed"

            # Get group penalty rules
            group = db.query(models.VikobaGroup).filter(
                models.VikobaGroup.id == hisa.group_id
            ).first()

            if not group:
                continue

            # Calculate penalty
            if group.penalty_type == "fixed":
                penalty_amount = float(group.penalty_value or 0)
            elif group.penalty_type == "percentage":
                penalty_amount = float(hisa.amount) * float(group.penalty_value or 0) / 100
            else:
                penalty_amount = float(group.penalty_value or 0)

            # Log penalty
            if penalty_amount > 0:
                penalty = models.HisaPenalty(
                    group_id=hisa.group_id,
                    member_id=hisa.member_id,
                    hisa_id=hisa.id,
                    penalty_date=today,
                    amount=penalty_amount,
                    status="unpaid"
                )
                db.add(penalty)

            # Get member name for notification
            member = db.query(models.VikobaMember).filter(
                models.VikobaMember.id == hisa.member_id
            ).first()

            member_name = member.full_name if member else "A member"

            send_push(
                db=db,
                company_id=group.company_id,
                notif_type="vikoba_missed",
                title=f"❌ Missed Hisa: {group.name}",
                message=f"{member_name} missed hisa of {float(hisa.amount):,.0f} TZS due {hisa.due_date}. Penalty applied: {penalty_amount:,.0f} TZS.",
                reference_id=hisa.id,
                reference_table="hisa_payments"
            )

        db.commit()

        # Also alert for upcoming hisa due tomorrow
        tomorrow = today + timedelta(days=1)
        upcoming = db.query(models.HisaPayment).filter(
            models.HisaPayment.status == "pending",
            models.HisaPayment.due_date == tomorrow
        ).all()

        for hisa in upcoming:
            group = db.query(models.VikobaGroup).filter(
                models.VikobaGroup.id == hisa.group_id
            ).first()
            member = db.query(models.VikobaMember).filter(
                models.VikobaMember.id == hisa.member_id
            ).first()
            if group and member:
                send_push(
                    db=db,
                    company_id=group.company_id,
                    notif_type="vikoba_reminder",
                    title=f"🔔 Hisa Due Tomorrow: {group.name}",
                    message=f"{member.full_name}'s hisa of {float(hisa.amount):,.0f} TZS is due tomorrow.",
                    reference_id=hisa.id,
                    reference_table="hisa_payments"
                )

        print(f"[Vikoba Agent] Processed {len(overdue_hisa)} overdue, {len(upcoming)} upcoming")
    finally:
        db.close()


# ─── Agent 4: Tender Agent ───────────────────────────────────

def tender_agent():
    """Alert when tender delivery deadlines are approaching."""
    db = SessionLocal()
    try:
        active_tenders = db.query(models.Tender).filter(
            models.Tender.status.in_(["won", "active", "planning"])
        ).all()

        for tender in active_tenders:
            days_left = days_until(tender.delivery_deadline)

            if days_left in [14, 7, 3, 1, 0]:
                # Check pending procurement items
                pending_items = db.query(models.ProcurementItem).filter(
                    models.ProcurementItem.tender_id == tender.id,
                    models.ProcurementItem.status == "pending"
                ).count()

                if days_left == 0:
                    title = f"🚨 DELIVERY TODAY: {tender.name}"
                    message = f"Tender '{tender.name}' delivery is TODAY. {pending_items} items still pending."
                else:
                    title = f"📦 Tender Deadline in {days_left} days"
                    message = f"'{tender.name}' delivery in {days_left} days. {pending_items} procurement items still pending."

                send_push(
                    db=db,
                    company_id=tender.company_id,
                    notif_type="tender_deadline",
                    title=title,
                    message=message,
                    reference_id=tender.id,
                    reference_table="tenders"
                )

        print(f"[Tender Agent] Checked {len(active_tenders)} tenders")
    finally:
        db.close()


# ─── Agent 5: Daily Summary Agent ───────────────────────────

def summary_agent():
    """Send evening P&L summary to all companies."""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        today = date.today()

        companies = db.query(models.Company).all()

        for company in companies:
            cid = company.id

            total_sales = db.query(func.coalesce(func.sum(models.SaleEntry.total_amount), 0)).filter(
                models.SaleEntry.company_id == cid,
                models.SaleEntry.sale_date == today
            ).scalar()

            total_purchases = db.query(func.coalesce(func.sum(models.Purchase.total_cost), 0)).filter(
                models.Purchase.company_id == cid,
                models.Purchase.purchase_date == today
            ).scalar()

            total_expenses = db.query(func.coalesce(func.sum(models.Expense.amount), 0)).filter(
                models.Expense.company_id == cid,
                models.Expense.expense_date == today
            ).scalar()

            net = float(total_sales) - float(total_purchases) - float(total_expenses)
            emoji = "📈" if net >= 0 else "📉"

            send_push(
                db=db,
                company_id=cid,
                notif_type="daily_summary",
                title=f"{emoji} Daily Summary — {today}",
                message=(
                    f"Sales: {float(total_sales):,.0f} TZS | "
                    f"Purchases: {float(total_purchases):,.0f} TZS | "
                    f"Expenses: {float(total_expenses):,.0f} TZS | "
                    f"Net: {net:,.0f} TZS"
                )
            )

        print(f"[Summary Agent] Sent summaries to {len(companies)} companies")
    finally:
        db.close()