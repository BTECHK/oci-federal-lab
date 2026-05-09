// oscap.go — runs oscap oval eval and parses the XML output.
package main

// ── Section 1: Run oscap subprocess ─────────────────────────────────
// WHAT: Execute `oscap oval eval --results /tmp/oscap-results.xml <oval-definition>`
//       with a context timeout; capture stdout and stderr
// LEARNING: os/exec.CommandContext, context.WithTimeout, cmd.Output vs cmd.CombinedOutput
// LOOK UP: exec.CommandContext, context.WithTimeout, cmd.Run
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 2: Parse XML results ─────────────────────────────────────
// WHAT: Unmarshal the oscap results XML into a Go struct; extract pass/fail counts
// LEARNING: encoding/xml struct tags, xml.Unmarshal, nested struct mapping
// LOOK UP: encoding/xml, xml.Unmarshal, struct tags `xml:"attr"`
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 3: Return OscapResult struct ────────────────────────────
// WHAT: Populate and return an OscapResult{Score float64, Findings map[string]int}
// LEARNING: Struct as a data transfer object between oscap.go and collector.go
// LOOK UP: Go struct literal, map[string]int initialization
//
// Write your implementation below. Check answers/ only after attempting.

// OscapResult holds parsed compliance metrics.
type OscapResult struct {
	Score    float64
	Findings map[string]int // severity → count: "high", "medium", "low"
}

func RunOscap(host string) (*OscapResult, error) {
	return nil, nil // remove stub when implementing
}

// ── Section 4 (P2): Multi-host goroutine pool ────────────────────────
// WHAT: Spawn one goroutine per host in a hosts slice, run RunOscap concurrently,
//       use sync.WaitGroup to coordinate, return map[host]*OscapResult.
// LEARNING: goroutine + sync.WaitGroup pattern, channel for results, bounded concurrency
// LOOK UP: sync.WaitGroup.Add/Done/Wait, buffered channels for result collection
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 5 (P3): Subprocess pattern reuse ─────────────────────────
// WHAT: Trivy and Cosign both use os/exec subprocess invocations like RunOscap.
//       Factor out a runCommand(name, args...) helper to avoid duplication.
// LEARNING: helper function refactor, generic subprocess error handling
// LOOK UP: os/exec.CommandContext, error wrapping with %w
//
// Write your implementation below. Check answers/ only after attempting.
