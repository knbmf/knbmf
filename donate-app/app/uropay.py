"""UroPay Merchant API (api.uropai.in) — HMAC-SHA256 signed orders."""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from typing import Any

import httpx

from .config import (
    BASE_URL,
    UROPAY_API_BASE,
    UROPAY_API_KEY,
    UROPAY_API_SECRET,
)


class UroPayError(RuntimeError):
    pass


def configured() -> bool:
    return bool(UROPAY_API_KEY and UROPAY_API_SECRET)


def _sign(method: str, path: str, query: str, body: str) -> dict[str, str]:
    timestamp = str(int(time.time()))
    nonce = str(uuid.uuid4())
    canonical = "\n".join([method, path, timestamp, nonce, query, body])
    signature = hmac.new(
        UROPAY_API_SECRET.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        "X-Api-Key": UROPAY_API_KEY,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": signature,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def verify_webhook(headers: dict[str, str], raw_body: str) -> bool:
    ts = headers.get("x-timestamp") or headers.get("X-Timestamp") or ""
    nonce = headers.get("x-nonce") or headers.get("X-Nonce") or ""
    sig = headers.get("x-signature") or headers.get("X-Signature") or ""
    if not (ts and nonce and sig and UROPAY_API_SECRET):
        return False
    canonical = "\n".join(["POST", "/tenant-webhook", ts, nonce, "", raw_body])
    expected = hmac.new(
        UROPAY_API_SECRET.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if len(expected) != len(sig):
        return False
    return hmac.compare_digest(expected, sig)


def create_order(
    *,
    tenant_ref: str,
    amount_rupees: int,
    email: str,
    phone: str,
    name: str,
) -> dict[str, Any]:
    if not configured():
        raise UroPayError(
            "UroPay keys are missing. Set UROPAY_API_KEY and UROPAY_API_SECRET "
            "from https://dashboard.uropai.in"
        )
    path = "/v1/orders"
    payload = {
        "tenantOrderRef": tenant_ref,
        "amount": int(amount_rupees),
        "currency": "INR",
        "paymentMethods": ["upi"],
        "customerEmail": email,
        "customerPhone": phone,
        "metaData": {
            "donor": name[:100],
            "source": "website",
        },
    }
    origin = (BASE_URL or "").rstrip("/")
    if origin.startswith("https://"):
        payload["returnUrl"] = f"{origin}/uropay/return?ref={tenant_ref}"
        payload["webhookUrl"] = f"{origin}/api/uropay/webhook"
    body = json.dumps(payload, separators=(",", ":"))
    headers = _sign("POST", path, "", body)
    with httpx.Client(timeout=25) as client:
        res = client.post(UROPAY_API_BASE.rstrip("/") + path, headers=headers, content=body)
    try:
        data = res.json()
    except Exception as exc:  # noqa: BLE001
        raise UroPayError(f"UroPay returned non-JSON ({res.status_code})") from exc
    if res.status_code not in (200, 201) or data.get("status") == "error":
        raise UroPayError(data.get("message") or f"UroPay error {res.status_code}")
    order = data.get("data") or {}
    if not order.get("openUrl"):
        raise UroPayError("UroPay did not return a checkout URL.")
    return order


def get_order(order_id: str) -> dict[str, Any]:
    if not configured():
        raise UroPayError("UroPay keys are missing.")
    path = f"/v1/orders/{order_id}"
    headers = _sign("GET", path, "", "")
    headers.pop("Content-Type", None)
    with httpx.Client(timeout=20) as client:
        res = client.get(UROPAY_API_BASE.rstrip("/") + path, headers=headers)
    data = res.json()
    if res.status_code != 200 or data.get("status") == "error":
        raise UroPayError(data.get("message") or f"UroPay lookup failed {res.status_code}")
    return data.get("data") or {}
