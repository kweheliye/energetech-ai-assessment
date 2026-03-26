import logging
import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "o3")
MAX_TOKENS     = int(os.getenv("MAX_TOKENS", "4096"))


def validate_config() -> None:
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is not set. Copy .env.example to .env.")
        sys.exit(1)
    logger.info("Configuration validated. Using model: %s", OPENAI_MODEL)


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=OPENAI_MODEL, api_key=SecretStr(OPENAI_API_KEY), max_tokens=MAX_TOKENS)
