# dr-health-probe

Phase 2 OCI Go Function. Concurrent k3s node health probe for DR drills.

**Trigger:** OCI Events rule on manual DR drill event.
**Reads:** `K3S_NODES` env (comma-separated node IPs), each `/health` endpoint.
**Writes:** Alert JSON to `dr-alerts/` bucket if any node is degraded.

## Patterns exercised

1. Go goroutines + `sync.WaitGroup` in a serverless context
2. `context.WithTimeout` for bounded concurrent HTTP
3. fdk-go handler signature (`io.Reader` / `io.Writer`)
4. OCI SDK Object Storage write from Go with resource principal auth

## Build + deploy

```bash
fn deploy --app fedplatform-functions
fn invoke fedplatform-functions dr-health-probe
```
