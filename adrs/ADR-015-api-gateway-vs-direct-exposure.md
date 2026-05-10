# ADR-015: OCI API Gateway in Front of FedTracker

**Status:** Accepted
**Date:** 2026-05-09
**Deciders:** Portfolio architect

## Context

In P1 and P2 the FedTracker FastAPI service was reachable directly on the lab VM at `10.0.2.201:8000`, fronted only by the network security list. P3 introduces external partner traffic — an OIDC-authenticated portal that calls the compliance and evidence endpoints. The two viable shapes:

1. **Direct exposure.** Public Load Balancer → fedtracker-app. Add JWT validation inside the FastAPI app. Rate limit with a Python middleware.
2. **API Gateway in front.** OCI API Gateway terminates external traffic, runs JWT validation + rate limiting + CORS + audit logging at the edge. fedtracker-app stays on the private subnet.

## Decision

Provision an OCI API Gateway in the public subnet with a `/v1` deployment routing `/personnel/*`, `/audit/*`, and `/compliance/*` to fedtracker-app on the private subnet. JWT auth, 100 req/sec/CLIENT_IP rate limit, CORS (fedplatform.gov origins), and access logging are all enforced at the gateway.

## Rationale

- **Compliance scope shrinks.** With JWT validation, rate limiting, and access logging at the edge, the FedTracker service only needs to handle authenticated requests from the gateway. Pen-test scope, audit scope, and the SSP boundary all narrow to the gateway tier.
- **Defense in depth.** A misconfigured FastAPI route can no longer expose unauth endpoints to the internet. Even if the backend ships with a debug route open, the gateway still requires a valid JWT.
- **Pure config, not code.** Rate limiting, CORS, JWT — three things you'd otherwise hand-roll in Python middleware. The gateway makes them HCL, which means version-controlled, peer-reviewed, and indistinguishable from infra.
- **Audit logging at the edge.** Every request hits OCI Logging before reaching the backend. Federal AU-2/AU-3 controls map cleanly. The backend doesn't need to log request metadata.
- **Private subnet stays private.** No public IP on the compute VM. The attack surface drops by an order of magnitude.

## Consequences

- **Two deploy artifacts.** `terraform apply` for the gateway, plus the existing FedTracker deploy. The gateway needs a JWKS URI from your OIDC provider before it can validate tokens.
- **Latency budget.** Each request now has a gateway hop. Measured in single-digit milliseconds in the same region; teach this in the implementation guide so learners size their SLO budget correctly.
- **Local dev divergence.** Developers calling the FastAPI directly skip JWT/rate-limiting. Document this clearly so a developer doesn't ship code that only worked because the local environment was unauth.
- **Cost.** OCI API Gateway is paid per million requests; price into the cost model. For Always Free experimentation, the gateway has a free tier but watch the rate ceiling.

## Learning Check

1. What is the OCI API Gateway request_policies block, and how does it differ from the spec's logging_policies block? Why are they on the deployment, not the gateway resource?
2. Why does this design use `rate_key = "CLIENT_IP"` for rate limiting, and what is the trade-off versus rate-limiting on the JWT subject?
3. How does the gateway's REMOTE_JWKS public key configuration handle key rotation, and what is the role of `max_cache_duration_in_hours`?
4. If the JWKS endpoint is unreachable when a client request arrives, what does the gateway return and how should monitoring detect this?
5. Walk through how this design would change if you needed mutual TLS between the gateway and fedtracker-app (mTLS) in addition to JWT — what gets configured on the gateway, what changes in the FastAPI app, and what new failure modes appear?
