import json
import logging
from datetime import datetime, timezone

import httpx

from .config import (
    PAYMENT_MODE,
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
    UPI_PAYEE_NAME,
    UPI_VPA,
)
from . import mswipe, uropay
from .db import SessionLocal
from .mailer import send_receipt
from .models import Donation, Seq


def next_web_note(db) -> str:
    row = db.get(Seq, "web")
    if row is None:
        row = Seq(name="web", n=0)
        db.add(row)
        db.flush()
    row.n += 1
    db.flush()
    return f"knbmf{row.n}"
from .qr import build_upi_uri, write_qr_png
from .receipts import receipt_email_html, write_receipt_pdf

log = logging.getLogger("donations")


def attach_qr(donation: Donation) -> Donation:
    note = (donation.note or donation.id).strip()
    vpa = (UPI_VPA or "").strip()
    if PAYMENT_MODE == "mswipe":
        link = mswipe.create_payment_link(
            donation_id=donation.id,
            amount_rupees=donation.amount_rupees,
            email=donation.email,
            phone=donation.phone,
            name=donation.name,
        )
        donation.provider = "mswipe"
        donation.provider_ref = link["trans_id"]
        donation.upi_uri = link["url"]
        return donation
    if uropay.configured():
        order = uropay.create_order(
            tenant_ref=donation.id,
            amount_rupees=donation.amount_rupees,
            email=donation.email,
            phone=donation.phone,
            name=donation.name,
        )
        donation.provider = "uropay"
        donation.provider_ref = str(order.get("id") or "")
        donation.upi_uri = str(order.get("openUrl") or "")
        return donation
    if PAYMENT_MODE == "razorpay" and RAZORPAY_KEY_ID:
        donation.provider = "razorpay"
        donation.upi_uri = _razorpay_qr(donation)
        write_qr_png(donation.id, donation.upi_uri)
        return donation
    if vpa and "@" in vpa and not vpa.startswith("set-upi-vpa"):
        donation.provider = "upi"
        donation.upi_uri = build_upi_uri(donation.amount_rupees, note, vpa=vpa)
        write_qr_png(donation.id, donation.upi_uri)
        return donation
    donation.provider = "demo"
    donation.upi_uri = ""
    return donation


def _razorpay_qr(donation: Donation) -> str:
    auth = (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
    payload = {
        "type": "upi_qr",
        "name": UPI_PAYEE_NAME[:20],
        "usage": "single_use",
        "fixed_amount": True,
        "payment_amount": donation.amount_rupees * 100,
        "description": donation.id,
        "notes": {"donation_id": donation.id},
    }
    r = httpx.post("https://api.razorpay.com/v1/payments/qr_codes", auth=auth, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    donation.provider_ref = data.get("id", "")
    image_url = data.get("image_url") or ""
    # Prefer NPCI UPI string if Razorpay returns one; else keep image_url for display.
    return data.get("upi_link") or image_url or build_upi_uri(donation.amount_rupees, donation.id)


def mark_paid(donation_id: str, utr: str = ""):
    db = SessionLocal()
    try:
        donation = db.get(Donation, donation_id)
        if donation is None:
            return None
        if donation.status == "paid":
            return donation
        donation.status = "paid"
        donation.paid_at = datetime.now(timezone.utc)
        if utr:
            donation.utr = utr
        db.commit()
        db.refresh(donation)
        _send_receipt(db, donation)
        db.commit()
        db.refresh(donation)
        return donation
    finally:
        db.close()


def _send_receipt(db, donation: Donation) -> None:
    try:
        pdf = write_receipt_pdf(donation)
        html = receipt_email_html(donation)
        result = send_receipt(
            donation.email,
            f"Donation receipt {donation.id} — {UPI_PAYEE_NAME}",
            html,
            pdf,
        )
        donation.receipt_sent_at = datetime.now(timezone.utc)
        donation.receipt_error = "" if result.startswith("sent") or result.startswith("saved") else result
        if result.startswith("saved"):
            donation.receipt_error = result
        db.add(donation)
    except Exception as exc:  # noqa: BLE001
        log.exception("receipt failed")
        donation.receipt_error = str(exc)[:500]
        db.add(donation)
