# Reusable Repo Structure Template

> Copy the prompt below and give it to any agent working on a new cloud project.
> Replace the placeholders with your project's details.

---

## Agent Prompt: Project Structure Convention

You are setting up a multi-phase cloud engineering portfolio project. Follow this structure exactly:

### Directory Layout

```
<project-name>/
├── phases/
│   ├── phase-1-<appname>-<theme>/
│   │   ├── terraform/           # IaC for this phase's infrastructure
│   │   ├── ansible/             # Config management
│   │   │   ├── playbooks/
│   │   │   ├── inventory/
│   │   │   ├── roles/
│   │   │   └── templates/
│   │   ├── app/                 # Application source code
│   │   ├── docker/              # Dockerfile, docker-compose
│   │   └── docs/
│   │       ├── implementation-guide.md
│   │       └── screenshots/     # Evidence for portfolio
│   ├── phase-2-<appname>-<theme>/
│   │   └── (same inner structure)
│   └── phase-3-<appname>-<theme>/
│       └── (same inner structure)
├── docs/                        # PROJECT-WIDE (spans all phases)
│   ├── ARCHITECTURE-DECISIONS.md
│   ├── LESSONS-LEARNED.md
│   ├── KNOWN-ISSUES.md
│   ├── PRD.md
│   └── plans/
├── tools/                       # Shared utilities (cost estimators, helpers)
├── .github/workflows/
├── README.md
├── .gitignore
└── .env.example
```

### Naming Conventions

**Phase folders:** `phase-<N>-<appname>-<theme>`
- Number for ordering
- App name for identity (e.g., fedtracker, cloudledger, sentinel-lab)
- Theme for the **unique skill** this phase demonstrates — NOT a generic category that applies to every phase

**Theme naming rules:**
- The theme must differentiate this phase from the others. If a skill appears in multiple phases (e.g., CI/CD, Terraform, Ansible), it is NOT a good theme.
- Good themes are specific to what makes this phase unique: `migration`, `dr-backup`, `gitops-security`
- Bad themes are generic categories: `cicd`, `infrastructure`, `automation`, `devops`
- 1-3 words max, hyphen-separated

**How to pick the right theme — ask yourself:**
> "If I removed the phase number, would someone still know which phase this is?"
> - `fedtracker-migration` — yes, only Phase 1 does migration
> - `fedcompliance-cicd` — no, all phases have CI/CD. What's unique? GitOps + supply chain security scanning
> - `fedcompliance-gitops-security` — yes, only Phase 3 does ArgoCD + Trivy + SBOM

**Examples (OCI Federal Lab):**
| Phase | App | Unique Skill | Folder Name |
|-------|-----|-------------|-------------|
| 1 | FedTracker | Legacy-to-cloud migration | `phase-1-fedtracker-migration` |
| 2 | FedAnalytics | Disaster recovery & backup | `phase-2-fedanalytics-dr` |
| 3 | FedCompliance | GitOps delivery + supply chain security | `phase-3-fedcompliance-gitops-security` |

**Examples across cloud providers:**
- `phase-1-cloudledger-migration` (AWS)
- `phase-2-cloudledger-ha-failover` (AWS — high availability, not just "backup")
- `phase-1-govmonitor-migration` (Azure)
- `phase-3-govmonitor-zero-trust` (Azure — specific security model, not "security")

**Implementation guides:** Always `implementation-guide.md` inside the phase's `docs/` folder (not in the root docs/).

**Deep dives / supplements:** Sibling files in the same `docs/` folder: `linux-admin-deep-dive.md`, `networking-deep-dive.md`, etc.

**Architecture decisions:** Single `ARCHITECTURE-DECISIONS.md` at root `docs/` level, reverse-chronological, ADR-NNN format.

### Rules

1. **Phase-first, tool-second** — group by phase, then by tool type inside each phase
2. **Project-wide docs at root `docs/`** — ADRs, lessons, known issues, PRD
3. **Phase-specific docs inside phase** — guides, screenshots, deep dives
4. **Shared tools at root `tools/`** — cost estimators, helper scripts
5. **Each phase is self-contained** — an interviewer can look at one phase folder and see everything
6. **No generic themes** — the theme must be unique to that phase. If a skill (CI/CD, Terraform, etc.) appears in every phase, it's NOT a good theme. Name the thing that makes this phase different.
7. **Screenshots per-phase** — evidence lives next to the guide it supports
8. **All commands in guides use full paths from repo root** — no ambiguity about working directory

### When creating a new phase

```bash
mkdir -p phases/phase-<N>-<appname>-<theme>/{terraform,ansible/{playbooks,inventory,roles,templates},app,docker,docs/screenshots}
```

Add `.gitkeep` to empty directories so they're tracked in git.
