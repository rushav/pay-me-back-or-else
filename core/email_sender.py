import os
import smtplib
import urllib.parse
from email.mime.text import MIMEText

import streamlit as st


def send_letter_email(
    to_email: str,
    debtor_name: str,
    letter_text: str,
    sender_name: str = "Pay Me Back or Else",
) -> tuple[bool, str]:
    """Send the letter via email. Returns (success, message)."""
    subject = f"You Owe Me Money, {debtor_name}"

    resend_key = st.secrets.get("RESEND_API_KEY", "") or os.environ.get("RESEND_API_KEY", "")
    if resend_key:
        return _send_resend(resend_key, to_email, subject, letter_text, sender_name)

    smtp_email = st.secrets.get("SMTP_EMAIL", "") or os.environ.get("SMTP_EMAIL", "")
    smtp_pass = st.secrets.get("SMTP_APP_PASSWORD", "") or os.environ.get("SMTP_APP_PASSWORD", "")
    if smtp_email and smtp_pass:
        return _send_smtp(smtp_email, smtp_pass, to_email, subject, letter_text)

    return False, "mailto"


def get_mailto_link(to_email: str, debtor_name: str, letter_text: str) -> str:
    """Generate a mailto: link as fallback."""
    subject = f"You Owe Me Money, {debtor_name}"
    params = urllib.parse.urlencode({"subject": subject, "body": letter_text}, quote_via=urllib.parse.quote)
    return f"mailto:{to_email}?{params}"


def _send_resend(api_key: str, to: str, subject: str, body: str, sender_name: str) -> tuple[bool, str]:
    try:
        import resend
        resend.api_key = api_key
        resend.Emails.send({
            "from": f"{sender_name} <onboarding@resend.dev>",
            "to": [to],
            "subject": subject,
            "text": body,
        })
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Failed to send via Resend: {e}"


def _send_smtp(email: str, password: str, to: str, subject: str, body: str) -> tuple[bool, str]:
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = email
        msg["To"] = to
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(email, password)
            server.sendmail(email, to, msg.as_string())
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Failed to send via SMTP: {e}"
