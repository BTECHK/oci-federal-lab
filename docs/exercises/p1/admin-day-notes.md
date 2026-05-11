# Admin Day P1 — Reflection Notes

**Theme:** Linux deep (RHEL/Oracle Linux family) — sshd_config, sudoers, systemd units, journalctl, dnf, users/groups/ACLs, SELinux contexts.

**Date executed:** _<fill in>_

---

## What I did

_<fill in: chronological narrative of the admin day. What sections did you cover? What commands did you run? What did each section teach you?>_

## What broke during testing

_<fill in: every admin day surfaces something unexpected. What was it? How did you find it?>_

## How I debugged

_<fill in: the commands/log lines/strace output that led you to root cause>_

## What I'd do differently

_<fill in: at scale, with more time, with production constraints — what would change?>_

## Key Takeaways (interview prep — 5 bullets)

1. **Decision/Pattern:** _<fill in: e.g., "I hardened sshd with PermitRootLogin no + AllowGroups admins because..." >_
2. **Tool/Command:** _<fill in: e.g., "Used `ss -tunlp` over `netstat` because..." >_
3. **Subtle gotcha:** _<fill in: e.g., "SELinux contexts persist after chmod, must use restorecon, not chcon for...">_
4. **Real-world relevance:** _<fill in: e.g., "Federal compliance requires audit rules in /etc/audit/rules.d/, not just /etc/audit.rules because...">_
5. **At scale:** _<fill in: e.g., "For 100 hosts, I'd Ansible-roll this config; for 1000 I'd ship audit logs to a central WEC server before processing.">_
