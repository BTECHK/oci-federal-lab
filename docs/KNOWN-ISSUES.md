# Known Issues & Patterns

Errors encountered during implementation. Reference before starting new phases or guides.

Last updated: 2026-03-30

---

## OCI Console Bugs

- VCN wizard corrupts tags when compartment has tag defaults with user-applied values — wizard wipes values on retry and injects phantom freeform tag (`VCN = <timestamp>`) → use CLI instead
- Tag default values get wiped to blank on wizard retry even when entered correctly
- Compartment dropdown in other services (VCN, Compute) may not show new compartments for several minutes → hard refresh (F5) required

## Guide Command Errors

- `su - clouduser` fails with "Permission denied" because cloud users have no password set → must use `sudo su - clouduser` (uses opc's NOPASSWD sudo, not the target user's password)
- On OL9, `opc` is NOT in the `wheel` group (unlike OL8) — sudo access comes from `/etc/sudoers.d/90-cloud-init-users` instead
- **(RESOLVED — no longer applicable on OL9)** `pip3.11` / `pip3` could install packages to a different site-packages path than `python3` used. On OL9, the guide now uses the system `python3` (3.9) directly, so `python3 -m pip install` works without alternatives juggling.
- **(RESOLVED — no longer applicable on OL9)** `sudo alternatives --set python3 /usr/bin/python3.11` would fail if the alternatives entry didn't exist, and even when it worked it broke `firewall-cmd` and `semanage` (which depend on Python 3.9's `gi` module). The guide no longer installs python3.11 — OL9's system `python3` is used instead.
- clouduser sudoers drop-in scoped to `systemctl restart/status fedtracker` only blocks later guide steps that need broader sudo (dnf, pip, alternatives, tee, chown, firewall-cmd) → use `NOPASSWD:ALL` for lab, tighten with Ansible on Day 3
- Step 11.5 `terraform.tfvars` references `~/.ssh/fedtracker.pub` which is never created anywhere in the guide → use existing bastion `.pub` key or generate a new one. Guide needs explicit instructions.
- **(RESOLVED)** Step 11.5 previously said "Oracle Linux 8" but OL9 is now the standard — image OCID lookup instructions updated to specify OL9 + aarch64 for A1 Flex shape
- Step 11.5 `private_key_path = "~/.oci/oci_api_key.pem"` may not exist locally — OCI API key was created on the legacy-server (now destroyed). Need local API key setup instructions before Terraform.

## OCI Documentation vs Reality

- VCN resource navigation: Internet Gateways, NAT Gateways, Route Tables, Security Lists, and Subnets are **tabs** at the top of the VCN detail page (Gateways, Routing, Security, Subnets) — NOT items in the left sidebar as many guides/tutorials describe
- Tag Defaults nav: NOT at `Governance → Tag Defaults`. Actual path: `Identity → Compartments → [compartment] → Tag Defaults tab`
- Cost Analysis: tags are under **Add filter → Tag**, not the "Grouping dimensions" dropdown
- Quota policy names in OCI docs don't always match API (e.g., `blockstorage` vs `block-storage`, `objectstorage` vs `object-storage`)
- `#` comments are NOT valid in OCI Policy Builder or Quota Policy editor — causes parser error
- Quota policies are NOT IAM policies — they live at `Governance → Quota Policies`, not `Identity → Policies`
- Object storage quotas use bytes not GB (20 GB = 21474836480 bytes)
- API Keys nav differs between Identity Domains (new) and old IAM: **Identity Domains:** Profile → My profile → Tokens and keys tab → API keys. **Old IAM:** Profile → User Settings → scroll to API Keys. Most new tenancies use Identity Domains. The GenAI "Create API key" page is a completely different thing — don't confuse it with Identity API keys
- Oracle rebranded Autonomous Database → **Autonomous AI Database**. Nav path is now `Oracle AI Database → Autonomous AI Database` (not `Oracle Database → Autonomous Database`). The "Databases" menu item is for MySQL HeatWave, PostgreSQL, NoSQL — not ADB. Create button now says "Create Autonomous AI Database". "Deployment type: Shared Infrastructure" is gone (just "Serverless"). OCPU → ECPU. Always Free auto-locks ECPU + storage (fields disappear when toggled)

## Windows / SSH Gotchas

- WSL2 handles `chmod 600` natively — no workaround needed. If using PowerShell as a fallback, use `icacls` instead
- Notepad saves files as `.txt` by default — SSH config must be named `config` not `config.txt`
- SSH config location: `C:\Users\<username>\.ssh\config` (no extension)
- WSL2 is the recommended terminal for all local commands on Windows (SSH, Ansible, Terraform, git)
- PowerShell has ssh built-in but no chmod equivalent — use only for Windows-specific tasks (`wsl --install`, `icacls`)

## OCI Free Tier Limitations

- VM.Standard.A1.Flex capacity frequently unavailable in all ADs — retry at off-peak hours or use different ADs
- A1 Flex + Oracle Linux 8 combo may not be available → use Oracle Linux 9 (same commands, now the default)
- A1 Flex memory is 6 GB per OCPU (not arbitrary) — 1 OCPU = 6 GB, 2 OCPU = 12 GB
- Tag namespace doesn't appear in Cost Analysis filter for 24-48hrs after creation (needs cost data)
- E2.1.Micro (1 OCPU / 1 GB) is always available as fallback but very small

## Copy-Paste Issues

- Never use `\` line continuations when pasting into Cloud Shell — paste as single lines
- OCI quota policy comments (`#`) cause API errors — keep comments separate from statements
- Always paste CLI commands as single lines — multi-line paste from LLMs adds invisible characters
- When copying OCIDs from OCI Console, watch for trailing spaces
- **VS Code markdown preview adds invisible anchor artifacts to code blocks** — copying HCL/Terraform from the rendered preview (not the raw `.md`) produces broken syntax like `"tenancy_ocid" ">variable "tenancy_ocid" {`. Always copy from the raw code block, not the preview. This also applies to any heading-like pattern inside a fenced code block.

## Guide Continuity Gaps (Fixed)

- **Day 1 app code lost on server termination** — Step 6.2 committed code to a local git repo on the legacy-server but never pushed to remote. Steps 9.5, 12.8 (Ansible deploy), 14.2 (Docker build), and git commits on Days 3 and 5 all assumed `app/main.py` existed in the local `~/oci-federal-lab` repo. Fixed by adding SCP + git push instructions to Step 6.2 and a migration checkpoint between Day 1 and Day 2.
- **Step 14.4 references `ssh legacy-server`** but by Day 4 the legacy server has been terminated → changed to `ssh app-server` (matches guide's SSH config alias from Step 8.10)
- **Legacy server never explicitly terminated** — No step in the guide instructed users to terminate the legacy-server or legacy-vcn before Day 2. Users need the OCPU capacity. Added Step 8.0 for explicit teardown with deletion order guidance.
