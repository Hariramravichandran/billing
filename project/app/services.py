import json
from fpdf import FPDF
import smtplib
import os
from email.message import EmailMessage

class PDF(FPDF):
    def header(self):
        """Custom header for the PDF"""
        self.set_font("Arial", "B", 12)
        self.cell(200, 10, "Billing Page", ln=True, align="C")
        self.ln(10)

    def footer(self):
        """Custom footer for the PDF"""
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_bill_pdf(purchase_data, pdf_filename):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)

    pdf.cell(200, 10, "Billing Page", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(40, 10, "Customer Email:", border=1)
    pdf.cell(150, 10, purchase_data["customer_email"], border=1, ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, "Bill Details", ln=True, align="C")
    pdf.ln(5)

    headers = ["Product ID", "Quantity", "Unit Price", "Tax Amount", "Total Price"]
    col_width = 40
    
    for header in headers:
        pdf.cell(col_width, 10, header, border=1, align="C")
    pdf.ln()

    #  Ensure purchase_items is a proper list of dictionaries
    purchase_items = purchase_data["purchase_items"]
    if isinstance(purchase_items, str):  
        purchase_items = json.loads(purchase_items)  # Convert JSON string to Python list

    for item in purchase_items:
        pdf.cell(col_width, 10, str(item.get("product_id", "-")), border=1)
        pdf.cell(col_width, 10, str(item.get("quantity", "-")), border=1)
        pdf.cell(col_width, 10, str(item.get("price_per_unit", "-")), border=1)
        pdf.cell(col_width, 10, str(item.get("tax_amount", "-")), border=1)
        pdf.cell(col_width, 10, str(item.get("total_price", "-")), border=1)
        pdf.ln()

    pdf.ln(10)
    pdf.cell(200, 10, f"Total Price: {purchase_data['total_amount']}", ln=True, align="R")

    pdf.output(pdf_filename)
    return pdf_filename

def send_email_with_attachment(to_email, pdf_filename):
    sender_email = "test1michaelvo@gmail.com"
    sender_password="mlau xvpp wkoe shqe" # Use environment variables instead of hardcoding passwords!

    subject = "Your Purchase Invoice"
    body = "Please find your invoice attached."

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with open(pdf_filename, "rb") as attachment:
        msg.add_attachment(attachment.read(), maintype="application", subtype="pdf", filename=os.path.basename(pdf_filename))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_email} with attachment {pdf_filename}")
    except Exception as e:
        print(f"Error sending email: {e}")
