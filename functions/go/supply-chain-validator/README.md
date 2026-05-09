# supply-chain-validator

Phase 3 OCI Go Function. Image push → signature verify + vulnerability scan.

**Trigger:** OCI Events on image push to OCI Container Registry.
**Runs:** `cosign verify` + `trivy image`.
**Writes:** Result JSON keyed by image to `supply-chain-results/` bucket.

## Patterns exercised

1. Parsing OCIR push notifications in Go
2. Chained subprocess invocations (`cosign`, then `trivy`) inside a serverless function
3. Composite PASS/FAIL verdicts with severity thresholds
4. OCI Object Storage put_object from Go with resource-principal auth

## Build + deploy

```bash
fn deploy --app fedplatform-functions --no-bump
fn invoke fedplatform-functions supply-chain-validator
```
