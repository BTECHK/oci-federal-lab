# ADR-014: gRPC Internal, REST External

**Status:** Accepted
**Date:** 2026-05-09
**Deciders:** Portfolio architect

## Context

The FedPlatform stack has two distinct call patterns:

1. **External clients → FedTracker API.** Browsers, CLI tools, partner systems. Diverse clients, weak coupling, schema evolution outside our control. Must be debuggable with `curl`. Must be cacheable.
2. **FedTracker API → fedagent compliance scanner.** Same datacenter, same ownership, narrow contract, latency-sensitive (called inline on `GET /personnel/{id}`).

Two transport choices apply: REST over JSON, or gRPC over protobuf. Federal architectures often use both — REST at the edge, gRPC behind it.

## Decision

REST stays the only external transport. gRPC is added as the internal transport for compliance lookups between fedtracker-app and fedagent.

## Rationale

- **Type-safe contracts.** `compliance.proto` is the auditable artifact of how internal data flows. Schema changes are reviewed once and propagated to both sides via codegen — no drift between hand-rolled JSON shapes.
- **Schema evolution.** Adding a field is non-breaking by definition (proto3). Servers embed `UnimplementedComplianceServiceServer`, so new RPCs added to the .proto don't break older deployed servers — they return `UNIMPLEMENTED` until a handler ships.
- **Lower per-call overhead.** Binary protobuf + HTTP/2 multiplexing is roughly an order of magnitude lighter than JSON-over-HTTP/1.1 once you're in the same VPC. Compliance enrichment runs on every `GET /personnel/{id}`; the saved milliseconds compound.
- **Federal angle.** Type-safe internal contracts are easier to audit than free-form JSON. The `.proto` file IS the documentation.
- **REST stays at the edge** because every cloud CLI, partner system, and `curl` test expects REST. JWT validation, rate limiting, and audit logging are well-trodden in API gateways for REST. Forcing external clients onto gRPC would push proxy and observability complexity onto every consumer.

## Consequences

- Two transport stacks to operate: HTTP/1.1 + JSON externally, HTTP/2 + protobuf internally. Each gets its own observability and TLS story.
- A codegen step is now required before `go build` (Go) and before `python -m uvicorn ...` (Python). `fedagent/proto/generate.sh` automates it; CI must run it before tests.
- gRPC tooling (`grpcurl`, `evans`) does not replace `curl`. Operators learning the platform need both.
- Streaming RPCs (P3 `StreamComplianceEvents`) become natural — server-streaming over HTTP/2 is a first-class gRPC primitive. Modeling the same thing in REST would force long-polling or SSE.

## Learning Check

1. Why is embedding `pb.UnimplementedComplianceServiceServer` in the Go server struct considered a forward-compatibility pattern, and what failure mode does it prevent?
2. What is the difference between `grpc.aio.insecure_channel` and `grpc.aio.secure_channel`, and when would the lab still use insecure in production-like topologies (and when would it absolutely not)?
3. How does proto3's "all fields optional" semantics interact with Pydantic models on the Python side — what default value does fedtracker-app see when fedagent omits `findings_high`?
4. What does HTTP/2 multiplexing give you over HTTP/1.1 keep-alive that makes a long-lived gRPC channel cheap to share across many concurrent calls?
5. If fedtracker-app calls `stub.GetOscapScore(...)` and fedagent has been redeployed mid-call, what does the client see — and how would you make the call retry-safe without introducing duplicate scans?
