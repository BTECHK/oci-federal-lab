# Runbook: Investigate Failed Deploy

**STATUS:** Scaffolded 2026-05-10. User fills exact commands during admin day P1 execution.

**When to use:** GitHub Actions pipeline failed; image push succeeded but rollout didn't progress; healthcheck failing post-deploy.
**Estimated time:** 10-30 minutes (depends on where the failure is)
**Severity context:** P2 — depends if it caused user-facing impact

## Symptom

- _<USER FILLS: GitHub Actions red? Ansible playbook failed? /health/deep red after rollout?>_

## Diagnostics

1. _<USER FILLS: where to start — Actions logs? journalctl on VM? OCIR image inspection?>_
2. _<USER FILLS: pull latest deploy log lines>_
3. _<USER FILLS: compare deployed image digest vs CI-built image digest>_
4. _<USER FILLS: check container start logs vs expected startup sequence>_

## Remediation

Depending on root cause:
- **Bad image:** _<USER FILLS: roll back to previous image, then investigate the bad build>_
- **Config error:** _<USER FILLS: re-deploy with corrected env vars>_
- **Infra-side (VM resource exhaustion / network):** _<USER FILLS: address the infra issue first>_
- **Healthcheck flakiness:** _<USER FILLS: confirm healthcheck logic correct, not just slow startup>_

**Rollback if remediation fails:** _<USER FILLS: revert to last-known-good image+config combination>_

## Verification

- _<USER FILLS: deploy succeeds, healthcheck green for 5 min, error rate normal>_

## Escalation

- **Page if:** rollback also fails, or production traffic affected > 15 min

## Postmortem trigger

- Always postmortem failed deploys to production. The pattern of what's failing is the signal.
