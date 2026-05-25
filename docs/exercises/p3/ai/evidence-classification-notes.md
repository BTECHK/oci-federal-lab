# P3 AI Evidence — LLM Evidence Classification + POA&M Drafting

Proof that the Ollama classifier (evidence-collector Section 6) and the
`poam-generator` function automate GRC toil, air-gapped.

> 📋 **EVIDENCE CHECKPOINT** — files to commit to `docs/exercises/p3/ai/`:
> - [ ] `classify-before-after.md` — a finding mapped by the OLD static stub vs the Ollama classifier (specific control_ids + confidence + rationale)
> - [ ] `low-confidence-fallback.txt` — a case where confidence < threshold falls back to the static table
> - [ ] `poam-draft.json` — a generated POA&M draft (all standard fields) marked `status: draft`
> - [ ] `signoff-gate.md` — note showing a draft is NOT treated as open until human sign-off
> - [ ] `airgap-note.txt` — confirmation both run on local Ollama with no external API
> - [ ] notes below

## What I built
-

## What broke / what I tuned
- (confidence threshold, JSON parsing, POA&M field completeness)

## Key Takeaways
- (see `adrs/ADR-022-llm-evidence-classification-poam.md`)
