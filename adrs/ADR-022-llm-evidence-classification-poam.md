# ADR-022: LLM Evidence Classification + POA&M Drafting (GRC Automation)

**Status:** Proposed (P3 introduces; user implements + finalizes)
**Date:** 2026-05-25
**Context phase:** Phase 3 — AI-augmented operations / GRC automation

---

## Context

Two manual, curator-heavy GRC steps exist today: (1) `evidence-collector` maps scan findings to controls with a hard-coded stub ("every High finding maps to every control") — noise an auditor won't trust; (2) turning a finding into a POA&M (Plan of Action & Milestones) is fully manual. v3 automates both with the **local Ollama** so the air-gap holds. This is the GRC-automation theme: turn curator toil into policy-driven, AI-assisted pipelines, offline.

## Decision

- **Classification** (`evidence-collector` Section 6): an Ollama classifier assigns each finding the most relevant NIST 800-53 / CMMC control_id(s) + a confidence score + rationale, with the static table as a low-confidence fallback (threshold via `CLASSIFY_MIN_CONFIDENCE`).
- **POA&M drafting** (new `poam-generator` function): drafts the standard POA&M fields from a HIGH finding + its classified control, writes a **draft** to `compliance-artifacts/poam-drafts/` (and optionally `poam_items` as `status='draft'`).
- Both run on local Ollama; drafts require human sign-off before they're "open".

## Alternatives Considered

| Option | Pro | Con | Verdict |
|---|---|---|---|
| **Ollama classifier + POA&M drafter** | Specific, defensible mappings; auto-drafted POA&Ms cut toil; air-gapped | LLM can misclassify; drafts need review | **Selected** |
| Keep the static finding→control table | Deterministic, zero model | "Every High → every control" is noise; not credible to an auditor | Rejected |
| Managed OCI Generative AI for classification | Scalable, less code | Not air-gapped — breaks the core constraint | Rejected; documented as cloud alternative |
| Manual classification + manual POA&M authoring | No model risk | The exact curator toil this is meant to remove | Rejected |

## Consequences

**Positive:**
- Findings get specific control mappings with a confidence signal, not a blanket map.
- POA&M drafts accelerate remediation paperwork; the human reviews/signs rather than authors from scratch.
- Air-gapped GRC automation — runs offline on the existing Ollama.

**Negative:**
- LLM classification can be wrong; mitigate with a confidence threshold + the static fallback + human review of low-confidence mappings.
- POA&M output is a **draft**: a sign-off gate (`status: draft → open`) is mandatory before it's treated as a real plan.
- `poam_items` table DDL is the user's to write (DB track); the function assumes it exists.

## Implementation Notes

- `evidence-collector/func.py` Section 6 — Ollama classifier; STRICT-JSON output; static fallback under threshold.
- `functions/python/poam-generator/` — new function (func.py + func.yaml + requirements + README); writes drafts to Object Storage; optional `poam_items` insert.
- `poam_items` table — user-written DDL (status, control_id, weakness, scheduled_completion, milestones, resources, created_at).
- Reuse the log-summarizer Ollama call pattern; `OLLAMA_URL` via env.

## Quiz (5 questions)

1. Why is an LLM classifier more defensible to an auditor than the static "every High → every control" table? What's the risk it introduces, and how do you bound it?
2. What do you do with a low-confidence classification — accept, fall back, or escalate? Where does the threshold live?
3. Why must a generated POA&M be a *draft* with a sign-off gate? What goes wrong if a draft is auto-promoted to "open"?
4. Both features run on local Ollama. What's the air-gap proof, and what would change if you used managed OCI GenAI instead?
5. How would you *evaluate* the classifier's accuracy over time (think LLM-as-judge / a labeled finding→control set)?

## Key Takeaways (interview prep)

1. **Decision:** Air-gapped GRC automation — an Ollama classifier for finding→control mapping (confidence + static fallback) and an Ollama POA&M drafter, both producing review-gated artifacts. **Tradeoff:** classifier/draft errors (bounded by confidence threshold + human sign-off) vs. eliminating curator toil.
2. **Pattern:** AI assists, human signs off; drafts are never auto-final for regulator-facing artifacts.
3. **Air-gap:** classification + drafting on local Ollama; managed GenAI is the non-air-gapped alternative, documented not adopted.
4. **Failure mode:** confident misclassification → confidence threshold + deterministic fallback + review of low-confidence items.
5. **At scale:** add an LLM-as-judge eval over a labeled finding→control set, track classifier accuracy as a metric, and feed corrections back as few-shot examples.
