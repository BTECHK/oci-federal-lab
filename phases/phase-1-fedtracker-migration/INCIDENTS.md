# Phase 1 Incident Catalog

Break scripts are in `breaks/` (gitignored). Solutions are in `solutions/` (gitignored). Write your postmortem in `postmortems/` after each incident.

---

## INC-001: AIDE Detects Unauthorized Binary Change

**Theme:** Security — file integrity monitoring  
**Difficulty:** Foundational  
**Phase:** 1 (AIDE introduced in the hardening steps)

### Symptom

AIDE's daily cron job writes an alert to `/var/log/aide/aide.log`. If email alerting is configured, you receive a message like:

```
AIDE: Warning — integrity check failed for /opt/fedtracker/fedagent
Changed attributes: sha512, size, mtime
```

Simultaneously, the FedAgent Prometheus endpoint shows `fedplatform_oscap_findings_total{severity="high"}` counter has increased since the last scrape.

### Where to Look

1. Run `aide --check` and read the full diff output — it shows which attributes changed (hash, size, mtime) for each affected path
2. Check `/var/log/aide/aide.log` for the specific file and timestamp of detection
3. Run `rpm -V <package>` (if the file belongs to a package) to check whether the binary was replaced outside the package manager
4. Review recent command history on the host: `history | grep -E "cp|mv|chmod|install"`
5. Check systemd journal for the fedagent service around the time of the change: `journalctl -u fedagent --since "2 hours ago"`

### Expected Diagnosis

The break script modified a file in `/opt/fedtracker/` — either replacing the `fedagent` binary or changing a configuration file. AIDE detected the hash change on its next scheduled run. Investigation should identify the specific file, the change type, and whether it was authorized.

### Resolution Steps

After diagnosing: restore the original file, re-initialize AIDE baseline if necessary (`aide --update`), and document the root cause in your postmortem.

### Postmortem

Write your postmortem in `postmortems/INC-001-aide-detection-postmortem.md`. Cover:
- Timeline (when the change was made vs. when AIDE detected it)
- Root cause
- Detection gap (how long between change and detection)
- Resolution
- What would reduce detection latency in production (real-time auditd vs. daily AIDE cron)
