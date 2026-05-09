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
