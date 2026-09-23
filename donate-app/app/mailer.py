import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from .config import (
    DATA_DIR,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USER,
)


def send_receipt(to_email: str, subject: str, html: str, pdf_path: Path) -> str:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content("Your donation receipt is attached as a PDF.")
    msg.add_alternative(html, subtype="html")
    pdf_bytes = pdf_path.read_bytes()
    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=pdf_path.name,
    )

    if not SMTP_PASSWORD:
        out = DATA_DIR / "outbox" / f"{pdf_path.stem}.eml"
        out.write_bytes(bytes(msg))
        return f"saved:{out}"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as smtp:
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)
    return "sent"
