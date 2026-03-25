# Known Issues & Patterns

Errors encountered during implementation. Reference before starting new phases or guides.

Last updated: 2026-03-25

---

## OCI Console Bugs

- VCN wizard corrupts tags when compartment has tag defaults with user-applied values — wizard wipes values on retry and injects phantom freeform tag (`VCN = <timestamp>`) → use CLI instead
- Tag default values get wiped to blank on wizard retry even when entered correctly
- Compartment dropdown in other services (VCN, Compute) may not show new compartments for several minutes → hard refresh (F5) required

## Guide Command Errors

- `su - clouduser` fails with "Permission denied" because cloud users have no password set → must use `sudo su - clouduser` (uses opc's NOPASSWD sudo, not the target user's password)
- On OL9, `opc` is NOT in the `wheel` group (unlike OL8) — sudo access comes from `/etc/sudoers.d/90-cloud-init-users` instead

## OCI Documentation vs Reality

- Tag Defaults nav: NOT at `Governance → Tag Defaults`. Actual path: `Identity → Compartments → [compartment] → Tag Defaults tab`
- Cost Analysis: tags are under **Add filter → Tag**, not the "Grouping dimensions" dropdown
- Quota policy names in OCI docs don't always match API (e.g., `blockstorage` vs `block-storage`, `objectstorage` vs `object-storage`)
- `#` comments are NOT valid in OCI Policy Builder or Quota Policy editor — causes parser error
- Quota policies are NOT IAM policies — they live at `Governance → Quota Policies`, not `Identity → Policies`
- Object storage quotas use bytes not GB (20 GB = 21474836480 bytes)

## Windows / SSH Gotchas

- `chmod 600` does NOT work in Git Bash on Windows — use `icacls` in PowerShell instead
- Notepad saves files as `.txt` by default — SSH config must be named `config` not `config.txt`
- SSH config location: `C:\Users\<username>\.ssh\config` (no extension)
- Git Bash is the best terminal for SSH on Windows (has ssh, supports Unix-style paths)
- PowerShell has ssh built-in but no chmod equivalent

## OCI Free Tier Limitations

- VM.Standard.A1.Flex capacity frequently unavailable in all ADs — retry at off-peak hours or use different ADs
- A1 Flex + Oracle Linux 8 combo may not be available → Oracle Linux 9 works fine (same commands)
- A1 Flex memory is 6 GB per OCPU (not arbitrary) — 1 OCPU = 6 GB, 2 OCPU = 12 GB
- Tag namespace doesn't appear in Cost Analysis filter for 24-48hrs after creation (needs cost data)
- E2.1.Micro (1 OCPU / 1 GB) is always available as fallback but very small

## Copy-Paste Issues

- Never use `\` line continuations when pasting into Cloud Shell — paste as single lines
- OCI quota policy comments (`#`) cause API errors — keep comments separate from statements
- Always paste CLI commands as single lines — multi-line paste from LLMs adds invisible characters
- When copying OCIDs from OCI Console, watch for trailing spaces
