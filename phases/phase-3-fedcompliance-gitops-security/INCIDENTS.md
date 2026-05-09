# Phase 3 Incident Catalog

Break scripts are in `breaks/` (gitignored). Solutions are in `solutions/` (gitignored). Write your postmortem in `postmortems/` after each incident.

---

## INC-004: TLS Certificate Expires Mid-Pipeline

**Theme:** Security — certificate lifecycle management
**Difficulty:** P3 multi-component

### Symptom

Jenkins pipeline fails with an SSL handshake error.
FedAgent metrics show `fedplatform_pipeline_last_build_status{job="deploy-fedcompliance"}` = 0.
`scripts/INC-004-cert-expiry-check.sh` exits 1 with "cert expires in 0 days".

### Where to Look

1. `openssl s_client -connect <host>:443 -showcerts` — view the cert chain.
2. Jenkins logs for SSL handshake errors.
3. Cert renewal cron / timer: `crontab -l | grep certbot` or `systemctl status certbot.timer`.
4. Kubernetes secret expiry: `kubectl get secret tls-cert -o yaml | grep notAfter`.

### Expected Diagnosis

The break script either modifies the cert expiry or disables the renewal job. Investigation finds the expired cert and triggers renewal.

### Prevention

`scripts/INC-004-cert-expiry-check.sh` — daily cert expiry check. Warns at 30 days; blocks the pipeline if any cert is expired.

### Postmortem

Write your postmortem in `postmortems/INC-004-cert-expiry-postmortem.md`. Cover the renewal gap, why the alert didn't fire sooner, and the runbook change you'd make.

---

## INC-005: SLO Error Budget Burn from Ollama Latency Spike

**Theme:** Reliability — SLO burn-rate response
**Difficulty:** P3 multi-component

### Symptom

`scripts/INC-005-slo-budget-check.py` exits 1: "Error budget < 20% remaining".
Ollama response times exceed 30 seconds, causing log-summarizer function timeouts.

### Where to Look

1. Ollama logs: `journalctl -u ollama -n 100`.
2. System resources: `top`, `free -h`, GPU utilization (if applicable).
3. FedAgent metrics for the recent error-rate spike.
4. log-summarizer function logs in the OCI console.

### Expected Diagnosis

The break script increases Ollama load or reduces VM resources. Investigation finds the resource contention and chooses a response: model swap, VM resize, or invoking the error-budget policy.

### Prevention

`scripts/INC-005-slo-budget-check.py` — tracks error-budget consumption against the 99.5% SLO target.

### Postmortem

Write your postmortem in `postmortems/INC-005-slo-burn-postmortem.md`. Cover the burn-rate signal, what action you took, and how you would tighten the alert threshold.
