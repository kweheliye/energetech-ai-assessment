"""
Tests for deterministic deal validation.
No LLM calls — pure Python logic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validator import validate_deal


BASE_DEAL = {
    "volume_mmbtu":        50_000,
    "price_usd_per_mmbtu": 8.40,
    "total_value_usd":     420_000.0,
    "delivery_start":      "2026-04-01",
    "delivery_end":        "2026-04-30",
    "validation_flags":    [],
}


def test_valid_deal_no_flags():
    flags = validate_deal(BASE_DEAL)
    assert flags == []


def test_total_value_mismatch():
    deal = {**BASE_DEAL, "total_value_usd": 500_000.0}
    flags = validate_deal(deal)
    assert any("total_value_mismatch" in f for f in flags)


def test_total_value_correct_within_tolerance():
    """Floating point differences under 1 cent should not flag."""
    deal = {**BASE_DEAL, "total_value_usd": 420_000.004}
    flags = validate_deal(deal)
    assert flags == []


def test_delivery_end_before_start():
    deal = {**BASE_DEAL, "delivery_start": "2026-04-30", "delivery_end": "2026-04-01"}
    flags = validate_deal(deal)
    assert any("delivery_period_invalid" in f for f in flags)


def test_delivery_end_same_as_start():
    deal = {**BASE_DEAL, "delivery_start": "2026-04-01", "delivery_end": "2026-04-01"}
    flags = validate_deal(deal)
    assert any("delivery_period_invalid" in f for f in flags)


def test_preserves_existing_llm_flags():
    deal = {**BASE_DEAL, "validation_flags": ["missing_field: governing_law"]}
    flags = validate_deal(deal)
    assert "missing_field: governing_law" in flags


def test_deduplicates_flags():
    deal = {**BASE_DEAL, "validation_flags": ["missing_field: x", "missing_field: x"]}
    flags = validate_deal(deal)
    assert flags.count("missing_field: x") == 1


def test_missing_fields_dont_crash():
    """Validator should handle missing keys gracefully."""
    flags = validate_deal({})
    assert isinstance(flags, list)
