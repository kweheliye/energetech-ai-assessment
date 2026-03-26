from langchain_core.messages import HumanMessage

SYSTEM_PROMPT = """\
You are a deal processing agent for an energy trading firm.

1. Extract all structured fields from the deal memo.
2. Flag anomalies: missing fields, inconsistent values, bad dates.
3. Call check_credit with the BUYER as counterparty and the deal volume in MMBtu.
4. After the credit check, output ONLY a valid JSON object — no markdown, no explanation.

Rules:
- Dates must be YYYY-MM-DD
- volume_mmbtu and price_usd_per_mmbtu must be numbers
- total_value_usd: use the value from the memo as-is
- validation_flags: [] if no issues
- Missing field → use null and add "missing_field: <name>" to validation_flags
"""

OUTPUT_SCHEMA = """\
{
  "reference": "string",
  "date": "YYYY-MM-DD",
  "seller": "string",
  "buyer": "string",
  "commodity": "string",
  "volume_mmbtu": number,
  "delivery_start": "YYYY-MM-DD",
  "delivery_end": "YYYY-MM-DD",
  "delivery_point": "string",
  "price_usd_per_mmbtu": number,
  "total_value_usd": number,
  "payment_terms": "string",
  "governing_law": "string",
  "confirmed_by": "string",
  "validation_flags": ["string"],
  "credit_check": {
    "counterparty": "string",
    "volume": number,
    "status": "approved | flagged | rejected",
    "message": "string"
  }
}"""


def build_user_prompt(deal_memo: str) -> HumanMessage:
    return HumanMessage(content=(
        f"Process this deal memo, call check_credit with the buyer and volume, "
        f"then return the final JSON matching this schema:\n\n{OUTPUT_SCHEMA}"
        f"\n\nDEAL MEMO:\n{deal_memo}"
    ))
