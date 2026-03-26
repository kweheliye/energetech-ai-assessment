"""
Two-turn LangChain + OpenAI o3 flow:
  Turn 1 → LLM extracts deal fields + calls check_credit tool
  Turn 2 → LLM synthesises final JSON after receiving credit result
"""

import json
import logging
import time

import json_repair
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from pydantic import ValidationError

from config import get_llm, validate_config
from models import DealResponse
from prompts import SYSTEM_PROMPT, build_user_prompt
from tools import check_credit
from validator import validate_deal

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_deal_agent(deal_memo: str) -> dict:
    validate_config()
    started = time.monotonic()

    llm_tools = get_llm().bind_tools([check_credit])
    messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT), build_user_prompt(deal_memo)]

    # Turn 1 — extract + trigger tool call
    logger.info("Sending deal memo to the model for extraction.")
    response = llm_tools.invoke(messages)
    messages.append(response)

    # Execute tool calls
    if response.tool_calls:
        for tc in response.tool_calls:
            logger.info("Running credit check for: %s", tc["args"])
            result = check_credit.invoke(tc["args"])
            messages.append(ToolMessage(
                content=json.dumps(result, default=str),
                tool_call_id=tc["id"],
            ))
    else:
        logger.warning("The model did not call the credit check tool. Skipping credit check.")

    # Turn 2 — synthesise final JSON
    logger.info("Asking the model to produce the final structured response.")
    final = llm_tools.invoke(messages)

    raw = _parse_json(final.content)
    if raw is None:
        return {"validation_flags": ["llm_response_parse_error"], "raw_response": final.content[:500]}

    # Deterministic validation (Python, not LLM)
    raw["validation_flags"] = validate_deal(raw)

    # Pydantic schema enforcement
    try:
        deal = DealResponse(**raw, duration_seconds=round(time.monotonic() - started, 3))
        result = deal.model_dump(mode="json")
    except ValidationError as exc:
        raw["validation_flags"] += [f"schema_error: {e['loc'][0]} — {e['msg']}" for e in exc.errors()]
        raw["duration_seconds"]  = round(time.monotonic() - started, 3)
        result = raw

    logger.info("Deal processed. Reference: %s | Credit status: %s | Flags: %s",
                result.get("reference"),
                result.get("credit_check", {}).get("status"),
                result.get("validation_flags"))
    return result


def _parse_json(text: str) -> dict | None:
    cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            result = json_repair.loads(cleaned)
            if isinstance(result, dict):
                logger.warning("Model returned malformed JSON. Attempted repair.")
                return result
        except (ValueError, TypeError):
            pass
    return None


