# evidence-collector

Phase 3 OCI Python Function. Compliance-evidence chainer.

**Trigger:** OCI Events on object create in `scan-results/` bucket (FedAgent writes scan output there).
**Reads:** Scan JSON + control catalog + audit log excerpt.
**Writes:** Evidence package under `compliance-artifacts/evidence-TIMESTAMP/` with manifest.

## Patterns exercised

1. Event-driven function chaining (FedAgent → OCI Events → this function)
2. Multi-source artifact assembly (Object Storage + REST API + DB)
3. CMMC control mapping from technical findings
4. Manifest-based package format with sha256 hashes

## Local test

```bash
fn deploy --app fedplatform-functions --no-bump
fn invoke fedplatform-functions evidence-collector
```
