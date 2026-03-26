"""
Tests for the FastAPI server.

run_deal_agent is mocked — no OpenAI API key required.
These tests verify HTTP routing, request validation, and response shape.
Memo is submitted as plain text (Content-Type: text/plain).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch

from fastapi.testclient import TestClient

from server import app

client = TestClient(app)

HEADERS = {"Content-Type": "text/plain"}

# Fixture: sample agent response

MOCK_DEAL_RESPONSE = {
    "reference":           "ET-2026-0441",
    "date":                "2026-03-18",
    "seller":              "Gulf Power Trading LLC",
    "buyer":               "Meridian Energy Partners FZE",
    "commodity":           "Natural Gas",
    "volume_mmbtu":        50000,
    "delivery_start":      "2026-04-01",
    "delivery_end":        "2026-04-30",
    "delivery_point":      "Title Transfer at Jebel Ali Hub",
    "price_usd_per_mmbtu": 8.40,
    "total_value_usd":     420000.0,
    "payment_terms":       "Net 5 business days after delivery",
    "governing_law":       "DIFC",
    "confirmed_by":        "Ahmed Al-Farsi (Gulf Power Trading LLC)",
    "validation_flags":    [],
    "credit_check": {
        "counterparty": "Meridian Energy Partners FZE",
        "volume":        50000,
        "status":        "approved",
        "message":       "credit check passed",
    },
    "request_id":       "deal_abc123",
    "duration_seconds": 3.5,
}

SAMPLE_MEMO = "DEAL CONFIRMATION\nDate: 18 March 2026\nReference: ET-2026-0441"


# Health check

def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# POST /process-deal — happy path

def test_process_deal_returns_200():
    with patch("server.run_deal_agent", return_value=MOCK_DEAL_RESPONSE):
        response = client.post("/process-deal", content=SAMPLE_MEMO, headers=HEADERS)
    assert response.status_code == 200


def test_process_deal_response_contains_required_fields():
    with patch("server.run_deal_agent", return_value=MOCK_DEAL_RESPONSE):
        data = client.post("/process-deal", content=SAMPLE_MEMO, headers=HEADERS).json()

    required = ["reference", "date", "seller", "buyer", "commodity",
                "volume_mmbtu", "delivery_start", "delivery_end",
                "price_usd_per_mmbtu", "total_value_usd", "credit_check"]
    for field in required:
        assert field in data, f"Missing field: {field}"


def test_process_deal_credit_check_present():
    with patch("server.run_deal_agent", return_value=MOCK_DEAL_RESPONSE):
        data = client.post("/process-deal", content=SAMPLE_MEMO, headers=HEADERS).json()
    assert data["credit_check"]["status"] == "approved"


def test_process_deal_passes_memo_to_agent():
    with patch("server.run_deal_agent", return_value=MOCK_DEAL_RESPONSE) as mock_agent:
        client.post("/process-deal", content=SAMPLE_MEMO, headers=HEADERS)
    mock_agent.assert_called_once_with(SAMPLE_MEMO)


# POST /process-deal — validation errors

def test_process_deal_rejects_empty_body():
    with patch("server.run_deal_agent", return_value=MOCK_DEAL_RESPONSE):
        response = client.post("/process-deal", content="", headers=HEADERS)
    assert response.status_code == 422


def test_process_deal_rejects_short_memo():
    with patch("server.run_deal_agent", return_value=MOCK_DEAL_RESPONSE):
        response = client.post("/process-deal", content="short", headers=HEADERS)
    assert response.status_code == 422


# POST /process-deal — agent parse failure

def test_process_deal_returns_422_on_parse_error():
    error_response = {"validation_flags": ["llm_response_parse_error"], "raw_response": "..."}
    with patch("server.run_deal_agent", return_value=error_response):
        response = client.post("/process-deal", content=SAMPLE_MEMO, headers=HEADERS)
    assert response.status_code == 422
