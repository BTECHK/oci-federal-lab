# Phase 1 — FedTracker Migration (Linux Admin Foundation)

**Public phase guide.** This is the shareable, tracked walkthrough of Phase 1. For the detailed local working notes, see `implementation-guide.md` (gitignored).

**Estimated effort:** ~48-54 focused hours (1 day = ~6 hours focused work).

---

## Phase Theme

Migrate a legacy on-prem application to OCI: hardened Oracle Linux VM, immutable audit log in Oracle ADB, Object Storage integration, OCI Functions for event-driven processing. Foundation for the compliance + DR + supply-chain work in P2 and P3.

## Architecture (end of phase)

```
External users → OCI Bastion (public subnet)
                 ↓ SSH (admin only)
                 → App Server VM (private subnet, hardened OL9)
                   ├── FedTracker API (FastAPI :8000)
                   ├── FedAgent (Go Prometheus exporter :9100)
                   └── fedplatform-cli (operator tool)
                 ↓
                 → Oracle ADB (Always Free)
                 → OCI Object Storage (audit-evidence, processed, artifacts)
                 → OCI Functions (audit-processor Py, health-checker-go)
                 → OCI Events (object-create + timer triggers)
```

Auth: OCI Identity Domains (IDCS) issues OAuth2 + JWT. API Gateway (added in P3) validates JWT statelessly via JWKS. API key for quota tracking (separate concern). gRPC mTLS + JWT-in-metadata between fedtracker-app and fedagent. (ADR-019.)

## Phase 1 Building Blocks

| Component | Status | Location |
|---|---|---|
| FedTracker API (Python) | scaffold + answers/ + migrated working code | `fedtracker-app/` |
| FedAgent (Go) | scaffold + answers/ | `fedagent/` |
| fedplatform-cli | scaffold + answers/ | `fedplatform-cli/` |
| audit-processor function (Py) | scaffold + answers/ | `functions/python/audit-processor/` |
| health-checker function (Go) | scaffold + answers/ | `functions/go/health-checker-go/` |
| ADRs 012-016 (foundational) | committed | `adrs/` |
| ADR-019 (IDCS) | committed (this addendum) | `adrs/ADR-019-idcs-vs-oauth-self-host.md` |

## Sequenced Steps (each with EVIDENCE CHECKPOINT)

### Step 1 — VCN + subnet provisioning

Provision the network layer via Terraform at `phases/phase-1-fedtracker-migration/terraform/network.tf`.

📋 **EVIDENCE CHECKPOINT** (commit to `docs/exercises/p1/`):
- [ ] `terraform plan` output → save as `docs/exercises/p1/command-outputs/p1-tf-network-plan.txt`
- [ ] `oci network vcn get --vcn-id <id>` → `docs/exercises/p1/command-outputs/p1-vcn-state.json`
- [ ] Screenshot of OCI console showing VCN topology → `docs/exercises/p1/screenshots/p1-vcn-topology.png`
- [ ] Update `docs/exercises/p1/admin-day-notes.md` with what surprised you

### Step 2 — App Server VM provisioning + Linux hardening

Stand up the App Server VM, harden per CIS Benchmark for OL9, install OpenSCAP + AIDE + fail2ban.

📋 **EVIDENCE CHECKPOINT**:
- [ ] Hardened sshd_config → `docs/exercises/p1/configs/sshd_config-hardened`
- [ ] `sshd -T` runtime config → `docs/exercises/p1/command-outputs/p1-sshd-runtime.txt`
- [ ] `sudo -l -U <user>` for test user → `docs/exercises/p1/command-outputs/p1-sudoers-test.txt`
- [ ] OpenSCAP baseline scan result → `docs/exercises/p1/configs/oscap-baseline.xml`
- [ ] AIDE init output → `docs/exercises/p1/command-outputs/p1-aide-init.txt`
- [ ] Screenshot of fail2ban status → `docs/exercises/p1/screenshots/p1-fail2ban-status.png`

### Step 3 — Oracle ADB provisioning + schema

Provision ADB Always Free. Write your DDL (see `database/`).

