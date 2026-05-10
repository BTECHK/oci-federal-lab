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

// ── Section 5 (P2): GetK3sNodeHealth handler ──────────────────────────
// WHAT: Reuse PollK3sNodes() from k3s.go (P2 answers) to build a
//       K3sNodeHealthResponse with one NodeStatus per node.
// LEARNING: gRPC server reuses domain helpers; the proto types are the
//           edge schema, internal types stay free.
// LOOK UP: pb.K3SNodeHealthResponse_NodeStatus, repeated field append
//
// CASING NOTE: protoc-gen-go uppercases the "K3s" acronym in Go type names.
// The proto message is `K3sNodeHealthResponse`, but the generated Go type
// is `pb.K3SNodeHealthResponse`. Python stubs preserve `K3sNodeHealthResponse`.
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 6 (P2): GetADBBackupStatus handler ────────────────────────
// WHAT: Call GetBackupAge for the configured ADB OCID, derive within_rpo
//       boolean (age < 4h), return ADBBackupStatusResponse.
// LEARNING: One handler can pull data from multiple sources (env, OCI CLI)
//           but should still complete inside the deadline.
// LOOK UP: time.Since, ctx.Deadline, status.Error wrapping
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 7 (P3): GetSupplyChainStatus handler ──────────────────────
// WHAT: Reuse Trivy + Cosign helpers from answers/trivy.go and cosign.go
//       for the requested image. Build SupplyChainStatusResponse.
// LEARNING: Combine multiple subprocess scans into a single proto response;
//           remember each subprocess inherits the gRPC handler's deadline.
// LOOK UP: ScanTrivy, VerifyCosign, prometheus label keys
//
// Write your implementation below. Check answers/ only after attempting.

// ── Section 8 (P3): StreamComplianceEvents handler ────────────────────
// WHAT: Server-streaming RPC. Hold a buffered channel of ComplianceEvent
//       and stream.Send each event as it arrives. Close the stream when
//       the client disconnects (stream.Context().Done()).
// LEARNING: gRPC server-streaming: handler signature is
//           (req, stream) and you call stream.Send(...) until the
//           client cancels. Don't block forever — drain on context cancel.
// LOOK UP: pb.ComplianceService_StreamComplianceEventsServer, ctx cancellation
//
// Write your implementation below. Check answers/ only after attempting.
