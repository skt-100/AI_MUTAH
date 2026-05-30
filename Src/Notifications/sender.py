import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import settings as st


def send_email(to_email, subject, body):
    """إرسال بريد إلكتروني عبر Gmail SMTP"""
    msg = MIMEMultipart()
    msg["From"]    = st.GMAIL_USER
    msg["To"]      = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(st.GMAIL_USER, st.GMAIL_PASSWORD)
        server.send_message(msg)