📋 **EVIDENCE CHECKPOINT**:
- [ ] ADB connection test via sqlplus / Python → `docs/exercises/p1/command-outputs/p1-adb-connect.txt`
- [ ] Your DDL committed under `database/schemas/`
- [ ] Your design rationale in `docs/architecture/database-design.md`
- [ ] Run `database/seed/generate.py` to populate test data
- [ ] EXPLAIN ANALYZE output for one key query → `docs/benchmarks/database/personnel-by-id-baseline.txt`
- [ ] Update `docs/benchmarks/database/personnel-by-id-annotation.md` with the query plan analysis

### Step 4 — FedTracker app deployment via Ansible

Deploy fedtracker-app from `answers/` to VM via Ansible playbooks.

📋 **EVIDENCE CHECKPOINT**:
- [ ] Ansible playbook run output → `docs/exercises/p1/command-outputs/p1-ansible-deploy.txt`
- [ ] curl GET /health/deep with annotated JSON → `docs/exercises/p1/command-outputs/p1-health-deep.json`
- [ ] systemctl status fedtracker → `docs/exercises/p1/command-outputs/p1-fedtracker-systemctl.txt`

### Step 5 — FedAgent + Prometheus scraping

Compile + deploy fedagent, configure local Prometheus to scrape :9100.

📋 **EVIDENCE CHECKPOINT**:
- [ ] go build output → `docs/exercises/p1/command-outputs/p1-fedagent-build.txt`
- [ ] curl localhost:9100/metrics → `docs/exercises/p1/command-outputs/p1-fedagent-metrics.txt`
- [ ] Screenshot of Grafana panel showing OpenSCAP score → `docs/exercises/p1/screenshots/p1-grafana-oscap.png`

### Step 6 — OCI Functions deployment

Deploy audit-processor and health-checker-go, wire OCI Events triggers.

📋 **EVIDENCE CHECKPOINT**:
- [ ] `fn deploy --app fedplatform` output → `docs/exercises/p1/command-outputs/p1-fn-deploy.txt`
- [ ] OCI Events rule list → `docs/exercises/p1/command-outputs/p1-events-rules.json`
- [ ] Test invocation: upload audit CSV, observe function output → `docs/exercises/p1/command-outputs/p1-audit-flow-trace.txt`

### Step 7 — IDCS OAuth + JWT auth wiring

Configure OCI Identity Domain app per ADR-019. Wire `fedtracker-app/auth.py` (scaffold) to validate JWTs.

📋 **EVIDENCE CHECKPOINT**:
- [ ] IDCS app config exported (no secrets) → `docs/exercises/p1/configs/idcs-app-config.json`
- [ ] curl with Bearer token: GET /personnel → expect 200 → `docs/exercises/p1/command-outputs/p1-auth-success.txt`
- [ ] curl WITHOUT Bearer token → expect 401 → `docs/exercises/p1/command-outputs/p1-auth-rejected.txt`

### Step 8 — Admin Day P1 (Linux deep)

Execute the dedicated Linux admin day per `admin-day-p1.md`. This is the rep-building day — not optional.

📋 See `admin-day-p1.md` for the full step list and EVIDENCE CHECKPOINTS.

### Step 9 — CI scanning baseline

Enable CodeQL + Dependabot + Trivy multi-scanner + Checkov in GitHub Actions.

📋 **EVIDENCE CHECKPOINT**:
- [ ] `.github/workflows/ci.yml` committed
- [ ] `.github/dependabot.yml` committed
- [ ] Screenshot of GitHub Security tab showing scans active → `docs/exercises/p1/screenshots/p1-ci-security-tab.png`

### Step 10 — INC-001 simulation + postmortem

Run the AIDE detection break per `phases/phase-1-fedtracker-migration/INCIDENTS.md`. Write the postmortem.

📋 **EVIDENCE CHECKPOINT**:
- [ ] AIDE detection output → `docs/exercises/p1/command-outputs/p1-aide-detection.txt`
- [ ] Your postmortem → `phases/phase-1-fedtracker-migration/postmortems/INC-001-aide-tamper.md`

---

## Phase 1 Key Takeaways (interview prep)

_<USER FILLS at end of phase — see `docs/retrospectives/p1-takeaways.md` for the consolidated format>_

1. **Linux hardening:** _<your top decision + rationale>_
2. **ADB design:** _<your schema decision + rationale>_
3. **gRPC + JWT:** _<the layered auth model you implemented>_
4. **INC-001 lesson:** _<what AIDE detection taught you about file integrity monitoring>_
5. **At scale:** _<what you'd change at 100 hosts / multi-region / production-tier ADB>_
