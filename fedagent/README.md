# FedAgent

Go Prometheus exporter for OpenSCAP compliance monitoring.
Part of FedPlatform — runs as a long-lived daemon on the OCI VM.

## Build and run
```bash
# Generate protobuf stubs first — required before `go build`.
./proto/generate.sh

go build -o fedagent ./...
./fedagent -host localhost -port 9100 -grpc-port 9101 -interval 1h
```

Endpoints:
- **HTTP** `:9100/metrics` — Prometheus scrape target
- **gRPC** `:9101` — internal `ComplianceService` (see `proto/compliance.proto` and adrs/ADR-014)

The `proto/generate.sh` script writes Go stubs under `pb/` (gitignored) and Python
stubs under `fedtracker-app/proto/`. Re-run it whenever `compliance.proto` changes.

## Patterns exercised
1. `prometheus.Collector` interface (Describe + Collect methods)
2. `goroutines` + `sync.Mutex` for concurrent, safe metric collection
3. `os/exec` subprocess invocation with timeout context
4. `encoding/xml` structured output parsing
5. **gRPC server** with `UnimplementedComplianceServiceServer` embedding for forward compatibility

## Phase evolution
- **P1:** Single-host OpenSCAP compliance score export + gRPC `GetOscapScore`
- **P2:** Multi-host goroutine polling, k3s node health gauges, ADB backup age metric, gRPC `GetK3sNodeHealth` + `GetADBBackupStatus`
- **P3:** Trivy image scan findings, Cosign validity gauge, Jenkins pipeline last-build-status, gRPC `GetSupplyChainStatus` + server-streaming `StreamComplianceEvents`
