# ADR-022: LLM Evidence Classification + POA&M Drafting (GRC Automation)

**Status:** Pending — decide at phase start; confirm consequences at phase end
**Date:** [date you decide]
**Context phase:** Phase 3 — AI-augmented operations / GRC automation

---

## The Problem

Two manual, curator-heavy GRC steps exist today: (1) `evidence-collector` maps scan findings to controls with a hard-coded stub ("every High finding maps to every control") — noise an auditor won't trust; (2) turning a finding into a POA&M (Plan of Action & Milestones) is fully manual. The air-gap must hold. Decide how (and whether) to automate each with the **local Ollama**, and what review gate protects regulator-facing output.

> **Scope note:** classification is the core P3 deliverable; **POA&M drafting is the stretch half** — do classification first, add the drafter if time allows.

## Options to Research

Before writing your decision, research these alternatives:

1. **Ollama classifier + POA&M drafter** (local LLM, confidence + static fallback, human sign-off)
   LOOK UP: STRICT-JSON LLM output, confidence thresholds, draft→open sign-off gates
2. **Keep the static finding→control table** (deterministic, zero model)
   LOOK UP: why "every High → every control" isn't auditor-credible
3. **Managed OCI Generative AI for classification**
   LOOK UP: why managed GenAI breaks the air-gap constraint
4. **Manual classification + manual POA&M authoring**
   LOOK UP: the curator-toil baseline this is meant to remove

For each, identify one advantage and one disadvantage specific to YOUR constraints (air-gap, auditor credibility, model-error risk). Decide where the confidence threshold lives and why a POA&M must be a draft.

## Your Decision

<!-- Decide BEFORE building evidence-collector Section 6 (+ optional poam-generator). Classification approach + fallback + sign-off gate + one-sentence why. -->

## Your Rationale

<!--
- Air-gap constraint (local Ollama)
- Auditor credibility (specific mappings vs blanket noise)
- Model-error bounding (confidence threshold + static fallback + human review)
- Production contrast (managed GenAI without air-gap)
-->

## Consequences

<!-- Fill at phase END: what it enabled (specific mappings, drafted POA&Ms), what it cost (misclassification risk), blast radius if a draft is auto-promoted to "open". -->

## Future Considerations

<!-- When would you add an LLM-as-judge eval over a labeled finding→control set, track classifier accuracy, and feed corrections back as few-shot examples? -->

---

## Quiz Questions

1. Why is an LLM classifier more defensible to an auditor than the static "every High → every control" table? What's the risk it introduces, and how do you bound it?
2. What do you do with a low-confidence classification — accept, fall back, or escalate? Where does the threshold live?
3. Why must a generated POA&M be a *draft* with a sign-off gate? What goes wrong if a draft is auto-promoted to "open"?
4. Both features run on local Ollama. What's the air-gap proof, and what would change if you used managed OCI GenAI instead?
5. How would you *evaluate* the classifier's accuracy over time (think LLM-as-judge / a labeled finding→control set)?

---

*Build steps + evidence: `docs/exercises/p3/ai/evidence-classification-notes.md`. After deciding, check your reasoning against: `answers/adrs/ADR-022-llm-evidence-classification-poam.md`.*
