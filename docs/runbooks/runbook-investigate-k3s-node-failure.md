# Runbook: Investigate k3s Node Failure

**STATUS:** Scaffolded 2026-05-10. User fills exact commands during admin day P2 execution.

**When to use:** `kubectl get nodes` shows NotReady; INC-003 prevention script alerted; pods evicted unexpectedly.
**Estimated time:** 15-45 minutes
**Severity context:** P2 single node; P1 multiple nodes simultaneously

## Symptom

- `kubectl get nodes` shows NotReady or Unknown
- `scripts/INC-003-k3s-dr-readiness.sh` exits non-zero
- Pods stuck Pending, ContainerCreating, or being evicted

## Diagnostics

1. `kubectl get nodes -o wide` — capture full state, IP, kernel version
2. `kubectl describe node <node-name>` — read conditions, events, allocatable
3. _<USER FILLS: SSH to the node, run journalctl -u k3s -n 200>_
4. _<USER FILLS: check disk space — df -h /var/lib/rancher/k3s>_
5. _<USER FILLS: check kubelet cert expiry — openssl x509 -noout -dates -in /var/lib/rancher/k3s/agent/client-kubelet.crt>_
6. _<USER FILLS: check k3s server reachability from agent>_

## Remediation

Depending on root cause:
- **Disk full:** _<USER FILLS: clear /var/log, prune old images, journal-vacuum>_
- **Cert expired:** _<USER FILLS: regenerate via k3s server>_
- **Network partition:** _<USER FILLS: check iptables, security list, firewalld>_
- **OOM:** _<USER FILLS: check dmesg for OOM kills, adjust pod resource limits>_

**Rollback if remediation fails:** _<USER FILLS: drain node, replace with new node, rejoin to cluster>_

## Verification

- `kubectl get nodes` shows Ready
- _<USER FILLS: test pod scheduling on the recovered node>_
- _<USER FILLS: confirm metric `fedplatform_k3s_node_ready{node=...}` returns to 1>_

## Escalation

- **Page if:** multiple nodes affected, or recovery time approaching RTO

## Postmortem trigger

- Always postmortem cluster-wide outages; single node failures only if pattern (3+ in a week)
