"""
server.py — FastAPI wrapper around the deal processing agent.

Endpoints:
  POST /process-deal   — submit a deal memo, get structured JSON back
  GET  /health         — liveness check
"""

import logging

from fastapi import FastAPI, HTTPException, Request

from agent import run_deal_agent

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Energetech Deal Processing Agent",
    description="Extracts structured data from deal confirmation memos and runs a credit check.",
    version="1.0.0",
)


# Endpoints

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process-deal")
async def process_deal(request: Request):
    """
    Submit a deal confirmation memo as plain text.

    Content-Type: text/plain
    Body: raw deal memo text
    """
    memo = (await request.body()).decode("utf-8").strip()

    if len(memo) < 10:
        raise HTTPException(status_code=422, detail="Memo is too short.")

    logger.info("Received deal memo (%d chars)", len(memo))

    result = run_deal_agent(memo)

    if "llm_response_parse_error" in result.get("validation_flags", []):
        raise HTTPException(status_code=422, detail="Agent could not parse a valid response from the LLM.")

    return result


# Entry Point

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
