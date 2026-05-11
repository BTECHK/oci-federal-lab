# Patch Simulation Report — OCI P3

**Scenario:** Simulate a critical kernel CVE patch on Oracle Linux 9 instances.

**Date executed:** _<fill in>_
**Total time:** _<fill in>_

---

## Pre-Patch State

**Capture before starting:**
- [ ] `uname -r` output → save as `evidence/admin/p3/command-outputs/pre-patch-kernel.txt`
- [ ] `uptime` → save as `evidence/admin/p3/command-outputs/pre-patch-uptime.txt`
- [ ] `dnf history list` → save as `evidence/admin/p3/command-outputs/pre-patch-dnf-history.txt`
- [ ] Application health: `curl -s localhost:8000/health/deep | jq .` → save as `evidence/admin/p3/command-outputs/pre-patch-app-health.json`
- [ ] Screenshot of OCI console showing instance state → `evidence/admin/p3/screenshots/pre-patch-instance.png`

## Patch Scenario

_<fill in: which CVE you're simulating, what the patch target is, what the rollback strategy is>_

Example scenario fields:
- **CVE:** _<fill in, e.g., CVE-2024-XXXX>_
- **Affected component:** _<fill in, e.g., kernel-5.14.0>_
- **Target version:** _<fill in>_
- **Rollback path:** _<fill in, e.g., dnf history rollback>_

## Pre-Reboot Validation

Commands run (in order):
1. _<fill in>_
2. _<fill in>_

## Reboot Orchestration

_<fill in: how you managed the reboot — single-host vs rolling, drain steps for k8s if applicable, monitoring during reboot>_

## Post-Reboot Verification

**Capture after reboot:**
- [ ] `uname -r` → `evidence/admin/p3/command-outputs/post-patch-kernel.txt` (should differ from pre-patch)
- [ ] `dnf history list` → `evidence/admin/p3/command-outputs/post-patch-dnf-history.txt`
- [ ] Application health (same endpoint as pre-patch) → `evidence/admin/p3/command-outputs/post-patch-app-health.json`
- [ ] Compare app metrics pre/post → annotate any differences

## Rollback Drill (mandatory — simulate a failed patch)

_<fill in: how you intentionally introduced a "failed patch" scenario and how you rolled back. Real rollback drill, not theoretical.>_

Rollback commands executed:
1. _<fill in>_
2. _<fill in>_

Post-rollback state vs pre-patch baseline:
- _<fill in: confirm uname -r matches pre-patch, app healthy>_

## Lessons + What I'd Do Differently at Scale

_<fill in: at 100 hosts, at 1000 hosts, with multi-region considerations>_

## Key Takeaways (interview prep — 5 bullets)

1. _<fill in>_
2. _<fill in>_
3. _<fill in>_
4. _<fill in>_
5. _<fill in>_
