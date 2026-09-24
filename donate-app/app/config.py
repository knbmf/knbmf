import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "qr").mkdir(exist_ok=True)
(DATA_DIR / "receipts").mkdir(exist_ok=True)
(DATA_DIR / "outbox").mkdir(exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
ADMIN_USER = os.getenv("ADMIN_USER", "admin@knbmf.com").strip().lower()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
PAYMENT_MODE = os.getenv("PAYMENT_MODE", "demo").strip().lower()

UPI_VPA = os.getenv("UPI_VPA", "").strip()
UPI_PAYEE_NAME = os.getenv(
    "UPI_PAYEE_NAME", "Kast Nivaran Balaji Mandir Foundation"
)

BANK_NAME = "Union Bank of India"
BANK_BRANCH = "Kashipur Main, Hotel Kumaon Plaza, Bazpur Road"
BANK_ACCOUNT = "524001010060627"
BANK_IFSC = "UBIN0552402"
BANK_MICR = "244026202"
ACCOUNT_NAME = "Kast Nivaran Balaji Mandir Foundation"

FOUNDATION = {
    "name": "Kast Nivaran Balaji Mandir Foundation",
    "cin": "U88900UT2025NPL019252",
    "pan": "AALCK8805B",
    "gstin": "05AALCK8805B1ZO",
    "tan": "MRTK08845E",
    "section8": "168829",
    "urn_12a": "AALCK8805BE20251",
    "urn_80g": "AALCK8805BF20261",
    "darpan": "UK/2026/0989165",
    "address": "Heritage City, Jaspur Khurd, Kashipur, Udham Singh Nagar, Uttarakhand 244713",
    "email": "support@kashtnivaranbalajimandirfoundation.org",
}

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.hostinger.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", FOUNDATION["email"])
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv(
    "SMTP_FROM",
    f"{FOUNDATION['name']} <{FOUNDATION['email']}>",
)

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "").strip()
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "").strip()
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "").strip()

UROPAY_API_KEY = os.getenv("UROPAY_API_KEY", "").strip()
UROPAY_API_SECRET = os.getenv("UROPAY_API_SECRET", "").strip()
UROPAY_API_BASE = os.getenv("UROPAY_API_BASE", "https://api.uropai.in").strip()

# Mswipe Pay by Link. Default host is live.
MSWIPE_BASE = os.getenv("MSWIPE_BASE", "https://pbl.mswipe.com/ipg/api").rstrip("/")
MSWIPE_USER_ID = os.getenv("MSWIPE_USER_ID", "").strip()
MSWIPE_CLIENT_ID = os.getenv("MSWIPE_CLIENT_ID", "").strip()
MSWIPE_PASSWORD = os.getenv("MSWIPE_PASSWORD", "").strip()
MSWIPE_CUST_CODE = os.getenv("MSWIPE_CUST_CODE", "").strip()
MSWIPE_APP_ID = os.getenv("MSWIPE_APP_ID", "api").strip() or "api"
MSWIPE_CHANNEL_ID = os.getenv("MSWIPE_CHANNEL_ID", "pbl").strip() or "pbl"
MSWIPE_RETURN_BASE = os.getenv("MSWIPE_RETURN_BASE", "http://127.0.0.1:8787").rstrip("/")

DATABASE_URL = f"sqlite:///{DATA_DIR / 'donations.db'}"
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8787")
