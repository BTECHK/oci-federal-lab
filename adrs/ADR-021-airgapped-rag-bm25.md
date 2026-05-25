# ADR-021: Air-Gapped Compliance RAG — BM25 / Vectorless Retrieval

**Status:** Pending — decide at phase start; confirm consequences at phase end
**Date:** [date you decide]
**Context phase:** Phase 2 — DR + AI-augmented compliance Q&A

---

## The Problem

FedTracker should answer plain-language compliance questions over the NIST 800-53 / 800-171 / CMMC L2 controls catalog ("what is AC-3?", "which controls cover audit logging?"). The hard constraint is **air-gap**: a federal/FedRAMP-aligned environment must keep this working with no outbound network and no external API. The query shape is keyword- and control-ID-driven, not free-form semantic prose. Decide how you retrieve, how generation runs offline, and how the chatbot grounds (or abstains).

## Options to Research

Before writing your decision, research these alternatives:

1. **BM25 / vectorless** (rank_bm25 or SQLite FTS5)
   LOOK UP: BM25Okapi, SQLite FTS5, sparse vs dense retrieval, exact control-ID fast path
2. **Dense-vector RAG** with local Ollama embeddings + a local vector store
   LOOK UP: local embedding models, vector store footprint, when semantic recall beats keyword
3. **OCI Generative AI Agents (managed RAG)**
   LOOK UP: why a managed/cloud RAG breaks the air-gap constraint
4. **Hybrid BM25 + dense (reciprocal-rank fusion)**
   LOOK UP: RRF, when hybrid recall is worth the extra moving parts

For each, identify one advantage and one disadvantage specific to YOUR constraints (air-gap, keyword/ID query shape, lab scale). Decide how generation runs (Ollama, offline) and how you stop a cited `control_id` that retrieval never returned.

## Your Decision

<!-- Decide BEFORE building fedtracker-app/rag.py + routes/chat.py. Retrieval approach + grounding/abstain rule + one-sentence why. -->

## Your Rationale

<!--
- Air-gap constraint (provable offline?)
- Query shape (keyword/control-ID vs semantic prose)
- Interview relevance ("RAG ≠ always vectors — pick retrieval by query shape")
- Production contrast (managed RAG with no air-gap requirement)
-->

## Consequences

<!-- Fill at phase END: what it enabled (offline Q&A), what it cost (weaker on pure-semantic queries), blast radius if the bot cites an unretrieved control_id. -->

## Future Considerations

<!-- When would you add a synonym map, a hybrid BM25+dense path, or move from in-memory BM25 to FTS5 as the catalog grows? -->

---

## Quiz Questions

1. Why BM25 instead of vector embeddings here, given the air-gap constraint and the query shape? What would push you to add a dense path?
2. What class of question does BM25 answer worse than a dense retriever, and how would you mitigate it without breaking air-gap?
3. How do you stop the chatbot from citing a control_id that retrieval never returned? Why is that failure especially bad for a compliance tool?
4. Describe the air-gap test that proves this works offline. What exactly do you block, and what's the expected result?
5. The catalog grows from 100 to 5,000 controls. Does anything about the BM25 approach change? When would FTS5 beat an in-memory BM25Okapi?

---

*Build steps + evidence: `docs/exercises/p2/ai/rag-chatbot-notes.md`. After deciding, check your reasoning against: `answers/adrs/ADR-021-airgapped-rag-bm25.md`.*
