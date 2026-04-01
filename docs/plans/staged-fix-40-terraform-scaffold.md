# Fix #40 — Terraform/Ansible Paths Must Match Repo Scaffold

## The Problem

The repo was scaffolded in the initial commit (`89be6a6`, March 22 2026) with this structure:

```
terraform/
├── environments/
│   ├── dev/.gitkeep
│   └── prod/.gitkeep
└── modules/.gitkeep

ansible/
├── inventory/.gitkeep
├── playbooks/.gitkeep
└── roles/.gitkeep
```

The implementation guide ignores this scaffold and tells users to create flat directories:

- **Step 11.2** says `mkdir -p ~/oci-federal-lab/terraform` then puts `.tf` files directly in `terraform/`
- **Step 12** says `mkdir -p ~/oci-federal-lab/ansible` and `ansible/playbooks`

This means the pre-created `environments/dev/`, `environments/prod/`, and `modules/` folders sit empty and unused while `.tf` files go in the wrong place.

## What to Change

### Terraform (Step 11.2 and all of Steps 11.3-11.9)

**Step 11.2 — Change directory creation:**

FROM:
```bash
mkdir -p ~/oci-federal-lab/terraform
cd ~/oci-federal-lab/terraform
```

TO:
```bash
# Your repo already has terraform/environments/dev/ from the initial scaffold.
# If it doesn't exist, create it:
mkdir -p ~/oci-federal-lab/terraform/environments/dev
cd ~/oci-federal-lab/terraform/environments/dev
```

Add context note after:
> **Why `environments/dev/`?** Real teams separate Terraform configurations by environment (dev, staging, prod). Your repo was scaffolded with this structure. We'll build all Day 2 infrastructure in `dev/`. Later you could create a `prod/` environment with different variable values (larger instances, stricter security groups) using the same `.tf` files.

**Steps 11.3-11.9 — Update all file paths:**

Every reference to `terraform/provider.tf`, `terraform/variables.tf`, `terraform/network.tf`, `terraform/compute.tf`, `terraform/outputs.tf` becomes:
- `terraform/environments/dev/provider.tf`
- `terraform/environments/dev/variables.tf`
- `terraform/environments/dev/network.tf`
- `terraform/environments/dev/compute.tf`
- `terraform/environments/dev/outputs.tf`

Every `cd ~/oci-federal-lab/terraform` becomes `cd ~/oci-federal-lab/terraform/environments/dev`

**Day 3 git commit (line ~5669):**
```bash
git add terraform/ ansible/ app/
```
This still works — `git add terraform/` recursively adds everything under it, including `environments/dev/`. No change needed here.

### Ansible (Steps 12.x)

**Step 12.1 — Change directory creation:**

FROM:
```bash
mkdir -p ~/oci-federal-lab/ansible
mkdir -p ~/oci-federal-lab/ansible/playbooks
```

TO:
```bash
# Your repo already has ansible/playbooks/ and ansible/roles/ from the initial scaffold.
# If they don't exist, create them:
mkdir -p ~/oci-federal-lab/ansible/playbooks
mkdir -p ~/oci-federal-lab/ansible/roles
cd ~/oci-federal-lab/ansible
```

The `ansible/inventory/` folder from the scaffold maps to where `inventory.ini` goes. Playbooks go in `ansible/playbooks/`. Templates can go in `ansible/templates/` (create if needed — wasn't in the scaffold).

**Step 12 inventory file path:**

FROM: `~/oci-federal-lab/ansible/inventory.ini`
TO: `~/oci-federal-lab/ansible/inventory/inventory.ini` (uses the pre-created `inventory/` folder)

OR keep it at `ansible/inventory.ini` if simpler — the `inventory/` folder can hold multiple inventory files later.

### Conditional mkdir Pattern

For every `mkdir -p` in the guide, use this pattern:

```markdown
> Your repo already has this directory from the initial scaffold. If starting fresh or it doesn't exist:
> ```bash
> mkdir -p path/to/directory
> ```
```

This handles both cases: users who cloned the scaffold AND users starting from scratch.

## Files to Modify

- `docs/phase-1-implementation-guide.md` — Steps 11.2-11.9 (Terraform paths), Steps 12.x (Ansible paths)
- `docs/phase-2-implementation-guide.md` — Check if same pattern exists
- `docs/phase-3-implementation-guide.md` — Check if same pattern exists

## Why This Matters

1. **Interview relevance:** `terraform/environments/dev/` shows you understand environment separation — a real-world pattern interviewers look for
2. **Repo consistency:** The scaffold tells a story about project organization. Empty unused folders undermine that story.
3. **No wasted work:** The scaffold was created intentionally per the design doc (`docs/plans/2026-03-18-interview-lab-project-design.md`, lines 703-747). The guide should use what's already there.

## Design Document Reference

The folder structure was specified in `docs/plans/2026-03-18-interview-lab-project-design.md` under "DELIVERABLES PER PHASE" (lines 703-747). The scaffold was created in the initial commit to match this spec.
