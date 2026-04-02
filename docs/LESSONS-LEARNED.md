# Lessons Learned — Building Hands-On Cloud Lab Guides

Platform-agnostic checklist of mistakes and oversights discovered while building this OCI lab. Reference this before starting any new lab guide on any cloud platform (AWS, Azure, GCP, OCI).

Last updated: 2026-03-30

---

## 1. Artifact Persistence

**Rule:** Every `git init` must be followed by `git remote add` + `git push`. Local-only repos on throwaway VMs = code loss.

- **Why:** Day 1 committed app code to a local repo on a VM that was terminated on Day 2. Four downstream steps (Ansible deploy, Docker build, Day 3/5 git commits) assumed the code existed locally. It didn't.
- **Check:** Before any "tear down this server" step, verify: where does the code live? Is it pushed to a remote? Can it be retrieved on a fresh machine?

**Rule:** Map every artifact created → where it's consumed → how it survives the gap between servers/phases.

- **Why:** Service accounts, directories, pip packages, config files all existed on the Day 1 VM but not on the Day 2 VM. The guide skipped the provisioning step.
- **Check:** Create a dependency matrix: file name | created in step X | consumed in step Y | persistence mechanism.

---

## 2. Guide Command Accuracy

**Rule:** Test every command on a fresh VM as the exact user the guide specifies. Not your dev machine, not root.

- **Why:** `su - clouduser` fails on cloud-init VMs (no password set) — must use `sudo su - clouduser`. Found 12 occurrences. Works fine on author's machine but fails for every reader.
- **Check:** Spin up a fresh instance, follow the guide from scratch, note every failure.

**Rule:** Use `python3 -m pip install` (not bare `pip3`). Use `python3` to run scripts.

- **Why:** `pip3` may install to a different site-packages than `python3` reads. On OL9, use the system `python3` directly -- installing a separate python3.11 and using `alternatives` breaks system tools (firewall-cmd, semanage) that depend on Python 3.9's `gi` module.
- **Check:** After every pip install, verify with the SAME interpreter: `python3 -c "import <package>"`.

**Rule:** Never assume `alternatives --set` works — the alternative must be registered with `--install` first.

- **Why:** `sudo alternatives --set python3 /usr/bin/python3.11` failed with "No such file or directory" if no alternatives entry existed. (No longer relevant on OL9 since the guide now uses the system python3.)
- **Check:** Run `alternatives --display python3` before `--set` to verify the option is registered.

---

## 3. Console/UI Navigation

**Rule:** Cloud console UIs change without warning. Verify every nav path against the live console before publishing.

- **Why:** OCI rebranded "Autonomous Database" → "Autonomous AI Database". Nav path changed from `Oracle Database → Autonomous Database` to `Oracle AI Database → Autonomous AI Database`. Form fields changed (OCPU→ECPU, Deployment type removed, Always Free auto-locks fields).
- **Check:** Screenshot the actual UI at time of writing. Include the date in the guide.

**Rule:** Specify whether UI elements are tabs, sidebar items, or dropdown options — don't say "navigate to X" without saying where X is.

- **Why:** Internet Gateways, Route Tables, Security Lists are **tabs** at the top of the VCN detail page, not items in the left sidebar. Six guide sections had the wrong location.
- **Check:** For every "click X" instruction, include: where on the page (tab, sidebar, dropdown, button).

**Rule:** Document form fields that disappear based on other selections.

- **Why:** OCI Always Free toggle auto-locks ECPU and storage amounts — the fields disappear. Users think they need to set values that no longer exist.
- **Check:** Test the form with every toggle/checkbox combination.

---

## 4. Cross-Day / Cross-Phase Dependencies

**Rule:** Before writing "Day N+1", list every artifact Day N created that Day N+1 needs. Document the transfer mechanism.

- **Why:** Day 2 needed clouduser, Python 3, pip packages, /opt/fedtracker directory, and three .py files -- none of which existed on the new VM. The guide said "copy from legacy server (if you still have it)" but the legacy server was gone.
- **Check:** Create an explicit "Migration Checkpoint" between phases. Verify-then-destroy, not destroy-then-hope.

**Rule:** If phases are "independent", prove it — don't just claim it.

- **Why:** Phases claimed independence but shared knowledge prerequisites. Phase 2 assumes you understand Terraform (taught in Phase 1). Phase 3 assumes k3s knowledge (taught in Phase 2). This is fine, but must be documented as "knowledge prerequisite, not infrastructure prerequisite."
- **Check:** Can someone with the right knowledge start Phase N without having done Phase N-1? If yes, document what knowledge they need. If no, it's not independent.

---

## 5. Network Architecture Assumptions

**Rule:** Test connectivity FROM the actual subnet where the app runs, not from a bastion or public VM.

- **Why:** Private subnet couldn't reach Oracle ADB — it needed a Service Gateway (for Oracle Services Network), not just a NAT Gateway (for internet). Connection hung silently. The bastion could reach the internet fine, masking the private subnet's problem.
- **Check:** For every "connect to service X" step, verify: what route does the traffic take? NAT GW? Service GW? Internet GW? Does the route table have the right rule?

**Rule:** Security list/firewall rules must exist BEFORE the step that tests connectivity.

- **Why:** Guide had `curl <PUBLIC_IP>:8000` before the Security List ingress rule for port 8000 was created. Users hit a timeout and thought the app was broken.
- **Check:** For every `curl` or connectivity test, trace back: is the port open in the cloud security group AND the OS firewall?

---

## 6. OS / Platform Differences

**Rule:** Document the exact OS version and test on it. Different versions of the "same" OS have different behavior.

