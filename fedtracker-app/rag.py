"""
rag.py — v3 (P2) air-gapped BM25 / vectorless retrieval over the controls catalog.

NO embedding model — pure sparse keyword/ID retrieval, so it runs FULLY OFFLINE
(the air-gap differentiator). Ollama is used only to GENERATE the answer in
routes/chat.py; retrieval here touches no network and no model. Deliberate
"RAG != always vectors" choice: controls are queried by ID ("AC-3") and keyword
("audit logging"), which is exactly what BM25 is good at.
"""

# ── Section 1: Load + chunk the controls catalog ──────────────────────
# WHAT: load_controls(path) -> list[Control]. Read the NIST 800-53 / 800-171 /
#       CMMC L2 controls catalog (JSON/markdown in-repo or Object Storage). One
#       control (or sub-control/enhancement) per chunk, tagged control_id +
#       framework so a citation maps to exactly one control.
# LEARNING: chunk on the control boundary, not fixed length — a citation must
#       resolve to a single control id. The catalog is curated content you own.
# LOOK UP: json.load; a dataclass Control(control_id, framework, title, text).
# ADR: adrs/ADR-021-airgapped-rag-bm25.md
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Build the BM25 index (no embeddings) ───────────────────
# WHAT: build_index(controls) -> index. Tokenize each control's title+text and
#       build a BM25 index (rank_bm25 BM25Okapi) OR a SQLite FTS5 table. No
#       embedding model, no vector store — that's what keeps this air-gap-pure.
# LEARNING: BM25 = term-frequency / inverse-document-frequency ranking. It needs
#       nothing but the corpus; rebuild only when the catalog changes.
# LOOK UP: rank_bm25.BM25Okapi(tokenized_corpus); or SQLite FTS5 virtual table.
# ADR: adrs/ADR-021-airgapped-rag-bm25.md
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: retrieve(query, k) ─────────────────────────────────────
# WHAT: retrieve(query, k=5) -> list[Control]. Two paths:
#       (a) exact control-ID fast path — if the query matches an ID pattern
#           (e.g. "AC-3", "AU-2(1)"), return that control directly.
#       (b) otherwise BM25 top-k over the prose query.
# LEARNING: a hybrid of exact-ID + BM25 covers both "what is AC-3" and "which
#       controls cover audit logging" without any embeddings.
# LOOK UP: a regex for control-ID shape; bm25.get_top_n(tokenized_query, corpus, n=k).
# ADR: adrs/ADR-021-airgapped-rag-bm25.md
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 4: format_context(controls) ───────────────────────────────
# WHAT: format_context(controls) -> str. Render the retrieved controls as a
#       prompt context block (control_id + framework + text) for the chatbot to
#       ground its answer on. The chatbot must cite ONLY ids present here.
# LEARNING: this is the retrieval->generation seam; grounding the model in the
#       retrieved control text is what stops hallucinated citations.
# LOOK UP: how routes/chat.py builds the Ollama prompt (mirrors log-summarizer).
# ADR: adrs/ADR-021-airgapped-rag-bm25.md
#
# Write your implementation below. Check answers/ only after attempting.
