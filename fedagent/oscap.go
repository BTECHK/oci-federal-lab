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
