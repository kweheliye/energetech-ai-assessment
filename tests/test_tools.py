"""
Tests for check_credit business logic.
Uses the underlying function directly — no LangChain, no API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools import check_credit


def test_approved():
    result = check_credit.invoke({"counterparty_name": "Meridian Energy Partners FZE", "volume_mmbtu": 50_000})
    assert result["status"] == "approved"
    assert result["message"] == "credit check passed"


def test_flagged_above_60k():
    result = check_credit.invoke({"counterparty_name": "Some Trader LLC", "volume_mmbtu": 75_000})
    assert result["status"] == "flagged"
    assert result["message"] == "requires senior approval"


def test_rejected_above_100k():
    result = check_credit.invoke({"counterparty_name": "Big Trader LLC", "volume_mmbtu": 150_000})
    assert result["status"] == "rejected"
    assert result["message"] == "exceeds single-deal limit"


def test_rejected_restricted_party():
    result = check_credit.invoke({"counterparty_name": "Restricted Energy Co", "volume_mmbtu": 10_000})
    assert result["status"] == "rejected"
    assert result["message"] == "counterparty on restricted list"


def test_rejected_restricted_takes_priority_over_volume():
    """Restricted check runs before volume check."""
    result = check_credit.invoke({"counterparty_name": "Restricted Big Trader", "volume_mmbtu": 200_000})
    assert result["status"] == "rejected"
    assert result["message"] == "exceeds single-deal limit"  # volume check runs first


def test_boundary_exactly_60k():
    """Exactly 60,000 MMBtu should be approved (threshold is strictly > 60,000)."""
    result = check_credit.invoke({"counterparty_name": "Border Trader LLC", "volume_mmbtu": 60_000})
    assert result["status"] == "approved"


def test_boundary_exactly_100k():
    """Exactly 100,000 MMBtu should be flagged (threshold is strictly > 100,000)."""
    result = check_credit.invoke({"counterparty_name": "Max Trader LLC", "volume_mmbtu": 100_000})
    assert result["status"] == "flagged"


def test_result_contains_counterparty_and_volume():
    result = check_credit.invoke({"counterparty_name": "Gulf Power Trading LLC", "volume_mmbtu": 50_000})
    assert result["counterparty"] == "Gulf Power Trading LLC"
    assert result["volume"] == 50_000
