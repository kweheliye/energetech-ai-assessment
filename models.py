import uuid
from datetime import date
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class CreditStatus(str, Enum):
    APPROVED = "approved"
    FLAGGED  = "flagged"
    REJECTED = "rejected"


class CreditCheckResult(BaseModel):
    counterparty: str
    volume:       float
    status:       CreditStatus
    message:      str


class DealExtraction(BaseModel):
    reference:           str
    date:                date
    seller:              str
    buyer:               str
    commodity:           str
    volume_mmbtu:        float = Field(..., gt=0)
    delivery_start:      date
    delivery_end:        date
    delivery_point:      str
    price_usd_per_mmbtu: float = Field(..., gt=0)
    total_value_usd:     float
    payment_terms:       str
    governing_law:       str
    confirmed_by:        str
    validation_flags:    List[str] = Field(default_factory=list)


class DealResponse(DealExtraction):
    credit_check:     CreditCheckResult
    request_id:       str   = Field(default_factory=lambda: f"deal_{uuid.uuid4().hex[:10]}")
    duration_seconds: float = 0.0
