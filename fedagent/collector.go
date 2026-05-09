// OscapCollector implements prometheus.Collector for OpenSCAP compliance data.
package main

import "github.com/prometheus/client_golang/prometheus"

// ── Section 1: Collector struct with metric descriptors ──────────────
// WHAT: Define OscapCollector struct holding *prometheus.Desc for each metric
// LEARNING: prometheus.Desc is metadata (name, help, label names) — created once at init
// LOOK UP: prometheus.NewDesc, prometheus.Desc, variableLabels parameter
//
// Write your implementation below. Check answers/ only after attempting.

type OscapCollector struct {
	// add your prometheus.Desc fields here
}

// ── Section 2: Describe — send metric descriptors ────────────────────
// WHAT: Send all *prometheus.Desc to the channel — tells Prometheus what metrics to expect
// LEARNING: Describe is called by Prometheus during registration and to detect conflicts
// LOOK UP: prometheus.Collector interface, ch <- descriptor
//
// Write your implementation below. Check answers/ only after attempting.

func (c *OscapCollector) Describe(ch chan<- *prometheus.Desc) {
}

// ── Section 3: Collect — run scan and emit metrics ───────────────────
// WHAT: Call RunOscap(), build prometheus.Metric values, send them to the channel
// LEARNING: prometheus.MustNewConstMetric, GaugeValue vs CounterValue
// LOOK UP: prometheus.MustNewConstMetric, prometheus.GaugeValue, prometheus.CounterValue
//
// Write your implementation below. Check answers/ only after attempting.

func (c *OscapCollector) Collect(ch chan<- prometheus.Metric) {
}

// ── Section 4 (P2): Additional metric descriptors ────────────────────
// WHAT: Add Desc fields for fedplatform_k3s_node_ready{node} and
//       fedplatform_backup_age_seconds{target}; register them via Describe.
// LEARNING: One collector can emit multiple metric families
// LOOK UP: prometheus.NewDesc with variable labels, gauge semantics
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 5 (P2): Emit k3s + backup metrics in Collect ─────────────
// WHAT: After emitting oscap metrics, call PollK3sNodes() + GetBackupAge()
//       and emit one metric per node and one per backup target.
// LEARNING: A single Collect() call should be cheap and concurrency-safe
// LOOK UP: prometheus.MustNewConstMetric, GaugeValue
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 6 (P3): Supply chain metric descriptors ──────────────────
// WHAT: Add Desc fields for fedplatform_trivy_findings_total{image, severity},
//       fedplatform_cosign_signature_valid{image}, and
//       fedplatform_pipeline_last_build_status{job}; register them in Describe.
// LEARNING: collectors with multiple data sources, label cardinality choices
// LOOK UP: prometheus.NewDesc with multiple labels
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 7 (P3): Emit Trivy + Cosign + Jenkins metrics ────────────
// WHAT: In Collect, call ScanTrivy(), VerifyCosign(), QueryJenkins() and
//       emit metrics. Cosign returns 0 or 1; Jenkins returns 0 or 1; Trivy
//       emits a counter per image × severity.
// LEARNING: emitting many label combinations in a single Collect call
// LOOK UP: prometheus.CounterValue vs GaugeValue choice per metric
//
// Write your implementation below. Check answers/ only after attempting.
