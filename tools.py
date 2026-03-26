from langchain_core.tools import tool


@tool
def check_credit(counterparty_name: str, volume_mmbtu: float) -> dict:
    """
    Check credit risk for a deal counterparty (always the BUYER).

    Args:
        counterparty_name: Full legal name of the buyer.
        volume_mmbtu: Deal volume in MMBtu.
    """
    base = {"counterparty": counterparty_name, "volume": volume_mmbtu}

    if volume_mmbtu > 100_000:
        return {**base, "status": "rejected", "message": "exceeds single-deal limit"}
    if "Restricted" in counterparty_name:
        return {**base, "status": "rejected", "message": "counterparty on restricted list"}
    if volume_mmbtu > 60_000:
        return {**base, "status": "flagged",  "message": "requires senior approval"}

    return {**base, "status": "approved", "message": "credit check passed"}
