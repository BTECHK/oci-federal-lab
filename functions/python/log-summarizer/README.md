# log-summarizer

Phase 2 OCI Python Function. Daily compliance-narrative generator.

**Trigger:** OCI Events scheduled rule (daily 23:00 UTC).
**Reads:** `app_logs` table in FedTracker ADB.
**Calls:** Ollama `/api/generate` for narrative LLM output.
**Writes:** Markdown summary to `compliance-artifacts/` Object Storage bucket.

## Patterns exercised

1. Resource principal authentication in OCI Functions
2. oracledb thin-mode connection with wallet auth
3. Ollama HTTP integration with timeout handling
4. OCI Object Storage `put_object` for artifact persistence
5. Prompt templating for structured compliance summaries

## Local test

```bash
fn deploy --app fedplatform-functions
fn invoke fedplatform-functions log-summarizer
```
