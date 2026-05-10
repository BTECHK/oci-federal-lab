# ADR-016: k3s in P2 Before OKE in P3

**Status:** Accepted
**Date:** 2026-05-09
**Deciders:** Portfolio architect

## Context

Phase 2 (FedAnalytics DR) and Phase 3 (FedCompliance) both run on Kubernetes. Two viable paths:

1. **k3s in P2, OKE Basic in P3** — DIY single-binary cluster first, managed cluster second.
2. **OKE Basic in both phases** — managed-only path, skip the DIY tier.

## Decision

Use k3s for P2 and OKE Basic for P3.

## Rationale

- **Pedagogy first.** k3s exposes the control plane (apiserver/etcd/controller-manager/scheduler bundled in `k3s server`), kubelet, Flannel CNI, and raw kubeconfig. The learner builds and breaks these primitives by hand before reaching for the managed abstraction.
- **Failure mode learning.** When something breaks in OKE, the answer is often "open a ticket." When something breaks in k3s, the answer is "read journalctl, restart kubelet, check certificate dates." That maps directly to L5/L6 SRE interview signal.
- **Cost.** k3s on a single OL9 VM costs Always Free tier; OKE Basic pricing kicks in once a managed cluster is provisioned. Spreading across phases keeps the lab inside the free tier longer.
- **DR drill realism.** P2's INC-003 (k3s node fails during DR drill) requires shell-level access to the kubelet — trivial on k3s, awkward on OKE.

## Consequences

- The learner has to install k3s manually in P2 (single binary, well-documented). One extra evening of work compared to skipping straight to OKE.
- Some k3s-specific commands won't transfer (e.g., `k3s kubectl` vs `kubectl`, embedded etcd vs external). The guide flags every divergence so muscle memory is correct.
- P3 introduces OKE Basic, Helm, and ArgoCD — the managed path. The migration story (k3s → OKE) is itself a teaching moment for "rebuild on managed Kubernetes."

## Learning Check

1. What four control-plane components does `k3s server` bundle into a single binary, and what does each do?
2. How does Flannel CNI assign pod IP addresses, and why does k3s default to it?
3. What is the difference between `kubectl get nodes` reporting `NotReady` because of `DiskPressure` vs `MemoryPressure` vs `Ready=False`?
4. Where does k3s store its kubeconfig file by default, and what permissions does it need to be readable by `kubectl` from a non-root user?
5. If you migrate from k3s to OKE Basic, which of your manifests need to change, and which are portable?
