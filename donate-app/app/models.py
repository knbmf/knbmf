from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import mapped_column

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Donation(Base):
    __tablename__ = "donations"

    id = mapped_column(String(32), primary_key=True)
    name = mapped_column(String(120), nullable=False)
    phone = mapped_column(String(15), nullable=False)
    email = mapped_column(String(180), nullable=False)
    amount_rupees = mapped_column(Integer, nullable=False)
    note = mapped_column(String(24), default="", index=True, nullable=False)
    status = mapped_column(String(20), default="pending", index=True, nullable=False)
    upi_uri = mapped_column(Text, default="")
    provider = mapped_column(String(40), default="upi")
    provider_ref = mapped_column(String(80), default="")
    utr = mapped_column(String(64), default="")
    created_at = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    paid_at = mapped_column(DateTime(timezone=True), nullable=True)
    receipt_sent_at = mapped_column(DateTime(timezone=True), nullable=True)
    receipt_error = mapped_column(Text, default="")


class Seq(Base):
    __tablename__ = "seq"

    name = mapped_column(String(20), primary_key=True)
    n = mapped_column(Integer, default=0, nullable=False)
