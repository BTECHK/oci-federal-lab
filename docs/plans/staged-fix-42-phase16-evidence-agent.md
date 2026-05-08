# Fix #42 — Phase 16 Retrofit: Add the Compliance Evidence Agent

**Status:** Planning only — not executed. Phase 1 is currently scope-frozen (see commit `a75fe02`, 2026-05-08), so the apply step requires explicit unfreeze approval before editing the implementation guide.

**Source spec:**
- `RETROFIT-TODO.md` item #6
- Master design `../../Project ideas/2026-03-18-interview-lab-project-design.md`, lines 266–286

**One-line goal:** Add a *second* AI block to Day 4 / Phase 16 that demonstrates **agentic AI** (ReAct loop + tool calling), distinct from the existing **linear collector** at Step 16.3 — which stays AS-IS.

**Why two blocks instead of replacing the first:** the linear collector is the right pattern for *scheduled* evidence collection (deterministic, scoreable, repeatable). The agent is the right pattern for *ad-hoc auditor questions* (dynamic, exploratory, citation-bearing). Showing both gives a stronger interview story than picking one.

---

## Where the new content lands

| Location | Change |
|---|---|
| Line ~6797 (Step 16 intro / Day 4 framing) | Add one paragraph: "Phase 16 builds two AI workloads — a linear collector (16.1–16.5) and an agentic evidence-investigation loop (16.6). Linear for scheduled FedRAMP reports; agentic for ad-hoc auditor questions." |
| Step 16.5 (line 7363) | No change — air-gap proof still applies to the linear collector. |
| **NEW Step 16.6 — Build the Compliance Evidence Agent** | Inserted between Step 16.5 (line 7393) and "Phase 16 Troubleshooting" (line 7395). Full new section, ~250 lines including code block. |
| Phase 16 Troubleshooting (line 7397) | Add 2 new rows: "Agent loops past iteration cap" → check `MAX_ITERATIONS`; "Agent hangs on tool call" → tool returned non-JSON, check the tool's stdout. |
| Day 4 Recap (line 7411) | Add bullet: "Built a ReAct compliance agent (~150 LOC) with 7 read-only tools, JSONL trace, citation-bearing finish handler." |

---

## New artifact

`/opt/fedtracker/compliance/compliance_agent.py` — ~150 LOC, Python.

**Companion files:**
- `/opt/fedtracker/compliance/agent-traces/` — directory the agent creates on first run; one JSONL file per invocation.
- No separate tool-registry file. The 7 tools live inside `compliance_agent.py` as a `TOOL_REGISTRY` dict.

---

## Architecture (ReAct loop)

```
                  ┌──────────────────────────────────────┐
                  │  user_question (CLI arg)             │
                  └────────────────┬─────────────────────┘
                                   ↓
                  ┌──────────────────────────────────────┐
                  │  Build system prompt + tool schema   │
                  │  (JSON tools spec, citation rules)   │
                  └────────────────┬─────────────────────┘
                                   ↓
        ┌──────────────────────────┴──────────────────────────┐
        │   Iteration k (k < MAX_ITERATIONS, tokens < BUDGET) │
        │                                                       │
        │   POST /api/chat to Ollama with conversation         │
        │     ↓                                                 │
        │   Parse tool_call from response                      │
        │     ↓                                                 │
        │   if tool == "finish":                                │
        │       require citations[] non-empty → exit            │
        │   else:                                               │
        │       call TOOL_REGISTRY[tool](args)                 │
        │       append observation to conversation              │
        │       append JSONL line to trace                      │
        └──────────────────────────────────────────────────────┘
```

**Model choice:** `tinyllama` cannot reliably emit structured JSON tool calls. Plan upgrades to `qwen2.5:1.5b` or `llama3.2:1b` (~1 GB additional pull, both fit on the 8 GB ARM A1.Flex VM). **Open question for user — confirm before apply.**

---

## The 7 tools

| Tool | Implementation | Read-only proof |
|---|---|---|
| `query_fedtracker_audit_db(sql)` | `sqlite3.connect("/app/fedtracker.db")` — connection opened with `uri=True` and `?mode=ro`. Reject any SQL not starting with `SELECT` (regex). | DB opened in RO mode at OS level. |
| `list_oci_iam_policies()` | Subprocess: `oci iam policy list --compartment-id <fedtracker-lab OCID> --all` | OCI CLI configured with read-only auth profile `compliance-agent`. |
| `get_oci_security_lists()` | Subprocess: `oci network security-list list --compartment-id <id> --all` | Same RO profile. |
| `get_cis_scan_results()` | Read latest `/opt/fedtracker/compliance/reports/stig-*.xml`, parse `<rule-result>` counts | Pure file read. |
| `list_evidence_artifacts()` | `os.listdir("/opt/fedtracker/compliance/reports/")` | Pure file read. |
| `read_evidence_artifact(name)` | `open(os.path.join("/opt/fedtracker/compliance/reports/", basename(name))).read()` — `os.path.basename` is the path-traversal guard | Pure file read, scoped dir. |
| `finish(verdict, citations)` | Returns `{verdict: str, citations: [{tool, args, iter}]}`; raises if `len(citations) == 0` | Terminal — no side effects. |

