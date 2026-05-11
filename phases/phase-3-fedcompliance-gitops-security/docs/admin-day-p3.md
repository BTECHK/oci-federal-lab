# Admin Day P3 — auditd + OpenSCAP + AIDE Deep + PAM + Kernel CVE Patch Sim

**Estimated effort:** ~6 focused hours (admin day) + ~3 focused hours (patch simulation drill).
**Goal:** Advanced compliance + security admin reps + the canonical "patch lifecycle" demonstration.

## Sections

### 1. auditd policy customization (60 min)

**Activities:**
- `/etc/audit/auditd.conf` — backlog, log rotation, action_mail_acct
- Custom rules in `/etc/audit/rules.d/`:
  - File access auditing: `-w /etc/passwd -p wa -k passwd_modify`
  - Syscall auditing: `-a always,exit -F arch=b64 -S execve -F uid>=1000 -F auid!=4294967295 -k command_exec`
  - User-session auditing: `-w /var/log/lastlog -p wa -k logins`
- `auditctl -l` to verify loaded rules
- `ausearch -k passwd_modify` to query the audit log for matched events
- Forward audit logs via plugin to remote syslog

📋 **EVIDENCE CHECKPOINT:**
- [ ] Your custom rules file → `docs/exercises/p3/configs/audit-rules-fedplatform.rules`
- [ ] auditctl -l → `docs/exercises/p3/command-outputs/p3-auditctl-list.txt`
- [ ] ausearch sample showing your rules catching activity → `docs/exercises/p3/command-outputs/p3-ausearch-sample.txt`

### 2. OpenSCAP profile authoring (60-90 min)

**Activities:**
- Run a baseline scan with stock OL9 STIG profile: `oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_stig --results stig-baseline.xml /usr/share/xml/scap/ssg/content/ssg-ol9-ds.xml`
- Open the resulting XML; identify rules that fail and rules that don't apply
- Write a **tailoring file** that adjusts profile (excludes rules that don't apply, modifies values for rules where lab vs prod differs)
- Re-scan with `--tailoring-file` and compare results
- Understand: XCCDF (the rules) vs OVAL (the checks) vs the report

📋 **EVIDENCE CHECKPOINT:**
- [ ] Baseline scan result → `docs/exercises/p3/configs/oscap-baseline.xml`
- [ ] Your tailoring file → `docs/exercises/p3/configs/oscap-tailoring.xml`
- [ ] Post-tailoring scan result → `docs/exercises/p3/configs/oscap-tailored.xml`
- [ ] Annotation on which rules you excluded and why → `docs/exercises/p3/admin-day-notes.md` (Section 2)

### 3. AIDE deep dive (45 min)

**Activities:**
- `/etc/aide.conf` — understand the macro language (file groups, rule combinations)
- Custom exclusions for volatile directories (logs, /tmp, /var/lib/containers/...)
- `aide --init` → initial baseline DB
- Schedule daily `aide --check` via systemd timer
- Test detection: modify a binary, run check, see the diff
- Re-baseline after authorized changes: `aide --update`

📋 **EVIDENCE CHECKPOINT:**
- [ ] Your aide.conf → `docs/exercises/p3/configs/aide.conf`
- [ ] Initial baseline (size, count of files) → `docs/exercises/p3/command-outputs/p3-aide-baseline.txt`
- [ ] Detection demo: file modified → aide --check output → `docs/exercises/p3/command-outputs/p3-aide-detection.txt`
- [ ] systemd timer for daily check → `docs/exercises/p3/configs/aide-check.timer`

### 4. PAM custom module configuration (45-60 min)

**Activities:**
- Pick ONE PAM module to deeply customize. Options:
  - `pam_pwquality` — password strength (minlen, dcredit, ucredit, lcredit, ocredit, etc.)
  - `pam_tally2` / `pam_faillock` — lockout after N failures
  - `pam_time` — restrict logins by time of day
- Modify `/etc/pam.d/system-auth` or `/etc/security/<config>.conf`
- Test: trigger the policy, observe denial, verify in audit log
- Document the security/usability tradeoff

📋 **EVIDENCE CHECKPOINT:**
- [ ] PAM config file → `docs/exercises/p3/configs/p3-pam-system-auth`
- [ ] Test trigger + denial trace → `docs/exercises/p3/command-outputs/p3-pam-test.txt`
- [ ] Audit log entry → `docs/exercises/p3/command-outputs/p3-pam-audit.txt`

### 5. Kernel CVE Patch Simulation (180 min, separate report)

**This is the canonical drill.** See `docs/exercises/p3/patch-simulation-report.md` for the full template.

Outline:
1. Capture pre-patch state (kernel version, uptime, app health, dnf history)
2. Plan the patch scenario (e.g., simulating CVE-2024-XXXX kernel patch)
3. Pre-reboot validation (run AIDE check, confirm no in-flight critical operations)
4. Execute `dnf update kernel`; observe install
5. Reboot orchestration (drain k8s if cluster, monitor with systemd-watchdog)
6. Post-reboot verification (new kernel running, AIDE clean, app healthy)
7. **Rollback drill** — force a "bad" kernel via `dnf history rollback`, verify recovery
8. Lessons + what'd you do differently at scale (Ansible orchestration, multi-host rolling, k8s drain coordination)

📋 **EVIDENCE CHECKPOINT:** all sections of `docs/exercises/p3/patch-simulation-report.md` filled in.

### 6. Wrap-up reflection (15 min)

Fill in `docs/exercises/p3/admin-day-notes.md` Key Takeaways section.

---

## Why this day matters

P3 is the "compliance + supply chain" phase. auditd + OpenSCAP + AIDE + PAM are the four pillars of Linux compliance monitoring. The patch simulation is the canonical "I can manage a production kernel patch with rollback" demonstration — this is what GovTech and federal hiring managers test for.
