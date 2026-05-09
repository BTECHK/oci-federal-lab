// health-checker-go — OCI Function (Go runtime)
// Polls FedTracker /health/deep and returns a structured health verdict.
package main

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"os"
	"time"

	fdk "github.com/fnproject/fdk-go"
)

// ── Section 1: Struct definitions ───────────────────────────────────
// WHAT: Define Go structs for the /health/deep JSON response and the verdict to return
// LEARNING: encoding/json struct tags — `json:"field_name"` for marshaling/unmarshaling
// LOOK UP: encoding/json struct tags, json.Unmarshal, json.Marshal
//
// Write your implementation below. Check answers/ only after attempting.

type ComponentStatus struct {
	// add fields matching /health/deep JSON response
}

type HealthVerdict struct {
	// add verdict fields: Function, CheckedAt, Target, Verdict, Failures
}

// ── Section 2: HTTP GET with context timeout ─────────────────────────
// WHAT: Perform HTTP GET to APP_HEALTH_URL within a 10-second timeout
// LEARNING: context.WithTimeout, http.NewRequestWithContext, http.Client.Do
// LOOK UP: context.WithTimeout, http.NewRequestWithContext
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 3: Unmarshal response and determine verdict ──────────────
// WHAT: Parse the JSON body; determine HEALTHY (200) vs DEGRADED (503) vs UNREACHABLE
// LEARNING: json.NewDecoder vs json.Unmarshal, handling non-2xx status codes
// LOOK UP: json.NewDecoder, io.ReadAll, http.Response.StatusCode
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 4: fdk-go handler and main ──────────────────────────────
// WHAT: Register handler with fdk.Handle; myHandler calls the health check logic
// LEARNING: fdk-go handler signature: func(ctx context.Context, in io.Reader) (interface{}, error)
// LOOK UP: github.com/fnproject/fdk-go, fdk.Handle
//
// Write your implementation below. Check answers/ only after attempting.

func myHandler(ctx context.Context, in io.Reader) (interface{}, error) {
	return nil, nil // remove stub when implementing
}

func main() {
	fdk.Handle(fdk.HandlerFunc(myHandler))
}
