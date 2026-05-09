# ADR-012: Prometheus Pull Model for OpenSCAP Metrics

**Status:** Accepted  
**Date:** 2026-05-08  
**Deciders:** Portfolio architect

---

## Context

FedAgent needs to expose OpenSCAP compliance scores continuously so that dashboards and alerting rules can track compliance posture over time. Two architectural options:

1. **Push model** — FedAgent calls the OCI Monitoring API (or a remote Prometheus Pushgateway) after each scan and submits metric data points.
2. **Pull model** — FedAgent runs an HTTP server exposing a `/metrics` endpoint in Prometheus text format; a Prometheus server scrapes it on a configurable interval.

---

## Decision

Use the **Prometheus pull model** (option 2). FedAgent exposes `/metrics` on `:9100`. Prometheus scrapes it.

---

## Rationale

| Criterion | Push (OCI Monitoring) | Pull (Prometheus) |
|---|---|---|
| Air-gap compatible | No — requires outbound HTTPS to OCI API | Yes — Prometheus is co-located, no egress |
| Cost | OCI Monitoring ingestion charges per data point | Free — Prometheus is self-hosted |
| FedRAMP suitability | Outbound call to cloud SaaS from compliance exporter raises audit concerns | Fully on-premises, no data leaves the environment |
| Ecosystem | OCI Console dashboards only | Prometheus + Grafana + AlertManager + recording rules |
| Implementation complexity | OCI SDK auth + API calls in every export | HTTP server with promhttp handler — idiomatic Go |
| Scrape gap on crash | Data points lost if push fails silently | Scrape fails visibly — Prometheus marks target as DOWN |

The air-gap and FedRAMP rationale is decisive. Federal environments under CMMC/FedRAMP often prohibit outbound data flows from compliance tooling. The Prometheus pull model keeps all metric data within the environment boundary.

---

## Consequences

- A Prometheus server must be deployed in the environment. Phase 1 uses a standalone Prometheus on the same VM (acceptable for a single-node lab). Phase 2 moves Prometheus into the k3s cluster.
- Metrics are only as fresh as the scrape interval (set to 1 hour for compliance scans — acceptable since OpenSCAP runs are expensive).
- FedAgent exposes a plaintext HTTP endpoint on `:9100` — restrict with firewall to Prometheus server IP only.

---

## Learning Check

1. What is the difference between a Prometheus `gauge` and a `counter`? Give an example of each from FedAgent's metrics.
2. Why does the Prometheus pull model suit air-gapped FedRAMP environments better than push?
3. What is the `prometheus.Collector` interface? Why implement it rather than using `prometheus.NewGaugeVec` directly?
4. How does `sync.Mutex` protect concurrent metric collection in FedAgent's `Collect()` method?
5. If two Prometheus scrapers hit FedAgent simultaneously without mutex protection, what is the specific failure mode?
