# Runbook: Rollback Bad Helm Release

**STATUS:** Scaffolded 2026-05-10. User fills exact commands during admin day P3 execution.

**When to use:** Helm release caused regression in OKE/k3s; ArgoCD synced a bad change; canary metrics red.
**Estimated time:** 5-15 minutes (rollback) + investigation time
**Severity context:** P1 if user-facing impact; P2 if internal/observability

## Symptom

- Error rate or latency alert post-deploy
- _<USER FILLS: ArgoCD shows last sync caused regression — what specific signals?>_

## Diagnostics

1. `helm history <release-name>` — identify recent revision
2. `helm get values <release-name> --revision N` — diff current vs previous values
3. _<USER FILLS: check ArgoCD sync history, identify the bad commit>_
4. _<USER FILLS: confirm symptom appeared at deploy timestamp (correlate)>_

## Remediation

1. `helm rollback <release-name> <previous-good-revision>`
2. _<USER FILLS: if ArgoCD: also revert the git commit (or auto-sync will re-roll forward)>_
3. _<USER FILLS: monitor pod rollout completion>_

**Rollback if remediation fails:** _<USER FILLS: manual kubectl rollout undo on the underlying deployment if helm rollback hangs>_

## Verification

- _<USER FILLS: pods at expected version, healthchecks green, error rate normal>_

## Escalation

- **Page if:** rollback fails, or user-facing impact > 10 min

## Postmortem trigger

- Always postmortem rollbacks of production releases — the bug got past CI/staging; need to know why
