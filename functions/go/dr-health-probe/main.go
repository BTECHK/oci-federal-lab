// dr-health-probe — Phase 2 Go OCI Function.
// Trigger: OCI Events on manual DR drill rule.
package main

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"os"

	fdk "github.com/fnproject/fdk-go"
)

// ── Section 1: fdk-go handler setup ───────────────────────────────────
// WHAT: Wire fdk.Handle(myHandler), parse k3s node IPs from K3S_NODES env
// LEARNING: Go serverless entrypoint, env-driven config in functions
// LOOK UP: fdk.Handle, fdk.HandlerFunc, os.Getenv, strings.Split
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 2: Goroutine per node /health call ────────────────────────
// WHAT: Launch a goroutine per node IP, each calls /health with a timeout
// LEARNING: goroutine + channel pattern, http.Client with context.WithTimeout
// LOOK UP: http.Client.Do, context.WithTimeout, sync.WaitGroup
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 3: sync.WaitGroup coordination ────────────────────────────
// WHAT: Wait for all goroutines, collect results into a slice
// LEARNING: WaitGroup.Add/Done/Wait, send-to-channel pattern
// LOOK UP: sync.WaitGroup, buffered channels for results
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 4: Write alert JSON to dr-alerts/ bucket ──────────────────
// WHAT: When any node degraded, marshal an alert JSON and upload via OCI SDK
// LEARNING: oci-go-sdk Object Storage client, resource-principal signer
// LOOK UP: github.com/oracle/oci-go-sdk/objectstorage, common.NewProvider
//
// Write your implementation below. Check answers/ only after attempting.

func myHandler(ctx context.Context, in io.Reader, out io.Writer) {
	// Stub. See answers/main.go for working implementation.
	resp := map[string]any{"status": "not_implemented"}
	body, _ := json.Marshal(resp)
	_, _ = out.Write(body)
}

func main() {
	_ = http.DefaultClient // satisfy import
	_ = os.Getenv          // satisfy import
	fdk.Handle(fdk.HandlerFunc(myHandler))
}
