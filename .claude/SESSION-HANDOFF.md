# Session Handoff — OCI Federal Lab

**Last session:** 2026-03-25 (late evening EST)
**Branch:** `standardize-guides-sop`
**Operator:** Kyne Atekwana (btechk)

---

## Project Overview

3-phase OCI cloud engineering lab for Accenture Federal Services Cloud Engineer / Linux Admin interview preparation. Built on Oracle Cloud Free Tier (brother's account — tenancy: `afungtu`).

**Guides:** ~317 pages across 3 phases + Linux deep dive
**Repo:** https://github.com/BTECHK/oci-federal-lab

---

## Current State — Where We Left Off

### OCI Infrastructure Created
- [x] OCI Account (tenancy: `afungtu`, user: `a.fungtu@gmail.com`, operator: Kyne)
- [x] Compartment: `fedtracker-lab`
- [x] Tag namespace: `fedlab-cost` with 5 keys (project, phase, component, lifetime, owner)
- [x] Tag defaults on compartment: phase (user-applied), project (fedtracker), owner (user-applied)
- [x] Budget: `fedlab-monthly-budget` — $200/month, scoped to root
- [x] Quota policy: `fedlab-quota-limits` (with corrected OCI quota names)
- [x] VCN: `legacy-vcn` (10.0.0.0/16) — created via CLI due to wizard tag bug
  - [x] Internet Gateway
  - [x] NAT Gateway
  - [x] Service Gateway
  - [x] Default route table (→ Internet Gateway)
  - [x] Private route table (→ NAT Gateway)
  - [x] Public subnet (10.0.0.0/24)
  - [x] Private subnet (10.0.1.0/24)
- [x] VM: `legacy-server` — VM.Standard.A1.Flex, 1 OCPU / 8 GB, Oracle Linux 9, AD 2
  - Public IP configured
  - SSH key downloaded to `C:\Users\k_a_s\.ssh\oci-federal-lab\`
- [x] SSH config set up — `ssh legacy-server` works from PowerShell/Git Bash
- [x] VS Code Remote SSH ready (extension installed, config pointed at key)

### Phase 1 Guide Progress
- Steps 1.1-1.4 COMPLETE (account, cost setup, compartment, VCN, VM launch, SSH)
- Step 1.5 (SSH into VM) — CONNECTED, verified opc user, explored sudo config
- **Next step:** Continue with Phase 1 Linux admin deep dive (user management, firewalld, systemd, etc.)
- User was at the point of running `sudo su - clouduser` after we fixed the guide

### Guide Fixes Applied This Session (9 commits)
1. Budget/spending alerts step added (Step 1.2.1)
2. Cost protection: 6 critical issues fixed (tag nav, ordering, quota names, comments, field names)
3. VCN CLI alternative section added (workaround for wizard tag bug)
4. Compartment propagation delay note
5. VM shape/image updated (OL8→OL8/9, A1 Flex capacity warning, E2.1.Micro fallback)
6. Windows SSH instructions (icacls, config.txt warning, Git Bash, VS Code)
7. `su - clouduser` → `sudo su - clouduser` (12 occurrences)
8. Phase 2 SME review fixes (Jenkins CLI path, wrong directory, cpu_core_count deprecation)
9. Hardcoded PII replaced with generic placeholders

---

## Key OCIDs (for CLI commands)

| Resource | OCID |
|---|---|
| Tenancy | `ocid1.tenancy.oc1..aaaaaaaalgvdg3uyogmkrx6zvdxzat44quwrg7jxoynjk5q43rvm36vt4jra` |
| Compartment (fedtracker-lab) | `ocid1.compartment.oc1..aaaaaaaashs5zel3yuwrlxxhsnndqgye6gnz7xsdtw76sugmmszp5lm645ha` |
| VCN (legacy-vcn) | `ocid1.vcn.oc1.iad.amaaaaaaqm4dtgqajih7bejbm3myksfg5nye2ynh2reds7gpfe4qmg2vq6tq` |
| Internet Gateway | `ocid1.internetgateway.oc1.iad.aaaaaaaafth7lc32rn3amli73l55ptjnb2fpaz3xiwedabqio5b74wgrarea` |
| NAT Gateway | `ocid1.natgateway.oc1.iad.aaaaaaaakk2srlgu6blijcchaus65ftppk3n7orzn5kk5lktv7nrjz6zjfva` |
| Service Gateway | `ocid1.servicegateway.oc1.iad.aaaaaaaa42qhmfqxrccm6hudvz4xdmt7ipntj2rzp3lxeqxusuv36kyu4kfq` |
| Default Route Table | `ocid1.routetable.oc1.iad.aaaaaaaasn6ksthkqyu44d7gfvjmlsouzukg7fki6xfgxzr5bxt2pnpkv7tq` |
| Private Route Table | `ocid1.routetable.oc1.iad.aaaaaaaaj4h7mlnltsthyivi7zot3sum4koznrqyds7juwhwyda5mep3ne3a` |
| User (opc) | `ocid1.user.oc1..aaaaaaaat5njoofwdcumhaq5klt6yjfuna2rcips4mukp7gtdnbhmyfr4yna` |

---

## Outstanding Issues / TODO

### Not Yet Fixed in Guide
- [ ] Phase 2 content gap: Days 3-5 missing (AIDE, ransomware sim, DR drill, k3s, WORM storage)
- [ ] Phase 2: `datetime.now(timezone.utc).isoformat() + "Z"` double timezone suffix (7 lines)
- [ ] Phase 2: `$OCI_NAMESPACE` env var used in Jenkins pipeline but never defined
- [ ] Phase 2: Ansible `copy: src` relative paths warning
- [ ] Phase 3: Terraform `tcp_options` syntax error (will fail `terraform validate`)
- [ ] Security lists not customized (using VCN defaults) — need to open ports for SSH(22), app(8000), etc. when guide requires it
- [ ] DHCP options not customized (using VCN defaults — fine for now)
- [ ] Guide version divergence: GitHub vs OneDrive step numbering may still differ slightly

### To Revisit Later
- [ ] Cost Analysis tag filter: `fedlab-cost` namespace won't appear until tagged resources incur costs (24-48hr delay)
- [ ] A1 Flex capacity: may want to retry creating with 2 OCPU / 12 GB when capacity opens up
- [ ] Tag defaults causing wizard failures — consider removing tag defaults entirely and tagging via CLI/Terraform instead

---

## Important Context for Next Session

1. **The user is following the OneDrive copy of the guide** opened in browser (crossnote markdown preview). The GitHub copy is the source of truth — sync OneDrive after any changes.

2. **VM is Oracle Linux 9, not OL8** — guide was written for OL8. Most commands are identical. Key difference: sudo via `/etc/sudoers.d/90-cloud-init-users` instead of wheel group.

3. **VCN was created via CLI** (not wizard) due to tag default bug. All resources are tagged with `fedlab-cost` namespace.

4. **Windows user** — SSH via Git Bash or PowerShell, `icacls` instead of `chmod 600`, watch for `.txt` extension issues from Notepad.

5. **Brother's account** — tenancy `afungtu`, $200 budget set. Be mindful of costs.

6. **Interview is this week** — prioritize getting through the guide over perfecting documentation.

7. **Copy-paste into Cloud Shell** — ALWAYS provide commands as single lines, never use `\` line continuations. The user confirmed this causes issues.

8. **Reference files:**
   - `docs/KNOWN-ISSUES.md` — errors and patterns encountered
   - `docs/phase-1-implementation-guide.md` — main guide being followed
   - `.claude/SESSION-HANDOFF.md` — this file

---

## SSH Quick Reference

```
# From PowerShell or Git Bash:
ssh legacy-server

# Or explicitly:
ssh -i "C:\Users\k_a_s\.ssh\oci-federal-lab\oci-federal-lab.legacy-server.private-key.ssh-key-2026-03-25.key" opc@<PUBLIC_IP>

# Config file: C:\Users\k_a_s\.ssh\config
```

---

## File Sync Command

After any guide changes, sync GitHub → OneDrive:
```
cp "C:\Users\k_a_s\OneDrive\Desktop\github\oci-federal-lab\docs\phase-1-implementation-guide.md" "C:\Users\k_a_s\OneDrive\Desktop\Accenture Federal Services - Cloud Engineer - Linux Admin\Project ideas\oci-federal-lab\docs\phase-1-implementation-guide.md"
```
