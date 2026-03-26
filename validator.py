"""
Deterministic validation — Python checks math and logic.
The LLM extracts values; we verify them independently.
"""

import logging
from datetime import date

logger = logging.getLogger(__name__)


def validate_deal(data: dict) -> list[str]:
    flags = list(data.get("validation_flags") or [])

    # Math: total must equal volume × price
    try:
        expected = round(float(data["volume_mmbtu"]) * float(data["price_usd_per_mmbtu"]), 2)
        actual   = round(float(data["total_value_usd"]), 2)
        if abs(actual - expected) > 0.01:
            flags.append(f"total_value_mismatch: memo={actual}, calculated={expected}")
            logger.warning("Total value mismatch detected. Memo says %s but volume x price gives %s.", actual, expected)
    except (KeyError, TypeError, ValueError):
        pass

    # Dates: delivery end must be after start
    try:
        start = date.fromisoformat(str(data["delivery_start"]))
        end   = date.fromisoformat(str(data["delivery_end"]))
        if end <= start:
            flags.append("delivery_period_invalid: end is not after start")
    except (KeyError, ValueError, TypeError):
        pass

    return list(dict.fromkeys(flags))  # deduplicate, preserve order
