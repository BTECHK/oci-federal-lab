# P2 AI Evidence — Air-Gapped BM25 RAG + Compliance Q&A Chatbot

Proof that `fedtracker-app/rag.py` + `routes/chat.py` answer compliance questions
fully offline (no embedding model, no outbound network).

> 📋 **EVIDENCE CHECKPOINT** — files to commit to `docs/exercises/p2/ai/`:
> - [ ] `airgap-test.txt` — block egress (firewall/iptables), then `POST /chat/ask` still returns a grounded answer. THE differentiator — capture the blocked-network proof.
> - [ ] `id-query.txt` — `"what is AC-3?"` → exact control returned + cited
> - [ ] `keyword-query.txt` — `"which controls cover audit logging?"` → BM25 top-k (show scores) + answer citing only retrieved ids
> - [ ] `abstain.txt` — an off-catalog question → "no matching control found" (no fabricated citation)
> - [ ] notes below

## What I built
-

## What broke / what I tuned
- (tokenization/stop-words, BM25 vs FTS5, synonym gaps, grounding guard)

## Key Takeaways
- (see `adrs/ADR-021-airgapped-rag-bm25.md`)
