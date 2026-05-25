"""
Chat routes — v3 (P2) air-gapped compliance Q&A chatbot.

RAG = BM25 retrieval (rag.py, no embedding model) + Ollama generation (same local
Ollama the log-summarizer function uses). Runs fully offline — the air-gap story.
Register this router in main.py (mirror the other routes/ includes).
"""
from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


# ── Section 1: POST /chat/ask ─────────────────────────────────────────
# WHAT: body {question}. Flow: rag.retrieve(question) -> rag.format_context() ->
#       build an Ollama prompt that says "answer ONLY from these controls, cite
#       control_ids" -> POST Ollama /api/generate -> return
#       {answer, cited_control_ids, retrieved_ids}.
# LEARNING: ground the answer in retrieved control text; the model must not cite
#       a control_id that wasn't retrieved. This is grounded generation, not
#       free recall.
# LOOK UP: requests.post(f"{OLLAMA_URL}/api/generate", json={"model","prompt",
#       "stream":False}) — same call shape as functions/python/log-summarizer.
# ADR: adrs/ADR-021-airgapped-rag-bm25.md
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Grounding guard (no-hallucinated-citations) ────────────
# WHAT: after generation, verify every control_id the model cited is in the
#       retrieved set; drop/flag any that aren't. If retrieve() returned nothing,
#       answer "no matching control found" rather than letting the model invent one.
# LEARNING: retrieval can miss; the safe failure is "I don't have a control for
#       that," never a confident fabrication — critical for a compliance tool.
# LOOK UP: set membership check of cited ids vs retrieved ids.
# ADR: adrs/ADR-021-airgapped-rag-bm25.md
#
# Write your implementation below. Check answers/ only after attempting.
