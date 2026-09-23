from datetime import datetime
from typing import Optional
from pathlib import Path
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .config import ACCOUNT_NAME, BANK_ACCOUNT, BANK_IFSC, BANK_NAME, DATA_DIR, FOUNDATION
from .words import rupees_in_words

IST = ZoneInfo("Asia/Kolkata")
MAROON = colors.HexColor("#6e2e26")
GOLD = colors.HexColor("#c4a04a")
INK = colors.HexColor("#1c1712")


def _ist(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(IST)
    return dt.astimezone(IST)


def receipt_pdf_path(donation_id: str) -> Path:
    return DATA_DIR / "receipts" / f"{donation_id}.pdf"


def write_receipt_pdf(donation) -> Path:
    path = receipt_pdf_path(donation.id)
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleKn",
        parent=styles["Title"],
        fontName="Times-Bold",
        fontSize=16,
        textColor=MAROON,
        spaceAfter=4,
    )
    sub = ParagraphStyle(
        "SubKn",
        parent=styles["Normal"],
        fontSize=9,
        textColor=INK,
        leading=12,
        alignment=1,
    )
    body = ParagraphStyle(
        "BodyKn",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=INK,
    )
    small = ParagraphStyle(
        "SmallKn",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#5d554b"),
    )

    paid = _ist(donation.paid_at or donation.created_at)
    story = [
        Paragraph(FOUNDATION["name"], title),
        Paragraph("Section 8 company · Donation receipt", sub),
        Paragraph(
            f"{FOUNDATION['address']}<br/>CIN {FOUNDATION['cin']} · PAN {FOUNDATION['pan']}",
            sub,
        ),
        Spacer(1, 8 * mm),
        Paragraph(f"<b>Receipt no.</b> {donation.id}", body),
        Paragraph(f"<b>Date &amp; time</b> {paid.strftime('%d %b %Y, %I:%M %p')} IST", body),
        Spacer(1, 4 * mm),
    ]

    rows = [
        [Paragraph("<b>Donor name</b>", body), Paragraph(donation.name, body)],
        [Paragraph("<b>Mobile</b>", body), Paragraph(donation.phone, body)],
        [Paragraph("<b>Email</b>", body), Paragraph(donation.email, body)],
        [
            Paragraph("<b>Amount</b>", body),
            Paragraph(f"₹ {donation.amount_rupees:,} ({rupees_in_words(donation.amount_rupees)})", body),
        ],
        [Paragraph("<b>Mode</b>", body), Paragraph("UPI (QR)", body)],
        [Paragraph("<b>Credited to</b>", body), Paragraph(f"{ACCOUNT_NAME}", body)],
        [Paragraph("<b>Bank</b>", body), Paragraph(f"{BANK_NAME} · A/c {BANK_ACCOUNT} · IFSC {BANK_IFSC}", body)],
    ]
    if donation.utr:
        rows.append([Paragraph("<b>UTR / ref</b>", body), Paragraph(donation.utr, body)])

    table = Table(rows, colWidths=[45 * mm, 125 * mm])
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e4d8c6")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#fbf7f0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story += [
        table,
        Spacer(1, 8 * mm),
        Paragraph(
            "12A URN AALCK8805BE20251 and 80G URN AALCK8805BF20261 are <b>provisional</b> "
            "for AY 2026–27 to 2028–29. Confirm with the office before claiming a deduction.",
            small,
        ),
        Spacer(1, 3 * mm),
        Paragraph(
            "This is a system-generated receipt. No signature is required. "
            f"Queries: {FOUNDATION['email']}",
            small,
        ),
    ]

    def draw_line(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(MAROON)
        canvas.rect(0, A4[1] - 8 * mm, A4[0], 8 * mm, fill=1, stroke=0)
        canvas.setFillColor(GOLD)
        canvas.rect(0, 0, A4[0], 6 * mm, fill=1, stroke=0)
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=f"Donation receipt {donation.id}",
        author=FOUNDATION["name"],
    )
    doc.build(story, onFirstPage=draw_line, onLaterPages=draw_line)
    return path


def receipt_email_html(donation) -> str:
    paid = _ist(donation.paid_at or donation.created_at)
    return f"""
    <div style="font-family:Georgia,serif;color:#1c1712">
      <h2 style="color:#6e2e26">{FOUNDATION["name"]}</h2>
      <p>Namaste {donation.name},</p>
      <p>We have received your donation of <b>₹ {donation.amount_rupees:,}</b>
      on {paid.strftime("%d %b %Y, %I:%M %p")} IST.</p>
      <p>Receipt number: <b>{donation.id}</b></p>
      <p>The amount is credited to the Foundation current account with {BANK_NAME}
      (A/c {BANK_ACCOUNT}, IFSC {BANK_IFSC}).</p>
      <p>The PDF receipt is attached. 12A / 80G approvals are provisional for AY 2026–27 to 2028–29.</p>
      <p>— Office mailbox {FOUNDATION["email"]}</p>
    </div>
    """
