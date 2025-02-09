# app/services.py
import smtplib
from email.message import EmailMessage

async def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = "noreply@billing.com"
    msg["To"] = to_email
    
    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("user@example.com", "password")
        server.send_message(msg)