// supply-chain-validator — Phase 3 Go OCI Function.
// Trigger: OCI Events on image push to OCI Container Registry.
package main

import (
	"context"
	"encoding/json"
	"io"
	"os"

	fdk "github.com/fnproject/fdk-go"
)

// ── Section 1: Parse OCIR push event ──────────────────────────────────
// WHAT: Decode the OCI Container Registry push notification, extract the
//       image reference (registry/repo:tag).
// LEARNING: OCIR event schema, json.Unmarshal into a typed struct
// LOOK UP: github.com/oracle/oci-go-sdk events documentation
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 2: Run Cosign verify ──────────────────────────────────────
// WHAT: Invoke `cosign verify --key <pubkey> <image>` via os/exec
// LEARNING: subprocess pattern in serverless, exit-code-as-result
// LOOK UP: os/exec.Command, cmd.CombinedOutput
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 3: Run Trivy scan ─────────────────────────────────────────
// WHAT: Invoke `trivy image --format json <image>`, parse JSON
// LEARNING: chained subprocess invocations, error propagation
// LOOK UP: encoding/json, exec.CommandContext
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 4: Build PASS/FAIL result ─────────────────────────────────
// WHAT: Aggregate cosign + trivy outputs, decide overall verdict
// LEARNING: composite verdict logic, severity thresholds (HIGH/CRITICAL fails)
// LOOK UP: struct tagging for JSON output
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 5: Write JSON to supply-chain-results/ bucket ─────────────
// WHAT: Use OCI Object Storage client to put a result JSON keyed by image
// LEARNING: writing structured artifacts from Go serverless
// LOOK UP: github.com/oracle/oci-go-sdk objectstorage, common.NewProvider
//
// Write your implementation below. Check answers/ only after attempting.

func myHandler(ctx context.Context, in io.Reader, out io.Writer) {
	resp := map[string]any{"status": "not_implemented"}
	body, _ := json.Marshal(resp)
	_, _ = out.Write(body)
}

func main() {
	_ = os.Getenv // satisfy import
	fdk.Handle(fdk.HandlerFunc(myHandler))
}
