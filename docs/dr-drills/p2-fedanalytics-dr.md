# DR Drill Report — P2 FedAnalytics

**Scenario:** k3s node failure during DR drill + cross-region ADB backup verification.
**Date executed:** _<fill in>_
**Total time:** _<fill in (target RTO: 30 min)>_
**Drill type:** Planned drill (NOT real incident)

---

## Pre-Drill SLI Snapshot

**Capture before injecting failure:**
- [ ] `kubectl get nodes -o wide` → save as `docs/exercises/p2/command-outputs/p2-drdrill-pre-nodes.txt`
- [ ] `fedplatform_backup_age_seconds` from Prometheus → annotate
- [ ] All `fedplatform_k3s_node_ready{node}` = 1 → confirm
- [ ] Grafana dashboard screenshot showing healthy state → `docs/exercises/p2/screenshots/p2-drdrill-pre.png`
- [ ] curl /health/deep → 200 with all components green → `docs/exercises/p2/command-outputs/p2-drdrill-pre-health.json`
- [ ] Note current RPO target (e.g., < 4h) and RTO target (e.g., < 30min)

## Stakeholder Notification

_<fill in: who you notified that drill is starting; document slack message / email send>_

## Failure Injection

**Choose ONE injection mode:**
- [ ] Mode A: cordon + drain a k3s node, simulate disk full or kubelet cert expiry
- [ ] Mode B: simulate ADB unavailable (block network from app subnet to ADB endpoint via security list)
- [ ] Mode C: simulate full region failover (more involved; only attempt if comfortable)

**Selected mode:** _<fill in>_

Commands executed:
1. _<fill in>_
2. _<fill in>_

**Time of injection:** _<HH:MM>_ — this is t=0 for RTO measurement.

## Failure Observation

**Capture during failure:**
- [ ] `kubectl get nodes` showing degraded state → `docs/exercises/p2/command-outputs/p2-drdrill-during-nodes.txt`
- [ ] dr-health-probe function invocation log → `docs/exercises/p2/command-outputs/p2-drdrill-probe.txt`
- [ ] Alerts that fired (Alertmanager) → annotate with alert names
- [ ] App behavior: /health/deep response → `docs/exercises/p2/command-outputs/p2-drdrill-during-health.json`

## Recovery Steps

Commands executed (in order):
1. _<fill in>_
2. _<fill in>_
3. _<fill in>_

**Time of full recovery:** _<HH:MM>_ — this is the end of RTO measurement.

## Measurements

- **RTO actual:** _<fill in: time from injection to full recovery>_
- **RTO target:** _<fill in: e.g., 30 min>_
- **RTO verdict:** _<met / missed>_
- **RPO actual:** _<fill in: data freshness gap at time of recovery>_
- **RPO target:** _<fill in: e.g., 4h>_
- **RPO verdict:** _<met / missed>_

## Post-Drill SLI Snapshot

**Capture after recovery:**
- [ ] `kubectl get nodes` all Ready → `docs/exercises/p2/command-outputs/p2-drdrill-post-nodes.txt`
- [ ] All `fedplatform_k3s_node_ready` = 1
- [ ] curl /health/deep → 200 with all components green → `docs/exercises/p2/command-outputs/p2-drdrill-post-health.json`
- [ ] Grafana screenshot showing recovery → `docs/exercises/p2/screenshots/p2-drdrill-post.png`

## Data Integrity Verification

- [ ] Row counts in personnel + audit_log + app_logs match pre-drill (no rows lost during failover)
- [ ] _<fill in: spot-check specific business-logic queries>_

## Postmortem

**What worked:**
_<fill in>_

**What didn't work:**
_<fill in: surprises, processes that didn't match what was documented, tools that broke>_

**What we'd change in real recovery vs drill:**
_<fill in: e.g., "would want a runbook for the cert-expiry case specifically — discovered it's not in our runbook library yet">_

**Action items from drill:**
- [ ] _<fill in: e.g., "Add cert-expiry runbook">_
- [ ] _<fill in>_

## Key Takeaways (interview prep — 5 bullets)

1. **DR architecture:** _<fill in>_
2. **RTO/RPO discipline:** _<fill in: what your actual measurement taught you>_
3. **Failure injection lesson:** _<fill in: what was surprising about the mode you chose>_
4. **Recovery automation gap:** _<fill in: what's still manual that should be automated>_
5. **At scale:** _<fill in: what's different at multi-region active-active vs active-passive>_