- **Why:** Oracle Linux 9 puts `opc` sudo access in `/etc/sudoers.d/90-cloud-init-users` instead of the `wheel` group (OL8). Same user, same cloud, different sudo mechanism.
- **Check:** Include `cat /etc/os-release` output in prerequisites. Note version-specific behavior in callout boxes.

**Rule:** Always provide the Windows equivalent for Unix commands that don't work in Git Bash.

- **Why:** `chmod 600 key.pem` does nothing in Git Bash on Windows. SSH fails silently with wrong permissions. Must use PowerShell `icacls` instead. Notepad saves files as `.txt` by default — SSH config must have no extension.
- **Check:** For every `chmod`, provide the `icacls` equivalent. For every file creation, warn about extensions.

---

## 7. Idempotency

**Rule:** Every script and manual step should be safe to re-run without side effects.

- **Why:** `cat >>` appends — if the user re-runs a step, the file content doubles. Python `__pycache__` bytecode cache lets the app keep running even after `chmod 000 main.py`, silently breaking troubleshooting exercises.
- **Check:** Use `cat >` for full file writes (overwrites). Use idempotency guards in scripts (`if ! command -v X; then install; fi`). Delete `__pycache__` when testing permission changes.

**Rule:** Heredoc delimiters must be unique across copy-paste blocks.

- **Why:** If two adjacent steps both use `EOF` as the delimiter, pasting them together closes the first heredoc early and the second block becomes a syntax error.
- **Check:** Use descriptive delimiters (`APPEOF`, `HEALTHEOF`, `SVCEOF`) to avoid collisions.

---

## 8. Documentation vs. Reality

**Rule:** Cloud provider documentation lags behind console changes. Verify everything against the live console.

- **Why:** OCI docs say `blockstorage` for quota policies, but the API uses `block-storage`. Comments (`#`) in quota policies cause parser errors despite being valid in other policy types.
- **Check:** Test every CLI command and console path at time of writing. Include the date.

**Rule:** Don't trust tutorials or guides written for older versions — verify the current state.

- **Why:** "Tag Defaults" nav path changed from `Governance → Tag Defaults` to `Identity → Compartments → [compartment] → Tag Defaults tab`. Multiple external guides have the old path.
- **Check:** Follow the guide step-by-step on a fresh account before publishing.

---

## 9. Copy-Paste from Rendered Docs

**Rule:** Code blocks in markdown guides must produce valid code when copied from ANY view — raw markdown, GitHub rendered, VS Code preview, IDE hover.

- **Why:** VS Code's markdown preview injects invisible anchor/tooltip HTML into fenced code blocks that look like headings. Copying HCL `variable "tenancy_ocid" {` from the preview produced `"tenancy_ocid" ">variable "tenancy_ocid" {` — completely broken syntax. The raw markdown was fine; the rendered view added artifacts.
- **Check:** Copy every code block from both the raw `.md` AND the rendered preview. Paste into the target file and verify it parses. If the guide is consumed via GitHub, also test GitHub's rendered markdown.

**Rule:** Use a consistent placeholder convention. `<DESCRIPTIVE_NAME>` for values the user fills in. No quotes around the brackets.

- **Why:** Mixed styles (`<YOUR_NAME>` vs `YOUR_ADMIN_PASSWORD_HERE` vs `<"YOUR_VALUE">`) confuse readers about what to replace and whether brackets/quotes are literal.
- **Check:** In shell/CLI commands and code blocks, use `<UPPERCASE_DESCRIPTIVE_NAME>` (e.g., `<COMPARTMENT_OCID>`, `<ADMIN_PASSWORD>`). In config files where angle brackets might conflict with syntax, use `YOUR_DESCRIPTIVE_NAME_HERE` without brackets. Pick one per context and be consistent.

---

## 10. Scaffold vs. Guide Consistency

**Rule:** If the repo is scaffolded with a directory structure upfront, the guide must acknowledge it — not silently recreate it with `mkdir -p`.

- **Why:** Initial scaffold created `terraform/environments/dev/`, `terraform/modules/`, `ansible/playbooks/`, `ansible/roles/` with `.gitkeep` placeholders. The guide then told users to `mkdir -p terraform/` and put files in flat `terraform/` — ignoring the pre-built `environments/dev/` structure. Users who cloned the repo saw one layout; the guide described a different one.
- **Check:** For every `mkdir -p` in the guide, verify: does this directory already exist in the repo scaffold? If yes, use the existing path. If the scaffold has subdirectories (like `environments/dev/`), direct users there instead of the parent. Add a conditional note: "Your repo already has this directory. If starting fresh, create it with `mkdir -p`."

---

## Pre-Flight Checklist (Scan Before Starting Any New Guide)

- [ ] Every `git init` has a corresponding `git push` to a remote
- [ ] Every "destroy this server" step has a "verify artifacts are saved" checkpoint before it
- [ ] Every command tested on a fresh VM as the correct user (not root, not author's machine)
- [ ] Every console nav path verified against the live UI with screenshots dated
- [ ] Every pip install uses `pythonX.Y -m pip install` (not `pip` or `pip3`)
- [ ] Every `chmod 600` has a Windows `icacls` alternative
- [ ] Every phase/day transition has a dependency matrix (what's needed, where it comes from)
- [ ] Every connectivity test has the firewall/security rules created BEFORE the test step
- [ ] OS version documented and version-specific behavior called out
- [ ] Scripts are idempotent (safe to re-run)
- [ ] Every `mkdir -p` in guide checked against repo scaffold — use existing paths, don't recreate
- [ ] Every code block tested by copying from rendered preview (not just raw markdown)
- [ ] Placeholder convention consistent: `<DESCRIPTIVE_NAME>` in commands, `YOUR_NAME_HERE` in config files
