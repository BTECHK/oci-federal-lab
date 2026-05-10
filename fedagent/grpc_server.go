// grpc_server.go — internal gRPC interface for ComplianceService.
//
// Internal-only listener (default :9101). External traffic continues to use
// REST on the FedTracker API. See adrs/ADR-014-grpc-internal-rest-external.md.
package main

// ── Section 1: Imports ───────────────────────────────────────────────
// WHAT: Import google.golang.org/grpc, generated pb stubs, fedagent oscap
// LEARNING: Generated stubs live at fedplatform/fedagent/pb after running
//           ./proto/generate.sh
// LOOK UP: google.golang.org/grpc, pb.RegisterComplianceServiceServer
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 2: ComplianceServer struct ────────────────────────────────
// WHAT: Define ComplianceServer that embeds pb.UnimplementedComplianceServiceServer
//       and holds a reference to the OscapCollector for scan reuse.
// LEARNING: Forward-compatible service — Unimplemented* embedded means new RPCs
//           added to the .proto won't break compilation, they'll return UNIMPLEMENTED
// LOOK UP: pb.UnimplementedComplianceServiceServer
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 3: GetOscapScore handler ──────────────────────────────────
// WHAT: Reuse oscap.go scan logic, build pb.GetOscapScoreResponse
// LEARNING: gRPC handler signature (ctx, *Request) (*Response, error),
//           map domain types → proto types, ISO 8601 timestamps
// LOOK UP: time.Now().UTC().Format(time.RFC3339), error wrapping with status.Error
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 4: Server registration helper ─────────────────────────────
// WHAT: NewGrpcServer() constructs *grpc.Server, registers ComplianceServer,
//       returns it for the main.go listener loop to call srv.Serve(lis)
// LEARNING: Separation of concerns — main.go owns the net.Listen,
//           this file owns the service wiring
// LOOK UP: grpc.NewServer, pb.RegisterComplianceServiceServer
//
// Write your implementation below. Check answers/ only after attempting.
