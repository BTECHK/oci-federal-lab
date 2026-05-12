package main

import (
	"testing"
	"time"

	"github.com/prometheus/client_golang/prometheus"
)

// ── Section 1: Table-driven test for compliance collector ───────────
// WHAT: Test NewOscapCollector + Describe using table-driven subtests.
//       Cases: verify descriptor count, check metric names after Collect,
//       test with empty host list.
// LEARNING: Go table-driven tests with t.Run() — the standard pattern for
//           parameterized testing. Each case is independent and named.
// LOOK UP: testing.T, t.Run, []struct test cases, prometheus.Desc,
//           chan<- prometheus.Metric
//
// Write your implementation below. Check answers/ only after attempting.

func TestOscapCollector_Describe(t *testing.T) {
	t.Skip("implement this test")
}

func TestOscapCollector_Collect(t *testing.T) {
	t.Skip("implement this test")
}
