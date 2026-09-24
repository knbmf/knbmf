import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import BackgroundTasks, Depends, FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, object_session
from starlette.middleware.sessions import SessionMiddleware

from .config import (
    ADMIN_PASSWORD,
    ADMIN_USER,
    DATA_DIR,
    FOUNDATION,
    PAYMENT_MODE,
    SECRET_KEY,
    UPI_VPA,
)
from .db import SessionLocal, init_db
from .models import Donation
from . import mswipe, uropay
from .payments import attach_qr, mark_paid, next_web_note
from .words import rupees_in_words

IST = ZoneInfo("Asia/Kolkata")
ROOT = Path(__file__).resolve().parent
SITE_ROOT = ROOT.parent.parent
PHONE_RE = re.compile(r"^[6-9]\d{9}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SITE_PAGES = {
    "about",
    "clinic",
    "projects",
    "work",
    "donate",
    "give",
    "transparency",
    "contact",
    "policies",
    "terms",
    "privacy_policy",
    "refund_policy",
    "return_policy",
    "shipping_policy",
    "404",
}

app = FastAPI(title="KNBMF Donations")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, same_site="lax")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
app.mount("/qr", StaticFiles(directory=DATA_DIR / "qr"), name="qr")
app.mount("/css", StaticFiles(directory=SITE_ROOT / "css"), name="site-css")
app.mount("/assets", StaticFiles(directory=SITE_ROOT / "assets"), name="site-assets")
@app.get("/js/pay-config.js")
def pay_config_js():
    # Same-origin when this app is serving the site, so local UAT does not call the public tunnel.
    if PAYMENT_MODE == "mswipe":
        return Response('window.KNBMF_PAY_API = "";\n', media_type="application/javascript")
    return FileResponse(SITE_ROOT / "js" / "pay-config.js", media_type="application/javascript")


app.mount("/js", StaticFiles(directory=SITE_ROOT / "js"), name="site-js")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def ist(dt):
    if dt is None:
        return "—"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST).strftime("%d %b %Y, %I:%M %p")


templates.env.filters["ist"] = ist
templates.env.filters["inr"] = lambda n: f"{int(n):,}"
templates.env.globals["foundation"] = FOUNDATION
templates.env.globals["payment_mode"] = PAYMENT_MODE


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup() -> None:
    init_db()


def new_id(db: Session) -> str:
    day = datetime.now(IST).strftime("%Y%m%d")
    for _ in range(12):
        candidate = f"KNBMF-{day}-{secrets.randbelow(9000) + 1000}"
        if db.get(Donation, candidate) is None:
            return candidate
    return f"KNBMF-{day}-{secrets.token_hex(3).upper()}"


def require_admin(request: Request) -> None:
    if not request.session.get("admin"):
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})


def _secret_match(given: str, expected: str) -> bool:
    given_b = given.encode()
    expected_b = expected.encode()
    if not expected_b or len(given_b) != len(expected_b):
        return False
    return secrets.compare_digest(given_b, expected_b)


@app.get("/", response_class=HTMLResponse)
def website_home():
    return FileResponse(SITE_ROOT / "index.html")


@app.get("/{page}.html")
def website_page(page: str):
    if page not in SITE_PAGES:
        raise HTTPException(404)
    path = SITE_ROOT / f"{page}.html"
    if not path.is_file():
        raise HTTPException(404)
    return FileResponse(path)


@app.get("/give", response_class=HTMLResponse)
def give_form(request: Request):
    return templates.TemplateResponse(
        "donate.html",
        {"request": request, "error": None, "form": {}},
    )


@app.post("/give")
@app.post("/donate")
def create_donation(
    request: Request,
    background: BackgroundTasks,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    amount: str = Form(...),
    db: Session = Depends(get_db),
):
    name = " ".join(name.strip().split())
    phone = re.sub(r"\D", "", phone)[-10:]
    email = email.strip().lower()
    error = None
    try:
        rupees = int(str(amount).replace(",", "").strip())
    except ValueError:
        rupees = 0
        error = "Enter the amount in whole rupees."
    if not name or len(name) < 2:
        error = "Please enter the donor name."
    elif not PHONE_RE.match(phone):
        error = "Enter a valid 10-digit Indian mobile number."
    elif not EMAIL_RE.match(email):
        error = "Enter a valid email — the receipt is sent here."
    elif rupees < 1 or rupees > 500000:
        error = "Amount must be between ₹1 and ₹5,00,000."
    if error:
        return templates.TemplateResponse(
            "donate.html",
            {
                "request": request,
                "error": error,
                "form": {"name": name, "phone": phone, "email": email, "amount": amount},
            },
            status_code=400,
        )

    donation = Donation(
        id=new_id(db),
        name=name,
        phone=phone,
        email=email,
        amount_rupees=rupees,
        note=next_web_note(db),
        status="pending",
    )
    try:
        attach_qr(donation)
    except (ValueError, uropay.UroPayError, mswipe.MswipeError) as exc:
        donation.status = "failed"
        donation.receipt_error = str(exc)[:500]
        db.add(donation)
        db.commit()
        return templates.TemplateResponse(
            "donate.html",
            {"request": request, "error": str(exc), "form": {"name": name, "phone": phone, "email": email, "amount": amount}},
            status_code=400,
        )
    db.add(donation)
    db.commit()

    if donation.provider in {"uropay", "mswipe"} and donation.upi_uri:
        return RedirectResponse(donation.upi_uri, status_code=303)

    if PAYMENT_MODE == "demo":
        donation_id = donation.id
        background.add_task(_demo_confirm, donation_id)

    return RedirectResponse(f"/pay/{donation.id}", status_code=303)


