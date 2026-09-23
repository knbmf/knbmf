from urllib.parse import quote

import segno

from .config import DATA_DIR, UPI_PAYEE_NAME, UPI_VPA


def build_upi_uri(amount_rupees: int, note: str, vpa=None) -> str:
    pa = (vpa or UPI_VPA).strip()
    if not pa or "@" not in pa or pa.startswith("set-upi-vpa"):
        raise ValueError("Set a real UPI ID in donate-app/.env (UPI_VPA), linked to Union Bank A/c 524001010060627.")
    # Many Indian apps reject %20 in pa/pn and .00 on whole rupees.
    pn = quote(UPI_PAYEE_NAME, safe=" ")
    am = str(int(amount_rupees))
    return f"upi://pay?pa={quote(pa, safe='@.')}&pn={pn}&am={am}&cu=INR"


def write_qr_png(donation_id: str, upi_uri: str) -> str:
    path = DATA_DIR / "qr" / f"{donation_id}.png"
    qr = segno.make(upi_uri, error="m")
    qr.save(str(path), scale=8, border=2, dark="#5a241e", light="#fffdf8")
    return str(path)
