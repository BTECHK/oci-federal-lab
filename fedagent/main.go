// FedAgent — Go Prometheus exporter for OpenSCAP compliance metrics.
// Part of FedPlatform. Exposes compliance scores on :9100/metrics.
package main

import (
	"flag"
	"net/http"
)

// ── Section 1: Flag parsing ──────────────────────────────────────────
// WHAT: Parse CLI flags: -host (target hostname), -port (metrics port), -interval (scan interval)
// LEARNING: Go flag package — flag.String, flag.Int, flag.Duration, flag.Parse
// LOOK UP: flag.String, flag.Duration, time.Duration
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 2: Prometheus registry and collector ─────────────────────
// WHAT: Create a non-default Prometheus registry, instantiate OscapCollector, register it
// LEARNING: Custom registry vs DefaultRegisterer — why prefer isolated registries in exporters
// LOOK UP: prometheus.NewRegistry(), prometheus.MustRegister
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 3: HTTP handler for /metrics ─────────────────────────────
// WHAT: Serve the Prometheus metrics endpoint using promhttp.HandlerFor
// LEARNING: promhttp.HandlerFor with a custom registry, http.NewServeMux
// LOOK UP: promhttp.HandlerFor, promhttp.HandlerOpts
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 4: HTTP server startup ───────────────────────────────────
// WHAT: Start the HTTP server, log the listening address, handle shutdown signals
// LEARNING: http.ListenAndServe, os/signal for graceful shutdown
// LOOK UP: http.ListenAndServe, os.Signal, signal.NotifyContext
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 5: gRPC server startup (P1 addition) ─────────────────────
// WHAT: Run a second listener on :9101 for the internal ComplianceService.
//       Use a goroutine and net.Listen("tcp", ":9101"); call NewGrpcServer
//       (defined in grpc_server.go) and srv.Serve(lis).
// LEARNING: Two listeners share one process — graceful shutdown must drain
//           BOTH before the program exits.
// LOOK UP: net.Listen, grpc.Server.GracefulStop, errgroup or sync.WaitGroup
//
// Write your implementation below. Check answers/ only after attempting.

func main() {
	_ = flag.String("host", "localhost", "Target hostname for OpenSCAP scan")
	_ = http.NewServeMux() // satisfy import; remove when implementing
}