def _demo_confirm(donation_id: str) -> None:
    import time

    time.sleep(12)
    mark_paid(donation_id, utr="DEMO")


@app.get("/pay/{donation_id}", response_class=HTMLResponse)
def pay_page(request: Request, donation_id: str, db: Session = Depends(get_db)):
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise HTTPException(404, "Donation not found")
    if donation.status == "paid":
        return RedirectResponse(f"/success/{donation.id}", status_code=303)
    return templates.TemplateResponse(
        "pay.html",
        {
            "request": request,
            "d": donation,
            "words": rupees_in_words(donation.amount_rupees),
            "has_vpa": bool(UPI_VPA),
        },
    )


def _new_pending_donation(db: Session, name: str, phone: str, email: str, rupees: int) -> Donation:
    donation = Donation(
        id=new_id(db),
        name=name,
        phone=phone,
        email=email,
        amount_rupees=rupees,
        note=next_web_note(db),
        status="pending",
    )
    try:
        attach_qr(donation)
    except (ValueError, uropay.UroPayError, mswipe.MswipeError) as exc:
        donation.status = "failed"
        donation.receipt_error = str(exc)[:500]
        db.add(donation)
        db.commit()
        raise
    db.add(donation)
    db.commit()
    db.refresh(donation)
    return donation


@app.post("/api/uropay/order")
async def api_uropay_order(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")
    name = " ".join(str(body.get("name") or "").strip().split())
    phone = re.sub(r"\D", "", str(body.get("phone") or ""))[-10:]
    email = str(body.get("email") or "").strip().lower()
    try:
        rupees = int(str(body.get("amount") or "").replace(",", "").strip())
    except ValueError:
        rupees = 0
    if not name or len(name) < 2:
        raise HTTPException(400, "Please enter the donor name.")
    if not PHONE_RE.match(phone):
        raise HTTPException(400, "Enter a valid 10-digit Indian mobile number.")
    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Enter a valid email.")
    if rupees < 1 or rupees > 500000:
        raise HTTPException(400, "Amount must be between ₹1 and ₹5,00,000.")
    try:
        donation = _new_pending_donation(db, name, phone, email, rupees)
    except (uropay.UroPayError, mswipe.MswipeError) as exc:
        raise HTTPException(502, str(exc)) from exc
    if donation.provider not in {"uropay", "mswipe"} or not donation.upi_uri:
        raise HTTPException(503, "Card and UPI checkout is not configured on the server.")
    return {
        "id": donation.id,
        "openUrl": donation.upi_uri,
        "provider": donation.provider,
        "amount": donation.amount_rupees,
    }


@app.post("/api/uropay/webhook")
async def api_uropay_webhook(request: Request):
    raw = (await request.body()).decode("utf-8")
    header_map = {k: v for k, v in request.headers.items()}
    if not uropay.verify_webhook(header_map, raw):
        raise HTTPException(401, "bad signature")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON")
    ref = str(payload.get("tenantOrderRef") or "")
    status = str(payload.get("status") or "")
    if status == "PAID" and ref:
        mark_paid(ref, utr=str(payload.get("orderId") or ""))
    return JSONResponse({"ok": True})


@app.get("/uropay/return")
def uropay_return(ref: str = "", db: Session = Depends(get_db)):
    if not ref:
        return RedirectResponse("/give.html", status_code=303)
    donation = db.get(Donation, ref)
    if donation is None:
        raise HTTPException(404, "Donation not found")
    if donation.status != "paid" and donation.provider_ref:
        try:
            order = uropay.get_order(donation.provider_ref)
            if str(order.get("status") or "") == "PAID":
                mark_paid(donation.id, utr=str(order.get("id") or ""))
                donation = db.get(Donation, ref)
        except uropay.UroPayError:
            pass
    if donation and donation.status == "paid":
        return RedirectResponse(f"/success/{donation.id}", status_code=303)
    return RedirectResponse(f"/pay/{ref}", status_code=303)


def _refresh_mswipe(donation: Donation) -> Donation:
    if donation.status == "paid" or donation.provider != "mswipe" or not donation.provider_ref:
        return donation
    try:
        row = mswipe.transaction_status(donation.provider_ref)
    except mswipe.MswipeError:
        return donation
    desc = str(row.get("Payment_Desc") or "")
    paid = str(row.get("Payment_Status")) == "1" or desc.lower() == "approved"
    if paid:
        utr = str(row.get("Payment_Id") or row.get("IPG_ID") or "")
        updated = mark_paid(donation.id, utr=utr)
        if updated is not None:
            return updated
    if str(row.get("Payment_Status")) == "0":
        donation.status = "failed"
        donation.receipt_error = (desc or "Payment was not completed")[:500]
        bound = object_session(donation)
        if bound is not None:
            bound.commit()
    return donation


@app.get("/mswipe/return")
def mswipe_return(ref: str = "", db: Session = Depends(get_db)):
    if not ref:
        return RedirectResponse("/give.html", status_code=303)
    donation = db.get(Donation, ref)
    if donation is None:
        raise HTTPException(404, "Donation not found")
    donation = _refresh_mswipe(donation)
    if donation.status == "paid":
        return RedirectResponse(f"/success/{donation.id}", status_code=303)
    return RedirectResponse(f"/pay/{ref}", status_code=303)


@app.post("/mswipe/backpost")
async def mswipe_backpost(request: Request):
    try:
        payload = await request.json()
    except Exception:
        form = await request.form()
        payload = dict(form)
    invoice = str(payload.get("ME_InvNo") or payload.get("invoice_id") or "")
    status = str(payload.get("TRAN_STATUS") or "").lower()
    if invoice and status == "approved":
        mark_paid(invoice, utr=str(payload.get("RRN") or payload.get("IPG_ID") or ""))
    return JSONResponse({"ok": True})


@app.get("/api/donations/{donation_id}")
def donation_status(donation_id: str, db: Session = Depends(get_db)):
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise HTTPException(404)
    donation = _refresh_mswipe(donation)
    return {
        "id": donation.id,
        "status": donation.status,
        "amount": donation.amount_rupees,
        "paid_at": ist(donation.paid_at),
    }


@app.get("/success/{donation_id}", response_class=HTMLResponse)
def success_page(request: Request, donation_id: str, db: Session = Depends(get_db)):
    donation = db.get(Donation, donation_id)
    if donation is None or donation.status != "paid":
        return RedirectResponse(f"/pay/{donation_id}", status_code=303)
    return templates.TemplateResponse("success.html", {"request": request, "d": donation})


@app.get("/receipt/{donation_id}.pdf")
def download_receipt(donation_id: str, db: Session = Depends(get_db)):
    donation = db.get(Donation, donation_id)
    if donation is None or donation.status != "paid":
        raise HTTPException(404)
    path = DATA_DIR / "receipts" / f"{donation_id}.pdf"
    if not path.exists():
        from .receipts import write_receipt_pdf

        write_receipt_pdf(donation)
    return FileResponse(path, filename=f"{donation_id}.pdf", media_type="application/pdf")


@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_form(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})


