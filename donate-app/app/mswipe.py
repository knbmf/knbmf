"""Mswipe Pay by Link. Live host by default.

Token and link calls follow docs.mswipe.com Getting Started:
  POST {base}/CreatePBLAuthToken
  POST {base}/MswipePayment
  POST {base}/getPBLTransactionDetails
"""

import logging
import time
import uuid
from urllib.parse import parse_qs, urlparse

import httpx

from .config import (
    MSWIPE_APP_ID,
    MSWIPE_BASE,
    MSWIPE_CHANNEL_ID,
    MSWIPE_CLIENT_ID,
    MSWIPE_CUST_CODE,
    MSWIPE_PASSWORD,
    MSWIPE_RETURN_BASE,
    MSWIPE_USER_ID,
)

log = logging.getLogger("donations.mswipe")

_token = ""
_token_until = 0.0


class MswipeError(Exception):
    pass


def configured() -> bool:
    return bool(MSWIPE_CLIENT_ID and MSWIPE_PASSWORD and MSWIPE_CUST_CODE)


def _post(path: str, body: dict) -> dict:
    url = f"{MSWIPE_BASE}/{path.lstrip('/')}"
    try:
        response = httpx.post(url, json=body, timeout=30)
    except httpx.HTTPError as exc:
        raise MswipeError(f"Mswipe did not respond ({exc.__class__.__name__}).") from exc
    try:
        data = response.json()
    except ValueError as exc:
        raise MswipeError(f"Mswipe returned a non-JSON response ({response.status_code}).") from exc
    if not isinstance(data, dict):
        raise MswipeError("Mswipe returned an unexpected response.")
    return data


def _auth_token() -> str:
    global _token, _token_until
    now = time.time()
    if _token and now < _token_until:
        return _token
    body = {
        "clientId": MSWIPE_CLIENT_ID,
        "password": MSWIPE_PASSWORD,
        "applId": MSWIPE_APP_ID,
        "channelId": MSWIPE_CHANNEL_ID,
    }
    if MSWIPE_USER_ID:
        body["userId"] = MSWIPE_USER_ID
    data = _post("CreatePBLAuthToken", body)
    if str(data.get("status")).lower() != "true" or not data.get("token"):
        message = str(data.get("msg") or data.get("responsemessage") or "token request failed")
        raise MswipeError(f"Mswipe login failed: {message}")
    _token = str(data["token"])
    _token_until = now + 20 * 60
    return _token


def create_payment_link(*, donation_id: str, amount_rupees: int, email: str, phone: str, name: str) -> dict:
    if not configured():
        raise MswipeError("Mswipe live keys are not set.")
    global _token, _token_until
    _token = ""
    _token_until = 0.0
    token = _auth_token()
    user_id = MSWIPE_USER_ID or MSWIPE_CUST_CODE
    body = {
        "amount": str(int(amount_rupees)),
        "mobileno": phone,
        "custcode": MSWIPE_CUST_CODE,
        "user_id": user_id,
        "sessiontoken": token,
        "versionno": "VER4.0.0",
        "imeino": "",
        "email_id": email,
        "invoice_id": donation_id,
        "request_id": uuid.uuid4().hex,
        "device_id": "",
        "addlnote1": name[:40],
        "addlnote2": "",
        "addlnote3": "",
        "addlnote4": "",
        "addlnote5": "",
        "addlnote6": "",
        "addlnote7": "",
        "addlnote8": "",
        "addlnote9": "",
        "addlnote10": "",
        "LinkValidity": "",
        "paymentreason": "Donation",
        "redirect_url": f"{MSWIPE_RETURN_BASE}/mswipe/return?ref={donation_id}",
        "IsSendSMS": False,
        "ConvAllow": "false",
        "ApplicationId": MSWIPE_APP_ID,
        "ChannelId": MSWIPE_CHANNEL_ID,
        "ClientId": MSWIPE_CLIENT_ID,
    }
    data = _post("MswipePayment", body)
    link = str(data.get("smslink") or "")
    ok = str(data.get("status")).lower() == "true" and link.startswith("http")
    if not ok:
        message = str(data.get("responsemessage") or data.get("msg") or "could not create payment link")
        if "token" in message.lower() or "authorized" in message.lower():
            _token = ""
            _token_until = 0.0
        raise MswipeError(f"Mswipe link failed: {message}")
    trans_id = (parse_qs(urlparse(link).query).get("TransID") or [""])[0]
    log.info("mswipe link created invoice=%s txn=%s", donation_id, data.get("txn_id"))
    return {"url": link, "trans_id": trans_id, "txn_id": str(data.get("txn_id") or "")}


def transaction_status(trans_id: str) -> dict:
    if not trans_id:
        return {}
    data = _post(
        "getPBLTransactionDetails",
        {"id": trans_id, "Latitude": "", "Longitude": "", "IP_Address": "", "User_Agent": "KNBMF"},
    )
    rows = data.get("Data") or []
    if not rows or not isinstance(rows, list):
        return {}
    row = rows[0] if isinstance(rows[0], dict) else {}
    return row
