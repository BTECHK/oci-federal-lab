# Runbook: Investigate Supply Chain Finding

**STATUS:** Scaffolded 2026-05-10. User fills exact commands during admin day P3 execution.

**When to use:** Trivy or Cosign verification failed on image push; supply-chain-validator function alerted; OCIR scan flagged HIGH/CRITICAL CVE.
**Estimated time:** 30-90 minutes
**Severity context:** P1 if CRITICAL CVE on production image; P2 for HIGH; P3 for MEDIUM/LOW

## Symptom

- _<USER FILLS: which scanner alerted (Trivy / Cosign / OCIR scan)? what severity? which image?>_

## Diagnostics

1. _<USER FILLS: pull the scan report from `evidence/supply-chain-results/` or OCIR console>_
2. _<USER FILLS: identify the specific CVE/findings — read the actual CVE description, not just the severity score>_
3. _<USER FILLS: is the vulnerability reachable in our use of the dependency? (just because installed doesn't mean exploitable)>_
4. _<USER FILLS: check if upstream has a patched version>_

## Remediation

Depending on root cause:
- **Patched version available:** _<USER FILLS: bump dependency in Dockerfile/requirements.txt, rebuild, re-sign>_
- **No patch yet:** _<USER FILLS: assess reachability, document risk acceptance in ADR, set monitoring alert for when patch lands>_
- **Cosign signature failure:** _<USER FILLS: verify signing key not rotated, confirm CI is using correct key>_

**Rollback if remediation fails:** _<USER FILLS: revert to previous signed image while remediation continues>_

## Verification

- _<USER FILLS: re-scan new image, confirm finding resolved>_
- _<USER FILLS: image signed + verifies via Cosign>_
- _<USER FILLS: deploy + post-deploy scan green>_

## Escalation

- **Page if:** CRITICAL CVE on production image with active exploitation publicly known

## Postmortem trigger

- Postmortem if CRITICAL got past CI scan; need to know why the gate didn't catch it
