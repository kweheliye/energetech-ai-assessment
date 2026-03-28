# Energetech — Deal Processing Agent

LangChain + OpenAI `o3` agent that extracts structured data from energy deal confirmation memos, validates the output, and runs a counterparty credit check via tool use.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your OPENAI_API_KEY
```

## Start the Server

```bash
python server.py
```

Server runs at `http://localhost:8000`.

## API Usage

### Health check

```bash
curl http://localhost:8000/health
```

### Submit a deal memo

Send the memo as plain text in the request body:

```bash
curl -X POST http://localhost:8000/process-deal \
  -H "Content-Type: text/plain" \
  --data "DEAL CONFIRMATION

Date: 18 March 2026
Reference: ET-2026-0441

Seller: Gulf Power Trading LLC
Buyer: Meridian Energy Partners FZE

Commodity: Natural Gas
Volume: 50,000 MMBtu
Delivery Period: 1 April 2026 – 30 April 2026
Delivery Point: Title Transfer at Jebel Ali Hub
Price: USD 8.40 per MMBtu
Payment Terms: Net 5 business days after delivery
Governing Law: DIFC

Confirmed by: Ahmed Al-Farsi (Gulf Power Trading LLC)"
```

Or from a file:

```bash
curl -X POST http://localhost:8000/process-deal \
  -H "Content-Type: text/plain" \
  --data-binary @memo.txt
```

### Postman / Curl 

- Method: `POST`
- URL: `http://localhost:8000/process-deal`
- Headers: `Content-Type: text/plain`
- Body: select **raw** → **Text**, paste the memo directly

## How It Works

Two-turn `o3` conversation via LangChain:
1. **Turn 1** — LLM extracts all 14 deal fields and calls `check_credit` as a tool
2. **Tool execution** — `check_credit()` runs locally (mock rules)
3. **Turn 2** — LLM synthesises final JSON with credit result embedded
4. **Validation** — Python checks math (`total = volume × price`) and date logic
5. **Schema enforcement** — Pydantic parses and validates the final output

## Run Tests (no API key needed)

```bash
pytest tests/ -v
```

## Files

| File | Purpose |
|---|---|
| `server.py` | FastAPI entry point |
| `agent.py` | LLM orchestration (two-turn loop) |
| `config.py` | Env validation + LLM factory |
| `models.py` | Pydantic models and enums |
| `tools.py` | `check_credit` mock + LangChain `@tool` |
| `prompts.py` | System + user prompts |
| `validator.py` | Deterministic post-extraction checks |

## What I'd Improve With More Time

- Async streaming to reduce perceived latency
- Multi-memo batch mode
- Retry with exponential backoff on API errors
- Expanded test suite covering edge-case memos (missing fields, ambiguous dates, non-USD pricing)
- Persist results to a database for audit trail and reporting
- LangSmith tracing for chain observability and token usage