---

## Guardrails (non-negotiable per spec)

1. **Read-only** — every tool above is bounded to file reads or read-only subprocess calls. No tool writes, no tool emits HTTP egress beyond `localhost:11434`.
2. **Iteration cap** — `MAX_ITERATIONS = 8`. The 9th call refuses with `"Aborted: agent exceeded iteration cap. Partial trace at <path>."`
3. **Token budget** — accumulate `prompt_eval_count + eval_count` from each Ollama response; abort at `TOKEN_BUDGET = 8000` cumulative.
4. **Mandatory citations** — `finish` tool's docstring + JSON schema require non-empty `citations`. The system prompt explicitly states: *"A verdict without citations is invalid. Each claim in your verdict must be traceable to one tool observation."*
5. **JSONL trace** — every iteration appends one line to `/opt/fedtracker/compliance/agent-traces/agent-<ISO-timestamp>.jsonl`. Schema: `{iter, role, tool_call: {name, args}, observation_excerpt, tokens_this_turn, tokens_cumulative}`. Used for auditor replay.

---

## Code skeleton (≈150 LOC target)

```python
#!/usr/bin/env python3
"""
Compliance Evidence Agent — agentic AI for ad-hoc auditor questions.

Companion to fedramp_agent.py:
- fedramp_agent.py = scheduled, deterministic FedRAMP scoring
- compliance_agent.py = ad-hoc, exploratory ReAct investigation

Usage: compliance_agent.py --question "..."
"""
import argparse, json, os, re, sqlite3, subprocess, sys, time
from datetime import datetime, timezone
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = os.environ.get("AGENT_MODEL", "qwen2.5:1.5b")
MAX_ITERATIONS = 8
TOKEN_BUDGET = 8000
REPORTS_DIR = "/opt/fedtracker/compliance/reports/"
TRACE_DIR = "/opt/fedtracker/compliance/agent-traces/"
DB_PATH = "/app/fedtracker.db"
COMPARTMENT_OCID = os.environ["FEDTRACKER_COMPARTMENT_OCID"]

# --- Tool implementations (each returns str observation) ---

def query_fedtracker_audit_db(sql: str) -> str:
    if not re.match(r"^\s*SELECT\b", sql, re.IGNORECASE):
        return "ERROR: only SELECT queries permitted"
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    rows = conn.execute(sql).fetchmany(50)
    conn.close()
    return json.dumps([dict(r) for r in rows], default=str)

def list_oci_iam_policies() -> str:
    r = subprocess.run(["oci", "iam", "policy", "list",
                        "--compartment-id", COMPARTMENT_OCID, "--all"],
                       capture_output=True, text=True, timeout=30)
    return r.stdout[:2000]  # truncate to fit context

# ... 4 more tools follow same pattern ...

def finish(verdict: str, citations: list) -> str:
    if not citations:
        return "ERROR: finish requires non-empty citations[]"
    return json.dumps({"verdict": verdict, "citations": citations})

TOOL_REGISTRY = {
    "query_fedtracker_audit_db": query_fedtracker_audit_db,
    "list_oci_iam_policies": list_oci_iam_policies,
    "get_oci_security_lists": ...,
    "get_cis_scan_results": ...,
    "list_evidence_artifacts": ...,
    "read_evidence_artifact": ...,
    "finish": finish,
}

TOOL_SCHEMA = [
    {"type": "function", "function": {
        "name": "query_fedtracker_audit_db",
        "description": "Run a read-only SELECT against fedtracker.db audit_log table.",
        "parameters": {"type": "object",
                       "properties": {"sql": {"type": "string"}},
                       "required": ["sql"]}}},
    # ... 6 more ...
]

SYSTEM_PROMPT = """You are a FedRAMP compliance auditor's investigator.
You answer the user's question by calling tools and citing evidence.
RULES:
- Use only the provided tools. No fabrication.
- Every claim in your final verdict MUST cite a tool call.
- Call `finish(verdict, citations)` to end. citations must be non-empty.
- You have at most 8 iterations and 8000 tokens."""

def run_agent(question: str) -> dict:
    os.makedirs(TRACE_DIR, exist_ok=True)
    trace_path = os.path.join(TRACE_DIR, f"agent-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonl")
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}]
    tokens_used = 0
    for k in range(MAX_ITERATIONS):
        if tokens_used >= TOKEN_BUDGET:
            return {"error": "token budget exceeded", "trace": trace_path}
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL, "messages": messages, "tools": TOOL_SCHEMA,
            "stream": False
        }, timeout=180).json()
        msg = resp["message"]
        tokens_used += resp.get("eval_count", 0) + resp.get("prompt_eval_count", 0)
        tool_calls = msg.get("tool_calls", [])
        if not tool_calls:
            messages.append(msg)
            continue
        for tc in tool_calls:
            name, args = tc["function"]["name"], tc["function"]["arguments"]
            obs = TOOL_REGISTRY[name](**args) if name != "finish" \
                  else TOOL_REGISTRY[name](args["verdict"], args["citations"])
            with open(trace_path, "a") as f:
                f.write(json.dumps({
                    "iter": k, "tool": name, "args": args,
                    "observation_excerpt": obs[:300],
                    "tokens_cumulative": tokens_used
                }) + "\n")
            if name == "finish":
                return json.loads(obs) if obs.startswith("{") else {"error": obs}
            messages.append(msg)
            messages.append({"role": "tool", "name": name, "content": obs})
    return {"error": "iteration cap hit", "trace": trace_path}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--question", required=True)
    args = p.parse_args()
    print(json.dumps(run_agent(args.question), indent=2))
```

