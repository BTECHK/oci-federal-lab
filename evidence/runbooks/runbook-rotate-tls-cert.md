# Runbook: Rotate TLS Certificate

**STATUS:** Scaffolded 2026-05-10. User fills exact commands during admin day P1 execution.

**When to use:** cert expiry within 30 days, or after a private key compromise.
**Estimated time:** 15-30 minutes (with verification + propagation)
**Severity context:** P1 if cert is expired (TLS handshake failure); P3 if scheduled rotation

## Symptom

- _<USER FILLS: scripts/INC-004-cert-expiry-check.sh alerts? Browser shows expired cert? Jenkins fails with SSL error?>_

## Diagnostics

1. `openssl s_client -connect <host>:443 -showcerts < /dev/null 2>/dev/null | openssl x509 -noout -dates`
2. _<USER FILLS: command to identify which secret holds the current cert (Vault / K8s secret / file path)>_
3. _<USER FILLS: command to check current cert is the one in use (cert serial match)>_

## Remediation

1. _<USER FILLS: cert generation command (Let's Encrypt? internal CA? OCI Certificate Service?)>_
2. _<USER FILLS: deploy the new cert (kubectl create secret, update Vault, scp to VM)>_
3. _<USER FILLS: reload service to pick up new cert>_

**Rollback if remediation fails:** _<USER FILLS: revert to previous cert secret/file; keep N-1 cert available for fast rollback>_

## Verification

- `openssl s_client -connect <host>:443 -showcerts < /dev/null 2>/dev/null | openssl x509 -noout -dates` — confirm new dates
- _<USER FILLS: end-to-end test (curl with cert validation, browser check)>_

## Escalation

- **Page if:** rotation fails AND old cert is within 7 days of expiry
- **Owner:** security on-call

## Postmortem trigger

- Cert expired (i.e., scheduled rotation missed) — always postmortem
