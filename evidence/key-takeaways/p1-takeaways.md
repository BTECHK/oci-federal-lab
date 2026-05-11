# Phase 1 Key Takeaways — Interview Prep

**USER FILLS at end of Phase 1.** This file is your compressed interview prep — 3-5 bullets per category that you'd lead with when an interviewer asks about the project.

---

## Architecture Decisions (distilled from ADRs 012-016 + 019)

1. **ADR-012 — Pull vs push metrics:** _<fill in>_
2. **ADR-013 — Instance-principal CLI auth:** _<fill in>_
3. **ADR-014 — gRPC internal, REST external:** _<fill in>_
4. **ADR-015 — API Gateway vs direct exposure:** _<fill in (when P3 done)>_
5. **ADR-019 — IDCS as IdP (federal angle):** _<fill in>_

## Operational Lessons (from incidents + admin day P1)

1. _<fill in: e.g., AIDE detection caught a binary swap; the fix path matters more than the detection itself>_
2. _<fill in: e.g., systemd unit Type=notify vs simple — what notify gives you for orchestrated startup>_
3. _<fill in: e.g., SELinux denial debugging via ausearch + audit2allow workflow>_
4. _<fill in>_
5. _<fill in>_

## What I Would Do Differently at Scale

1. _<fill in: e.g., "at 100 hosts, Ansible-roll the OL9 hardening instead of manual; deploy via image bake (Packer)" >_
2. _<fill in: e.g., "production ADB tier with cross-region failover group, not just backup-and-restore" >_
3. _<fill in>_

## Strongest Stories For Interview (top 2-3)

1. **The INC-001 AIDE story:** _<fill in: symptom → diagnosis → fix → prevention script>_
2. **The 4-quadrant restructure decision:** _<fill in: single app per phase → Python+Go+serverless×2+CLI; why this teaches more reps>_
3. _<fill in: another strong story unique to your execution>_
