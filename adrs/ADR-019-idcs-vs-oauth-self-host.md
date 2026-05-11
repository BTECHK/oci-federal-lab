# ADR-019: IDCS / Identity Domains as IdP vs Self-Hosted OAuth

**Status:** Proposed (P1 formalizes; user implements + finalizes)
**Date:** 2026-05-10 (locked via v1 addendum)
**Context phase:** Phase 1 — FedTracker Migration (formalized retroactively)

---

## Context

FedTracker API and fedagent gRPC service need user-facing OAuth2 authentication (Authorization Code + PKCE for browser/CLI users) and service-to-service auth (Client Credentials). JWT is the access token format; gateway validates statelessly via JWKS.

Choice: who issues the JWT?
- **OCI Identity Domains (formerly IDCS)** — OCI's managed IdP. FedRAMP-authorized. Free tier covers small footprint.
- **Self-hosted Keycloak** — open source, full control, can be customized.
- **External managed (Auth0, Okta)** — proven, but separate vendor relationship + cost.

## Decision

Use **OCI Identity Domains** as the IdP for both user and service-to-service JWT issuance. OCI API Gateway validates JWT against IDCS JWKS endpoint statelessly. fedagent gRPC interceptor does the same for service calls.

## Alternatives Considered

| Option | Pro | Con | Verdict |
|---|---|---|---|
| OCI Identity Domains | FedRAMP-authorized (federal narrative), free tier, native integration with OCI API Gateway JWT validation, no separate VM to operate | OCI-specific — not portable to other clouds | **Selected** |
| Self-hosted Keycloak on VM | Cloud-portable, full customization | Operational overhead (patching Keycloak, backup, HA), counts against Always Free OCPU | Rejected — operational cost > customization value at lab scale |
| Auth0 free tier | Mature, broad SDK support | External vendor; some features behind paid plan; less Federal-narrative fit | Rejected — federal compliance angle weak |
| API key only | Simple, no IdP needed | Not OAuth, not JWT, doesn't show identity layering | Rejected — fails the interview narrative |

## Consequences

**Positive:**
- Federal compliance angle: FedRAMP-authorized IdP is a real plus for the GovTech-style hiring signal
- Zero infrastructure to operate; IDCS is managed
- JWKS endpoint URL hardcoded in Gateway policy; statless validation = no IdP callbacks on hot path
- Existing OCI Vault works for storing client_secret for Client Credentials flow

**Negative:**
- Cloud-coupled — moving this stack to AWS would require swapping in Cognito (or analogous Entra ID for Azure, Identity Platform for GCP)
- Free tier limits (low users, low MAU) — fine for lab, would need paid tier for any real user base

## Implementation Notes

- Terraform resource: `oci_identity_domains_app` configured for OAuth flows
- API Gateway request policy: JWT validation against IDCS issuer URL
- gRPC interceptor: validates `authorization` metadata Bearer token
- API key (existing) stays as **quota tracking only**, separate concern from auth — see API Gateway request policies for rate limiting

## Quiz (5 questions)

1. Why is stateless JWT validation (via JWKS) faster than calling back to the IdP for every request? What's the worst-case latency cost of the callback approach?

2. Authorization Code + PKCE — what specific attack does PKCE mitigate that plain Authorization Code does not?

3. If IDCS were unavailable for 10 minutes, what happens to:
   - New logins (Authorization Code flow)?
   - Existing valid JWTs in flight?
   - Services renewing tokens via Client Credentials?

4. Why keep the API key separate from JWT auth instead of using JWT scope claims for quota? What does separating these concerns buy you operationally?

5. If FedRAMP compliance wasn't a factor, would Keycloak self-hosted be a better choice? Walk through the operational tradeoff at 10× the lab's user count.

## Key Takeaways (interview prep)

1. **Decision:** Managed IdP (IDCS) over self-hosted (Keycloak) because operational cost of running Keycloak HA exceeds the customization value at portfolio + lab scale. At enterprise scale the calculus flips — Keycloak's policy customization is worth the ops cost.

2. **Layered auth model:** API key for client identification + quota; JWT for user/service identity; mTLS for transport security (in gRPC). Three concerns, three mechanisms. Common mistake is conflating them — "we use API keys for auth" is the candidate I wouldn't hire.

3. **PKCE specifically:** mitigates authorization code interception attack against public clients (mobile apps, CLI tools). The code_verifier proves the client that started the flow is the one redeeming the code. Standard now even for confidential clients.

4. **JWKS makes JWT validation stateless** at the gateway — gateway fetches public keys hourly, validates signatures locally, no callback to IdP per request. This is why API Gateway can validate 1000s of req/sec without IdP being a bottleneck.

5. **Federal angle:** IDCS being FedRAMP-authorized is the kind of compliance detail GovTech hiring managers ask about. "We layered Federal-authorized IdP under OCI API Gateway, validated JWT statelessly, kept the audit gate at the edge" is the answer.