@app.post("/admin/login")
def admin_login(request: Request, email: str = Form(...), password: str = Form(...)):
    ok_user = _secret_match(email.strip().lower(), ADMIN_USER)
    ok_pass = _secret_match(password, ADMIN_PASSWORD)
    if not (ok_user and ok_pass):
        return templates.TemplateResponse(
            "admin_login.html",
            {"request": request, "error": "Wrong email or password."},
            status_code=401,
        )
    request.session["admin"] = True
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request, db: Session = Depends(get_db)):
    require_admin(request)
    rows = db.scalars(select(Donation).order_by(Donation.created_at.desc())).all()
    for row in rows:
        if row.status == "pending" and row.provider == "mswipe" and row.provider_ref:
            _refresh_mswipe(row)
    rows = db.scalars(select(Donation).order_by(Donation.created_at.desc())).all()
    counts = {"paid": 0, "failed": 0, "pending": 0}
    for row in rows:
        counts[row.status] = counts.get(row.status, 0) + 1
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "rows": rows, "counts": counts},
    )


@app.post("/admin/donations/{donation_id}/confirm")
def admin_confirm(request: Request, donation_id: str, utr: str = Form(""), db: Session = Depends(get_db)):
    require_admin(request)
    if db.get(Donation, donation_id) is None:
        raise HTTPException(404)
    mark_paid(donation_id, utr=utr.strip())
    return RedirectResponse("/admin", status_code=303)


@app.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request):
    from .config import RAZORPAY_WEBHOOK_SECRET

    body = await request.body()
    if RAZORPAY_WEBHOOK_SECRET:
        import hashlib
        import hmac

        sig = request.headers.get("X-Razorpay-Signature", "")
        expect = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expect):
            raise HTTPException(400, "bad signature")
    payload = await request.json()
    notes = (
        payload.get("payload", {})
        .get("qr_code", {})
        .get("entity", {})
        .get("notes", {})
    )
    donation_id = notes.get("donation_id")
    if not donation_id:
        payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
        donation_id = (payment.get("notes") or {}).get("donation_id")
        utr = payment.get("acquirer_data", {}).get("rrn") or payment.get("id", "")
    else:
        utr = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("id", "")
    if donation_id:
        mark_paid(donation_id, utr=str(utr))
    return JSONResponse({"ok": True})
