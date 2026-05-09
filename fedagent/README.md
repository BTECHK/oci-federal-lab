# FedAgent

Go Prometheus exporter for OpenSCAP compliance monitoring.
Part of FedPlatform — runs as a long-lived daemon on the OCI VM.

## Build and run
```bash
go build -o fedagent ./...
./fedagent -host localhost -port 9100 -interval 1h
```
Metrics endpoint: http://localhost:9100/metrics

## Patterns exercised
1. `prometheus.Collector` interface (Describe + Collect methods)
2. `goroutines` + `sync.Mutex` for concurrent, safe metric collection
3. `os/exec` subprocess invocation with timeout context
4. `encoding/xml` structured output parsing

## Phase evolution
- **P1:** Single-host OpenSCAP compliance score export
- **P2:** Multi-host goroutine polling, k3s node health gauges, ADB backup age metric
- **P3:** Trivy image scan findings, Cosign validity gauge, Jenkins pipeline last-build-status
