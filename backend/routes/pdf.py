from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
import models
from core.security import get_current_user
from database import get_db
from weasyprint import HTML, CSS
from jinja2 import Template
import base64

router = APIRouter(prefix="/pdf", tags=["PDF Generation"])


def get_company_info(company_id: str, db: Session):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    return company


def generate_document_html(document, company, items, db: Session):
    """Generate HTML for document using Jinja2 template"""
    
    # Load company logo if available
    logo_html = ""
    if company.logo_url:
        logo_html = f'<img src="{company.logo_url}" alt="Company Logo" style="max-height: 60px;">'
    
    # Generate items HTML
    items_html = ""
    for item in items:
        items_html += f"""
        <tr>
            <td>{item.description}</td>
            <td style="text-align: center;">{item.quantity}</td>
            <td style="text-align: center;">{item.unit or ''}</td>
            <td style="text-align: right;">{document.currency} {item.unit_price:,.2f}</td>
            <td style="text-align: right;">{document.currency} {item.total:,.2f}</td>
        </tr>
        """
    
    # Document type labels
    document_labels = {
        'QUO': 'QUOTATION',
        'PRO': 'PROFORMA INVOICE',
        'INV': 'INVOICE',
        'RCP': 'RECEIPT',
        'CRN': 'CREDIT NOTE',
        'DBN': 'DEBIT NOTE',
        'DLN': 'DELIVERY NOTE'
    }
    
    document_label = document_labels.get(document.document_type, document.document_type)
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #333;
            }}
            .company-info {{
                flex: 1;
            }}
            .company-info h1 {{
                margin: 0;
                font-size: 24px;
                color: #2c3e50;
            }}
            .company-info p {{
                margin: 5px 0;
                font-size: 12px;
                color: #666;
            }}
            .logo {{
                flex: 0 0 auto;
            }}
            .document-title {{
                text-align: center;
                margin: 30px 0;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }}
            .document-title h2 {{
                margin: 0;
                font-size: 28px;
                color: #2c3e50;
            }}
            .client-section {{
                margin: 30px 0;
                padding: 20px;
                background-color: #f9f9f9;
                border-radius: 5px;
            }}
            .client-section h3 {{
                margin: 0 0 10px 0;
                font-size: 14px;
                color: #666;
            }}
            .client-section p {{
                margin: 5px 0;
                font-size: 14px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 30px 0;
            }}
            th {{
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                text-align: left;
                font-size: 12px;
            }}
            td {{
                padding: 12px;
                border-bottom: 1px solid #ddd;
                font-size: 12px;
            }}
            .totals {{
                text-align: right;
                margin-top: 30px;
            }}
            .totals-row {{
                display: flex;
                justify-content: flex-end;
                padding: 10px 0;
                font-size: 14px;
            }}
            .totals-label {{
                margin-right: 30px;
                color: #666;
            }}
            .totals-value {{
                font-weight: bold;
                min-width: 150px;
            }}
            .grand-total {{
                background-color: #2c3e50;
                color: white;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .grand-total .totals-value {{
                font-size: 18px;
            }}
            .footer {{
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
            .signature {{
                margin-top: 30px;
                padding-top: 40px;
                text-align: right;
            }}
            .signature-line {{
                border-top: 1px solid #333;
                display: inline-block;
                padding-top: 5px;
                margin-left: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">
                {logo_html}
            </div>
            <div class="company-info">
                <h1>{company.name}</h1>
                <p>{company.address or ''}</p>
                <p>TIN: {company.tin or 'N/A'} | Phone: {company.phone or 'N/A'}</p>
                {company.bank_name and company.bank_account_number and f"<p>Bank: {company.bank_name} | Account: {company.bank_account_number}</p>"}
            </div>
        </div>
        
        <div class="document-title">
            <h2>{document_label}</h2>
            <p>Number: {document.document_number} | Date: {document.issue_date}</p>
            {document.due_date and f"<p>Due Date: {document.due_date}</p>"}
        </div>
        
        <div class="client-section">
            <h3>BILL TO:</h3>
            <p><strong>{document.client_name}</strong></p>
            <p>{document.client_address}</p>
            {document.client_tin and f"<p>TIN: {document.client_tin}</p>"}
            {document.client_phone and f"<p>Phone: {document.client_phone}</p>"}
            {document.client_email and f"<p>Email: {document.client_email}</p>"}
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Description</th>
                    <th style="text-align: center;">Quantity</th>
                    <th style="text-align: center;">Unit</th>
                    <th style="text-align: right;">Unit Price</th>
                    <th style="text-align: right;">Total</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>
        
        <div class="totals">
            <div class="totals-row">
                <span class="totals-label">Subtotal:</span>
                <span class="totals-value">{document.currency} {document.subtotal:,.2f}</span>
            </div>
            {document.vat_rate and document.vat_rate > 0 and f"""
            <div class="totals-row">
                <span class="totals-label">VAT ({document.vat_rate}%):</span>
                <span class="totals-value">{document.currency} {document.vat_amount:,.2f}</span>
            </div>
            """}
            <div class="totals-row grand-total">
                <span class="totals-label">GRAND TOTAL:</span>
                <span class="totals-value">{document.currency} {document.grand_total:,.2f}</span>
            </div>
        </div>
        
        {document.notes and f"""
        <div style="margin-top: 30px; padding: 20px; background-color: #f9f9f9; border-radius: 5px;">
            <h3 style="margin: 0 0 10px 0; font-size: 14px; color: #666;">NOTES:</h3>
            <p style="margin: 0; font-size: 14px;">{document.notes}</p>
        </div>
        """}
        
        <div class="footer">
            <p>Thank you for your business!</p>
            <p>Generated by Company Manager</p>
        </div>
        
        <div class="signature">
            <span class="signature-line">Authorized Signature</span>
        </div>
    </body>
    </html>
    """
    
    return html_template


@router.get("/documents/{document_id}")
def generate_document_pdf(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate PDF for a business document"""
    
    # Get document
    document = db.query(models.BusinessDocument).filter(
        models.BusinessDocument.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check access
    if document.sender_company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get company info
    company = get_company_info(document.sender_company_id, db)
    
    # Get document items
    items = db.query(models.DocumentItem).filter(
        models.DocumentItem.document_id == document_id
    ).all()
    
    # Generate HTML
    html_content = generate_document_html(document, company, items, db)
    
    # Generate PDF using WeasyPrint
    try:
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={document.document_type}_{document.document_number}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/payslips/{payroll_item_id}")
def generate_payslip_pdf(
    payroll_item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate PDF for employee payslip"""
    
    # Get payroll item
    payroll_item = db.query(models.PayrollItem).filter(
        models.PayrollItem.id == payroll_item_id
    ).first()
    
    if not payroll_item:
        raise HTTPException(status_code=404, detail="Payroll item not found")
    
    # Get related data
    payroll_run = db.query(models.PayrollRun).filter(
        models.PayrollRun.id == payroll_item.payroll_run_id
    ).first()
    
    employee = db.query(models.Employee).filter(
        models.Employee.id == payroll_item.employee_id
    ).first()
    
    company = get_company_info(current_user.company_id, db)
    
    # Get deductions and allowances
    deductions = db.query(models.PayrollDeduction).filter(
        models.PayrollDeduction.payroll_item_id == payroll_item_id
    ).all()
    
    allowances = db.query(models.PayrollAllowance).filter(
        models.PayrollAllowance.payroll_item_id == payroll_item_id
    ).all()
    
    # Generate payslip HTML
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #333;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                color: #2c3e50;
            }}
            .employee-info {{
                margin: 30px 0;
                padding: 20px;
                background-color: #f9f9f9;
                border-radius: 5px;
            }}
            .employee-info p {{
                margin: 5px 0;
                font-size: 14px;
            }}
            .salary-section {{
                margin: 30px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th {{
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                text-align: left;
                font-size: 12px;
            }}
            td {{
                padding: 12px;
                border-bottom: 1px solid #ddd;
                font-size: 12px;
            }}
            .amount {{
                text-align: right;
            }}
            .total {{
                background-color: #2c3e50;
                color: white;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>PAYSLIP</h1>
            <p>{company.name}</p>
            <p>Period: {payroll_run.period_month}/{payroll_run.period_year}</p>
        </div>
        
        <div class="employee-info">
            <p><strong>Employee:</strong> {employee.full_name}</p>
            <p><strong>Position:</strong> {employee.position or 'N/A'}</p>
            <p><strong>Department:</strong> {employee.department or 'N/A'}</p>
        </div>
        
        <div class="salary-section">
            <h3>EARNINGS</h3>
            <table>
                <tr>
                    <th>Description</th>
                    <th class="amount">Amount</th>
                </tr>
                <tr>
                    <td>Basic Salary</td>
                    <td class="amount">TZS {payroll_item.basic_salary:,.2f}</td>
                </tr>
                {''.join([f'<tr><td>{a.allowance_name}</td><td class="amount">TZS {a.amount:,.2f}</td></tr>' for a in allowances])}
            </table>
            
            <h3>DEDUCTIONS</h3>
            <table>
                <tr>
                    <th>Description</th>
                    <th class="amount">Amount</th>
                </tr>
                {''.join([f'<tr><td>{d.deduction_name}</td><td class="amount">TZS {d.amount:,.2f}</td></tr>' for d in deductions])}
            </table>
            
            <h3>SUMMARY</h3>
            <table>
                <tr>
                    <td>Gross Pay</td>
                    <td class="amount">TZS {payroll_item.gross_pay:,.2f}</td>
                </tr>
                <tr>
                    <td>Total Deductions</td>
                    <td class="amount">TZS {payroll_item.total_deductions:,.2f}</td>
                </tr>
                <tr class="total">
                    <td><strong>NET PAY</strong></td>
                    <td class="amount"><strong>TZS {payroll_item.net_pay:,.2f}</strong></td>
                </tr>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Company Manager</p>
        </div>
    </body>
    </html>
    """
    
    # Generate PDF
    try:
        pdf_bytes = HTML(string=html_template).write_pdf()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=payslip_{employee.full_name.replace(' ', '_')}_{payroll_run.period_month}_{payroll_run.period_year}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")