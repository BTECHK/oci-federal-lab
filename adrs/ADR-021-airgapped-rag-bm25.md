# ADR-021: Air-Gapped Compliance RAG — BM25 / Vectorless Retrieval

**Status:** Proposed (P2 introduces; user implements + finalizes)
**Date:** 2026-05-25
**Context phase:** Phase 2 — DR + AI-augmented compliance Q&A

---

## Context

FedTracker should answer plain-language compliance questions over the NIST 800-53 / 800-171 / CMMC L2 controls catalog ("what is AC-3?", "which controls cover audit logging?"). The hard constraint is **air-gap**: a federal/FedRAMP-aligned environment must keep this working with no outbound network and no external API. The query shape is keyword- and control-ID-driven, not free-form semantic prose. This realizes the previously-placeholder "AI-augmented operations" idea — done on the existing local Ollama, offline.

## Decision

Use **BM25 / vectorless retrieval** (`fedtracker-app/rag.py`) over the controls catalog, with **Ollama for answer generation only** (`fedtracker-app/routes/chat.py`, `POST /chat/ask`). **No embedding model and no vector store** — retrieval is pure sparse keyword/ID ranking, so the whole path runs fully air-gapped. The chatbot cites only control_ids returned by retrieval; if nothing matches, it says so.

## Alternatives Considered

| Option | Pro | Con | Verdict |
|---|---|---|---|
| **BM25 / vectorless** (rank_bm25 or SQLite FTS5) | No model at all → maximally air-gap-pure; keyword/ID-precise; trivial to rebuild | Pure-semantic queries with no keyword overlap rank worse | **Selected** |
| Dense-vector RAG with local Ollama embeddings + local vector store | Better on paraphrased/semantic queries | Needs an embedding model loaded + a vector store; heavier; overkill for ID/keyword lookups | Rejected as primary; viable as a future hybrid |
| OCI Generative AI Agents (managed RAG) | Managed, scalable, less code | NOT air-gapped — defeats the core constraint | Rejected; documented as the cloud alternative |
| Hybrid BM25 + dense (reciprocal-rank fusion) | Best recall across query shapes | More moving parts than lab scale needs today | Deferred — add if BM25 recall proves insufficient |

## Consequences

**Positive:**
- Fully air-gapped: no embedding model, no vector store, no outbound calls — provable by running with the network blocked.
- Keyword/control-ID precise — nails "what is AC-3" and "controls for audit logging".
- Cheap and simple: the index is just the corpus; rebuild on catalog change.

**Negative:**
- A purely semantic query that shares no keywords with the control text will retrieve poorly; mitigate with a small synonym map or add a hybrid path later.
- BM25 quality depends on tokenization/stop-words; control text is jargon-heavy and needs light tuning.
- The controls catalog is curated by hand — coverage gaps mean missed answers.

## Implementation Notes

- `fedtracker-app/rag.py` — load+chunk catalog (one control per chunk), BM25 index, `retrieve(query,k)` with an exact control-ID fast path, `format_context()`.
- `fedtracker-app/routes/chat.py` — `POST /chat/ask`; build the grounded Ollama prompt (same `/api/generate` call shape as `functions/python/log-summarizer`); verify cited ids ⊆ retrieved ids.
- Register the chat router in `fedtracker-app/main.py`.
- Controls catalog: JSON in-repo (or Object Storage); `OLLAMA_URL` via env.
- **Air-gap test** belongs in the evidence: block egress, prove `/chat/ask` still answers.

## Quiz (5 questions)

1. Why BM25 instead of vector embeddings here, given the air-gap constraint and the query shape? What would push you to add a dense path?
2. What class of question does BM25 answer worse than a dense retriever, and how would you mitigate it without breaking air-gap?
3. How do you stop the chatbot from citing a control_id that retrieval never returned? Why is that failure especially bad for a compliance tool?
4. Describe the air-gap test that proves this works offline. What exactly do you block, and what's the expected result?
5. The catalog grows from 100 to 5,000 controls. Does anything about the BM25 approach change? When would FTS5 beat an in-memory BM25Okapi?

## Key Takeaways (interview prep)

1. **Decision:** Air-gapped compliance Q&A via BM25/vectorless retrieval + local Ollama generation — no embedding model, no vector store. **Tradeoff:** weaker on purely-semantic queries vs. fully offline + ID/keyword precision.
2. **Pattern:** "RAG ≠ always vectors." Pick retrieval by query shape — sparse/BM25 for ID/keyword lookups; dense for semantic narrative matching. This lab is the sparse case.
3. **Grounding:** cite only retrieved control_ids; abstain ("no matching control") rather than fabricate — non-negotiable for compliance.
4. **Air-gap proof:** the differentiator no cloud-API RAG can claim — block the network and it still answers, because nothing leaves the box.
5. **At scale:** add a synonym map, then a hybrid BM25+dense with rank fusion; move from in-memory BM25 to FTS5 (or an offline vector index) as the catalog grows.
