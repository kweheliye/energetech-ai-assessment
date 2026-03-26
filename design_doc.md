# Real-Time Credit Risk Flagging — Design Document

**Prepared for:** CEO & Engineering
**Scope:** 4-week delivery
**Author:** Kamal Weheliye

---

## What We're Building

The current system extracts deal data from incoming confirmations and writes it to the database. We're adding a **pre-confirmation credit risk layer** that evaluates each deal before it's written, and alerts the commercial team if a counterparty looks risky.

**New components:**

| Component | What it does |
|---|---|
| `CreditLimitStore` | Maintains a table of counterparty credit limits and cumulative exposure (new DB table) |
| `RiskEvaluator` | Pure Python service: given a deal, checks remaining headroom and recent flags for the counterparty |
| `Pre-Confirmation Hook` | Thin middleware inserted before the existing DB write — calls Extractor → RiskEvaluator → returns result |
| `Alert Dispatcher` | Sends a Slack/email notification to the commercial team when a deal is flagged or rejected |

The existing deal extractor (Part 1) is reused as-is. No changes to the current extraction or DB schema in week one.

---

## What We Build First (Week 1 MVP)

**Goal:** Get a real flag in front of a trader before end of week.

1. `RiskEvaluator` with **hardcoded limits in a config file** — no new DB table yet. This delivers value immediately with zero infrastructure risk.
2. Pre-confirmation hook wired into the **existing submission endpoint only** (traders use one primary path).
3. **Slack alert** when a deal is flagged — one message, counterparty name, volume, reason.
4. Test harness: five representative memos (approved, flagged, rejected × 2, restricted party).

Deferred to weeks 2–4: live limit tracking from the DB, senior-approval workflow, audit log, UI dashboard, external sanctions/bureau API.

---

## Key Risks

**Technical**
- The LLM extraction adds ~1–2 seconds to the deal submission path. If traders expect instant confirmation, we must move to **async flagging** (optimistic write, post-hoc risk annotation) — synchronous blocking is not viable at low latency.
- LLM hallucination on poorly formatted memos can produce wrong counterparty names, leading to missed or false risk flags. Mitigation: Pydantic validation + confidence threshold before any block decision.

**Operational**
- Traders will find alternate entry paths if the primary one blocks deals. The hook must cover **all** submission routes, not just the UI.
- Hardcoded limits will go stale within days unless there's a clear owner. This is the biggest operational risk.

---

## One Thing to Clarify Before Starting

**Who owns and updates counterparty credit limits?**

Without a trusted, maintained data source, the system can enforce static thresholds but cannot track real exposure across multiple deals. The Week 1 MVP uses hardcoded limits — but we need to agree on ownership before Week 2 or the system becomes misleading rather than protective.