(Above is illustrative — actual file fills in the four `...` tools to hit the ~150 LOC target.)

---

## Verify section (the part to copy into the guide)

```bash
# Pull the upgraded model (one-time, ~1 GB)
ollama pull qwen2.5:1.5b

# Set the compartment OCID env var (instance metadata or .bashrc)
export FEDTRACKER_COMPARTMENT_OCID="ocid1.compartment.oc1..xxxxx"

# Run with a sample auditor question
python3 /opt/fedtracker/compliance/compliance_agent.py \
  --question "Which CIS findings overlap with the top 5 EXPORT events from the audit log this week?"

# Inspect the trace
ls -la /opt/fedtracker/compliance/agent-traces/
cat /opt/fedtracker/compliance/agent-traces/*.jsonl | jq .
```

**Expected:** A JSON verdict with `citations[]` populated, and a JSONL trace showing tool calls in order.

---

## Interview framing block (copy into Step 16.6)

> **💼 Interview Insight — Linear vs Agentic AI:** "I built two AI workloads in the same phase to show I understand when each pattern fits. The linear collector runs every night and produces a deterministic FedRAMP score against a fixed checklist — that's the right shape for compliance reporting. The agent answers free-form auditor questions like 'show me the controls that failed and have related EXPORT events in the audit log' — that's the right shape for compliance investigation. Same data sources, same Ollama localhost, but one is scheduled-and-scoreable and the other is dynamic-and-citation-bearing. The agent has hard guardrails because federal auditors care more about traceability than cleverness: 8-iteration cap, 8000-token budget, read-only tools, JSONL trace for replay, and a finish handler that rejects any verdict without citations."

---

## Acceptance criteria

- [ ] Step 16 intro names both AI blocks and the scheduled-vs-ad-hoc framing.
- [ ] Step 16.6 inserted as its own H3 between 16.5 and Phase 16 Troubleshooting.
- [ ] `compliance_agent.py` is a complete, runnable file (no `...` placeholders) — all 7 tools implemented.
- [ ] Verify section runs end-to-end against tinyllama-substitute model on the existing app-server VM.
- [ ] JSONL trace file is auditor-readable (one event per line, parseable with `jq .`).
- [ ] Phase 16 Troubleshooting table gains the 2 new rows.
- [ ] Day 4 Recap mentions the new build.
- [ ] No edits to Step 16.3 (linear collector stays AS-IS).

---

## Open questions before apply

1. **Phase 1 scope freeze** — apply requires unfreezing Phase 1, OR moving this block to a Phase 2/3 callback ("Phase 1 built linear; here's the agentic equivalent"). Which?
2. **Model bump** — confirm OK to pull `qwen2.5:1.5b` (~1 GB) on top of tinyllama. tinyllama can't do tool calls reliably.
3. **OCI CLI auth profile for the agent** — should the agent use the same OCI CLI config the user already has, or a dedicated read-only profile? Dedicated profile is cleaner but adds setup steps.
