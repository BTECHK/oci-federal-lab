# Phase 2 Incident Catalog

Break scripts are in `breaks/` (gitignored). Solutions are in `solutions/` (gitignored). Write your postmortem in `postmortems/` after each incident.

---

## INC-002: OpenSCAP Score Drops After Package Update

**Theme:** Security — compliance regression detection
**Difficulty:** P2 integration

### Symptom

FedAgent metrics show `fedplatform_oscap_score` dropped from 87 to 61.
`scripts/INC-002-oscap-regression.sh` exits 1 with a regression warning.

### Where to Look

1. Run `oscap oval eval --results scan-results.xml /usr/share/xml/scap/ssg/content/ssg-ol9-oval.xml` and compare against the baseline.
2. Check `rpm -Va` for modified package files.
3. Check `rpm -q --changelog <package>` for recent changes.
4. Compare `/opt/fedtracker/oscap-baseline.txt` to the current score.

### Expected Diagnosis

The break script installs a non-CIS-compliant package. Investigation finds the package and either removes it or accepts the deviation with documented justification.

### Prevention

`scripts/INC-002-oscap-regression.sh` — detects score drops before they persist.

### Postmortem

Write your postmortem in `postmortems/INC-002-oscap-regression-postmortem.md`. Cover what changed, how detection happened, and what guardrail you would add.

---

## INC-003: k3s Node Fails During DR Drill

**Theme:** Kubernetes — node failure recovery
**Difficulty:** P2 integration

### Symptom

`kubectl get nodes` shows a node in `NotReady` state during the DR drill.
`scripts/INC-003-k3s-dr-readiness.sh` exits 1 before the drill starts.

### Where to Look

1. `journalctl -u k3s -n 100` on the failing node.
2. `kubectl describe node <node-name>` for conditions and events.
3. Disk space: `df -h /var/lib/rancher/k3s`.
4. Kubelet cert expiry: `openssl x509 -noout -dates -in /var/lib/rancher/k3s/agent/client-kubelet.crt`.

### Expected Diagnosis

The break script fills disk on the worker node or expires a cert. Investigation traces the NotReady condition to its root cause.

### Prevention

`scripts/INC-003-k3s-dr-readiness.sh` — validates k3s cluster health before DR drills begin.

### Postmortem

Write your postmortem in `postmortems/INC-003-k3s-node-failure-postmortem.md`. Cover the failure mode, detection latency, and the readiness gate you would add to the drill runbook.
