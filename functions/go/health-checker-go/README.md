# health-checker-go

OCI Function (Go runtime). Polls FedTracker /health/deep every 5 minutes.
Returns a structured verdict: HEALTHY, DEGRADED, or UNREACHABLE.

Trigger: OCI Events timer (every 5 minutes)
Cold start: ~5ms (vs ~100ms for the Python equivalent — teaching point)

## Patterns exercised
1. fdk-go handler signature (MyHandler func(ctx, io.Reader) (interface{}, error))
2. http.Client with context timeout
3. encoding/json unmarshal into structs
4. Structured HEALTHY/DEGRADED/UNREACHABLE verdict logic

## Build
```bash
go build -o health-checker-go ./...
```
