# Admin Day P1 — Linux Deep (RHEL / Oracle Linux family)

**Estimated effort:** ~6 focused hours (one full admin day).
**Goal:** Build muscle memory on Linux fundamentals that surfaced as a gap in recent interview. Don't optimize for finishing fast — optimize for the reps.

## Sections (sequenced)

### 1. sshd_config hardening (45-60 min)

Walk through every line of a hardened sshd_config and understand WHY each line is there. Reference: CIS Benchmark for OL9, sections 5.2.x.

**Activities:**
- Read and annotate the entire sshd_config in `evidence/admin/p1/configs/sshd_config-hardened`
- Apply: PermitRootLogin no, PasswordAuthentication no (after confirming key-based works!), Ciphers (modern only), MACs (modern only), KexAlgorithms (modern only), MaxAuthTries 4, ClientAliveInterval 300, ClientAliveCountMax 0, AllowGroups <restrict>, LoginGraceTime 60, UseDNS no
- Test: `sshd -t` for syntax, `sshd -T | grep -i <option>` for runtime values

📋 **EVIDENCE CHECKPOINT:**
- [ ] Hardened sshd_config → `evidence/admin/p1/configs/sshd_config-hardened`
- [ ] `sshd -T` output → `evidence/admin/p1/command-outputs/p1-sshd-runtime.txt`
- [ ] Notes on each non-default setting and why → `evidence/admin/p1/admin-day-notes.md` (Section 1)

### 2. sudoers + privilege management (30-45 min)

**Activities:**
- Create `/etc/sudoers.d/fedplatform-admins` with explicit user + command grants
- Use NOPASSWD sparingly; understand the security tradeoff
- Test: `sudo -l -U <user>` shows expected grants
- Test: attempt unauthorized command, expect denied + audit entry
- Audit: `journalctl _COMM=sudo` shows the denied attempt

📋 **EVIDENCE CHECKPOINT:**
- [ ] sudoers.d file → `evidence/admin/p1/configs/sudoers.d-fedplatform-admins`
- [ ] `sudo -l -U <test-user>` → `evidence/admin/p1/command-outputs/p1-sudoers-test.txt`
- [ ] journalctl entry for denied sudo → `evidence/admin/p1/command-outputs/p1-sudoers-deny.txt`

### 3. systemd unit authoring (45-60 min)

**Activities:**
- Write a custom systemd unit for fedtracker-app (Type=notify, After=network-online.target, restart policy, resource limits)
- Use drop-in: `/etc/systemd/system/fedtracker.service.d/override.conf` for env vars
- Understand: After= vs Requires= vs Wants=, Type=notify vs simple vs forking, Restart= options
- Test: `systemctl daemon-reload`, start, status, stop, restart, enable
- Test: introduce a deliberate config error, observe systemctl status output, debug

📋 **EVIDENCE CHECKPOINT:**
- [ ] systemd unit file → `evidence/admin/p1/configs/fedtracker.service`
- [ ] systemctl status output (healthy) → `evidence/admin/p1/command-outputs/p1-fedtracker-systemctl.txt`
- [ ] systemctl status output (intentional failure mode) → `evidence/admin/p1/command-outputs/p1-fedtracker-systemctl-failed.txt`

### 4. journalctl deep querying (30 min)

**Activities:**
- Query by unit, priority, time range, boot
- Persistent storage: confirm `/var/log/journal/` exists, query across reboots
- Filter: `journalctl -u fedtracker -p err --since "1 hour ago"`
- Follow: `journalctl -u fedtracker -f` (then leave running, generate test traffic)
- Export: structured JSON with `-o json` for tooling consumption

📋 **EVIDENCE CHECKPOINT:**
- [ ] 5-10 useful journalctl query examples with output → `evidence/admin/p1/command-outputs/p1-journalctl-queries.txt`

### 5. dnf hands-on (30-45 min)

**Activities:**
- `dnf history` — every change to your package state, with rollback capability
- `dnf history rollback <transaction-id>` — actually rollback (test on a test package first)
- Repo priorities: `/etc/yum.repos.d/`, priority= directive, why ordering matters
- GPG keys: `dnf info <pkg>` shows signing key; reject unsigned
- dnf modules: `dnf module list nodejs`, switch streams

📋 **EVIDENCE CHECKPOINT:**
- [ ] `dnf history list` → `evidence/admin/p1/command-outputs/p1-dnf-history.txt`
- [ ] Rollback experiment trace → `evidence/admin/p1/command-outputs/p1-dnf-rollback.txt`

### 6. Users / groups / ACLs (30 min)

**Activities:**
- Primary group vs supplementary groups; `id <user>`, `groups <user>`, `getent group <name>`
- POSIX ACLs: `getfacl <file>`, `setfacl -m u:alice:r-- <file>`, default ACLs on directories
- Understand: when traditional u/g/o is enough, when ACLs are needed (multi-tenant directories)

📋 **EVIDENCE CHECKPOINT:**
- [ ] Demo file with ACLs applied: `getfacl` output → `evidence/admin/p1/command-outputs/p1-acl-demo.txt`

### 7. SELinux contexts (45 min)

**Activities:**
- `getenforce`, `setenforce 0` (temporarily for testing), `sestatus`
- `ls -Z`, `ps -Z`, `id -Z`
- `chcon` for one-off, `restorecon` to restore from policy, `semanage fcontext` to make persistent
- Practice: relocate fedtracker logs to non-standard path, observe denial, fix with semanage + restorecon
- audit2allow workflow: `ausearch -m avc | audit2allow -M mypol`

📋 **EVIDENCE CHECKPOINT:**
- [ ] Initial SELinux denial → `evidence/admin/p1/command-outputs/p1-selinux-denial.txt`
- [ ] semanage + restorecon resolution → `evidence/admin/p1/command-outputs/p1-selinux-fix.txt`
- [ ] audit2allow output for the policy module created → `evidence/admin/p1/configs/p1-selinux-mypol.te`

### 8. Wrap-up reflection (15 min)

Fill in `evidence/admin/p1/admin-day-notes.md` Key Takeaways section with 5 bullets.

---

## Bonus (if time allows)

- AIDE custom rule set in `/etc/aide.conf`; rebuild baseline; test detection
- Set up `auditd` with a custom rule in `/etc/audit/rules.d/`; trigger and search via `ausearch`
- Cron vs systemd timers — write the same task both ways, compare reliability

---

## Why this day matters

Linux/Docker basics surfaced as an interview gap. This day is the muscle-memory builder. The activities here are the canonical "junior interview" content; the reps make them automatic so under L6 interview pressure they're not the part that takes thought.
