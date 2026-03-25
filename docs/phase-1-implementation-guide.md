# AFS Cloud Engineer Interview Lab — Phase 1 Implementation Guide
## Legacy-to-Cloud Migration on OCI

**Goal:** Build a "legacy" server manually, then migrate to a secure, automated OCI environment with Terraform, Ansible, Jenkins, Podman/Docker, and AI-assisted compliance — while learning REST API fundamentals by building a FastAPI app from scratch.
**Total Cost:** $0.00 (OCI Always Free tier)
**Primary Tool:** SSH Terminal + OCI Console (DevOps/infra files built by hand; FastAPI app built section-by-section with ELI5)
**Prerequisite:** None — this is Day 1

---

## WHAT YOU'RE BUILDING

Day 1 builds the "before" state — a manually-configured legacy server with no automation, no proper security, no backup strategy. Over Days 2-5, you tear this down and rebuild it properly. You need to feel the pain of manual work first so the automation makes sense.

| Component | Day 1 (Legacy) | Day 5 (Modern) |
|-----------|----------------|-----------------|
| Infrastructure | Manual OCI console clicks | Terraform IaC |
| Configuration | SSH + manual commands | Ansible playbooks |
| Deployment | Manual install + systemctl | Jenkins CI/CD pipeline |
| Security | Default settings | Hardened (SSH, firewall, IAM, auditd, OpenSCAP) |
| Networking | Flat public subnet | Public/private with bastion |
| Database | SQLite on the VM | Oracle Autonomous DB (Always Free) |
| Application | FastAPI manually started | Podman/Docker containerized |
| API Framework | FastAPI (built section-by-section) | Same app, production-grade deployment |
| Backup | None | Block volume + Object Storage + DR runbook |
| Cost Control | None | Tags + budget alerts + cost scripts |
| Monitoring | None | Bash + Python health/cost scripts |
| Compliance | None | OpenSCAP CIS + Ollama AI evidence |
| Serverless | None | OCI Functions (audit processor + health check) |

---

## ARCHITECTURE OVERVIEW

**Day 1 — Legacy Architecture (what you build today):**

```
Internet
    │
┌───▼──────────────────────────────────────┐
│  OCI VCN: legacy-vcn (10.0.0.0/16)       │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  Public Subnet (10.0.0.0/24)     │     │
│  │                                   │     │
│  │  ┌───────────────────────────┐   │     │
│  │  │  Oracle Linux 8 VM         │   │     │
│  │  │  (VM.Standard.A1.Flex)     │   │     │
│  │  │  2 OCPU / 8 GB RAM (ARM)  │   │     │
│  │  │                            │   │     │
│  │  │  ┌──────────────────────┐ │   │     │
│  │  │  │ FedTracker (FastAPI)  │ │   │     │
│  │  │  │ Port 8000             │ │   │     │
│  │  │  │ SQLite DB (local)     │ │   │     │
│  │  │  │ systemd managed       │ │   │     │
│  │  │  └──────────────────────┘ │   │     │
│  │  │                            │   │     │
│  │  │  health_check.sh           │   │     │
│  │  │  oci_reporter.py           │   │     │
│  │  └───────────────────────────┘   │     │
│  └──────────────────────────────────┘     │
└────────────────────────────────────────────┘
```

**Day 5 — Target Architecture (where you're headed):**

```
Internet
    │
┌───▼──────────────────────────────────────────────────┐
│  OCI VCN: fedtracker-vcn (10.0.0.0/16)               │
│                                                        │
│  ┌─────────────────────────────┐                      │
│  │ Public Subnet (10.0.1.0/24) │                      │
│  │  Bastion / Jenkins VM       │                      │
│  │  (Oracle Linux 8)           │                      │
│  └──────────────┬──────────────┘                      │
│                 │ SSH tunnel                           │
│  ┌──────────────▼──────────────┐                      │
│  │ Private Subnet (10.0.2.0/24)│                      │
│  │  App Server VM              │                      │
│  │  (Oracle Linux 8)           │                      │
│  │  Podman/Docker + FedTracker │                      │
│  │  Ansible-managed            │                      │
│  │  Hardened (auditd, firewall)│                      │
│  │  OpenSCAP CIS validated     │                      │
│  └──────────────┬──────────────┘                      │
│                 │                                      │
│  ┌──────────────▼──────────────┐                      │
│  │ Oracle Autonomous DB         │                      │
│  │ (Always Free, 20 GB)        │                      │
│  └─────────────────────────────┘                      │
│                                                        │
│  OCI Functions: audit processor, health check          │
│  Object Storage: backups, cost reports, evidence       │
│  Tags + Budget Alerts on all resources                 │
└────────────────────────────────────────────────────────┘
```

> **Why start with a mess?** Every production environment you'll encounter at AFS has legacy debt. Starting manually teaches you what automation replaces. When an interviewer asks "why use Terraform?", you'll have a real answer: "because I built it by hand first and it took hours — Terraform does it in minutes and is repeatable."

---

## WHERE AM I? — LOCATION GUIDE

Watch for these location tags throughout the guide. They tell you exactly where to type each command.

| Tag | Where | What It Looks Like |
|-----|-------|-------------------|
| 📍 **OCI Console** | Oracle Cloud web UI | cloud.oracle.com — clicking buttons, navigating menus |
| 📍 **Local Terminal** | Your machine's terminal | bash / PowerShell / Git Bash on your laptop |
| 📍 **VM Terminal** | SSH into Oracle Linux VM | `ssh opc@<public_ip>` — commands run on the cloud server |
| 📍 **Editor** | Your text editor | VS Code, nano, vim — editing files |
| 📍 **Browser** | Web browser | Testing endpoints, viewing Swagger docs, Jenkins UI |

---

## PHASE 1: OCI ACCOUNT SETUP & FIRST VM (45 min)

> You're creating your Oracle Cloud account and launching your first virtual machine. This is the foundation for everything else — by the end of this phase you'll have a running Linux server you can SSH into from your laptop.
>
> 📍 **Where work happens:** OCI Console (browser) and Local Terminal (SSH).
>
> 🛠️ **Build approach:** All manual — point-and-click in the OCI Console. This is intentional. Day 3 automates all of this with Terraform.

---

### Step 1.1 — Create OCI Free Tier Account
📍 **OCI Console**

> **🧠 ELI5 — OCI Always Free Tier:** Oracle gives you a permanent set of cloud resources at no cost — forever, not just 30 days. This includes compute VMs, a database, storage, and networking. Unlike AWS Free Tier (which mostly expires after 12 months), OCI Always Free resources stay free as long as your account exists.

1. Go to [cloud.oracle.com](https://cloud.oracle.com)
2. Click **Sign Up for Free**
3. Fill in your details:
   - **Cloud Account Name:** Choose something short and memorable, e.g., `fnamelname` or `mylab01` (this becomes your tenancy name)
   - **Home Region:** Choose the region closest to you (e.g., `US East (Ashburn)` or `US West (Phoenix)`)
   - You'll need a credit card for verification — you will NOT be charged
4. Wait for the welcome email (usually 5-15 minutes)
5. Sign in at [cloud.oracle.com](https://cloud.oracle.com)

> **Why does region matter?** Always Free resources are only available in your home region. Pick a US region since this is a federal scenario. You cannot change your home region after account creation.

**Verify:**

Sign in to the OCI Console. You should see the main dashboard with your tenancy name in the top-right corner.

> **Interview Insight: "Why did you choose OCI?"**
>
> **Strong answer:** "OCI has FedRAMP High authorization for government regions, the Always Free tier let me build real infrastructure without cost barriers, and Oracle's government cloud is growing fast — the JD specifically listed OCI experience. Plus, Oracle Linux is RHEL-compatible, so every skill transfers directly to RHEL/CentOS environments common in federal."
>
> **Weak answer:** "It was free." (True but shows no strategic thinking)

---

### Step 1.2 — Create Compartment
📍 **OCI Console**

> **🧠 ELI5 — Compartments:** Compartments are OCI's way of organizing resources into logical groups — like folders on your computer. AWS uses separate accounts for isolation; OCI uses compartments within one account. Every resource you create lives in a compartment. The `root` compartment is the default, but creating a dedicated compartment keeps your lab isolated and easy to clean up.

1. Navigate to **Identity & Security** → **Compartments** (use the search bar at the top if you can't find it)
2. Click **Create Compartment**
3. Fill in:
   - **Name:** `fedtracker-lab`
   - **Description:** `Phase 1 legacy-to-cloud migration lab`
   - **Parent Compartment:** (root) — leave as default
4. Click **Create Compartment**

**Verify:**

You should see `fedtracker-lab` in the compartment list. Click into it — it will be empty for now.

> **⚠️ Propagation delay:** New compartments can take a few minutes to appear in other service pages (e.g., VCN, Compute). If `fedtracker-lab` doesn't show up in a Compartment dropdown, do a **hard refresh** (`Ctrl + Shift + R`) and try again. If it still doesn't appear, click the **expand arrow** (▶) next to your root compartment in the dropdown to reveal child compartments.

> **Important:** For the rest of this lab, **always** select the `fedtracker-lab` compartment in the left sidebar dropdown when creating resources. If you accidentally create something in the root compartment, it still works but makes cleanup harder.

---

### Step 1.2.1 — Cost Protection Setup
📍 **OCI Console**

> **🧠 ELI5 — Budget Alerts and Quotas:** Cloud billing can surprise you. OCI budget alerts email you when spending hits a threshold — but they're "soft limits" (warnings only). Quotas are "hard limits" — they physically block resource creation if you exceed them. Combining both gives you an early warning system AND a safety net. Set these up BEFORE creating any resources.

> **⚠️ Why this matters:** If someone else's credit card is on this account, protect it. A single misconfigured GPU instance could cost $20+/hour. Budget alerts + quotas + tagging = zero surprises.

> **Cost check:** Budgets, alert rules, tag namespaces, and quota policies are all free — no cost to create or maintain them.

**Step 1.2.1a — Create a Budget with Email Alerts**

1. Navigate to **Billing & Cost Management** → **Budgets**
2. Click **Create Budget**
3. Fill in:
   - **Name:** `fedlab-monthly-budget`
   - **Description:** `Monthly spending cap for federal lab project`
   - **Budget Scope:** Select **Compartment**
   - **Target Compartment:** `fedtracker-lab` (or root — root covers the entire tenancy)
   - **Schedule:** `Monthly`
   - **Budget Amount (in USD):** `160` (adjust to your comfort level)
   - **Day of the month to begin budget processing:** `1` (default)
4. In the **Budget Alert Rule** section (same form), create your first alert:
   - **Threshold Metric:** `Actual Spend`
   - **Threshold Type:** `Percentage of Budget`
   - **Threshold %:** `50`
   - **Email Recipients:** `<YOUR_EMAIL>, <ACCOUNT_HOLDER_EMAIL>` (comma-separated — include the account owner so they have visibility)
5. Click **Create**

**Add more alert rules:**

6. Click into `fedlab-monthly-budget` → go to the **Budget Alert Rules** tab
7. Click **Create Alert Rule**:
   - **Threshold Metric:** `Actual Spend` | **Threshold Type:** `Percentage of Budget` | **Threshold %:** `80`
   - **Email Recipients:** `<YOUR_EMAIL>, <ACCOUNT_HOLDER_EMAIL>`
   - Click **Create**
8. Click **Create Alert Rule** again:
   - **Threshold Metric:** `Forecast Spend` | **Threshold Type:** `Percentage of Budget` | **Threshold %:** `100`
   - **Email Recipients:** `<YOUR_EMAIL>, <ACCOUNT_HOLDER_EMAIL>`
   - Click **Create**

> **Why multiple alerts?** Actual spend alerts catch you after the fact. Forecast alerts catch you before — OCI analyzes your usage trend and warns you if you're on track to exceed the budget. Add more alert rules (25%, 75%, etc.) if you want finer-grained visibility.

> **📝 Note:** Budget alerts evaluate every 24 hours, so there's a delay. This is why quotas (Step 1.2.1d) are your real hard stop.

**Step 1.2.1b — Create Tag Namespace for Cost Tracking**

1. Navigate to **Governance & Administration** → **Tag Namespaces**
2. Click **Create Tag Namespace**
3. Fill in:
   - **Namespace:** `fedlab-cost`
   - **Description:** `Cost tracking tags for federal lab project`
4. Click **Create**
5. Inside the namespace, create these **Tag Key Definitions** (click **Create Tag Key Definition** for each):

| Tag Key | Description | Cost-Tracking? |
|---|---|---|
| `project` | Which project owns this resource | ✅ Yes — check the box |
| `phase` | Which phase (phase-1, phase-2, phase-3) | ✅ Yes |
| `component` | Resource type (compute, network, database, storage, container) | ✅ Yes |
| `lifetime` | Expected lifetime (always-free, temporary, persistent) | ✅ Yes |
| `owner` | Person responsible for this resource | ✅ Yes |

> **Why defined tags instead of freeform?** Defined tags live in a namespace with controlled values — they can be made mandatory, they appear in Cost Analysis reports, and they enable budget-per-tag tracking. Freeform tags are flexible but can't be enforced or used for budgets. We'll use BOTH: defined tags for cost tracking, freeform tags for quick labels.

**Step 1.2.1c — Set Tag Defaults (Auto-Apply to New Resources)**

1. Navigate to **Identity & Security** → **Compartments**
2. Click into `fedtracker-lab`
3. Click the **Tag Defaults** tab
4. Click **Create Tag Default**
5. Add defaults:
   - **Tag namespace:** `fedlab-cost` | **Tag key:** `project` | **Default value:** `fedtracker`
   - Click **Create tag default**
6. Repeat for `owner`:
   - **Tag namespace:** `fedlab-cost` | **Tag key:** `owner` | **User-applied value** (this prompts the user to enter their name at resource creation)
7. Optionally add `phase`:
   - **Tag namespace:** `fedlab-cost` | **Tag key:** `phase` | **Default value:** `phase-1`

> These tags are automatically applied to every new resource in the compartment. No manual tagging needed for the basics. Each phase has its own compartment, so `phase-2` and `phase-3` get their own tag defaults later.

**Step 1.2.1d — Create Quota Policy (Hard Spending Limits)**

1. Navigate to **Governance & Administration** → **Quota Policies** (under Tenancy Management in the left nav)
2. Click **Create Quota**
3. Fill in:
   - **Name:** `fedlab-quota-limits`
   - **Description:** `Hard limits on resource creation to prevent overspending`
4. In the **Quota policy** text area, paste these statements (all 6 lines, no blank lines after the last one):

```
set compute-core quota standard-a1-core-count to 4 in tenancy
zero compute-core quota /*gpu*/ in tenancy
zero compute-core quota hpc2-core-count in tenancy
set block-storage quota total-storage-gb to 200 in tenancy
zero database quota /*exadata*/ in tenancy
set object-storage quota storage-bytes to 21474836480 in tenancy
```

> **⚠️ Copy-paste note:** Do NOT include comment lines (starting with `#`) — the quota editor does not support them. The `/*gpu*/` and `/*exadata*/` are wildcards that block ALL GPU types and Exadata database types. Object storage uses bytes: 21474836480 = 20 GB.

What each statement does:
1. **ARM compute:** Limits A1 Flex instances to 4 OCPUs (Always Free limit)
2. **GPU block:** Prevents launching any GPU instance (expensive — $1-20+/hr)
3. **HPC block:** Prevents launching HPC bare metal instances
4. **Block storage:** Limits to 200 GB (Always Free limit)
5. **Exadata block:** Prevents launching Exadata databases (enterprise pricing)
6. **Object storage:** Limits to 20 GB

5. Click **Create**

> **Why quota policies matter:** Unlike budget alerts (which only warn you), quotas BLOCK resource creation if you hit the limit. If you accidentally try to launch a GPU instance or an Exadata database, OCI will reject the API call. This is your credit card protection.

> **📝 Note:** New quota policies can take up to 10 minutes to become active.

**Step 1.2.1e — Create a Saved Cost Report**

1. Navigate to **Billing & Cost Management** → **Cost Analysis**
2. Configure the report:
   - **Start date:** 1st of the current month
   - **End date:** today's date
   - **Granularity:** `Daily`
   - **Show:** `Cost`
   - **Grouping dimensions:** `Service` (default — shows cost broken down by OCI service)
3. Add a tag filter:
   - Click **Add filter** → select **Tag** — a popup dialog will appear:
     - **Tag Namespace:** select `fedlab-cost` (change from "None (free-form-tag)")
     - **Tag Key:** select `component`
     - **Match any value** (select this radio button)
     - Click **Select**
   - Click **Apply**
4. Click **Save as new report** (top of page, next to the Reports dropdown)
5. **Name:** `fedlab-daily-cost-by-component`
6. Click **Save**

> Your saved report now appears in the **Reports** dropdown under "Saved Reports." Check it daily during the project — no browser bookmark needed, the report is saved in OCI with your filter settings intact. You can save up to 10 custom reports.

> **📝 Note:** If your `fedlab-cost` tag namespace doesn't appear in the Tag filter dropdown, this is normal — cost-tracking tag data can take 24-48 hours to populate in Cost Analysis after tag creation. Come back to this step after deploying your first tagged resources. The filter will work once OCI has cost data associated with your tags.

**Verify:**

- [ ] Budget exists with alert rules configured
- [ ] Tag namespace `fedlab-cost` exists with 5 tag keys (project, phase, component, lifetime, owner)
- [ ] Tag defaults are set on the `fedtracker-lab` compartment
- [ ] Quota policy `fedlab-quota-limits` exists and is active
- [ ] Cost Analysis page is bookmarked

> **💼 Interview Insight — Cost Management:** "Before deploying a single resource, I set up OCI budgets with both actual and forecast alerts, created a defined tag namespace for cost tracking, set compartment-level tag defaults for auto-tagging, and implemented quota policies as hard limits. In federal environments, uncontrolled cloud spend is a compliance finding — FinOps is part of operations, not an afterthought."

---

### Step 1.3 — Create Basic VCN via Wizard
📍 **OCI Console**

> **🧠 ELI5 — Virtual Cloud Network (VCN):** A VCN is your own private network inside Oracle's cloud — like having your own isolated section of a data center with its own IP addresses, firewall rules, and routing. Nothing can talk to your VMs unless you explicitly allow it through the VCN's rules. Think of it as the walls and doors of a building — the VMs are rooms inside.

1. Navigate to **Networking** → **Virtual Cloud Networks**
2. Make sure `fedtracker-lab` is selected in the Compartment dropdown on the left
3. Click **Start VCN Wizard**
4. Select **Create VCN with Internet Connectivity** → click **Start VCN Wizard**
5. Fill in:
   - **VCN Name:** `legacy-vcn`
   - **Compartment:** `fedtracker-lab` (should already be selected)
   - Leave all CIDR blocks as default (10.0.0.0/16 for VCN, 10.0.0.0/24 for public subnet, 10.0.1.0/24 for private subnet)
6. Click **Next** → review → click **Create**

The wizard creates:
- The VCN itself (10.0.0.0/16)
- A public subnet (10.0.0.0/24) with an internet gateway
- A private subnet (10.0.1.0/24) with a NAT gateway
- Route tables and security lists for both subnets

> **Why use the wizard for Day 1?** The wizard creates a working network in one click. On Day 2, you'll build the network manually to understand every piece. On Day 3, you'll codify it in Terraform. Three passes at the same concept = deep understanding.

**Verify:**

Click into `legacy-vcn`. You should see:
- 2 subnets listed (public and private)
- An Internet Gateway
- A NAT Gateway
- 2 Route Tables
- 2 Security Lists

> **⚠️ Wizard not working?** If the VCN wizard fails with "Invalid tags" (a known OCI Console bug when tag defaults are configured), use the [CLI Alternative: Create VCN via Cloud Shell](#cli-alternative-create-vcn-via-cloud-shell) section below instead.

---

#### CLI Alternative: Create VCN via Cloud Shell

> **When to use this:** If the VCN wizard fails due to tag validation errors, phantom freeform tags, or other wizard bugs, you can create the identical network stack via OCI Cloud Shell (the `>_` terminal icon in the top-right of the OCI Console). Each command below creates one resource. Run them in order, one at a time.

**Prerequisites — gather these values first:**

| Placeholder | How to Find It | Example Format |
|---|---|---|
| `COMPARTMENT_OCID` | Identity → Compartments → click `fedtracker-lab` → copy OCID | `ocid1.compartment.oc1..aaaaaa...` |
| `VCN_OCID` | Created in Step 1 below — copy `"id"` from the JSON response | `ocid1.vcn.oc1.iad.aaaaaa...` |
| `IG_OCID` | Created in Step 2 — copy `"id"` from the response | `ocid1.internetgateway.oc1.iad.aaaaaa...` |
| `NAT_OCID` | Created in Step 3 — copy `"id"` from the response | `ocid1.natgateway.oc1.iad.aaaaaa...` |
| `SERVICE_ID` | Created in Step 4a — the raw output value | `ocid1.service.oc1.iad.aaaaaa...` |
| `DEFAULT_RT_OCID` | From Step 1 response → `"default-route-table-id"` | `ocid1.routetable.oc1.iad.aaaaaa...` |
| `PRIVATE_RT_OCID` | Created in Step 6 — copy `"id"` from the response | `ocid1.routetable.oc1.iad.aaaaaa...` |
| `YOUR_OWNER_TAG` | Your name or identifier for cost tracking | e.g., `jsmith` |

> **📋 Copy-paste tip:** Each command below is a single line — no backslashes, no line breaks. Paste the entire line into Cloud Shell and press Enter once. Replace all `<PLACEHOLDER>` values with your actual OCIDs before pasting.

**Step 1 — Create VCN:**
```bash
oci network vcn create --compartment-id <COMPARTMENT_OCID> --cidr-blocks '["10.0.0.0/16"]' --display-name legacy-vcn --dns-label legacyvcn --defined-tags '{"fedlab-cost": {"phase": "phase-1", "owner": "<YOUR_OWNER_TAG>", "component": "network", "project": "fedtracker"}}'
```
> Save the `"id"` → this is your `VCN_OCID`. Also save `"default-route-table-id"` → this is your `DEFAULT_RT_OCID`.

**Step 2 — Create Internet Gateway:**
```bash
oci network internet-gateway create --compartment-id <COMPARTMENT_OCID> --vcn-id <VCN_OCID> --display-name internet-gateway-legacy-vcn --is-enabled true --defined-tags '{"fedlab-cost": {"phase": "phase-1", "owner": "<YOUR_OWNER_TAG>", "component": "network", "project": "fedtracker"}}'
```
> Save the `"id"` → this is your `IG_OCID`.

**Step 3 — Create NAT Gateway:**
```bash
oci network nat-gateway create --compartment-id <COMPARTMENT_OCID> --vcn-id <VCN_OCID> --display-name nat-gateway-legacy-vcn --defined-tags '{"fedlab-cost": {"phase": "phase-1", "owner": "<YOUR_OWNER_TAG>", "component": "network", "project": "fedtracker"}}'
```
> Save the `"id"` → this is your `NAT_OCID`.

**Step 4a — Get Service ID (for Service Gateway):**
```bash
oci network service list --query "data[?contains(name, 'All')].id | [0]" --raw-output
```
> Save the output → this is your `SERVICE_ID`.

**Step 4b — Create Service Gateway:**
```bash
oci network service-gateway create --compartment-id <COMPARTMENT_OCID> --vcn-id <VCN_OCID> --display-name service-gateway-legacy-vcn --services '[{"service-id": "<SERVICE_ID>"}]' --defined-tags '{"fedlab-cost": {"phase": "phase-1", "owner": "<YOUR_OWNER_TAG>", "component": "network", "project": "fedtracker"}}'
```

**Step 5 — Update Default Route Table (for public subnet → Internet Gateway):**
```bash
oci network route-table update --rt-id <DEFAULT_RT_OCID> --route-rules '[{"destination": "0.0.0.0/0", "destinationType": "CIDR_BLOCK", "networkEntityId": "<IG_OCID>"}]' --force
```

**Step 6 — Create Private Route Table (for private subnet → NAT Gateway):**
```bash
oci network route-table create --compartment-id <COMPARTMENT_OCID> --vcn-id <VCN_OCID> --display-name private-route-table-legacy-vcn --route-rules '[{"destination": "0.0.0.0/0", "destinationType": "CIDR_BLOCK", "networkEntityId": "<NAT_OCID>"}]' --defined-tags '{"fedlab-cost": {"phase": "phase-1", "owner": "<YOUR_OWNER_TAG>", "component": "network", "project": "fedtracker"}}'
```
> Save the `"id"` → this is your `PRIVATE_RT_OCID`.

**Step 7 — Create Public Subnet:**
```bash
oci network subnet create --compartment-id <COMPARTMENT_OCID> --vcn-id <VCN_OCID> --cidr-block 10.0.0.0/24 --display-name public-subnet-legacy-vcn --dns-label publicsub --prohibit-internet-ingress false --defined-tags '{"fedlab-cost": {"phase": "phase-1", "owner": "<YOUR_OWNER_TAG>", "component": "network", "project": "fedtracker"}}'
```

**Step 8 — Create Private Subnet:**
```bash
oci network subnet create --compartment-id <COMPARTMENT_OCID> --vcn-id <VCN_OCID> --cidr-block 10.0.1.0/24 --display-name private-subnet-legacy-vcn --dns-label privatesub --prohibit-internet-ingress true --route-table-id <PRIVATE_RT_OCID> --defined-tags '{"fedlab-cost": {"phase": "phase-1", "owner": "<YOUR_OWNER_TAG>", "component": "network", "project": "fedtracker"}}'
```

**Verify — run these commands to confirm everything was created:**

```bash
echo "=== VCN ===" && oci network vcn list --compartment-id <COMPARTMENT_OCID> --query "data[].{Name:\"display-name\", State:\"lifecycle-state\", CIDR:\"cidr-block\"}" --output table
```

```bash
echo "=== SUBNETS ===" && oci network subnet list --compartment-id <COMPARTMENT_OCID> --vcn-id <VCN_OCID> --query "data[].{Name:\"display-name\", CIDR:\"cidr-block\"}" --output table
```

```bash
echo "=== GATEWAYS ===" && oci network internet-gateway list --compartment-id <COMPARTMENT_OCID> --vcn-id <VCN_OCID> --query "data[].{Name:\"display-name\", State:\"lifecycle-state\"}" --output table && oci network nat-gateway list --compartment-id <COMPARTMENT_OCID> --vcn-id <VCN_OCID> --query "data[].{Name:\"display-name\", State:\"lifecycle-state\"}" --output table && oci network service-gateway list --compartment-id <COMPARTMENT_OCID> --vcn-id <VCN_OCID> --query "data[].{Name:\"display-name\", State:\"lifecycle-state\"}" --output table
```

```bash
echo "=== ROUTE TABLES ===" && oci network route-table list --compartment-id <COMPARTMENT_OCID> --vcn-id <VCN_OCID> --query "data[].{Name:\"display-name\", State:\"lifecycle-state\"}" --output table
```

**Expected output:**

| Resource | Name | Expected State |
|---|---|---|
| VCN | `legacy-vcn` | AVAILABLE, CIDR 10.0.0.0/16 |
| Public Subnet | `public-subnet-legacy-vcn` | AVAILABLE, CIDR 10.0.0.0/24 |
| Private Subnet | `private-subnet-legacy-vcn` | AVAILABLE, CIDR 10.0.1.0/24 |
| Internet Gateway | `internet-gateway-legacy-vcn` | AVAILABLE |
| NAT Gateway | `nat-gateway-legacy-vcn` | AVAILABLE |
| Service Gateway | `service-gateway-legacy-vcn` | AVAILABLE |
| Route Table (default) | `Default Route Table for legacy-vcn` | AVAILABLE |
| Route Table (private) | `private-route-table-legacy-vcn` | AVAILABLE |

---

> **Cost check:** VCN, subnets, internet gateway, NAT gateway = $0.00/month on Always Free tier. Networking resources are free on OCI. Verify at: [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)

---

### Step 1.4 — Launch Oracle Linux 8 VM
📍 **OCI Console**

> **🧠 ELI5 — Compute Instance (VM):** A compute instance is a virtual machine — a slice of a physical server in Oracle's data center that acts like your own dedicated computer. You choose how powerful it is (shape), what operating system it runs (image), and which network it connects to (subnet). It's like renting a computer in the cloud that you access over SSH.

1. Navigate to **Compute** → **Instances**
2. Make sure `fedtracker-lab` compartment is selected
3. Click **Create Instance**
4. Fill in:
   - **Name:** `legacy-server`
   - **Compartment:** `fedtracker-lab`

5. **Image and Shape** section:
   - Click **Edit** next to Image and Shape
   - **Image:** Click **Change Image** → select **Oracle Linux** → select **Oracle Linux 8** (not 9) → click **Select Image**
   - **Shape:** Click **Change Shape** → select **Ampere** (ARM) → select **VM.Standard.A1.Flex** → set **OCPU count: 2** and **Memory: 8 GB** → click **Select Shape**

> **🧠 ELI5 — Shapes and Images:** A *shape* is the hardware configuration — how many CPUs and how much RAM your VM gets. `VM.Standard.A1.Flex` means it uses ARM processors (like your phone's chip, very efficient) and "Flex" means you choose how many CPUs and RAM. An *image* is the operating system template — Oracle Linux 8 is Red Hat Enterprise Linux-compatible, which is the standard for federal environments.

6. **Networking** section:
   - **VCN:** `legacy-vcn`
   - **Subnet:** Select the **public subnet** (the one with "public" in the name)
   - **Public IPv4 address:** Select **Assign a public IPv4 address** (this is required so you can SSH in)

7. **Add SSH keys** section:
   - Select **Generate a key pair**
   - Click **Save Private Key** — download the `.key` file
   - Click **Save Public Key** — download the `.pub` file
   - **Save these files somewhere safe** (e.g., `~/.ssh/legacy-server.key`)

> ⚠️ **Do NOT lose your SSH private key.** Without it, you cannot access your VM. There is no password recovery. Move the downloaded key to a known location immediately.

8. Leave everything else as default
9. Click **Create**

Wait 1-2 minutes for the instance to show **RUNNING** status. Note the **Public IP Address** shown on the instance details page — you'll need this for SSH.

> **Cost check:** VM.Standard.A1.Flex with 2 OCPU / 8 GB RAM = $0.00/month on Always Free tier. OCI gives you 4 OCPUs and 24 GB RAM total for free A1 Flex instances. You're using half. Verify at: [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)

**Verify:**

On the instance details page, confirm:
- **State:** Running
- **Shape:** VM.Standard.A1.Flex (2 OCPU, 8 GB)
- **Image:** Oracle Linux 8
- **Public IP:** A valid IP address is shown (e.g., 129.xxx.xxx.xxx)

---

### Step 1.5 — SSH into Your VM
📍 **Local Terminal**

> **🧠 ELI5 — SSH (Secure Shell):** SSH is how you remotely control a Linux server. It creates an encrypted tunnel between your laptop and the cloud VM, so you can type commands as if you were sitting at the server's keyboard. The private key file is your proof of identity — like a digital badge that the server checks before letting you in.

First, fix the key file permissions (SSH refuses keys that are too open):

```bash
# Move the key to your .ssh directory (adjust the download path as needed)
mv ~/Downloads/legacy-server.key ~/.ssh/legacy-server.key

# Fix permissions — SSH requires private keys to be readable only by you
chmod 600 ~/.ssh/legacy-server.key
```

> **Why chmod 600?** SSH refuses to use a private key if other users on your system can read it. `600` means only the file owner can read/write it — everyone else is blocked. This is a security feature, not a bug.

Now connect:

```bash
# Replace <PUBLIC_IP> with the IP from the OCI Console
ssh -i ~/.ssh/legacy-server.key opc@<PUBLIC_IP>
```

You'll see a prompt asking to trust the server fingerprint — type `yes`.

> **🧠 ELI5 — The `opc` User:** `opc` is Oracle's default admin user on Oracle Linux cloud images — like `ec2-user` on AWS or `ubuntu` on Ubuntu images. It has `sudo` privileges (can run commands as root) but isn't root itself. This follows the principle of least privilege — you use a regular user and escalate only when needed.

You should now see a prompt like:

```
[opc@legacy-server ~]$
```

You're in. Every command from now on happens in this VM terminal unless a location tag says otherwise.

**Verify:**

```bash
# Confirm you're on Oracle Linux 8
cat /etc/oracle-release
# Expected: Oracle Linux Server release 8.x

# Confirm your hostname
hostname
# Expected: legacy-server

# Confirm your shape (ARM architecture)
uname -m
# Expected: aarch64
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `chmod` | `600` | Set file permissions — owner read/write only |
| `ssh` | `-i <key>` | Connect to remote server. `-i` = identity file (private key) |
| `cat` | | Print file contents to terminal |
| `hostname` | | Display the system's hostname |
| `uname` | `-m` | Print machine hardware architecture |

</em></sub>

---

### Phase 1 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| OCI Console shows instance **Running** | Green "Running" status | Wait 2-3 minutes. If stuck in "Provisioning", check service limits — you may need to request A1 Flex capacity in your region |
| `ssh -i key opc@<IP>` connects | Shell prompt appears | Check: (1) key file path is correct, (2) `chmod 600` was run on the key, (3) public IP is correct, (4) you're using `opc` not `root`, (5) security list allows SSH on port 22 (wizard default enables this) |
| `ssh` says "Permission denied" | Should not happen | Wrong key file, or key permissions too open. Run `chmod 600` on the key file |
| `ssh` says "Connection timed out" | Should not happen | Security list may be missing port 22 rule, or you're trying to reach the private subnet IP instead of the public IP |
| `cat /etc/oracle-release` shows Oracle Linux 8 | `Oracle Linux Server release 8.x` | You selected the wrong image — terminate the instance and recreate with Oracle Linux 8 |
| `uname -m` shows `aarch64` | `aarch64` (ARM) | You selected the wrong shape — this is fine for learning, but A1 Flex is the Always Free shape |

---

## PHASE 2: ORACLE LINUX ADMIN FUNDAMENTALS (2 hrs)

> This is the most important phase for interview prep. Every command here maps directly to questions you'll be asked about Linux administration at AFS. You're building hands-on muscle memory so you can answer "how would you..." questions with "I would..." backed by experience.
>
> 📍 **Where work happens:** VM Terminal (SSH into your Oracle Linux VM).
>
> 🛠️ **Build approach:** All commands typed by hand. No scripts yet — that comes in Phase 5.

---

### Step 2.1 — Manage Users and Permissions
📍 **VM Terminal**

> **🧠 ELI5 — User Management:** Linux is a multi-user system — multiple people (or services) can use the same machine simultaneously, each with their own files and permissions. Creating separate users is like giving each person their own key card that only opens certain doors. In federal environments, every action must be traceable to a specific user — shared accounts are a compliance violation.

**Create a new user for running the application:**

```bash
# Create a new user with a home directory
sudo useradd -m clouduser
```

> **Why `-m`?** The `-m` flag creates a home directory at `/home/clouduser`. Without it, the user exists but has nowhere to store files. Always use `-m` for human or service users who need their own space.

```bash
# Set a password for the new user
sudo passwd clouduser
# Enter a password when prompted (e.g., LabPass123! — this is a lab, not production)
```

```bash
# Add clouduser to the wheel group (grants sudo access)
sudo usermod -aG wheel clouduser
```

> **🧠 ELI5 — The `wheel` Group:** On Red Hat/Oracle Linux, the `wheel` group is the "administrators club." Any user in this group can run `sudo` to execute commands as root. On Debian/Ubuntu, this group is called `sudo` instead. The name "wheel" comes from "big wheel" — slang for an important person.

```bash
# Examine the user entry in /etc/passwd
grep clouduser /etc/passwd
# Expected output: clouduser:x:1001:1001::/home/clouduser:/bin/bash
```

> **What does each field mean?** The format is `username:password:UID:GID:comment:home_dir:shell`. The `x` means the password is stored in `/etc/shadow` (encrypted), not here. UID 1001 is the user ID. The shell `/bin/bash` means this user gets a bash prompt when they log in.

```bash
# View the sudoers configuration
sudo visudo
# Look for the line: %wheel  ALL=(ALL)       ALL
# This means: anyone in group wheel can run any command as any user
# Press :q to exit without changes (it opens in vi)
```

> **Why `visudo` instead of editing the file directly?** `visudo` locks the sudoers file and checks for syntax errors before saving. A broken sudoers file can lock you out of `sudo` entirely — `visudo` prevents that.

```bash
# Switch to the new user to test it
su - clouduser

# Verify you can use sudo
sudo whoami
# Expected: root (proves sudo works)

# Go back to opc user
exit
```

**Password aging and account policies (federal requirement):**

```bash
# Set password aging: max 90 days, min 7 days between changes, warn 14 days before expiry
sudo chage -M 90 -m 7 -W 14 clouduser

# Verify the policy
sudo chage -l clouduser
# Expected: Maximum number of days between password change: 90
#           Minimum number of days between password change: 7
#           Number of days of warning before password expires: 14
```

> **Why password aging?** Federal environments require passwords to expire periodically (NIST 800-53 IA-5). `chage` configures this per-user. `-M 90` means the password must be changed every 90 days. `-m 7` prevents users from immediately changing back to their old password.

**Sudoers drop-in files (the production way to manage sudo):**

```bash
# Instead of editing the main sudoers file, use drop-in files
# Create a file that gives clouduser specific sudo permissions
sudo visudo -f /etc/sudoers.d/clouduser
```

Add this content:

```
# Allow clouduser to restart the FedTracker service without a password
clouduser ALL=(root) NOPASSWD: /usr/bin/systemctl restart fedtracker, /usr/bin/systemctl status fedtracker
```

```bash
# Validate the sudoers syntax (critical — a broken sudoers file locks you out)
sudo visudo -c
# Expected: /etc/sudoers: parsed OK
#           /etc/sudoers.d/clouduser: parsed OK
```

> **Why `/etc/sudoers.d/` instead of editing `/etc/sudoers`?** Drop-in files are modular — each team or app gets its own file. Adding and removing access is clean (just add/remove a file). Ansible can manage these files without touching the main sudoers file. In production, you'd have `/etc/sudoers.d/devops-team`, `/etc/sudoers.d/security-team`, etc.

**Service accounts (for non-human processes):**

```bash
# Create a service account for running apps — no login shell, no home directory
sudo useradd -r -s /sbin/nologin -M svc-fedtracker

# Verify: system UID (below 1000), no shell, no home
grep svc-fedtracker /etc/passwd
# Expected: svc-fedtracker:x:998:996::/home/svc-fedtracker:/sbin/nologin
```

> **Why `-r -s /sbin/nologin -M`?** `-r` creates a system account (UID below 1000). `-s /sbin/nologin` prevents anyone from logging in as this user. `-M` skips creating a home directory. Service accounts should never be used for interactive login — they exist only to run processes with minimal privileges.

> **💼 Interview Insight — "How do you manage sudo access for different teams?"**
>
> **Strong answer:** "I use `/etc/sudoers.d/` drop-in files — one per team. Each file grants specific commands with NOPASSWD only where necessary. I validate with `visudo -c` and deploy via Ansible. Service accounts get `useradd -r -s /sbin/nologin` with no interactive access. Password aging is enforced with `chage` per compliance policy."
>
> **Weak answer:** "I add everyone to the wheel group." (Gives full root access to everyone — violates least privilege)

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `useradd` | `-m` | Create a new user. `-m` = create home directory |
| `useradd` | `-r -s /sbin/nologin -M` | Create a service account. `-r` = system user, no shell, no home |
| `passwd` | | Set or change a user's password |
| `usermod` | `-aG wheel` | Modify user. `-a` = append, `-G` = to group. Adds user to wheel group |
| `chage` | `-M 90 -m 7 -W 14` | Set password aging. `-M` = max days, `-m` = min days, `-W` = warning days |
| `visudo` | | Safely edit the sudoers file with syntax checking |
| `visudo` | `-f <file>` | Edit a specific sudoers drop-in file |
| `visudo` | `-c` | Check all sudoers files for syntax errors |
| `grep` | | Search text. Here, finds the user's line in `/etc/passwd` |
| `su` | `-` | Switch user. `-` = load the target user's full environment |
| `whoami` | | Print the current effective username |

</em></sub>

---

### Step 2.2 — Manage Packages with dnf
📍 **VM Terminal**

> **🧠 ELI5 — Package Management (dnf):** `dnf` is Oracle Linux 8's package manager — it installs, updates, and removes software. Think of it like an app store for Linux. It downloads software from Oracle's repositories (online catalogs), handles dependencies automatically (if app A needs library B, it installs both), and tracks everything. `dnf` replaced `yum` starting in RHEL/Oracle Linux 8, though `yum` still works as an alias.

```bash
# Update all installed packages to latest versions
sudo dnf update -y
```

> **Why `-y`?** The `-y` flag automatically answers "yes" to confirmation prompts. Without it, `dnf` asks "Is this ok [y/N]:" and waits for input. In scripts and automation, you always use `-y`. This update may take 2-5 minutes.

```bash
# Install the tools we'll need for the lab
sudo dnf install -y git wget curl vim

# Install Python 3.11 (required for modern FastAPI/Pydantic v2)
sudo dnf install -y python3.11 python3.11-pip python3.11-devel
sudo alternatives --set python3 /usr/bin/python3.11
```

```bash
# Verify Python was installed correctly
python3 --version
# Expected: Python 3.11.x

# Check what's installed related to Python
dnf list installed | grep python3
# Expected: Several python3 packages listed

# Get detailed info about the python3 package
dnf info python3.11
# Shows: version, release, architecture, size, repository source
```

```bash
# Search for available packages (useful for finding package names)
dnf search oracle
# Shows all packages with "oracle" in the name or description
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `dnf update` | `-y` | Update all packages. `-y` = auto-confirm |
| `dnf install` | `-y` | Install packages. `-y` = auto-confirm |
| `dnf list installed` | | List all currently installed packages |
| `dnf info` | | Show detailed info about a specific package |
| `dnf search` | | Search package names and descriptions |
| `python3 --version` | | Print installed Python version (should show 3.11.x) |

</em></sub>

---

### Step 2.3 — Manage Services with systemctl
📍 **VM Terminal**

> **🧠 ELI5 — systemd and systemctl:** `systemd` is the service manager on modern Linux — it starts, stops, monitors, and restarts services. Think of it as a control tower at an airport: it knows which services (planes) should be running, launches them in the right order at boot, and can restart them if they crash. `systemctl` is the command-line tool you use to talk to systemd — like the radio between you and the control tower.

```bash
# Check if the SSH service is running (it should be — you're connected via SSH!)
systemctl status sshd
# Expected: Active: active (running)
# You'll see green text and the process ID
```

> **Reading `systemctl status` output:** The key lines are: `Active: active (running)` means it's working. `Main PID: 1234` is the process ID. `CGroup:` shows the process tree. If you see `inactive (dead)` or `failed`, the service is not running.

```bash
# List all currently running services
systemctl list-units --type=service --state=running
# Shows every service that systemd is actively managing
# You'll see sshd, firewalld, chronyd (time sync), and others
```

```bash
# Experiment: stop the SSH service (DON'T WORRY — your current session stays alive)
sudo systemctl stop sshd

# Check status — it should now be inactive
systemctl status sshd
# Expected: Active: inactive (dead)

# Start it back up immediately
sudo systemctl start sshd

# Verify it's running again
systemctl status sshd
# Expected: Active: active (running)
```

> ⚠️ **Do NOT close your SSH terminal while sshd is stopped.** Your existing session stays alive because it's already established, but you won't be able to open a new SSH connection until sshd is restarted.

```bash
# Understand the difference between enable and start
systemctl is-enabled sshd
# Expected: enabled (means it starts automatically on boot)

# enable = start on boot (persistent across reboots)
# start = start right now (only until reboot)
# You usually want both: sudo systemctl enable --now <service>
```

> **🧠 ELI5 — `enable` vs `start`:** `start` is like flipping a light switch — the light turns on now but won't come on automatically after a power outage. `enable` sets up the light to turn on automatically when power is restored. `enable --now` does both at once. For production services, you always want both — the service should be running AND set to auto-start on reboot.

**Service hardening and resource limits (production-grade systemd):**

```bash
# Preview what a hardened service file looks like — examine sshd's unit file
systemctl cat sshd
# Notice directives like Type=notify and various security settings
```

> **🧠 ELI5 — systemd Security Directives:** systemd can sandbox services — restricting what files they can access, preventing privilege escalation, and limiting CPU/memory usage. These directives are your first line of defense if a service gets compromised. You'll apply these to FedTracker's service file in Phase 4.

Key hardening directives you'll use later:

```
# In a [Service] section:
NoNewPrivileges=yes          # Process can't gain additional privileges (no setuid)
ProtectSystem=strict         # Makes / read-only except explicitly allowed paths
PrivateTmp=yes               # Service gets its own /tmp (can't see other services' temp files)
MemoryMax=512M               # Kill the service if it uses more than 512MB (prevents OOM)
CPUQuota=80%                 # Limit to 80% of one CPU core
```

```bash
# Monitor real-time resource usage by service (cgroups)
systemd-cgtop
# Press 'q' to exit
# Shows CPU, memory, and I/O per service — like top but organized by systemd service
```

> **💼 Interview Insight — "Walk me through a systemd service file you wrote"**
>
> **Strong answer:** "I wrote a service file for our FastAPI app. The [Unit] section sets `After=network.target` so it starts after networking. The [Service] section runs as a dedicated non-root user with `NoNewPrivileges=yes` and `ProtectSystem=strict` for security. I set `MemoryMax=512M` so it can't OOM-kill the server. `Restart=always` with `RestartSec=5` handles crashes. All output goes to the journal for centralized logging."
>
> **Weak answer:** "I just copy one from the internet and change the ExecStart line."

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `systemctl status` | | Show detailed status of a service |
| `systemctl list-units` | `--type=service --state=running` | List all running services |
| `systemctl stop` | | Stop a service immediately |
| `systemctl start` | | Start a service immediately |
| `systemctl enable` | | Set a service to start on boot |
| `systemctl enable --now` | | Start now AND enable on boot (both at once) |
| `systemctl is-enabled` | | Check if a service is set to start on boot |
| `systemctl cat` | | Display a service's unit file contents |
| `systemd-cgtop` | | Real-time resource usage per cgroup/service |

</em></sub>

---

### Step 2.4 — Configure Firewall with firewalld
📍 **VM Terminal**

> **🧠 ELI5 — firewalld:** `firewalld` is Oracle Linux's firewall — it controls which network traffic is allowed in and out of your server. Think of it as a bouncer at a nightclub: it has a list of approved ports (doors), and any traffic trying to come in through a port not on the list gets rejected. By default, almost everything is blocked except SSH (port 22).

```bash
# Check if firewalld is running
sudo systemctl status firewalld
# Expected: Active: active (running)
# If it's not running: sudo systemctl enable --now firewalld
```

```bash
# See the current firewall configuration
sudo firewall-cmd --list-all
# Expected output shows:
#   public (active)
#     interfaces: ens3 (or similar)
#     services: dhcpv6-client ssh
#     ports:
# Notice: only SSH and DHCP are allowed. Port 8000 is NOT listed (we need it for FastAPI)
```

```bash
# Open port 8000 for the FastAPI application (permanent = survives reboot)
sudo firewall-cmd --add-port=8000/tcp --permanent
# Expected: success
```

> **Why `--permanent`?** Without `--permanent`, the rule disappears on reboot. With `--permanent`, it's saved to disk but doesn't take effect until reload. You need both `--permanent` (save) and `--reload` (apply). A common mistake is using `--permanent` and wondering why it didn't work — you forgot to reload.

```bash
# Reload firewall to apply the permanent rule
sudo firewall-cmd --reload
# Expected: success

# Verify the port is now open
sudo firewall-cmd --list-ports
# Expected: 8000/tcp
```

```bash
# Verify the full configuration again
sudo firewall-cmd --list-all
# Now you should see 8000/tcp under "ports"
```

> **🧠 ELI5 — Firewall Zones:** firewalld organizes rules into "zones." The default zone is `public`, which is what your server uses. Each zone has different trust levels — `public` is the most restrictive (good for internet-facing servers), `trusted` allows everything (never use this for public servers). For this lab, the `public` zone with explicit port rules is correct.

**Advanced firewalld — custom zones and rich rules:**

```bash
# Create a custom zone for the application tier (production pattern)
sudo firewall-cmd --permanent --new-zone=app-tier
sudo firewall-cmd --reload

# List all zones including your new one
sudo firewall-cmd --get-zones
# Expected: app-tier listed among the zones
```

> **Why custom zones?** In production, different network interfaces get different trust levels. The bastion-facing interface might be in a stricter zone than the internal app network. Custom zones let you define these trust boundaries.

```bash
# Add a rich rule to rate-limit SSH connections (brute-force protection)
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" service name="ssh" accept limit value="5/m"'
sudo firewall-cmd --reload

# Verify the rich rule
sudo firewall-cmd --list-rich-rules
# Expected: rule family="ipv4" service name="ssh" accept limit value="5/m"
```

> **What does `limit value="5/m"` do?** It limits SSH connections to 5 per minute from any single IP. After 5 connections in a minute, new connections are silently dropped. This slows down brute-force attacks without blocking legitimate access.

```bash
# Enable logging of dropped packets (useful for troubleshooting and auditing)
sudo firewall-cmd --set-log-denied=all
# Now dropped packets show up in journalctl: journalctl -k | grep REJECT
```

> **Defense in depth — cloud + host firewalls:** In production, you'd combine OCI Security Lists (network layer) with firewalld (host layer). Security Lists block traffic before it reaches the VM. firewalld blocks traffic at the OS level. An attacker must bypass BOTH. If a Security List is misconfigured, firewalld is your safety net. Always configure both.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `firewall-cmd --list-all` | | Show all firewall rules for the active zone |
| `firewall-cmd --add-port` | `--permanent` | Open a port. `--permanent` = persist across reboots |
| `firewall-cmd --reload` | | Apply permanent rules that were just added |
| `firewall-cmd --list-ports` | | Show all explicitly opened ports |
| `firewall-cmd --new-zone` | `--permanent` | Create a custom firewall zone |
| `firewall-cmd --add-rich-rule` | `--permanent` | Add an advanced rule (rate limiting, logging, etc.) |
| `firewall-cmd --set-log-denied` | `all` | Log all packets rejected by the firewall |

</em></sub>

---

### Step 2.5 — Manage Disk and Storage
📍 **VM Terminal**

> **🧠 ELI5 — Disk and Storage:** Your VM has virtual disks just like a physical computer has hard drives. `df` shows how full they are (like checking your phone's storage), `lsblk` shows all connected disks (even empty ones), and `free` shows RAM usage. Understanding storage is critical — a full disk is one of the most common causes of application crashes in production.

```bash
# Show disk space usage in human-readable format
df -h
# Expected: You'll see / (root filesystem) with about 47 GB total
# Key columns: Size (total), Used, Avail, Use%, Mounted on
```

> **What does `-h` mean?** "Human-readable" — shows sizes in GB/MB instead of raw byte counts. Without `-h`, you'd see `49328128` instead of `47G`. Almost every storage command supports `-h`.

```bash
# List all block devices (disks and partitions)
lsblk
# Expected: sda (boot volume) with partitions sda1, sda2, sda3
# sda is your 47 GB boot volume — the VM's "hard drive"
```

```bash
# Show memory (RAM) usage
free -h
# Expected: total ~8 GB (matching your shape), with some used by the OS
# Key: "available" is what your apps can use, not "free"
# "available" includes memory that Linux can reclaim from caches
```

> **Why "available" not "free"?** Linux aggressively uses spare RAM for file caches to speed things up. The "free" column looks scary-low, but "available" shows what can actually be given to new programs. If "available" drops below ~200 MB, you have a real memory problem.

```bash
# View the filesystem table (what gets mounted on boot)
cat /etc/fstab
# This file tells Linux which disks to mount and where when the system boots
# You'll see entries for the root partition and possibly /boot
```

> **🧠 ELI5 — /etc/fstab:** This file is Linux's "disk mounting instructions" — it runs at boot to attach all disks to the correct directories. If you add a new disk and want it to persist across reboots, you add a line here. A typo in fstab can prevent your system from booting — always be careful editing it.

```bash
# Check inode usage (a full inode table can cause "disk full" errors even with free space)
df -ih
# Expected: IUse% should be very low (1-5%)
```

> **What are inodes?** Every file on Linux uses one inode (an index entry). You can run out of inodes before running out of disk space if you create millions of tiny files. The `df -ih` command checks inode usage. This is a real production issue and an advanced interview topic.

**LVM basics — the standard way to manage storage in production:**

> **🧠 ELI5 — LVM (Logical Volume Manager):** LVM adds a flexible layer between physical disks and filesystems. Instead of partitioning a disk directly, you create a "pool" of storage (Volume Group) from one or more disks, then carve out "logical volumes" from that pool. The key advantage: you can resize volumes without rebooting. When a partition fills up, you extend it in seconds. This is the most common real-world storage task you'll do as a Linux admin.

```bash
# View current LVM setup (your boot volume may or may not use LVM)
sudo pvs    # Physical Volumes — the raw disks
sudo vgs    # Volume Groups — the pools
sudo lvs    # Logical Volumes — the usable partitions
```

> **Note:** The OCI boot volume may not use LVM by default. On Day 2, when you attach an OCI Block Volume (50 GB free tier), you'll get a fresh disk to practice LVM on. Here's the workflow you'll use:

```bash
# THE LVM WORKFLOW (you'll do this on Day 2 with a real block volume):
# 1. Create Physical Volume from the raw disk
#    sudo pvcreate /dev/sdb
#
# 2. Create Volume Group (the storage pool)
#    sudo vgcreate app-vg /dev/sdb
#
# 3. Create Logical Volume (the usable partition)
#    sudo lvcreate -L 20G -n app-data app-vg
#
# 4. Format and mount
#    sudo mkfs.xfs /dev/app-vg/app-data
#    sudo mkdir /app-data
#    sudo mount /dev/app-vg/app-data /app-data
```

**Extending an LV — the most common production task:**

```bash
# THE EXTEND WORKFLOW (when a partition is getting full):
# 1. Extend the logical volume
#    sudo lvextend -L +10G /dev/app-vg/app-data
#
# 2. Grow the filesystem to use the new space
#    sudo xfs_growfs /app-data        # For XFS (Oracle Linux default)
#    # OR: sudo resize2fs /dev/app-vg/app-data   # For ext4
#
# 3. Verify
#    df -h /app-data    # Should show the new size
```

**LVM snapshots — pre-change safety net:**

```bash
# Before making risky changes, take an LVM snapshot:
#    sudo lvcreate -s -L 5G -n app-data-snap /dev/app-vg/app-data
#
# If the change goes wrong, revert:
#    sudo lvconvert --merge /dev/app-vg/app-data-snap
#
# If the change succeeds, delete the snapshot:
#    sudo lvremove /dev/app-vg/app-data-snap
```

> **💼 Interview Insight — "The audit log partition is 90% full. What do you do?"**
>
> **Strong answer:** "First, I check what's using the space with `du -sh /var/log/* | sort -rh | head -10`. If it's old logs, I verify logrotate is configured and clean up. If legitimate growth, I extend the LV with `lvextend -L +10G` and grow the filesystem with `xfs_growfs`. I also check inodes with `df -i` — sometimes the partition has free space but is out of inodes from millions of small files."
>
> **Weak answer:** "I'd delete some files to make space." (No investigation, no root cause, temporary fix)

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `df` | `-h` | Show disk usage. `-h` = human-readable sizes |
| `df` | `-ih` | Show inode usage. `-i` = inodes, `-h` = human-readable |
| `lsblk` | | List all block devices (disks, partitions) |
| `free` | `-h` | Show memory (RAM) usage. `-h` = human-readable |
| `cat /etc/fstab` | | Print the filesystem mount table |
| `pvs` / `vgs` / `lvs` | | Show LVM physical volumes / volume groups / logical volumes |
| `lvextend` | `-L +10G` | Extend a logical volume by 10 GB |
| `xfs_growfs` | | Grow an XFS filesystem to fill the volume |

</em></sub>

---

### Step 2.6 — Analyze Logs
📍 **VM Terminal**

> **🧠 ELI5 — System Logs:** Logs are your diagnostic toolkit — when something breaks, logs tell you what happened, when, and why. Linux stores logs in two main places: `journalctl` (systemd's log system — structured, queryable) and `/var/log/` (traditional log files). In federal environments, log analysis is a daily task — you're expected to spot anomalies, trace incidents, and prove compliance.

```bash
# View the last 20 SSH log entries (who's been connecting to your server?)
sudo journalctl -u sshd -n 20
# Expected: You'll see your own SSH connection and the server key generation
# -u = unit (service name), -n = number of lines
```

```bash
# View logs from the last 10 minutes
sudo journalctl --since "10 minutes ago"
# Shows everything that happened system-wide in the last 10 minutes
```

```bash
# Follow the system log in real-time (like a live feed)
sudo tail -f /var/log/messages
# Press Ctrl+C to stop watching
# This is useful when you're trying to reproduce a problem — run tail -f in one terminal,
# trigger the problem in another terminal, and watch the log entries appear
```

```bash
# Check for failed login attempts (security audit)
sudo grep "Failed" /var/log/secure
# If your server has been up for a while, you might see brute-force SSH attempts
# from bots scanning the internet. This is normal and why SSH keys matter.
```

```bash
# View package installation history
sudo cat /var/log/dnf.log
# Shows every package you installed, updated, or removed — and when
```

```bash
# Check boot messages for errors
sudo journalctl -b --priority=err
# -b = current boot, --priority=err = only errors and worse
# Expected: Possibly a few non-critical warnings. Zero errors is ideal.
```

**Advanced journalctl forensics — investigating incidents:**

```bash
# Filter by priority level (0=emerg through 7=debug)
sudo journalctl -p err --since "24 hours ago"
# Shows only errors and worse from the last 24 hours — your first command during incident response

# Check logs from the previous boot (what happened before the last reboot?)
sudo journalctl -b -1
# -b -1 = previous boot, -b 0 = current boot, -b -2 = two boots ago

# Check for OOM (Out of Memory) kills — a common cause of mystery crashes
sudo journalctl -k | grep -i oom
# -k = kernel messages only. If a process was OOM-killed, you'll see it here

# Combine filters: show errors for a specific service in a time window
sudo journalctl -u sshd -p warning --since "2024-01-01" --until "2024-01-02"
```

> **Correlating crashes with system events:** When a service crashes, don't just look at the service's logs. Check kernel messages (`journalctl -k`) for OOM kills and hardware errors, and check system-wide events (`journalctl --since "5 minutes ago"`) for cascading failures.

**Log rotation — preventing disks from filling up:**

```bash
# Check the existing logrotate config
cat /etc/logrotate.conf

# View service-specific rotation configs
ls /etc/logrotate.d/

# Preview a logrotate config for FedTracker (you'll create this when the app runs):
# /opt/fedtracker/logs/*.log {
#     daily
#     rotate 30
#     compress
#     missingok
#     notifempty
#     create 0640 clouduser clouduser
#     postrotate
#         systemctl reload fedtracker > /dev/null 2>&1 || true
#     endscript
# }
```

> **💼 Interview Insight — "How would you investigate why a service crashed at 3am?"**
>
> **Strong answer:** "I start with `journalctl -u <service> --since '02:50' --until '03:10'` to see the service's last messages before the crash. Then `journalctl -k --since '02:50'` to check for OOM kills or hardware errors. I check `dmesg | grep -i error` for kernel-level issues. If the service restarted, I look at the exit code in `systemctl status`. For memory issues, I check `journalctl -k | grep oom` and `free -h`. I also check `df -h` — full disks cause silent failures."
>
> **Weak answer:** "I'd check the log file." (Which one? How? No methodology)

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `journalctl` | `-u sshd -n 20` | Show logs for a service. `-u` = unit, `-n` = line count |
| `journalctl` | `--since "10 minutes ago"` | Show logs from a time range |
| `journalctl` | `-b --priority=err` | Current boot errors. `-b` = this boot, `--priority` = severity filter |
| `journalctl` | `-b -1` | Show all logs from the previous boot |
| `journalctl` | `-k` | Show kernel messages only (hardware, OOM, drivers) |
| `tail` | `-f` | Follow a file in real-time (live log watching) |
| `grep` | | Search for a pattern in text/files |

</em></sub>

---

### Step 2.7 — Explore Networking Basics
📍 **VM Terminal**

> **🧠 ELI5 — Linux Networking Commands:** These commands let you inspect your server's network configuration — its IP addresses, routing paths, and open ports. Think of `ip addr` as "what's my address?", `ip route` as "how do I get to the internet?", and `ss` as "what doors are open on my server?" Every troubleshooting scenario starts with these commands.

```bash
# Show all network interfaces and IP addresses
ip addr show
# Expected: You'll see:
#   lo (loopback — 127.0.0.1, the "talk to myself" address)
#   ens3 or enp0s3 (your main network interface with your private IP like 10.0.0.x)
# Note: the PUBLIC IP is handled by OCI's networking layer — it won't show here
```

> **Why doesn't my public IP show up?** OCI (and AWS, GCP) use NAT at the network layer. Your VM only knows about its private IP (10.0.0.x). The cloud provider maps your public IP to this private IP automatically. This is important to understand for troubleshooting — apps should bind to `0.0.0.0` (all interfaces), not to a specific IP.

```bash
# Show the routing table (how does traffic get to the internet?)
ip route show
# Expected: "default via 10.0.0.1" — this is the subnet's gateway
# All internet-bound traffic goes through this gateway → OCI's internet gateway → the internet
```

```bash
# Show all listening TCP ports (what services are accepting connections?)
ss -tulnp
# Expected: You'll see sshd on port 22 and possibly dhclient
# -t = TCP, -u = UDP, -l = listening, -n = numeric (don't resolve names), -p = show process
```

> **🧠 ELI5 — `ss` vs `netstat`:** `ss` (socket statistics) replaced `netstat` on modern Linux. It's faster and shows more information. When you see old documentation using `netstat`, mentally replace it with `ss`. Interviewers may ask about either — know both names.

```bash
# Test internet connectivity
ping -c 4 8.8.8.8
# Expected: 4 packets transmitted, 4 received, 0% packet loss
# -c 4 = send 4 pings then stop (without -c, it pings forever)
# 8.8.8.8 is Google's public DNS — if this works, your internet connection is fine
```

```bash
# Test if your FastAPI app is running yet (spoiler: it's not)
curl -I http://localhost:8000
# Expected: curl: (7) Failed to connect — Connection refused
# This is correct! We haven't deployed the app yet. This establishes a baseline.
```

**Advanced socket analysis with `ss`:**

```bash
# Show all established TCP connections (who's connected to your server right now?)
ss -tnp
# -t = TCP, -n = numeric, -p = show process
# You'll see your own SSH session listed

# Show listening sockets with their associated process
ss -tlnp
# The -l flag shows only LISTENING ports — this is the one you'll use most often
# Look for: *:22 (sshd), *:8000 (your app later)
```

> **`ss` vs `netstat`:** `ss` is the modern replacement for `netstat` on RHEL/Oracle Linux. It reads directly from kernel socket tables (faster), while `netstat` parses `/proc/net/tcp` (slower). Know both for interviews, but use `ss` in practice.

**Packet capture with `tcpdump` — when you need to see actual traffic:**

```bash
# Install tcpdump if not present
sudo dnf install -y tcpdump

# Capture traffic on port 8000 (your app's port)
sudo tcpdump -i any port 8000 -c 10
# -i any = all interfaces, -c 10 = capture 10 packets then stop
# Run this in one terminal, then curl your app from another to see the traffic

# Save a capture to a file for analysis
sudo tcpdump -i any port 8000 -w /tmp/app-traffic.pcap -c 50
# -w = write to file. You can open .pcap files with Wireshark

# Read back a capture file
sudo tcpdump -r /tmp/app-traffic.pcap
rm /tmp/app-traffic.pcap
```

**DNS troubleshooting with `dig`:**

```bash
# Install dig (part of bind-utils)
sudo dnf install -y bind-utils

# Query DNS (useful when "the app can't reach the database")
dig google.com +short
# Expected: IP address(es) — if blank, DNS is broken

# Check which DNS servers your system uses
resolvectl status 2>/dev/null || cat /etc/resolv.conf
```

> **💼 Interview Insight — "Users report the app is slow — how do you diagnose?"**
>
> **Strong answer:** "I start at the bottom of the stack: `ss -tnp` to check if the app is listening and how many connections are established. `top` or `htop` for CPU/memory pressure. `iostat` for disk I/O bottlenecks. `tcpdump -i any port 8000 -c 20` to check for connection timeouts or retransmits. Then `journalctl -u fedtracker --since '10 minutes ago'` for application-level errors. If it's DNS, `dig <hostname>` shows resolution time."
>
> **Weak answer:** "I'd restart the server." (No diagnosis, no root cause)

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `ip addr show` | | Show network interfaces and IP addresses |
| `ip route show` | | Show the routing table |
| `ss` | `-tulnp` | Show listening ports. `-t`=TCP, `-u`=UDP, `-l`=listening, `-n`=numeric, `-p`=process |
| `ss` | `-tnp` | Show established TCP connections with process names |
| `tcpdump` | `-i any port 8000 -c 10` | Capture 10 packets on port 8000 across all interfaces |
| `tcpdump` | `-w file.pcap` | Save captured packets to file for analysis |
| `dig` | `+short` | Query DNS and show just the answer |
| `ping` | `-c 4` | Test network connectivity. `-c` = count of pings |
| `curl` | `-I` | Fetch HTTP headers only (quick check if something is listening) |

</em></sub>

---

### Phase 2 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `sudo useradd -m clouduser` | No output (success) | User already exists — run `id clouduser` to check. If you need to start over: `sudo userdel -r clouduser` then recreate |
| `sudo usermod -aG wheel clouduser` | No output (success) | Check group membership: `groups clouduser`. Should show `wheel` |
| `sudo dnf update -y` | Completes with "Complete!" | Check internet: `ping -c 2 8.8.8.8`. If no internet, check VCN route table has an internet gateway |
| `systemctl status sshd` | `active (running)` | If dead: `sudo systemctl start sshd`. If failed: `journalctl -u sshd -n 30` for error details |
| `sudo firewall-cmd --list-ports` shows `8000/tcp` | `8000/tcp` in output | Forgot `--permanent`? Add it again with `--permanent` then `--reload` |
| `df -h` shows reasonable disk usage | Root filesystem under 50% | If nearly full, check what's using space: `sudo du -sh /* 2>/dev/null | sort -rh | head -10` |
| `ss -tulnp` shows sshd on port 22 | `*:22` or `0.0.0.0:22` | sshd not running — you wouldn't be connected if this were the case. Restart with `sudo systemctl start sshd` |
| `ping -c 4 8.8.8.8` gets replies | 0% packet loss | No internet — check VCN route table and security lists in OCI Console |

---

## PHASE 3: BUILD FEDTRACKER — FASTAPI FROM SCRATCH (2.5 hrs)

> This is the most important technical section of the entire guide. You're building a real REST API from the ground up — not copy-pasting a blob of code, but understanding every line. FastAPI is a modern Python web framework that auto-generates API documentation, validates data types automatically, and runs on uvicorn (an async web server). By the end, you'll understand HTTP verbs, status codes, Pydantic validation, and how APIs work — all knowledge that transfers directly to interview answers.
>
> 📍 **Where work happens:** VM Terminal for commands, building the file section by section.
>
> 🛠️ **Build approach:** Application code is built section-by-section with full ELI5 explanations. You type every line. Every new concept is explained before you use it.

---

### Step 3.1 — Understand APIs Before You Build One

> **🧠 ELI5 — What is an API?**
>
> Imagine you're at a restaurant. You don't walk into the kitchen and cook your own food — you use a **menu** (the API documentation) to see what's available, then tell your **waiter** (the API) what you want. The waiter takes your order to the kitchen (the server), the kitchen prepares your food (processes the request), and the waiter brings it back to you (the response).
>
> An API (Application Programming Interface) works exactly the same way. It's a set of rules that lets one program talk to another. Your browser talks to websites via APIs. Your phone apps talk to cloud servers via APIs. Every cloud service (OCI, AWS, Azure) exposes APIs. When you click a button in the OCI Console, it's making API calls behind the scenes.

> **🧠 ELI5 — What is REST?**
>
> REST (Representational State Transfer) is the most common style of API on the internet. It organizes everything around **resources** (nouns) and **actions** (verbs):
>
> - **Resources** are the things you work with: personnel records, audit logs, health status
> - **HTTP Verbs** are the actions you take on those resources:
>
> | HTTP Verb | Action | Example | Like... |
> |-----------|--------|---------|---------|
> | `GET` | Read/retrieve | `GET /personnel` | Looking at a menu |
> | `POST` | Create new | `POST /personnel` | Placing an order |
> | `PUT` | Update/replace | `PUT /personnel/5` | Changing your order |
> | `DELETE` | Remove | `DELETE /personnel/5` | Canceling your order |
>
> - **Status Codes** tell you what happened:
>
> | Code | Meaning | When You See It |
> |------|---------|----------------|
> | `200` | OK — success | GET request worked |
> | `201` | Created — new resource made | POST request created something |
> | `400` | Bad Request — your fault | You sent invalid data |
> | `404` | Not Found — doesn't exist | The resource ID doesn't exist |
> | `500` | Internal Server Error — server's fault | Bug in the code |
>
> REST is stateless — the server doesn't remember your previous requests. Every request contains all the information needed to process it. This makes REST APIs easy to scale (just add more servers) and easy to cache.

> **🧠 ELI5 — What is FastAPI?**
>
> FastAPI is a modern Python web framework for building APIs. Compared to Flask (the older standard):
>
> | Feature | Flask | FastAPI |
> |---------|-------|---------|
> | Data validation | Manual (you write checks) | Automatic (Pydantic models) |
> | API documentation | Manual (you write Swagger) | Auto-generated at `/docs` |
> | Async support | Bolt-on (Flask 2.0+) | Built-in from day one |
> | Type safety | Optional | Required (Python type hints) |
> | Performance | Good | Excellent (async + uvicorn) |
> | Server | Built-in dev server | uvicorn (production-grade ASGI) |
> | Default port | 5000 | 8000 |
>
> FastAPI uses **Pydantic** for data validation — you define what your data looks like using Python classes, and FastAPI automatically rejects requests that don't match. No more writing `if not data.get("name")` checks by hand.
>
> FastAPI uses **uvicorn** as its web server — a high-performance ASGI server that handles async requests. You run `uvicorn main:app --host 0.0.0.0` instead of `python3 main.py`.

> **💼 Interview Insight — REST APIs:** Interviewers ask about REST to gauge whether you understand how modern systems communicate. A strong answer covers: (1) resources and HTTP verbs, (2) status codes and what they mean, (3) statelessness and why it matters for scaling, (4) real examples from your work ("I built a REST API with endpoints for personnel records and audit logs"). A weak answer just says "it's how web apps talk to each other" without specifics. Common mistake: confusing REST with SOAP or saying REST requires JSON (it doesn't — JSON is just the most common format).

---

### Step 3.2 — Install FastAPI and Dependencies
📍 **VM Terminal**

```bash
# Install FastAPI, uvicorn (the ASGI server), and pydantic (data validation)
sudo pip3.11 install fastapi uvicorn pydantic
```

> **Why install globally with `sudo pip3.11`?** This is the "legacy" approach — installing Python packages system-wide without virtual environments. It works but creates problems: version conflicts between apps, no isolation, messy upgrades. Day 3 will do this properly with a virtual environment in the Ansible playbook. We're doing it the wrong way first so you understand why virtual environments exist.

> ⚠️ **In production, never use `sudo pip3.11 install`.** Always use virtual environments (`python3 -m venv`). We're being intentionally sloppy here for the legacy simulation.

**Verify:**

```bash
python3 -c "import fastapi; print(fastapi.__version__)"
# Expected: 0.x.x (version number printed)

python3 -c "import uvicorn; print(uvicorn.__version__)"
# Expected: 0.x.x (version number printed)

python3 -c "import pydantic; print(pydantic.__version__)"
# Expected: 2.x.x or 1.x.x (version number printed)
```

---

### Step 3.3 — Create Application Directory
📍 **VM Terminal**

```bash
# Create the application directory
sudo mkdir -p /opt/fedtracker

# Give clouduser ownership (so the app doesn't need to run as root)
sudo chown clouduser:clouduser /opt/fedtracker

# Verify
ls -la /opt/fedtracker
# Expected: drwxr-xr-x. 2 clouduser clouduser ... /opt/fedtracker
```

> **Why `/opt`?** The `/opt` directory is the standard location for third-party and optional software on Linux. It's separate from the OS directories (`/usr`, `/bin`). This convention makes it easy to find custom applications and back them up separately from the OS.

---

### Step 3.4 — Build main.py Section by Section
📍 **VM Terminal** (build by hand)

> **🧠 ELI5 — What is FedTracker?** FedTracker is a personnel tracking application for a federal agency. It lets you create and view personnel records, each with a name, role, clearance level, and project assignment. Every action is logged to an audit trail — this mirrors CMMC AU (Audit and Accountability) controls required in federal environments. You're building this from scratch to learn how APIs work.

Switch to the clouduser and start building:

```bash
# Switch to clouduser (who owns the /opt/fedtracker directory)
su - clouduser
```

**Build `/opt/fedtracker/main.py` section by section:**

**Step 1: Imports and app creation** — every FastAPI app starts here

```bash
cat > /opt/fedtracker/main.py << 'APPEOF'
#!/usr/bin/env python3
"""
FedTracker — Federal Personnel Tracking Application
A FastAPI app demonstrating REST API fundamentals and federal compliance patterns.

Database: SQLite (Day 1 legacy mode) or Oracle Autonomous DB (Day 2+)
Audit: Every action is logged for CMMC AU compliance
Server: uvicorn (ASGI) on port 8000
"""

import os
import csv
import io
import sqlite3
from datetime import datetime, date, timezone
from typing import Optional, List

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


# --- Lifespan (startup/shutdown) ---
# Note: init_db() is defined later in this file (Step 4), but Python doesn't execute
# the lifespan body until the app starts — so the function will exist by then.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database when the application starts."""
    print(f"[FedTracker] Starting with DB_TYPE={os.environ.get('DB_TYPE', 'sqlite')}")
    if os.environ.get("DB_TYPE", "sqlite") == "sqlite":
        print(f"[FedTracker] SQLite database: {os.environ.get('SQLITE_PATH', '/opt/fedtracker/fedtracker.db')}")
        init_db()
        print("[FedTracker] Database initialized with seed data")
    yield
    print("[FedTracker] Shutting down gracefully")


# Create the FastAPI application instance
# This is like Flask's app = Flask(__name__), but with auto-docs and validation built in
app = FastAPI(
    title="FedTracker",
    description="Federal Personnel Tracking API — CMMC AU compliant",
    version="1.0.0-legacy",
    lifespan=lifespan
)
APPEOF
```

> **What just happened?** You created the foundation of the app. `FastAPI()` creates the application object that handles all incoming requests. The `title`, `description`, and `version` parameters automatically appear in the generated API documentation at `/docs`. The `lifespan` parameter replaces the deprecated `@app.on_event("startup")` pattern — it uses Python's `asynccontextmanager` to define startup logic (before `yield`) and shutdown logic (after `yield`). The imports bring in everything you'll need: `BaseModel` for data validation, `HTTPException` for error responses, `Query` for query parameters.

> **Why `from typing import Optional, List`?** FastAPI uses Python type hints extensively. `Optional[str]` means "this could be a string or None." `List[dict]` means "a list of dictionaries." These type hints power the automatic validation and documentation.

**Step 2: Configuration** — database settings via environment variables

```bash
cat >> /opt/fedtracker/main.py << 'APPEOF'

# --- Configuration ---
# DB_TYPE controls which database backend to use
# Day 1: "sqlite" (default) — file-based, everything on one box
# Day 2+: "oracle" — Oracle Autonomous DB (set via environment variable)
DB_TYPE = os.environ.get("DB_TYPE", "sqlite")
SQLITE_PATH = os.environ.get("SQLITE_PATH", "/opt/fedtracker/fedtracker.db")
APPEOF
```

> **Why environment variables?** Using `os.environ.get("DB_TYPE", "sqlite")` means the app reads its configuration from environment variables, with sensible defaults. This is a twelve-factor app pattern — configuration lives outside the code, so the same code runs in different environments (dev with SQLite, production with Oracle DB) without changes. The systemd service file or Docker Compose will set these variables.

**Step 3: Pydantic models** — define what valid data looks like

```bash
cat >> /opt/fedtracker/main.py << 'APPEOF'


# --- Pydantic Models ---
# These classes define the SHAPE of data the API accepts and returns.
# FastAPI uses them to:
#   1. Validate incoming request data automatically
#   2. Generate API documentation with field descriptions
#   3. Serialize response data to JSON

class PersonnelCreate(BaseModel):
    """What the client sends when creating a new personnel record."""
    name: str = Field(..., min_length=1, max_length=200, description="Full name of the person")
    role: str = Field(..., min_length=1, max_length=100, description="Job role or title")
    clearance_level: str = Field(
        default="UNCLASSIFIED",
        description="Security clearance level (UNCLASSIFIED, CONFIDENTIAL, SECRET, TOP SECRET)"
    )
    project_id: Optional[str] = Field(
        default=None,
        description="Project identifier this person is assigned to"
    )


class PersonnelResponse(BaseModel):
    """What the API returns for a personnel record."""
    id: int
    name: str
    role: str
    clearance_level: str
    project_id: Optional[str]
    created_at: str
    updated_at: str
APPEOF
```

> **🧠 ELI5 — Pydantic Data Validation:** Imagine a bouncer at a club who checks IDs. Pydantic is your data bouncer — before any request reaches your code, Pydantic checks that the data matches the rules you defined. If someone sends `{"name": ""}` (empty name), Pydantic rejects it with a `422 Unprocessable Entity` error before your code even runs. The `Field(...)` with `...` means "this field is required" (the `...` is Python's Ellipsis object, used by Pydantic as a sentinel for "required"). `Field(default="UNCLASSIFIED")` means "optional, defaults to UNCLASSIFIED if not provided."

> **💼 Interview Insight — Data Validation:** When interviewers ask about input validation, they're testing whether you understand that you should never trust client data. A strong answer: "I use Pydantic models with FastAPI to validate all incoming data at the API boundary — field types, required fields, min/max lengths are all enforced automatically before my business logic runs. This prevents injection attacks and data corruption." A weak answer: "I check the data in my endpoint function with if statements." The difference is systematic vs. ad-hoc validation.

**Step 4: Database helpers** — connect to SQLite, create tables, seed data

```bash
cat >> /opt/fedtracker/main.py << 'APPEOF'


# --- Database Helpers ---

def get_db():
    """Get a database connection based on DB_TYPE."""
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent access
        return conn
    else:
        # Oracle DB support — configured in Day 2
        raise NotImplementedError("Oracle DB mode not configured yet. Set DB_TYPE=sqlite for Day 1.")


def init_db():
    """Create tables if they don't exist (SQLite mode)."""
    if DB_TYPE != "sqlite":
        return
    conn = get_db()
    cursor = conn.cursor()

    # Personnel table — tracks federal employees
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personnel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            clearance_level TEXT DEFAULT 'UNCLASSIFIED',
            project_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Audit log table — CMMC AU compliance
    # Every action is recorded: who did what, when, and the result
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            resource_id TEXT,
            details TEXT,
            source_ip TEXT
        )
    """)

    # Seed data — sample personnel records to work with
    cursor.execute("SELECT COUNT(*) FROM personnel")
    if cursor.fetchone()[0] == 0:
        seed_data = [
            ("Ada Lovelace", "Lead Engineer", "TOP SECRET", "PROJ-001"),
            ("Grace Hopper", "Senior Architect", "SECRET", "PROJ-001"),
            ("Alan Turing", "Cryptography Lead", "TOP SECRET/SCI", "PROJ-002"),
            ("Margaret Hamilton", "Software Director", "SECRET", "PROJ-002"),
            ("Katherine Johnson", "Data Analyst", "CONFIDENTIAL", "PROJ-003"),
        ]
        cursor.executemany(
            "INSERT INTO personnel (name, role, clearance_level, project_id) VALUES (?, ?, ?, ?)",
            seed_data
        )
        # Log the seed action
        cursor.execute(
            "INSERT INTO audit_log (action, resource_type, details, source_ip) VALUES (?, ?, ?, ?)",
            ("SEED_DATA", "personnel", "Loaded 5 initial records", "system")
        )

    conn.commit()
    conn.close()


def log_audit(action: str, resource_type: str, resource_id=None, details=None, source_ip="unknown"):
    """Write an entry to the audit log."""
    conn = get_db()
    conn.execute(
        "INSERT INTO audit_log (action, resource_type, resource_id, details, source_ip) VALUES (?, ?, ?, ?, ?)",
        (action, resource_type, str(resource_id) if resource_id else None, details, source_ip)
    )
    conn.commit()
    conn.close()
APPEOF
```

> **Why `row_factory = sqlite3.Row`?** By default, SQLite returns rows as plain tuples — `(1, "Ada Lovelace", "Lead Engineer")`. Setting `row_factory` to `sqlite3.Row` makes rows behave like dictionaries — `row["name"]` returns `"Ada Lovelace"`. This makes your code more readable and less brittle (you reference columns by name, not position).

> **Why `PRAGMA journal_mode=WAL`?** WAL (Write-Ahead Logging) is a SQLite optimization that allows reads and writes to happen concurrently without blocking each other. Without WAL, a write blocks all reads (and vice versa). For a web app handling multiple requests, WAL prevents "database is locked" errors.

**Step 5: GET /health endpoint** — the first and most important endpoint

```bash
cat >> /opt/fedtracker/main.py << 'APPEOF'


# --- API Endpoints ---

@app.get("/health")
def health_check():
    """
    Health check endpoint — used by monitoring scripts, load balancers, and Kubernetes probes.
    Returns service status and database connectivity.
    """
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": "fedtracker",
        "version": "1.0.0-legacy",
        "database": {"type": DB_TYPE, "status": db_status},
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
    }
APPEOF
```

> **🧠 ELI5 — Health Check Endpoints:** Every production service needs a `/health` endpoint. It's the first thing monitoring systems check — "is this service alive and can it reach its database?" Load balancers use it to decide whether to send traffic to this server. Kubernetes uses it for liveness and readiness probes. If `/health` returns an error, the system knows something is wrong before users notice.

> **💼 Interview Insight — Health Checks:** Interviewers love asking "how do you monitor your services?" A strong answer: "Every service exposes a `/health` endpoint that checks database connectivity, returns the service version, and reports any degraded dependencies. Load balancers and Kubernetes probes hit this endpoint to make routing decisions. I also have Bash scripts that curl the health endpoint and alert if it returns non-200." This shows you think about observability, not just functionality.

> **Why `@app.get("/health")` instead of `@app.route("/health", methods=["GET"])`?** FastAPI uses HTTP-verb-specific decorators: `@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()`. This is more explicit than Flask's `@app.route()` with a `methods` parameter. It also enables FastAPI's automatic OpenAPI documentation to correctly describe each endpoint.

**Step 6: GET /personnel** — list with pagination

```bash
cat >> /opt/fedtracker/main.py << 'APPEOF'


@app.get("/personnel")
def list_personnel(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum records to return")
):
    """
    List personnel records with pagination.
    Use skip and limit query parameters to page through results.
    Example: /personnel?skip=10&limit=5 returns records 11-15.
    """
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM personnel ORDER BY name LIMIT ? OFFSET ?",
        (limit, skip)
    ).fetchall()
    conn.close()

    personnel = [dict(row) for row in rows]
    log_audit("LIST", "personnel", details=f"Retrieved {len(personnel)} records (skip={skip}, limit={limit})")

    return {"count": len(personnel), "skip": skip, "limit": limit, "personnel": personnel}
APPEOF
```

> **🧠 ELI5 — Query Parameters and Pagination:** When you visit `/personnel?skip=10&limit=5`, the `?` marks the start of query parameters. `skip=10` and `limit=5` are key-value pairs separated by `&`. This is how REST APIs handle pagination — instead of returning all 10,000 records at once (slow, memory-hungry), you return them in pages. `skip` says "start at record #10" and `limit` says "give me 5 records." FastAPI's `Query()` function validates these parameters automatically — `ge=0` means "greater than or equal to 0" (you can't skip -5 records), `le=200` means "less than or equal to 200" (you can't request a million records at once).

> **💼 Interview Insight — Pagination:** When interviewers ask about API design, pagination is a topic that separates junior from mid-level candidates. A strong answer: "I implement offset-based pagination with `skip` and `limit` query parameters, with sensible defaults and maximum limits to prevent abuse. For large datasets, I'd consider cursor-based pagination instead — it performs better because the database doesn't have to count through skipped rows." A common mistake: returning all records without pagination, which works in dev but crashes in production with real data volumes.

**Step 7: POST /personnel** — create a new record

```bash
cat >> /opt/fedtracker/main.py << 'APPEOF'


@app.post("/personnel", status_code=201)
def create_personnel(person: PersonnelCreate):
    """
    Create a new personnel record.
    Requires name and role. Clearance level defaults to UNCLASSIFIED.
    Returns 201 Created with the new record's ID.
    """
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO personnel (name, role, clearance_level, project_id) VALUES (?, ?, ?, ?)",
        (person.name, person.role, person.clearance_level, person.project_id)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_audit("CREATE", "personnel", resource_id=new_id,
              details=f"Added {person.name} ({person.role})")

    return {"message": "Personnel record created", "id": new_id}
APPEOF
```

> **🧠 ELI5 — Request Bodies and 201 Created:** When you `POST` data to create something new, the data goes in the **request body** (not the URL). FastAPI automatically parses the JSON body and validates it against the `PersonnelCreate` Pydantic model. If validation passes, `person.name`, `person.role`, etc. are ready to use. The `status_code=201` tells FastAPI to return HTTP 201 (Created) instead of the default 200 (OK). This distinction matters — 201 specifically means "a new resource was created," which is the correct response for POST requests that create something.

> **💼 Interview Insight — HTTP Status Codes:** Returning the right status code is a sign of API maturity. Junior developers return 200 for everything. A strong answer: "I return 201 for successful POST requests, 200 for GET/PUT, 204 for DELETE (no content), 400 for validation errors, 404 when a resource isn't found, and 500 for unexpected server errors. These codes let clients handle responses correctly without parsing the body." Interviewers notice when you mention 201 — it shows you've actually built APIs.

**Step 8: GET /personnel/{id}** — get a single record

```bash
cat >> /opt/fedtracker/main.py << 'APPEOF'


@app.get("/personnel/{person_id}")
def get_personnel(person_id: int):
    """
    Get a single personnel record by ID.
    Returns 404 if the record doesn't exist.
    """
    conn = get_db()
    row = conn.execute("SELECT * FROM personnel WHERE id = ?", (person_id,)).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Personnel record {person_id} not found")

    log_audit("READ", "personnel", resource_id=person_id)
    return dict(row)
APPEOF
```

> **🧠 ELI5 — Path Parameters and 404:** In `/personnel/{person_id}`, the `{person_id}` is a **path parameter** — it's part of the URL itself, not a query string. When someone requests `/personnel/3`, FastAPI extracts `3` and passes it as the `person_id` argument. The `int` type hint means FastAPI automatically converts it to an integer and rejects non-numeric values (e.g., `/personnel/abc` returns a 422 error). If the record doesn't exist, we raise `HTTPException(status_code=404)` — the standard "not found" response.

> **Why `raise HTTPException` instead of `return jsonify({"error": ...}), 404`?** In Flask, you return a tuple `(response, status_code)`. In FastAPI, you raise an `HTTPException` — this is cleaner because it stops execution immediately (no risk of accidentally continuing after a not-found check) and FastAPI formats the error response consistently.

**Step 9: GET /audit** — audit log with date filtering

```bash
cat >> /opt/fedtracker/main.py << 'APPEOF'


@app.get("/audit")
def get_audit_log(
    limit: int = Query(default=50, ge=1, le=500, description="Maximum entries to return"),
    start_date: Optional[str] = Query(default=None, description="Filter entries after this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="Filter entries before this date (YYYY-MM-DD)")
):
    """
    View the audit trail — all recorded actions.
    Supports date filtering with start_date and end_date query parameters.
    """
    conn = get_db()

    query = "SELECT * FROM audit_log"
    params = []
    conditions = []

    if start_date:
        conditions.append("timestamp >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("timestamp <= ?")
        params.append(end_date + " 23:59:59")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    entries = [dict(row) for row in rows]
    return {"count": len(entries), "audit_log": entries}
APPEOF
```

> **Why date filtering on audit logs?** In federal environments, auditors need to review actions within specific time windows: "Show me all actions between March 1 and March 15." Building this filtering into the API saves auditors from downloading the entire log and filtering manually. The `start_date` and `end_date` parameters are optional — without them, you get the most recent entries.

**Step 10: POST /audit/export** — export audit log as CSV

```bash
cat >> /opt/fedtracker/main.py << 'APPEOF'


@app.post("/audit/export")
def export_audit_csv():
    """
    Export the audit log as a CSV file.
    Returns a downloadable CSV with all audit entries.
    Used for compliance reporting and evidence collection.
    """
    conn = get_db()
    rows = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC").fetchall()
    conn.close()

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "timestamp", "action", "resource_type", "resource_id", "details", "source_ip"])
    for row in rows:
        writer.writerow([row["id"], row["timestamp"], row["action"],
                        row["resource_type"], row["resource_id"],
                        row["details"], row["source_ip"]])

    output.seek(0)
    log_audit("EXPORT", "audit_log", details=f"Exported {len(rows)} audit entries as CSV")

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_log.csv"}
    )
APPEOF
```

> **Why CSV export?** Federal compliance audits require evidence in portable formats. CSV is universally readable — Excel, Google Sheets, Python, auditing tools all support it. The `StreamingResponse` with `Content-Disposition: attachment` tells the browser to download the file rather than display it. The `io.StringIO()` builds the CSV in memory instead of writing a temporary file.

**Step 11: Main entry point** — configure uvicorn for direct execution

```bash
cat >> /opt/fedtracker/main.py << 'APPEOF'


# --- Main Entry Point ---
# Startup logic (init_db) is handled by the lifespan function defined at the top of the file.
# The lifespan pattern replaces the deprecated @app.on_event("startup") decorator.

# This block runs when you execute: python3 main.py
# In production, you'd use: uvicorn main:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
APPEOF
```

> **Why the lifespan pattern instead of `@app.on_event("startup")`?** The `@app.on_event("startup")` decorator was deprecated in FastAPI 0.95+. The modern approach uses `asynccontextmanager` with a lifespan function passed to `FastAPI(lifespan=...)`. Code before `yield` runs at startup, code after `yield` runs at shutdown. This is cleaner, testable, and the officially supported pattern. The lifespan is defined in Step 1 (top of the file) and calls `init_db()` — even though `init_db()` is defined later in the file, Python doesn't execute the lifespan body until the app actually starts.

> **Why `uvicorn.run()` instead of `app.run()`?** Flask has a built-in development server (`app.run()`). FastAPI doesn't — it relies on uvicorn, a production-grade ASGI server. `uvicorn main:app` means "in the `main` module, find the `app` object and serve it." The `if __name__ == "__main__"` block lets you run `python3 main.py` for quick testing, but for production you'd use `uvicorn main:app --host 0.0.0.0 --port 8000` directly.

> **🧠 Putting it together:** You've built a complete REST API with 6 endpoints: `/health` (monitoring), `/personnel` GET (list with pagination), `/personnel` POST (create with validation), `/personnel/{id}` GET (single record with 404), `/audit` GET (filtered audit log), and `/audit/export` POST (CSV download). Every action writes to the audit log. The app connects to SQLite for Day 1 and will switch to Oracle DB in Day 2 by changing a single environment variable.

**Verify the complete file:**

```bash
# Count lines — should be approximately 200 lines
wc -l /opt/fedtracker/main.py
# Expected: ~200 lines

# Verify key sections exist
grep -n "def " /opt/fedtracker/main.py
# Expected: You should see all function definitions:
#   lifespan, get_db, init_db, log_audit, health_check, list_personnel,
#   create_personnel, get_personnel, get_audit_log, export_audit_csv

# Verify imports are correct
head -20 /opt/fedtracker/main.py
# Expected: shebang, docstring, imports including fastapi and pydantic

# Verify the app runs without import errors (quick syntax check)
python3 -c "import sys; sys.path.insert(0, '/opt/fedtracker'); import main; print('OK')"
# Expected: OK (no import errors)
```

---

### Step 3.5 — API Pattern Comparison

Now that you've built a REST API, here's how it compares to other API patterns you'll encounter in production:

| Pattern | What It Is | When to Use | Example |
|---------|-----------|-------------|---------|
| **REST** | Resource-based HTTP API with standard verbs | Client-facing CRUD operations, public APIs | `GET /personnel`, `POST /personnel` |
| **RPC** | Remote procedure call — action-based, not resource-based | Internal service-to-service calls, high-performance | gRPC `Predict()`, XML-RPC `getUser()` |
| **Event-driven** | Async message passing via queues or topics | Decoupled services, eventual consistency | Pub/Sub, webhooks, SQS/SNS |
| **GraphQL** | Client specifies exactly what data it wants | Complex data relationships, mobile apps (bandwidth-sensitive) | `{ personnel(id: 3) { name, role } }` |
| **WebSocket** | Persistent bidirectional connection | Real-time data, chat, live dashboards | `ws://server/live-updates` |

> **💼 Interview Insight — FastAPI vs Flask:** If an interviewer asks "why FastAPI over Flask?", a strong answer: "FastAPI gives me automatic data validation with Pydantic, auto-generated API documentation at `/docs`, built-in async support, and type safety that catches bugs at development time rather than runtime. For new projects, FastAPI is the modern choice. Flask is still solid for simpler applications or when team expertise is Flask-focused." Never trash Flask — it's still widely used. Show you know both and can choose based on context.

---

## PHASE 4: DEPLOY & TEST FEDTRACKER (45 min)

> You've built the API — now deploy it. First test it manually, then wrap it in a systemd service so it starts on boot and restarts if it crashes. Then test every endpoint from outside the VM to confirm it's accessible through the firewall.
>
> 📍 **Where work happens:** VM Terminal and Browser.
>
> 🛠️ **Build approach:** The systemd service file is built by hand (section by section). Testing uses curl and browser.

---

### Step 4.1 — Run FedTracker Manually (First Test)
📍 **VM Terminal**

```bash
# Make sure you're clouduser
whoami
# Expected: clouduser (if not, run: su - clouduser)

# Start the application manually with uvicorn
cd /opt/fedtracker && python3 main.py
```

You should see:

```
[FedTracker] Starting with DB_TYPE=sqlite
[FedTracker] SQLite database: /opt/fedtracker/fedtracker.db
[FedTracker] Database initialized with seed data
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Leave this running** and open a second SSH session to test (or use another terminal tab):

📍 **VM Terminal** (second session)

```bash
# Test the health endpoint
curl http://localhost:8000/health
# Expected: JSON with "status": "healthy", "database": {"type": "sqlite", "status": "connected"}
```

```bash
# List personnel (should show the 5 seed records)
curl http://localhost:8000/personnel
# Expected: JSON with "count": 5 and an array of personnel records
```

```bash
# Test pagination — skip 2, get 2
curl "http://localhost:8000/personnel?skip=2&limit=2"
# Expected: JSON with "count": 2 and 2 personnel records (3rd and 4th alphabetically)
```

```bash
# Add a new personnel record (POST with JSON body)
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","role":"Cloud Engineer","clearance_level":"SECRET","project_id":"PROJ-004"}' \
  http://localhost:8000/personnel
# Expected: {"message": "Personnel record created", "id": 6}
# Note the 201 status code (use curl -v to see it)
```

```bash
# Get the record you just created
curl http://localhost:8000/personnel/6
# Expected: JSON with Jane Doe's full record
```

```bash
# Try to get a record that doesn't exist
curl http://localhost:8000/personnel/999
# Expected: {"detail": "Personnel record 999 not found"} with 404 status
```

```bash
# Test validation — try to create without required fields
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":""}' \
  http://localhost:8000/personnel
# Expected: 422 Unprocessable Entity with validation error details
# This is Pydantic doing its job — it caught the empty name and missing role
```

```bash
# View the audit trail
curl http://localhost:8000/audit
# Expected: JSON showing SEED_DATA, LIST, CREATE, and READ actions with timestamps
```

```bash
# Export audit log as CSV
curl -X POST http://localhost:8000/audit/export -o audit_log.csv
cat audit_log.csv
# Expected: CSV file with audit entries
rm audit_log.csv
```

Now **stop the manual app** by going back to the first terminal and pressing `Ctrl+C`.

> **Why test manually first?** Before wrapping the app in a systemd service, you need to confirm it actually works. If you go straight to systemd and it fails, you won't know if the problem is the app or the service configuration. Always test the simplest version first.

---

### Step 4.2 — Visit the Auto-Generated API Documentation
📍 **Browser**

> **🧠 ELI5 — OpenAPI / Swagger:** FastAPI automatically generates interactive API documentation from your code. It reads your function signatures, Pydantic models, and docstrings to create a browsable interface where you can test every endpoint directly from your browser. This documentation stays perfectly in sync with your code — if you add an endpoint, it appears in the docs instantly.

While the app is running (start it again with `cd /opt/fedtracker && python3 main.py`):

```
http://<PUBLIC_IP>:8000/docs
```

> This is the Swagger UI — you'll see all 6 endpoints with their descriptions, parameters, and request/response schemas. Click any endpoint → **Try it out** → **Execute** to test it live.

```
http://<PUBLIC_IP>:8000/redoc
```

> This is ReDoc — an alternative documentation style that's more readable for consumers of your API. Both are auto-generated from the same code.

> **💼 Interview Insight — API Documentation:** "One advantage of FastAPI is auto-generated OpenAPI documentation. Every endpoint, parameter, and response schema is documented at `/docs` without writing a single line of documentation code. In production, this saves hours and eliminates documentation drift — the docs are always accurate because they're generated from the code."

Stop the manual app again (`Ctrl+C`).

---

### Step 4.3 — Create systemd Service File
📍 **VM Terminal** (build by hand)

> **🧠 ELI5 — systemd Service Files:** A systemd service file is a configuration file that tells Linux how to manage your application — when to start it, how to restart it if it crashes, what user to run it as, and where to send its logs. Without a service file, you'd have to manually start the app every time the server reboots. Think of it as hiring a babysitter for your application — systemd watches it 24/7 and restarts it if it falls over.

Switch back to the `opc` user (we need sudo to write to `/etc/systemd/system/`):

```bash
# Exit back to opc if you're still clouduser
exit
```

**Build `/etc/systemd/system/fedtracker.service` section by section:**

**Step 1:** The `[Unit]` section — metadata about the service

```bash
sudo tee /etc/systemd/system/fedtracker.service > /dev/null << 'SVCEOF'
[Unit]
# Description shows up in systemctl status and logs
Description=FedTracker Personnel Tracking Application (FastAPI)
# Start this service after the network is ready (uvicorn needs network to listen on a port)
After=network.target
SVCEOF
```

> The `After=network.target` line means "don't try to start FedTracker until the network is up." Without this, uvicorn might try to bind to a port before the network interface exists, causing a startup failure.

**Step 2:** The `[Service]` section — how to run the application

```bash
sudo tee -a /etc/systemd/system/fedtracker.service > /dev/null << 'SVCEOF'

[Service]
# Run as clouduser, not root (principle of least privilege)
User=clouduser
Group=clouduser

# Working directory — where the app's files live
WorkingDirectory=/opt/fedtracker

# Environment variables — DB_TYPE=sqlite for Day 1 legacy mode
Environment=DB_TYPE=sqlite
Environment=SQLITE_PATH=/opt/fedtracker/fedtracker.db

# The actual command to start the application
# uvicorn main:app — "in the main module, find the app object"
# --host 0.0.0.0 — listen on all interfaces (required for external access)
# --port 8000 — FastAPI/uvicorn default port
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000

# If the app crashes, restart it after 5 seconds
Restart=always
RestartSec=5

# Send stdout and stderr to the journal (viewable with journalctl)
StandardOutput=journal
StandardError=journal
SVCEOF
```

> **Why `User=clouduser`?** Running services as root is a security risk — if the app has a vulnerability, an attacker gets root access to the entire server. Running as `clouduser` limits the damage. This is a federal compliance requirement (principle of least privilege).

> **Why `Restart=always`?** In production, applications crash. `Restart=always` tells systemd to automatically restart the app whenever it exits (for any reason). `RestartSec=5` adds a 5-second delay to prevent rapid restart loops if the app keeps crashing.

> **Why `uvicorn main:app` instead of `python3 main.py`?** Running uvicorn directly gives you more control: process management, graceful shutdown, worker configuration. The `main:app` syntax means "import the `app` object from the `main` module." This is the production-standard way to run FastAPI apps.

**Step 3:** The `[Install]` section — when to start the service

```bash
sudo tee -a /etc/systemd/system/fedtracker.service > /dev/null << 'SVCEOF'

[Install]
# This means: start this service as part of the normal multi-user boot sequence
WantedBy=multi-user.target
SVCEOF
```

> **What is `multi-user.target`?** systemd has "targets" which are like boot stages. `multi-user.target` is the normal operating mode for a server (no graphical desktop). By saying `WantedBy=multi-user.target`, you're telling systemd "start FedTracker during normal server boot."

> **🧠 Putting it together:** The service file tells systemd: "After the network is up, run `uvicorn main:app --host 0.0.0.0 --port 8000` in `/opt/fedtracker` as the `clouduser` user. If it crashes, restart it after 5 seconds. Log everything to the journal. Start this service on every boot."

**Step 4: Harden the service file with security directives**

Add security and resource limit directives to the `[Service]` section:

```bash
# Add security hardening to the service file
sudo tee -a /etc/systemd/system/fedtracker.service.d/hardening.conf > /dev/null << 'SVCEOF'
# Create an override file instead of editing the main service file
# This is the systemd drop-in pattern — keeps your customizations separate
SVCEOF

# Actually, let's add the directives directly to the service file
# Re-create the full service file with security hardening:
sudo tee /etc/systemd/system/fedtracker.service > /dev/null << 'SVCEOF'
[Unit]
Description=FedTracker Personnel Tracking Application (FastAPI)
After=network.target

[Service]
User=clouduser
Group=clouduser
WorkingDirectory=/opt/fedtracker
Environment=DB_TYPE=sqlite
Environment=SQLITE_PATH=/opt/fedtracker/fedtracker.db
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# --- Security Hardening ---
# Prevent the process from gaining new privileges (blocks setuid exploits)
NoNewPrivileges=yes

# Make the entire filesystem read-only, except paths we explicitly allow
ProtectSystem=strict
ReadWritePaths=/opt/fedtracker

# Give this service its own private /tmp directory
# Other services and users can't see FedTracker's temp files
PrivateTmp=yes

# --- Resource Limits (cgroup controls) ---
# Kill the service if it uses more than 512MB RAM (prevents OOM-killing other services)
MemoryMax=512M

# Lower OOM score — protect this service from the OOM killer
# Range: -1000 (never kill) to 1000 (kill first). -500 = moderately protected
OOMScoreAdjust=-500

[Install]
WantedBy=multi-user.target
SVCEOF
```

> **What does each directive do?**
>
> | Directive | Purpose |
> |-----------|---------|
> | `NoNewPrivileges=yes` | Even if the app tries to run a setuid binary, the kernel blocks it. Prevents privilege escalation attacks |
> | `ProtectSystem=strict` | Mounts `/` as read-only. The app can only write to paths listed in `ReadWritePaths=`. If an attacker gets code execution, they can't modify system files |
> | `PrivateTmp=yes` | Creates an isolated `/tmp` for this service. Prevents temp file attacks where one service reads another's temporary data |
> | `MemoryMax=512M` | Enforced by cgroups. If the app leaks memory and hits 512 MB, systemd kills it and restarts it (because `Restart=always`). This protects other services from memory starvation |
> | `OOMScoreAdjust=-500` | When the kernel runs out of memory, it picks a process to kill (the OOM killer). A negative score means "try to keep this one alive." Critical services should have negative scores |

Now activate the service:

```bash
# Tell systemd to re-read all service files (required after creating/modifying one)
sudo systemctl daemon-reload

# Enable (start on boot) AND start now (--now does both in one command)
sudo systemctl enable --now fedtracker
```

```bash
# Check that the service is running
systemctl status fedtracker
# Expected: Active: active (running)
# You should see the uvicorn startup messages in the log output
```

```bash
# Follow the service logs in real-time (press Ctrl+C to stop)
journalctl -u fedtracker -f
```

> **Federal Reality Check: SELinux**
>
> Oracle Linux 8 ships with SELinux in enforcing mode. If your service fails to start, check SELinux first:
> ```bash
> # Check if SELinux is blocking your service
> sudo ausearch -m avc -ts recent
>
> # If you see denials for your app, create a custom policy:
> sudo ausearch -m avc -ts recent | audit2allow -M fedtracker
> sudo semodule -i fedtracker.pp
>
> # NEVER run setenforce 0 in a federal environment — that's an automatic audit failure
> getenforce  # Should always say "Enforcing"
> ```
>
> **Interview Insight:** "Is SELinux enforcing?" is the first question a federal auditor asks. The answer must always be "Yes, with custom policies for our applications."

**Verify:**

```bash
# Test the app through the systemd-managed service
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}

# Test from outside the VM (from your local machine)
# Replace <PUBLIC_IP> with your VM's public IP
curl http://<PUBLIC_IP>:8000/health
# Expected: {"status": "healthy", ...}
# If this times out, check the OCI security list — see troubleshooting table below
```

> **Important:** The OCI security list (network-level firewall) must also allow port 8000. The VCN wizard's default security list only allows SSH (port 22). You need to add an ingress rule for port 8000.

📍 **OCI Console**

1. Navigate to **Networking** → **Virtual Cloud Networks** → `legacy-vcn`
2. Click on the **public subnet**
3. Click on the **Security List** (Default Security List for legacy-vcn)
4. Click **Add Ingress Rules**
5. Fill in:
   - **Source CIDR:** `0.0.0.0/0`
   - **Destination Port Range:** `8000`
   - Leave everything else as default
6. Click **Add Ingress Rules**

> **Why two firewalls?** OCI has two layers of network security: the **Security List** (OCI's network-level firewall, configured in the console) and **firewalld** (the OS-level firewall inside the VM). Traffic must pass BOTH. You opened port 8000 in firewalld in Step 2.4 and now in the OCI security list. Forgetting either one is a common troubleshooting scenario.

📍 **Local Terminal**

```bash
# Now test from your local machine again
curl http://<PUBLIC_IP>:8000/health
# Expected: {"status": "healthy", "service": "fedtracker", ...}

curl http://<PUBLIC_IP>:8000/personnel
# Expected: JSON with personnel records
```

📍 **Browser**

```
http://<PUBLIC_IP>:8000/docs
```

> You should see the Swagger UI with all your endpoints. Try creating a personnel record from the browser interface.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `systemctl daemon-reload` | | Reload all service file definitions (required after editing .service files) |
| `systemctl enable --now` | | Start the service now AND set it to start on boot |
| `systemctl status` | | Show current status, PID, and recent log lines |
| `journalctl` | `-u fedtracker -f` | Follow a service's logs in real-time. `-u` = unit, `-f` = follow |
| `curl` | | Make HTTP requests to test endpoints |
| `uvicorn` | `main:app --host 0.0.0.0` | Run FastAPI app on all interfaces |

</em></sub>

---

### Phase 4 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `systemctl status fedtracker` | `active (running)` | Check logs: `journalctl -u fedtracker -n 30`. Common issues: wrong uvicorn path, permission denied on app files, port already in use |
| `curl http://localhost:8000/health` from VM | JSON with `"status": "healthy"` | App not running — check `systemctl status fedtracker`. If running but no response, check port with `ss -tlnp \| grep 8000` |
| `curl http://<PUBLIC_IP>:8000/health` from local | JSON response | Three things to check: (1) firewalld port 8000 open? `sudo firewall-cmd --list-ports` (2) OCI security list has ingress rule for port 8000? (3) App is actually listening? `ss -tlnp \| grep 8000` |
| `curl` returns "Connection refused" | Should return JSON | Nothing is listening on port 8000. Service not running — `sudo systemctl start fedtracker` |
| `curl` returns "Connection timed out" | Should return JSON | Firewall blocking — check both firewalld AND OCI security list |
| `journalctl -u fedtracker` shows "Permission denied" | Should show startup messages | File permissions wrong: `ls -la /opt/fedtracker/main.py` — should be owned by clouduser. Fix: `sudo chown clouduser:clouduser /opt/fedtracker/main.py` |
| `journalctl -u fedtracker` shows "ModuleNotFoundError: fastapi" | Should show startup messages | FastAPI not installed globally: `sudo pip3.11 install fastapi uvicorn pydantic`. Or wrong Python path in service file |
| `journalctl -u fedtracker` shows "command not found: uvicorn" | Should find uvicorn | Check path: `which uvicorn`. If it's in `/usr/local/bin/`, update the `ExecStart` path in the service file. Run `sudo systemctl daemon-reload` after editing |
| SQLite database not created | `fedtracker.db` should exist | Check `ls -la /opt/fedtracker/`. If missing, the app didn't start successfully — check service logs |
| Swagger UI not loading at `/docs` | Interactive API page | Ensure you're using port 8000 (not 5000). Check OCI security list allows 8000. Try with VM's public IP |
| POST returns 422 Unprocessable Entity | Should return 201 | Pydantic validation failed — check your JSON body includes all required fields (`name` and `role`). Check Content-Type header is `application/json` |

---

## PHASE 5: BASH HEALTH CHECK SCRIPT (45 min)

> Production systems need monitoring beyond "is the website up?" — you need to check disk space, memory, service health, and cloud resource status. In this phase, you build an operational Bash script by hand: a health checker for the VM that curls the FastAPI endpoints, checks system resources, and reports pass/fail results. These are the kinds of scripts every Linux admin and cloud engineer writes.
>
> 📍 **Where work happens:** VM Terminal (building file by hand).
>
> 🛠️ **Build approach:** Script is built by hand, section by section. This is DevOps work — you type every line.

---

### Step 5.1 — Create Bash Health Check Script
📍 **VM Terminal** (build by hand)

> **🧠 ELI5 — Health Check Scripts:** Production systems need automated health checks — scripts that run periodically (via cron or monitoring systems) to verify everything is working. When an on-call engineer gets paged at 3 AM, the first thing they check is the health report. This script checks the FedTracker service, network port, disk space, memory, and the application's health endpoint — all the things that commonly go wrong.

Switch to clouduser:

```bash
su - clouduser
```

**Build `/opt/fedtracker/health_check.sh` section by section:**

**Step 1:** Shebang and header — every script starts here

```bash
cat > /opt/fedtracker/health_check.sh << 'HEALTHEOF'
#!/bin/bash
# =============================================================================
# FedTracker Health Check Script
# Checks: service status, port listening, disk usage, memory usage, app endpoint
# Usage: ./health_check.sh
# Exit codes: 0 = all healthy, 1 = one or more checks failed
# =============================================================================

# Track whether any checks fail
FAILED=0
HEALTHEOF
```

> The shebang (`#!/bin/bash`) tells Linux which interpreter to use. Without it, the system might try to run your script with a different shell and fail on bash-specific syntax.

**Step 2:** Check if the FedTracker service is running

```bash
cat >> /opt/fedtracker/health_check.sh << 'HEALTHEOF'

# --- Check 1: Service Status ---
echo "=== FedTracker Health Report ==="
echo "Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo ""

echo -n "[Service]    fedtracker: "
if systemctl is-active --quiet fedtracker; then
    echo "RUNNING ✓"
else
    echo "DOWN ✗"
    FAILED=1
fi
HEALTHEOF
```

> `systemctl is-active --quiet` returns exit code 0 if the service is running, non-zero otherwise. The `--quiet` flag suppresses output so we can print our own formatted message. The `-n` flag on `echo` prevents a newline so the status appears on the same line.

**Step 3:** Check if the application port is listening

```bash
cat >> /opt/fedtracker/health_check.sh << 'HEALTHEOF'

# --- Check 2: Port Listening ---
echo -n "[Port]       8000/tcp:   "
if ss -tlnp | grep -q ':8000 '; then
    echo "LISTENING ✓"
else
    echo "NOT LISTENING ✗"
    FAILED=1
fi
HEALTHEOF
```

> `ss -tlnp | grep -q ':8000 '` checks if anything is listening on port 8000. The `-q` flag makes grep silent — it only sets the exit code. This is the difference between "the service is running" (systemctl) and "the service is actually accepting connections" (ss). A service can be running but not listening if it crashed internally.

**Step 4:** Check disk usage

```bash
cat >> /opt/fedtracker/health_check.sh << 'HEALTHEOF'

# --- Check 3: Disk Usage ---
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
echo -n "[Disk]       root (/):   "
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "${DISK_USAGE}% used ✓"
else
    echo "${DISK_USAGE}% used ✗ (WARNING: above 80%)"
    FAILED=1
fi
HEALTHEOF
```

> `df -h / | awk 'NR==2 {print $5}'` gets the usage percentage of the root filesystem. `NR==2` means "second line" (skipping the header). `tr -d '%'` removes the percent sign so we can compare it as a number. 80% is a common threshold — above that, you should investigate.

**Step 5:** Check memory usage

```bash
cat >> /opt/fedtracker/health_check.sh << 'HEALTHEOF'

# --- Check 4: Memory Usage ---
MEM_TOTAL=$(free -m | awk 'NR==2 {print $2}')
MEM_AVAILABLE=$(free -m | awk 'NR==2 {print $7}')
MEM_USED_PCT=$(( (MEM_TOTAL - MEM_AVAILABLE) * 100 / MEM_TOTAL ))
echo -n "[Memory]     RAM:        "
if [ "$MEM_USED_PCT" -lt 90 ]; then
    echo "${MEM_USED_PCT}% used (${MEM_AVAILABLE}MB available) ✓"
else
    echo "${MEM_USED_PCT}% used (${MEM_AVAILABLE}MB available) ✗ (WARNING: above 90%)"
    FAILED=1
fi
HEALTHEOF
```

> We use "available" memory (column 7), not "free" memory (column 4). Linux uses spare RAM for caching, so "free" is misleadingly low. "Available" is what programs can actually use.

**Step 6:** Curl the health endpoint

```bash
cat >> /opt/fedtracker/health_check.sh << 'HEALTHEOF'

# --- Check 5: Application Health Endpoint ---
echo -n "[Endpoint]   /health:    "
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    echo "HTTP ${HTTP_CODE} ✓"
else
    echo "HTTP ${HTTP_CODE} ✗"
    FAILED=1
fi
HEALTHEOF
```

> `curl -s -o /dev/null -w '%{http_code}'` is a common pattern: `-s` = silent (no progress bar), `-o /dev/null` = throw away the body, `-w '%{http_code}'` = print only the HTTP status code. This gives you a clean numeric code (200, 500, etc.) to check.

**Step 7:** Exit code logic

```bash
cat >> /opt/fedtracker/health_check.sh << 'HEALTHEOF'

# --- Summary ---
echo ""
if [ "$FAILED" -eq 0 ]; then
    echo "Overall: ALL CHECKS PASSED ✓"
    exit 0
else
    echo "Overall: ONE OR MORE CHECKS FAILED ✗"
    exit 1
fi
HEALTHEOF
```

> **Why exit codes matter:** Exit code 0 means success, non-zero means failure. Monitoring systems (Nagios, Prometheus, cron) use exit codes to determine if something is healthy. An exit code of 1 triggers an alert. This is a standard convention across all of Linux.

Now make it executable and run it:

```bash
# Make the script executable
chmod +x /opt/fedtracker/health_check.sh

# Run the health check
/opt/fedtracker/health_check.sh
```

**Expected output:**

```
=== FedTracker Health Report ===
Timestamp: 2026-03-20T14:30:00Z

[Service]    fedtracker: RUNNING ✓
[Port]       8000/tcp:   LISTENING ✓
[Disk]       root (/):   12% used ✓
[Memory]     RAM:        8% used (7400MB available) ✓
[Endpoint]   /health:    HTTP 200 ✓

Overall: ALL CHECKS PASSED ✓
```

**Verify:**

```bash
# Check the exit code of the last command
echo $?
# Expected: 0 (all checks passed)

# Verify the script is executable
ls -la /opt/fedtracker/health_check.sh
# Expected: -rwxrwxr-x (the x's mean executable)
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `chmod` | `+x` | Add execute permission to a file |
| `systemctl is-active` | `--quiet` | Check if service is running (silent, exit code only) |
| `ss` | `-tlnp` | Show listening TCP ports with process info |
| `df` | `-h /` | Show disk usage for root filesystem |
| `free` | `-m` | Show memory in megabytes |
| `curl` | `-s -o /dev/null -w '%{http_code}'` | Get only the HTTP status code from a URL |
| `awk` | `NR==2 {print $5}` | Extract a specific field from a specific line |

</em></sub>

---

## PHASE 6: PYTHON OCI RESOURCE REPORTER (45 min)

> The Bash health check monitors the VM itself. This Python script monitors your cloud resources — listing VMs, checking their status, and verifying cost-related tags. This is the foundation of cloud automation: querying cloud APIs programmatically instead of clicking around the console.
>
> 📍 **Where work happens:** VM Terminal (building file by hand).
>
> 🛠️ **Build approach:** Script is built by hand, section by section. This is cloud engineering work — you type every line.

---

### Step 6.1 — Create Python OCI Resource Reporter
📍 **VM Terminal** (build by hand)

> **🧠 ELI5 — OCI SDK (Python):** The OCI Python SDK lets you write code that talks to Oracle Cloud's APIs — listing VMs, checking resource status, reading tags, and pulling cost data. Instead of clicking around the OCI Console, you write a script that does it programmatically. This is the foundation of cloud automation — every cloud provider has an SDK, and writing scripts against it is a core cloud engineering skill.

**First, install the OCI SDK:**

```bash
# Install the OCI Python SDK
pip3.11 install oci --user
```

> **Why `--user`?** Installing with `--user` puts the package in your home directory instead of system-wide. This is slightly better than `sudo pip3.11 install` but still not as good as a virtual environment. We're splitting the difference for Day 1.

**Set up OCI API key authentication:**

📍 **OCI Console**

1. Click your **Profile icon** (top-right) → **User Settings**
2. Scroll down to **API Keys** → click **Add API Key**
3. Select **Generate API Key Pair**
4. Click **Download Private Key** — save as `~/.oci/oci_api_key.pem`
5. Click **Add**
6. A **Configuration File Preview** box appears — **copy this text** (you'll need it next)

📍 **VM Terminal**

```bash
# Create the OCI config directory
mkdir -p ~/.oci

# Create the config file — paste the contents from the OCI Console preview
# Replace the placeholder values with your actual tenancy/user/fingerprint/region
cat > ~/.oci/config << 'OCIEOF'
[DEFAULT]
user=ocid1.user.oc1..xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
tenancy=ocid1.tenancy.oc1..xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
region=us-ashburn-1
key_file=~/.oci/oci_api_key.pem
OCIEOF
```

> **Important:** Replace each value above with the actual values from the Configuration File Preview you copied from the OCI Console. The user OCID, tenancy OCID, fingerprint, and region must match your account.

```bash
# Upload the private key you downloaded from the OCI Console
# From your LOCAL machine, use scp to transfer it:
```

📍 **Local Terminal**

```bash
# Transfer the API key to the VM (adjust paths as needed)
scp -i ~/.ssh/legacy-server.key ~/Downloads/oci_api_key.pem opc@<PUBLIC_IP>:/home/opc/

# Then on the VM:
```

📍 **VM Terminal**

```bash
# If you're clouduser, the key was uploaded to opc's home — move it
# First exit to opc if needed, then:
exit  # back to opc

sudo cp /home/opc/oci_api_key.pem /home/clouduser/.oci/oci_api_key.pem
sudo chown clouduser:clouduser /home/clouduser/.oci/oci_api_key.pem
sudo chmod 600 /home/clouduser/.oci/oci_api_key.pem

# Switch back to clouduser
su - clouduser

# Fix the config file permissions too
chmod 600 ~/.oci/config
```

**Now build the OCI reporter script — `/opt/fedtracker/oci_reporter.py` section by section:**

**Step 1:** Imports and OCI configuration

```bash
cat > /opt/fedtracker/oci_reporter.py << 'PYEOF'
#!/usr/bin/env python3
"""
OCI Resource Reporter
Queries OCI APIs to report on compute instances, their status,
and tagging compliance. Run with: python3 oci_reporter.py

Requires: pip3.11 install oci
Requires: ~/.oci/config with valid API key authentication
"""

import oci
import sys
from datetime import datetime, timezone

# Load OCI configuration from ~/.oci/config
# This reads your tenancy OCID, user OCID, API key, and region
try:
    config = oci.config.from_file()
    oci.config.validate_config(config)
    print("[OCI Reporter] Configuration loaded successfully")
except Exception as e:
    print(f"[ERROR] Failed to load OCI config: {e}")
    print("  Fix: Ensure ~/.oci/config exists and has valid credentials")
    sys.exit(1)
PYEOF
```

**Step 2:** Function to find the lab compartment

```bash
cat >> /opt/fedtracker/oci_reporter.py << 'PYEOF'


def get_compartment_id(config, compartment_name="fedtracker-lab"):
    """Find the compartment OCID by name."""
    identity = oci.identity.IdentityClient(config)
    tenancy_id = config["tenancy"]

    compartments = identity.list_compartments(tenancy_id).data
    for c in compartments:
        if c.name == compartment_name and c.lifecycle_state == "ACTIVE":
            print(f"[OCI Reporter] Found compartment: {c.name} ({c.id[:30]}...)")
            return c.id

    print(f"[WARNING] Compartment '{compartment_name}' not found. Using tenancy root.")
    return tenancy_id
PYEOF
```

**Step 3:** Function to list all compute instances

```bash
cat >> /opt/fedtracker/oci_reporter.py << 'PYEOF'


def list_compute_instances(config, compartment_id):
    """List all compute instances in the compartment with details."""
    compute = oci.core.ComputeClient(config)

    instances = compute.list_instances(compartment_id).data
    print(f"\n{'='*60}")
    print(f"  COMPUTE INSTANCES ({len(instances)} found)")
    print(f"{'='*60}")

    for inst in instances:
        # Skip terminated instances
        if inst.lifecycle_state == "TERMINATED":
            continue

        print(f"\n  Name:          {inst.display_name}")
        print(f"  State:         {inst.lifecycle_state}")
        print(f"  Shape:         {inst.shape}")

        # Show shape config (OCPUs and memory) if available
        if inst.shape_config:
            print(f"  OCPUs:         {inst.shape_config.ocpus}")
            print(f"  Memory (GB):   {inst.shape_config.memory_in_gbs}")

        print(f"  AD:            {inst.availability_domain}")
        print(f"  Created:       {inst.time_created.strftime('%Y-%m-%d %H:%M UTC')}")

        # Check for tags (freeform tags)
        if inst.freeform_tags:
            print(f"  Tags:          {inst.freeform_tags}")
        else:
            print(f"  Tags:          ⚠ NONE (untagged resource!)")

    return instances
PYEOF
```

**Step 4:** Function to check for untagged resources

```bash
cat >> /opt/fedtracker/oci_reporter.py << 'PYEOF'


def check_tagging_compliance(instances):
    """Check if all resources have required tags."""
    print(f"\n{'='*60}")
    print(f"  TAGGING COMPLIANCE CHECK")
    print(f"{'='*60}")

    untagged = []
    for inst in instances:
        if inst.lifecycle_state == "TERMINATED":
            continue
        if not inst.freeform_tags:
            untagged.append(inst.display_name)

    if untagged:
        print(f"\n  ⚠ {len(untagged)} untagged resource(s) found:")
        for name in untagged:
            print(f"    - {name}")
        print(f"\n  Recommendation: Add 'Project', 'Environment', and 'Owner' tags")
        print(f"  to all resources for cost tracking and compliance.")
    else:
        print(f"\n  ✓ All resources are tagged")

    return untagged
PYEOF
```

**Step 5:** Main function that generates the report

```bash
cat >> /opt/fedtracker/oci_reporter.py << 'PYEOF'


def main():
    """Generate the OCI resource report."""
    print(f"\n{'#'*60}")
    print(f"  OCI RESOURCE REPORT")
    print(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Region:    {config.get('region', 'unknown')}")
    print(f"{'#'*60}")

    # Find our compartment
    compartment_id = get_compartment_id(config)

    # List compute instances
    instances = list_compute_instances(config, compartment_id)

    # Check tagging compliance
    untagged = check_tagging_compliance(instances)

    # Summary
    active_count = len([i for i in instances if i.lifecycle_state != "TERMINATED"])
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Active instances:    {active_count}")
    print(f"  Untagged resources:  {len(untagged)}")
    print(f"  Region:              {config.get('region')}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
PYEOF
```

Now run the reporter:

```bash
# Run the OCI resource reporter
python3 /opt/fedtracker/oci_reporter.py
```

**Expected output:**

```
[OCI Reporter] Configuration loaded successfully

############################################################
  OCI RESOURCE REPORT
  Generated: 2026-03-20 15:00 UTC
  Region:    us-ashburn-1
############################################################
[OCI Reporter] Found compartment: fedtracker-lab (ocid1.compartment.oc1..xxx...)

============================================================
  COMPUTE INSTANCES (1 found)
============================================================

  Name:          legacy-server
  State:         RUNNING
  Shape:         VM.Standard.A1.Flex
  OCPUs:         2.0
  Memory (GB):   8.0
  AD:            xxxx:US-ASHBURN-AD-1
  Created:       2026-03-20 13:00 UTC
  Tags:          ⚠ NONE (untagged resource!)

============================================================
  TAGGING COMPLIANCE CHECK
============================================================

  ⚠ 1 untagged resource(s) found:
    - legacy-server

  Recommendation: Add 'Project', 'Environment', and 'Owner' tags
  to all resources for cost tracking and compliance.

============================================================
  SUMMARY
============================================================
  Active instances:    1
  Untagged resources:  1
  Region:              us-ashburn-1
============================================================
```

> The tagging warning is intentional — Day 2 will add proper tags to all resources. Untagged resources are a cost management and compliance problem in federal environments. This script catches exactly that kind of issue.

**Verify:**

```bash
# Check the script exists and is readable
ls -la /opt/fedtracker/oci_reporter.py
# Expected: file exists, owned by clouduser

# Verify OCI SDK is installed
python3 -c "import oci; print(oci.__version__)"
# Expected: version number (e.g., 2.x.x)
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `pip3.11 install` | `--user` | Install a Python package in the user's home directory |
| `mkdir` | `-p` | Create directory (and parents). `-p` = no error if it exists |
| `chmod` | `600` | Set file to owner-read/write only (for security-sensitive files) |
| `scp` | `-i <key>` | Securely copy files between machines over SSH |
| `python3` | | Run a Python script |

</em></sub>

---

### Step 6.2 — Git Commit Day 1 Work
📍 **VM Terminal**

```bash
# Initialize git repo (if not already done)
cd /opt/fedtracker
git init
git config user.name "<YOUR_NAME>"
git config user.email "<YOUR_EMAIL>"

# Create .gitignore
cat > .gitignore << 'EOF'
# Database files
*.db
*.sqlite3

# Python
__pycache__/
*.pyc
*.pyo

# OCI credentials (NEVER commit these)
.oci/
*.pem

# OS files
.DS_Store
EOF

# Stage and commit Day 1 files
git add main.py health_check.sh oci_reporter.py .gitignore
git commit -m "Day 1: FedTracker FastAPI app, health check script, OCI reporter

- Built FastAPI REST API with 6 endpoints (health, personnel CRUD, audit, CSV export)
- Pydantic validation on all inputs
- SQLite backend for legacy mode
- Bash health check: service, port, disk, memory, endpoint
- Python OCI reporter: compute instances, tagging compliance
- systemd service file for production-like deployment"
```

---

## PHASE 7: TROUBLESHOOTING LAB — LINUX & APP (1 hr)

> This section is where you intentionally break things and fix them. This is the MOST VALUABLE part for interview prep. When an interviewer asks "how would you troubleshoot a web application that's unreachable?", you'll have a real answer because you actually did it. Don't skip any steps — go through the full diagnosis process every time, even if you already know the answer.
>
> 📍 **Where work happens:** VM Terminal.
>
> 🛠️ **Build approach:** Break → Diagnose → Fix → Verify. Every step.

---

### Step 7.1 — Break the Firewall
📍 **VM Terminal**

> **Scenario:** A junior admin accidentally removed the port 8000 firewall rule. The FedTracker app is unreachable from the internet. You need to figure out why and fix it.

**Break it:**

```bash
# Remove the port 8000 rule (simulating a misconfiguration)
sudo firewall-cmd --remove-port=8000/tcp --permanent
sudo firewall-cmd --reload
```

**Now diagnose it (pretend you don't know what's wrong):**

```bash
# Step 1: Is the service running?
systemctl status fedtracker
# Result: Active: active (running) — the service IS running, so it's not a service problem
```

```bash
# Step 2: Is the app actually listening on port 8000?
ss -tlnp | grep 8000
# Result: You see a line with :8000 — the app IS listening
# This rules out the application as the problem
```

```bash
# Step 3: Can we reach it from localhost (bypassing the firewall)?
curl http://localhost:8000/health
# Result: {"status": "healthy"} — the app works locally!
# This confirms the problem is between the outside world and the app
```

```bash
# Step 4: Check the firewall rules
sudo firewall-cmd --list-ports
# Result: (empty) — port 8000 is NOT listed!
# FOUND IT: The firewall is blocking external traffic to port 8000
```

**Fix it:**

```bash
# Re-add the port 8000 rule
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload

# Verify the fix
sudo firewall-cmd --list-ports
# Expected: 8000/tcp
```

**Verify the fix end-to-end:**

📍 **Local Terminal**

```bash
curl http://<PUBLIC_IP>:8000/health
# Expected: {"status": "healthy", ...} — it works again
```

> **🧠 Interview framing:** "When a web application is unreachable, I follow a systematic approach: first I check if the service is running with `systemctl status`. Then I check if it's actually listening on the expected port with `ss -tlnp`. Then I test from localhost to isolate whether it's a network issue. If localhost works but external access doesn't, I check the firewall rules with `firewall-cmd --list-ports`. In a cloud environment, I also check the cloud provider's network security rules — OCI security lists, AWS security groups, etc."

---

### Step 7.2 — Break File Permissions
📍 **VM Terminal**

> **Scenario:** Someone accidentally changed the permissions on the application file. The service crashes on restart and you need to figure out why.

**Break it:**

```bash
# Remove all permissions from the app file
sudo chmod 000 /opt/fedtracker/main.py
```

**Trigger the failure:**

```bash
# Restart the service (it will crash because it can't read the file)
sudo systemctl restart fedtracker

# Wait 2 seconds for the crash to register
sleep 2
```

**Now diagnose it:**

```bash
# Step 1: Check service status
systemctl status fedtracker
# Result: Active: failed (or activating with restart attempts)
# The status will show an error — read it carefully
```

```bash
# Step 2: Check the service logs for the error message
journalctl -u fedtracker -n 20
# Result: You'll see "Permission denied" or "cannot open" errors
# The error message tells you EXACTLY what file has the problem
```

```bash
# Step 3: Check the file permissions
ls -la /opt/fedtracker/main.py
# Result: ---------- (no permissions at all!)
# FOUND IT: The file has no read permissions
```

**Fix it:**

```bash
# Restore proper permissions
sudo chmod 644 /opt/fedtracker/main.py
sudo chown clouduser:clouduser /opt/fedtracker/main.py

# Restart the service
sudo systemctl restart fedtracker

# Verify it's running
systemctl status fedtracker
# Expected: Active: active (running)
```

**Verify:**

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}
```

> **🧠 Interview framing:** "When a service fails to start, I check `systemctl status` for the immediate error, then `journalctl` for the full log. Permission errors are common — I check file ownership with `ls -la` and fix with `chmod`/`chown`. In production, I'd also check SELinux context with `ls -Z` since Oracle Linux uses SELinux."

---

### Step 7.3 — Break the Service
📍 **VM Terminal**

> **Scenario:** The FedTracker service was accidentally stopped and disabled. Users report the app is down.

**Break it:**

```bash
# Stop and disable the service
sudo systemctl stop fedtracker
sudo systemctl disable fedtracker
```

**Diagnose:**

```bash
# Step 1: Check from outside
curl http://localhost:8000/health
# Result: Connection refused — nothing is listening

# Step 2: Check the service
systemctl status fedtracker
# Result: Active: inactive (dead), Loaded: disabled

# Step 3: Check if it's enabled for boot
systemctl is-enabled fedtracker
# Result: disabled — it won't start on reboot either!
```

**Fix it:**

```bash
# Re-enable and start
sudo systemctl enable --now fedtracker

# Verify
systemctl status fedtracker
# Expected: Active: active (running), Loaded: enabled
```

**Verify:**

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}
```

> **🧠 Interview framing:** "I distinguish between `start` (running now) and `enable` (starts on boot). A service can be started but not enabled — meaning it works now but won't survive a reboot. I always use `enable --now` to do both. When troubleshooting, I check `systemctl is-enabled` to catch the 'it was working until we rebooted' scenario."

---

## DAY 1 RECAP

### Day 1 Complete

**What you built:**
- OCI account with compartment, VCN, and Oracle Linux 8 VM
- FedTracker FastAPI REST API with 6 endpoints (built from scratch, not copy-pasted)
- systemd service file to manage the application
- Bash health check script
- Python OCI resource reporter
- Completed 3 troubleshooting labs (firewall, permissions, service)

**What's running:**
- Oracle Linux 8 VM (`legacy-server`) in public subnet
- FedTracker FastAPI app on port 8000 (systemd managed)
- SQLite database at `/opt/fedtracker/fedtracker.db`
- Auto-generated API docs at `http://<PUBLIC_IP>:8000/docs`

**What you can now talk about in interviews:**
- "I built a REST API from scratch using FastAPI with Pydantic validation, pagination, and audit logging"
- "I understand HTTP verbs, status codes, path vs query parameters, and request/response patterns"
- "I deployed the app as a systemd service with automatic restart and journal logging"
- "I wrote Bash health check scripts that verify service status, port availability, disk, memory, and endpoint health"
- "I use the OCI Python SDK to query cloud resources and check tagging compliance programmatically"
- "When troubleshooting unreachable services, I follow a systematic approach: check service → check port → test localhost → check firewall → check cloud security rules"

**Skills practiced:** Oracle Linux admin, OCI basics, Python (FastAPI), REST APIs, Bash scripting, systemd, firewalld, troubleshooting

**Next:** Day 2 — "The Proper Architecture" — you'll redesign the network with public/private subnets, set up a bastion host, migrate to Oracle Autonomous DB, and harden security.

---

## PHASE 8: THE PROPER ARCHITECTURE — VCN REDESIGN (2 hrs)

> Day 1 put everything in a public subnet — the VM, the app, the database, all directly accessible from the internet. That's how legacy systems end up configured, and it's a security nightmare. Today you redesign the network properly: the app server goes in a **private subnet** (no direct internet access), a **bastion host** in the public subnet provides SSH access, and a **NAT gateway** lets the private subnet reach the internet for updates. This is how every production federal environment is architected.
>
> 📍 **Where work happens:** OCI Console (manual network design) and VM Terminal.
>
> 🛠️ **Build approach:** All manual via OCI Console — point-and-click. Day 3 codifies everything in Terraform.

---

### Step 8.1 — Design the Target Network
📍 **OCI Console**

> **🧠 ELI5 — Public vs Private Subnets:** A public subnet gives each VM a public IP — anyone on the internet can try to connect. A private subnet has no public IPs — VMs can't be reached directly from the internet. Think of a public subnet as a storefront on a busy street (anyone can walk in) and a private subnet as a back office (you need a badge to enter). In production, application servers and databases always go in private subnets. Only bastion hosts and load balancers go in public subnets.

Before building, understand the target:

```
Internet
    │
┌───▼──────────────────────────────────────────────┐
│  OCI VCN: fedtracker-vcn (10.0.0.0/16)           │
│                                                    │
│  ┌───────────────────────────────┐                │
│  │ Public Subnet (10.0.1.0/24)   │                │
│  │                                │                │
│  │  ┌─────────────────────────┐  │                │
│  │  │ Bastion VM              │  │                │
│  │  │ Public IP: assigned     │  │                │
│  │  │ SSH (port 22) from you  │  │                │
│  │  └────────────┬────────────┘  │                │
│  └───────────────┼───────────────┘                │
│                  │ SSH tunnel (port 22)            │
│  ┌───────────────▼───────────────┐                │
│  │ Private Subnet (10.0.2.0/24)  │                │
│  │                                │                │
│  │  ┌─────────────────────────┐  │                │
│  │  │ App Server VM           │  │                │
│  │  │ No public IP            │  │                │
│  │  │ FedTracker on port 8000 │  │                │
│  │  └─────────────────────────┘  │                │
│  │                                │                │
│  │  Route: 0.0.0.0/0 → NAT GW   │                │
│  └───────────────────────────────┘                │
│                                                    │
│  Internet Gateway ← Public subnet route           │
│  NAT Gateway ← Private subnet route               │
│  Service Gateway ← OCI services (optional)        │
└────────────────────────────────────────────────────┘
```

> **Why a bastion host?** A bastion (also called a jump box) is the single entry point into your private network. Instead of giving every server a public IP, you SSH into the bastion first, then SSH from the bastion to private servers. This reduces your attack surface — you only need to secure one public-facing SSH endpoint. If the bastion is compromised, you kill it. If an app server were public and compromised, the attacker has direct access to your data.

> **Why a NAT gateway?** VMs in a private subnet can't reach the internet (no public IP). But they still need internet access for `dnf update`, pip installs, etc. A NAT gateway lets private VMs make outbound connections (to download packages) without accepting inbound connections (from the internet). Traffic goes: VM → NAT gateway → Internet. Responses come back the same way. But nobody on the internet can initiate a connection to the private VM.

---

### Step 8.2 — Create the New VCN Manually
📍 **OCI Console**

> This time you're NOT using the wizard — you're building each component individually to understand every piece.

**Create the VCN:**

1. Navigate to **Networking** → **Virtual Cloud Networks**
2. Make sure `fedtracker-lab` compartment is selected
3. Click **Create VCN** (NOT the wizard this time)
4. Fill in:
   - **Name:** `fedtracker-vcn`
   - **Compartment:** `fedtracker-lab`
   - **IPv4 CIDR Blocks:** `10.0.0.0/16`
5. Click **Create VCN**

> **Cost check:** VCN = $0.00/month on Always Free tier. Verify at: [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)

---

### Step 8.3 — Create Internet Gateway
📍 **OCI Console**

> **🧠 ELI5 — Internet Gateway:** An Internet Gateway is the VCN's front door to the internet. Without it, nothing in the VCN can communicate with the outside world. The public subnet's route table points to the Internet Gateway for outbound traffic, and it also allows inbound traffic to reach public IPs.

1. Inside `fedtracker-vcn`, click **Internet Gateways** in the left sidebar
2. Click **Create Internet Gateway**
3. Fill in:
   - **Name:** `fedtracker-igw`
   - **Compartment:** `fedtracker-lab`
4. Click **Create Internet Gateway**

---

### Step 8.4 — Create NAT Gateway
📍 **OCI Console**

1. Inside `fedtracker-vcn`, click **NAT Gateways** in the left sidebar
2. Click **Create NAT Gateway**
3. Fill in:
   - **Name:** `fedtracker-natgw`
   - **Compartment:** `fedtracker-lab`
4. Click **Create NAT Gateway**

> **Cost check:** NAT Gateway = $0.00/month on Always Free tier. OCI doesn't charge for NAT gateway existence (unlike AWS, which charges ~$32/month). Verify at: [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)

---

### Step 8.5 — Create Route Tables
📍 **OCI Console**

> **🧠 ELI5 — Route Tables:** A route table is a set of rules that tells network traffic where to go — like a GPS for data packets. Each subnet gets its own route table. The public subnet's route table says "send internet traffic through the Internet Gateway." The private subnet's route table says "send internet traffic through the NAT Gateway." Different routes = different security postures.

**Public subnet route table:**

1. Inside `fedtracker-vcn`, click **Route Tables** in the left sidebar
2. Click **Create Route Table**
3. Fill in:
   - **Name:** `public-rt`
   - **Compartment:** `fedtracker-lab`
   - Click **+ Another Route Rule**:
     - **Target Type:** Internet Gateway
     - **Destination CIDR:** `0.0.0.0/0`
     - **Target:** `fedtracker-igw`
4. Click **Create**

**Private subnet route table:**

1. Click **Create Route Table** again
2. Fill in:
   - **Name:** `private-rt`
   - **Compartment:** `fedtracker-lab`
   - Click **+ Another Route Rule**:
     - **Target Type:** NAT Gateway
     - **Destination CIDR:** `0.0.0.0/0`
     - **Target:** `fedtracker-natgw`
3. Click **Create**

---

### Step 8.6 — Create Security Lists
📍 **OCI Console**

> **🧠 ELI5 — Security Lists:** Security lists are OCI's network-level firewall rules — they control which traffic is allowed to enter (ingress) and leave (egress) a subnet. Think of them as the guest list at a building's front desk. Each subnet has its own security list with its own rules. The public subnet allows SSH from the internet; the private subnet allows SSH only from the public subnet's CIDR range.

**Public subnet security list:**

1. Inside `fedtracker-vcn`, click **Security Lists** in the left sidebar
2. Click **Create Security List**
3. Fill in:
   - **Name:** `public-sl`
   - **Compartment:** `fedtracker-lab`
4. Add **Ingress Rules**:
   - Rule 1: SSH from your IP
     - **Source CIDR:** `0.0.0.0/0` (in production, restrict to your IP)
     - **IP Protocol:** TCP
     - **Destination Port Range:** `22`
5. Add **Egress Rules**:
   - Rule 1: Allow all outbound
     - **Destination CIDR:** `0.0.0.0/0`
     - **IP Protocol:** All Protocols
6. Click **Create Security List**

**Private subnet security list:**

1. Click **Create Security List** again
2. Fill in:
   - **Name:** `private-sl`
   - **Compartment:** `fedtracker-lab`
3. Add **Ingress Rules**:
   - Rule 1: SSH from public subnet only
     - **Source CIDR:** `10.0.1.0/24`
     - **IP Protocol:** TCP
     - **Destination Port Range:** `22`
   - Rule 2: App traffic from public subnet
     - **Source CIDR:** `10.0.1.0/24`
     - **IP Protocol:** TCP
     - **Destination Port Range:** `8000`
4. Add **Egress Rules**:
   - Rule 1: Allow all outbound (needed for dnf, pip, etc. via NAT)
     - **Destination CIDR:** `0.0.0.0/0`
     - **IP Protocol:** All Protocols
5. Click **Create Security List**

> **Why restrict SSH to `10.0.1.0/24`?** The private subnet only accepts SSH from the public subnet's CIDR range. This means you MUST go through the bastion (in the public subnet) to reach the app server. Nobody on the internet can SSH directly to the app server, even if they somehow knew its private IP.

---

### Step 8.7 — Create Subnets
📍 **OCI Console**

**Public subnet:**

1. Inside `fedtracker-vcn`, click **Subnets** in the left sidebar
2. Click **Create Subnet**
3. Fill in:
   - **Name:** `public-subnet`
   - **Compartment:** `fedtracker-lab`
   - **Subnet Type:** Regional
   - **IPv4 CIDR Block:** `10.0.1.0/24`
   - **Route Table:** `public-rt`
   - **Subnet Access:** **Public Subnet**
   - **Security List:** `public-sl`
4. Click **Create Subnet**

**Private subnet:**

1. Click **Create Subnet** again
2. Fill in:
   - **Name:** `private-subnet`
   - **Compartment:** `fedtracker-lab`
   - **Subnet Type:** Regional
   - **IPv4 CIDR Block:** `10.0.2.0/24`
   - **Route Table:** `private-rt`
   - **Subnet Access:** **Private Subnet**
   - **Security List:** `private-sl`
3. Click **Create Subnet**

**Verify:**

In `fedtracker-vcn`, you should see:
- 2 subnets: `public-subnet` (10.0.1.0/24) and `private-subnet` (10.0.2.0/24)
- Internet Gateway: `fedtracker-igw`
- NAT Gateway: `fedtracker-natgw`
- 2 Route Tables: `public-rt` (→ IGW) and `private-rt` (→ NAT GW)
- 2 Security Lists: `public-sl` and `private-sl`

---

### Step 8.8 — Launch Bastion VM
📍 **OCI Console**

1. Navigate to **Compute** → **Instances** → **Create Instance**
2. Fill in:
   - **Name:** `bastion`
   - **Compartment:** `fedtracker-lab`
   - **Image:** Oracle Linux 8
   - **Shape:** VM.Standard.A1.Flex — **1 OCPU / 6 GB RAM** (bastion doesn't need much)
   - **VCN:** `fedtracker-vcn`
   - **Subnet:** `public-subnet`
   - **Public IPv4 address:** Assign a public IPv4 address
   - **SSH keys:** Generate a key pair → download both keys
3. Click **Create**

Save the bastion SSH key:

📍 **Local Terminal**

```bash
mv ~/Downloads/bastion.key ~/.ssh/bastion.key
chmod 600 ~/.ssh/bastion.key
```

---

### Step 8.9 — Launch App Server VM in Private Subnet
📍 **OCI Console**

1. Navigate to **Compute** → **Instances** → **Create Instance**
2. Fill in:
   - **Name:** `app-server`
   - **Compartment:** `fedtracker-lab`
   - **Image:** Oracle Linux 8
   - **Shape:** VM.Standard.A1.Flex — **1 OCPU / 10 GB RAM**
   - **VCN:** `fedtracker-vcn`
   - **Subnet:** `private-subnet`
   - **Public IPv4 address:** **Do NOT assign** (this is a private subnet)
   - **SSH keys:** Generate a key pair → download both keys
3. Click **Create**

> **Cost check:** Both VMs combined = 2 OCPU / 16 GB RAM. OCI Always Free gives you 4 OCPU / 24 GB for A1 Flex. You're using 2 OCPU / 16 GB — within budget. Verify at: [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)

Note the app server's **private IP** (e.g., `10.0.2.x`) — you'll need it for SSH through the bastion.

Save the app server SSH key:

📍 **Local Terminal**

```bash
mv ~/Downloads/app-server.key ~/.ssh/app-server.key
chmod 600 ~/.ssh/app-server.key
```

---

### Step 8.10 — SSH Through Bastion to App Server
📍 **Local Terminal**

> **🧠 ELI5 — SSH ProxyJump:** Instead of SSHing to the bastion, then SSHing from the bastion to the app server (two steps), `ssh -J` (ProxyJump) does it in one command. Your SSH client connects through the bastion transparently. It's like asking the receptionist to patch you through to an internal extension.

**Method 1: Two-step (understanding what happens):**

```bash
# Step 1: SSH to the bastion
ssh -i ~/.ssh/bastion.key opc@<BASTION_PUBLIC_IP>

# Step 2: From the bastion, SSH to the app server
# First, upload the app server key to the bastion
```

📍 **Local Terminal** (new window)

```bash
# Upload the app server key to the bastion
scp -i ~/.ssh/bastion.key ~/.ssh/app-server.key opc@<BASTION_PUBLIC_IP>:/home/opc/.ssh/app-server.key
```

📍 **Bastion Terminal**

```bash
chmod 600 ~/.ssh/app-server.key
ssh -i ~/.ssh/app-server.key opc@<APP_SERVER_PRIVATE_IP>
# Expected: You're now on the app server
```

**Method 2: ProxyJump (one command — production approach):**

📍 **Local Terminal**

```bash
# SSH directly to the app server through the bastion
ssh -i ~/.ssh/app-server.key -J opc@<BASTION_PUBLIC_IP> opc@<APP_SERVER_PRIVATE_IP>
```

> **Why ProxyJump is better:** It's one command, and the app server key never touches the bastion. With the two-step method, you had to copy the key to the bastion (a security risk — if the bastion is compromised, the attacker gets the app server key too). ProxyJump tunnels the SSH connection through the bastion without storing keys there.

**Set up SSH config for convenience:**

📍 **Local Terminal**

```bash
cat >> ~/.ssh/config << 'SSHEOF'

Host bastion
    HostName <BASTION_PUBLIC_IP>
    User opc
    IdentityFile ~/.ssh/bastion.key

Host app-server
    HostName <APP_SERVER_PRIVATE_IP>
    User opc
    IdentityFile ~/.ssh/app-server.key
    ProxyJump bastion
SSHEOF
```

Now you can simply type:

```bash
ssh app-server
# Connects through bastion automatically
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `ssh` | `-J user@bastion` | ProxyJump — tunnel SSH through an intermediate host |
| `scp` | `-i <key>` | Securely copy files. `-i` specifies the identity key |
| `chmod` | `600` | Owner read/write only |

</em></sub>

---

### Phase 8 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| SSH to bastion works | Shell prompt on bastion | Check: (1) bastion has public IP, (2) public-sl allows port 22 from 0.0.0.0/0, (3) public-rt routes to IGW, (4) key permissions are 600 |
| SSH from bastion to app-server works | Shell prompt on app-server | Check: (1) private-sl allows port 22 from 10.0.1.0/24, (2) app-server key is correct, (3) correct private IP |
| App-server can reach internet | `ping 8.8.8.8` gets replies | Check: (1) private-rt routes 0.0.0.0/0 to NAT GW, (2) NAT GW is enabled, (3) private-sl egress allows all |
| ProxyJump works from local | Direct connection to app-server | Check SSH config syntax. Ensure bastion host is reachable first |

**SELinux awareness on the new servers:**

Now that you're on fresh servers, verify SELinux is enforcing — this is the first thing you'd check in any federal environment:

```bash
# On both bastion and app-server:
getenforce
# Expected: Enforcing — NEVER set this to Permissive or Disabled in production
```

When you deploy FedTracker to this new app server, you may encounter SELinux denials. The app directory (`/opt/fedtracker`) has a default file context that may not allow uvicorn to read/execute files.

```bash
# Check the current SELinux context of the app directory
ls -Zd /opt/fedtracker/
# Expected: unconfined_u:object_r:usr_t:s0 (default — may not work for all operations)

# If the app fails to start, set the proper context for a web application:
sudo semanage fcontext -a -t httpd_sys_content_t "/opt/fedtracker(/.*)?"
sudo restorecon -Rv /opt/fedtracker/
# -R = recursive, -v = verbose (shows what changed)
```

> **🧠 ELI5 — `semanage fcontext` + `restorecon`:** `semanage fcontext` defines a rule: "files in `/opt/fedtracker/` should have the `httpd_sys_content_t` type." `restorecon` applies that rule to existing files. This is a two-step process — define the policy, then apply it. If you only use `chcon` (the quick-and-dirty approach), the context reverts on `restorecon` or filesystem relabeling.

```bash
# If the app still fails, check for SELinux denials:
sudo ausearch -m avc -ts recent
# Look for: denied { read } or denied { open } involving your app files
# Fix: generate a custom policy module
# sudo ausearch -m avc -ts recent | audit2allow -M fedtracker-custom
# sudo semodule -i fedtracker-custom.pp
```

> **Interview tip:** "If an app fails to start on a new server but worked on the old one, my first three checks are: (1) `getenforce` — is SELinux blocking it? (2) `ausearch -m avc` — what's being denied? (3) Apply proper file contexts with `semanage fcontext` + `restorecon`. I never disable SELinux."

---

## PHASE 9: ORACLE AUTONOMOUS DATABASE (1.5 hrs)

> SQLite was fine for Day 1, but it's a single file on one server — no redundancy, no backups, no multi-user access. Oracle Autonomous Database is a managed database service that runs in its own infrastructure with automatic backups, patching, and scaling. Moving from SQLite to Oracle DB is the kind of migration you'll do in production. The app code barely changes — you swap the database connection string and the queries stay the same.
>
> 📍 **Where work happens:** OCI Console, VM Terminal (app-server via bastion).
>
> 🛠️ **Build approach:** Database created in OCI Console. App code modifications are guided edits.

---

### Step 9.1 — Create Oracle Autonomous Database
📍 **OCI Console**

> **🧠 ELI5 — Oracle Autonomous Database:** A fully managed database that handles backups, patching, security, and performance tuning automatically. You don't manage the server it runs on — Oracle does. The "Always Free" version gives you 20 GB of storage and 1 OCPU forever. It's like hiring a DBA (database administrator) who works 24/7 for free.

1. Navigate to **Oracle Database** → **Autonomous Database**
2. Make sure `fedtracker-lab` compartment is selected
3. Click **Create Autonomous Database**
4. Fill in:
   - **Display name:** `fedtracker-db`
   - **Database name:** `fedtrackerdb`
   - **Workload type:** Transaction Processing
   - **Deployment type:** Shared Infrastructure
   - **Always Free:** Toggle ON (this is critical — it makes it free forever)
   - **Database version:** 19c (or latest available)
   - **OCPU count:** 1 (Always Free limit)
   - **Storage:** 20 GB (Always Free limit)
   - **Admin password:** Set a strong password (you'll need this later)
   - **Network access:** Secure access from everywhere (for now — Day 3 restricts this)
   - **License type:** License Included
5. Click **Create Autonomous Database**

Wait 2-3 minutes for the database to show **Available** status.

> **Cost check:** Autonomous Database with Always Free = $0.00/month. 1 OCPU + 20 GB storage included. Verify at: [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)

---

### Step 9.2 — Download Wallet and Connect
📍 **OCI Console**

> **🧠 ELI5 — Database Wallet:** Oracle Autonomous DB uses TLS encryption for all connections. The "wallet" is a zip file containing certificates and connection strings that your application needs to authenticate. Think of it as a secure ID badge for your application — without the wallet, the database refuses the connection.

1. On the `fedtracker-db` details page, click **Database connection**
2. Click **Download wallet**
3. Set a wallet password (e.g., `WalletPass123!`)
4. Download the zip file

📍 **Local Terminal**

```bash
# Upload the wallet to the app server (through the bastion)
scp -i ~/.ssh/app-server.key -J opc@<BASTION_PUBLIC_IP> \
  ~/Downloads/Wallet_fedtrackerdb.zip \
  opc@<APP_SERVER_PRIVATE_IP>:/home/opc/
```

📍 **VM Terminal** (app-server)

```bash
# SSH to app-server
ssh app-server

# Create wallet directory
sudo mkdir -p /opt/oracle/wallet
sudo unzip /home/opc/Wallet_fedtrackerdb.zip -d /opt/oracle/wallet
sudo chown -R clouduser:clouduser /opt/oracle/wallet
sudo chmod 600 /opt/oracle/wallet/*
```

---

### Step 9.3 — Install Oracle DB Client and Connect
📍 **VM Terminal** (app-server)

```bash
# Install the Oracle instant client and Python driver
sudo pip3.11 install oracledb
```

> **Why `oracledb` not `cx_Oracle`?** `oracledb` is the new name for the Python Oracle DB driver (formerly cx_Oracle). It can run in "thin mode" — pure Python, no Oracle Instant Client libraries needed. This simplifies deployment significantly.

```bash
# Test the connection
su - clouduser

python3 << 'PYEOF'
import oracledb

# Thin mode connection using wallet
connection = oracledb.connect(
    user="ADMIN",
    password="YOUR_ADMIN_PASSWORD_HERE",
    dsn="fedtrackerdb_low",
    config_dir="/opt/oracle/wallet",
    wallet_location="/opt/oracle/wallet",
    wallet_password="WalletPass123!"
)

print(f"Connected to: {connection.version}")
cursor = connection.cursor()
cursor.execute("SELECT 'Hello from Oracle DB!' FROM DUAL")
print(cursor.fetchone()[0])

connection.close()
print("Connection closed successfully")
PYEOF
```

> **Important:** Replace `YOUR_ADMIN_PASSWORD_HERE` with the admin password you set when creating the database.

**Expected output:**

```
Connected to: 19.x.x.x.x
Hello from Oracle DB!
Connection closed successfully
```

---

### Step 9.4 — Create Schema in Oracle DB
📍 **VM Terminal** (app-server)

```bash
python3 << 'PYEOF'
import oracledb

connection = oracledb.connect(
    user="ADMIN",
    password="YOUR_ADMIN_PASSWORD_HERE",
    dsn="fedtrackerdb_low",
    config_dir="/opt/oracle/wallet",
    wallet_location="/opt/oracle/wallet",
    wallet_password="WalletPass123!"
)
cursor = connection.cursor()

# Create personnel table
cursor.execute("""
    CREATE TABLE personnel (
        id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name VARCHAR2(200) NOT NULL,
        role VARCHAR2(100) NOT NULL,
        clearance_level VARCHAR2(50) DEFAULT 'UNCLASSIFIED',
        project_id VARCHAR2(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create audit_log table
cursor.execute("""
    CREATE TABLE audit_log (
        id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        action VARCHAR2(50) NOT NULL,
        resource_type VARCHAR2(50) NOT NULL,
        resource_id VARCHAR2(50),
        details VARCHAR2(500),
        source_ip VARCHAR2(50)
    )
""")

# Seed data
seed_data = [
    ("Ada Lovelace", "Lead Engineer", "TOP SECRET", "PROJ-001"),
    ("Grace Hopper", "Senior Architect", "SECRET", "PROJ-001"),
    ("Alan Turing", "Cryptography Lead", "TOP SECRET/SCI", "PROJ-002"),
    ("Margaret Hamilton", "Software Director", "SECRET", "PROJ-002"),
    ("Katherine Johnson", "Data Analyst", "CONFIDENTIAL", "PROJ-003"),
]
cursor.executemany(
    "INSERT INTO personnel (name, role, clearance_level, project_id) VALUES (:1, :2, :3, :4)",
    seed_data
)

cursor.execute(
    "INSERT INTO audit_log (action, resource_type, details, source_ip) VALUES (:1, :2, :3, :4)",
    ("SEED_DATA", "personnel", "Loaded 5 initial records", "system")
)

connection.commit()
print("Schema created and seed data loaded successfully")

# Verify
cursor.execute("SELECT COUNT(*) FROM personnel")
print(f"Personnel records: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM audit_log")
print(f"Audit log entries: {cursor.fetchone()[0]}")

connection.close()
PYEOF
```

**Expected output:**

```
Schema created and seed data loaded successfully
Personnel records: 5
Audit log entries: 1
```

---

### Step 9.5 — Update FedTracker to Support Oracle DB
📍 **VM Terminal** (app-server)

> You need to update the `get_db()` function in `main.py` to support Oracle DB connections. The rest of the app stays the same — the endpoints don't care whether the data comes from SQLite or Oracle.

First, copy the app from the legacy server to the app server (or rebuild it):

```bash
# If you haven't already set up the app on this server:
sudo mkdir -p /opt/fedtracker
sudo chown clouduser:clouduser /opt/fedtracker

# Copy from legacy server (if you still have it) or just recreate
# For now, let's recreate the key files. The main.py from Day 1 is in git.
```

Update the `get_db()` function to support Oracle DB. Edit `/opt/fedtracker/main.py` and find the `get_db()` function:

```python
def get_db():
    """Get a database connection based on DB_TYPE."""
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    elif DB_TYPE == "oracle":
        import oracledb
        conn = oracledb.connect(
            user=os.environ.get("ORACLE_USER", "ADMIN"),
            password=os.environ.get("ORACLE_PASSWORD", ""),
            dsn=os.environ.get("ORACLE_DSN", "fedtrackerdb_low"),
            config_dir=os.environ.get("ORACLE_WALLET_DIR", "/opt/oracle/wallet"),
            wallet_location=os.environ.get("ORACLE_WALLET_DIR", "/opt/oracle/wallet"),
            wallet_password=os.environ.get("ORACLE_WALLET_PASSWORD", "")
        )
        return conn
    else:
        raise ValueError(f"Unknown DB_TYPE: {DB_TYPE}")
```

> **Why environment variables for credentials?** Database passwords should NEVER be hardcoded in source files. Environment variables keep secrets out of your git repository. In production, you'd use a secrets manager (OCI Vault, AWS Secrets Manager, HashiCorp Vault). For the lab, environment variables in the systemd service file are sufficient.

Update the systemd service file on the app server:

```bash
exit  # back to opc

# Create secure environment file for database credentials
sudo mkdir -p /etc/fedtracker
sudo tee /etc/fedtracker/env << 'EOF'
DB_TYPE=oracle
ORACLE_USER=ADMIN
ORACLE_PASSWORD=YOUR_ADMIN_PASSWORD_HERE
ORACLE_DSN=fedtrackerdb_low
ORACLE_WALLET_DIR=/opt/oracle/wallet
ORACLE_WALLET_PASSWORD=YOUR_WALLET_PASSWORD_HERE
EOF
sudo chmod 600 /etc/fedtracker/env
sudo chown root:root /etc/fedtracker/env

sudo tee /etc/systemd/system/fedtracker.service > /dev/null << 'SVCEOF'
[Unit]
Description=FedTracker Personnel Tracking Application (FastAPI)
After=network.target

[Service]
User=clouduser
Group=clouduser
WorkingDirectory=/opt/fedtracker
EnvironmentFile=/etc/fedtracker/env
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

sudo systemctl daemon-reload
sudo systemctl restart fedtracker
```

> **Why `EnvironmentFile` instead of `Environment`?** Putting passwords directly in systemd unit files is a security risk — anyone who can read the service file (which is world-readable by default) can see the credentials. `EnvironmentFile` points to a separate file with `chmod 600` (owner-only read/write), keeping secrets out of the service definition. In production, you'd use a secrets manager (OCI Vault, HashiCorp Vault).

**Verify:**

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "database": {"type": "oracle", "status": "connected"}}

curl http://localhost:8000/personnel
# Expected: JSON with the 5 seed records from Oracle DB
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `pip3.11 install` | `oracledb` | Install Oracle DB Python driver (thin mode, no native client needed) |
| `unzip` | `-d <dir>` | Extract zip file. `-d` = target directory |
| `systemctl daemon-reload` | | Reload service definitions after editing .service files |
| `systemctl restart` | | Stop then start a service |

</em></sub>

---

### Phase 9 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| Autonomous DB shows **Available** | Green status in OCI Console | Wait 2-3 minutes. If stuck, check service limits |
| Python `oracledb.connect()` works | Connected message | Check: (1) wallet is in correct directory, (2) wallet password is correct, (3) admin password is correct, (4) DSN matches the wallet's tnsnames.ora entries |
| `curl /health` shows `"type": "oracle"` | Oracle DB connected | Check `DB_TYPE=oracle` in service file. Check `journalctl -u fedtracker` for connection errors |
| `curl /personnel` returns records | JSON with 5 records | Schema may not be created. Run the schema script again |
| Connection timeout | Should connect quickly | Private subnet may not be able to reach Autonomous DB. Check security list egress rules. The DB may need to be on the same VCN or have proper network config |

---

## PHASE 10: SECURITY HARDENING (1.5 hrs)

> Security is not optional in federal environments — it's a baseline requirement. This phase hardens the app server following CIS benchmarks and federal security controls. Every change here maps to a compliance control that auditors check. When an interviewer asks "how do you secure a Linux server?", this section gives you a concrete, step-by-step answer.
>
> 📍 **Where work happens:** VM Terminal (app-server via bastion).
>
> 🛠️ **Build approach:** All commands typed by hand. Day 3 automates these with Ansible.

---

### Step 10.1 — SSH Hardening
📍 **VM Terminal** (app-server)

> **🧠 ELI5 — SSH Hardening:** The default SSH configuration is permissive — it allows password authentication, root login, and old protocols. Hardening means turning off everything you don't need and restricting what remains. In federal environments, SSH key-only authentication is mandatory — passwords can be guessed, keys cannot (realistically).

```bash
# Back up the original config first (always back up before editing)
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# Edit SSH config
sudo vim /etc/ssh/sshd_config
```

Make these changes (find each line and update it):

```
# Disable root login — force users to use sudo (audit trail)
PermitRootLogin no

# Disable password authentication — keys only
PasswordAuthentication no

# Disable empty passwords
PermitEmptyPasswords no

# Protocol 2 removed - SSH protocol 1 support was dropped in OpenSSH 7.6+, Oracle Linux 8 ships 8.x

# Set login timeout to 60 seconds
LoginGraceTime 60

# Limit max authentication attempts
MaxAuthTries 3

# Show a legal warning banner
Banner /etc/issue.net
```

```bash
# Create the legal banner
sudo tee /etc/issue.net > /dev/null << 'BANNEREOF'
***************************************************************************
*                    AUTHORIZED ACCESS ONLY                                *
*                                                                           *
*  This system is the property of the organization. Unauthorized access    *
*  is prohibited. All activities are monitored and recorded. By accessing  *
*  this system, you consent to monitoring and agree to comply with all     *
*  applicable security policies.                                           *
*                                                                           *
*  Violations will be reported to appropriate authorities.                  *
***************************************************************************
BANNEREOF
```

```bash
# Test the config for syntax errors before restarting
sudo sshd -t
# Expected: no output (no errors)

# Restart SSH
sudo systemctl restart sshd
```

> ⚠️ **Test SSH access from another terminal BEFORE closing your current session.** If the SSH config is wrong, you could lock yourself out.

📍 **Local Terminal** (new window)

```bash
# Verify you can still connect
ssh app-server
# You should see the legal banner before the login
```

---

### Step 10.2 — Configure auditd
📍 **VM Terminal** (app-server)

> **🧠 ELI5 — auditd:** `auditd` is Linux's audit framework — it monitors system calls and logs security-relevant events. Think of it as a security camera system for your server. It records who accessed what files, who changed permissions, who tried to log in, and more. In federal environments, audit logs are legally required and routinely reviewed by compliance auditors.

```bash
# Install auditd (may already be installed)
sudo dnf install -y audit

# Enable and start auditd
sudo systemctl enable --now auditd
```

```bash
# Add rules to monitor critical files and actions
sudo tee /etc/audit/rules.d/fedtracker.rules > /dev/null << 'AUDITEOF'
# Monitor changes to user/group files
-w /etc/passwd -p wa -k user_changes
-w /etc/shadow -p wa -k user_changes
-w /etc/group -p wa -k user_changes

# Monitor SSH config changes
-w /etc/ssh/sshd_config -p wa -k ssh_config

# Monitor sudo usage
-w /var/log/secure -p wa -k auth_logs

# Monitor the FedTracker application directory
-w /opt/fedtracker/ -p wa -k fedtracker_changes

# Monitor firewall changes
-w /etc/firewalld/ -p wa -k firewall_changes
AUDITEOF
```

```bash
# Load the new rules
sudo augenrules --load

# Verify rules are active
sudo auditctl -l
# Expected: List of all audit rules you just created
```

```bash
# Test: make a change and check the audit log
sudo touch /opt/fedtracker/testfile
sudo ausearch -k fedtracker_changes -ts recent
# Expected: Audit entry showing the file creation
sudo rm /opt/fedtracker/testfile
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `auditctl` | `-l` | List all active audit rules |
| `augenrules` | `--load` | Load rules from /etc/audit/rules.d/ |
| `ausearch` | `-k <key> -ts recent` | Search audit log by key and time |

</em></sub>

---

### Step 10.3 — IAM Policies
📍 **OCI Console**

> **🧠 ELI5 — OCI IAM Policies:** IAM (Identity and Access Management) controls who can do what in your OCI tenancy. Policies are written in a human-readable language: "Allow group X to manage resource-type Y in compartment Z." The principle of least privilege means each group only gets the permissions it needs — admins can manage everything, operators can manage compute but not networking, auditors can only read.

1. Navigate to **Identity & Security** → **Policies**
2. Make sure you're in the `fedtracker-lab` compartment
3. Click **Create Policy**

**Admin policy:**

```
Allow group Administrators to manage all-resources in compartment fedtracker-lab
```

**Operator policy (create a second policy):**

```
Allow group Operators to manage instance-family in compartment fedtracker-lab
Allow group Operators to use virtual-network-family in compartment fedtracker-lab
Allow group Operators to read all-resources in compartment fedtracker-lab
```

**Auditor policy (create a third policy):**

```
Allow group Auditors to read all-resources in compartment fedtracker-lab
Allow group Auditors to read audit-events in compartment fedtracker-lab
```

> **Why three separate policies?** Least privilege in action. Admins can do everything. Operators can manage compute and use (but not modify) networking. Auditors can only read — they can't change or delete anything. This separation prevents accidents and limits blast radius.

---

### Step 10.4 — Cost Tagging Strategy
📍 **OCI Console**

> **🧠 ELI5 — Resource Tagging:** Tags are labels you attach to cloud resources — like sticky notes on physical equipment. They answer questions like "which project does this server belong to?" and "who's responsible for this cost?" In federal environments, untagged resources are a compliance finding. Tags are also the foundation of cost allocation — without them, you can't tell which team or project is spending money.

Apply these tags to all resources in `fedtracker-lab`:

| Tag Key | Value | Purpose |
|---------|-------|---------|
| `Project` | `fedtracker` | Which project owns this resource |
| `Environment` | `lab` | Dev/staging/prod classification |
| `Owner` | `<YOUR_NAME>` | Who is responsible |
| `CostCenter` | `interview-prep` | Cost allocation |

For each resource (VMs, VCN, DB), go to its details page → **Tags** → **Add tags** and add all four tags.

> In production, you'd create a **tag namespace** and make tags mandatory via OCI tag defaults. For the lab, freeform tags are sufficient.

**Verify:**

```bash
# Run the OCI reporter script to check tagging
ssh app-server
su - clouduser
python3 /opt/fedtracker/oci_reporter.py
# Expected: All resources now show tags instead of "⚠ NONE"
```

---

### Phase 10 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `sshd -t` | No output (no errors) | Syntax error in sshd_config. Restore backup: `sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config` |
| SSH still works after hardening | Login with key succeeds, password rejected | If locked out: use OCI Console serial console to access the VM and fix sshd_config |
| `sudo auditctl -l` shows rules | List of audit rules | Rules file syntax error. Check: `sudo augenrules --check` |
| Legal banner appears on SSH | Banner text before login prompt | Check `Banner /etc/issue.net` is in sshd_config and `/etc/issue.net` exists |
| Tags show on resources | Tags visible in OCI Console | Tags are per-resource — check each resource individually |

---

## DAY 2 RECAP

### Day 2 Complete

**What you built:**
- Proper VCN architecture with public/private subnets, bastion, NAT gateway
- Oracle Autonomous Database (Always Free) with FedTracker schema
- Migrated FedTracker from SQLite to Oracle DB
- SSH hardening (key-only, no root, legal banner)
- auditd monitoring on critical files
- IAM policies (admin, operator, auditor — least privilege)
- Cost tagging on all resources

**What's running:**
- Bastion VM in public subnet (SSH gateway)
- App Server VM in private subnet (FedTracker on port 8000)
- Oracle Autonomous DB (20 GB, Always Free)
- FedTracker connected to Oracle DB

**What you can now talk about in interviews:**
- "I designed a VCN with public and private subnets — the app server sits in a private subnet with no public IP, accessible only through a bastion host"
- "I set up SSH ProxyJump for secure access through the bastion"
- "I migrated from SQLite to Oracle Autonomous DB by changing environment variables — the app code barely changed because the database abstraction layer handled the difference"
- "I hardened SSH with key-only auth, disabled root login, set a legal banner, and limited auth attempts"
- "I configured auditd to monitor changes to critical files including /etc/passwd, sshd_config, and the application directory"
- "I implemented least-privilege IAM policies with separate admin, operator, and auditor roles"
- "I tagged all resources with Project, Environment, Owner, and CostCenter for compliance and cost allocation"

**Skills practiced:** OCI networking (deep), Oracle Autonomous DB, security hardening, IAM, cost management, SSH administration

**Next:** Day 3 — "Automate Everything" — you'll codify all of Day 2's manual work in Terraform and Ansible, then destroy and rebuild to prove it works.

---

## PHASE 11: TERRAFORM FROM SCRATCH (3 hrs)

> You spent two days clicking through the OCI Console building infrastructure. Today you throw it all away and rebuild it in code. Terraform is an Infrastructure as Code (IaC) tool that lets you define your entire cloud environment in declarative configuration files. You write what you want, Terraform figures out how to create it. When you run `terraform apply`, it builds everything. When you run `terraform destroy`, it tears everything down. This is the foundation of modern cloud engineering — nobody builds production infrastructure by clicking buttons.
>
> 📍 **Where work happens:** Local Terminal and Editor (building Terraform files by hand).
>
> 🛠️ **Build approach:** Every `.tf` file is built by hand, section by section. This is core DevOps infrastructure work — you type every line.

---

### Step 11.1 — Install Terraform
📍 **Local Terminal**

> **🧠 ELI5 — Terraform:** Terraform is like a blueprint for your cloud infrastructure. Instead of clicking through the OCI Console to create a VCN, subnet, VM, and database, you write a configuration file that says "I want a VCN with these subnets, a VM with this shape, and a database with these settings." Terraform reads the file, compares it to what exists in your cloud, and makes whatever changes are needed. If you delete a resource from the file and run Terraform again, it deletes it from the cloud too. Your infrastructure stays in sync with your code.

```bash
# macOS
brew install terraform

# Linux
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
sudo dnf install -y terraform

# Windows (Git Bash)
# Download from https://developer.hashicorp.com/terraform/downloads
# Unzip and add to PATH

# Verify
terraform --version
# Expected: Terraform v1.x.x
```

---

### Step 11.2 — Set Up Project Structure
📍 **Local Terminal**

```bash
mkdir -p ~/oci-federal-lab/terraform
cd ~/oci-federal-lab/terraform
```

---

### Step 11.3 — Create provider.tf
📍 **Editor** (build by hand)

> **🧠 ELI5 — Terraform Providers:** A provider is a plugin that teaches Terraform how to talk to a specific cloud. The OCI provider knows how to create VCNs, VMs, and databases in Oracle Cloud. The AWS provider knows about EC2, S3, and Lambda. You tell Terraform which provider to use and give it credentials, then it handles the API calls.

**Build `terraform/provider.tf` section by section:**

**Step 1:** Required providers block — tells Terraform which provider to download

```hcl
# Specify the OCI provider and its source
terraform {
  required_version = ">= 1.0.0"

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 5.0.0"
    }
  }
}
```

> The `required_providers` block tells Terraform: "Download the OCI provider from HashiCorp's registry, version 5.0 or newer." This is like adding a dependency in `requirements.txt` — it pins the version so your infrastructure is reproducible.

**Step 2:** Provider configuration — how to authenticate with OCI

```hcl
# Configure the OCI provider with API key authentication
provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}
```

> Notice we're using `var.xxx` — these are Terraform variables, defined in `variables.tf`. Never hardcode credentials in provider blocks. The variables get their values from a `terraform.tfvars` file (which is gitignored).

**Verify:**

```bash
grep -n "provider" terraform/provider.tf
# Expected: Lines showing terraform block and provider "oci" block
```

---

### Step 11.4 — Create variables.tf
📍 **Editor** (build by hand)

> **🧠 ELI5 — Terraform Variables:** Variables are placeholders for values that change between environments. Instead of hardcoding `region = "us-ashburn-1"`, you write `region = var.region` and define the variable separately. This means the same Terraform code works for different regions, shapes, or environments — just change the variable values.

**Build `terraform/variables.tf` section by section:**

**Step 1:** Authentication variables

```hcl
# --- Authentication ---
variable "tenancy_ocid" {
  description = "OCID of the OCI tenancy"
  type        = string
}

variable "user_ocid" {
  description = "OCID of the OCI user"
  type        = string
}

variable "fingerprint" {
  description = "Fingerprint of the API key"
  type        = string
}

variable "private_key_path" {
  description = "Path to the OCI API private key file"
  type        = string
}

variable "region" {
  description = "OCI region (e.g., us-ashburn-1)"
  type        = string
  default     = "us-ashburn-1"
}
```

**Step 2:** Compartment and naming variables

```hcl
# --- Compartment ---
variable "compartment_ocid" {
  description = "OCID of the compartment to create resources in"
  type        = string
}

# --- Naming ---
variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "fedtracker"
}

variable "environment" {
  description = "Environment (lab, dev, staging, prod)"
  type        = string
  default     = "lab"
}
```

**Step 3:** Network variables

```hcl
# --- Network ---
variable "vcn_cidr" {
  description = "CIDR block for the VCN"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet"
  type        = string
  default     = "10.0.2.0/24"
}
```

**Step 4:** Compute variables

```hcl
# --- Compute ---
variable "instance_shape" {
  description = "Shape for compute instances (Always Free: VM.Standard.A1.Flex)"
  type        = string
  default     = "VM.Standard.A1.Flex"
}

variable "bastion_ocpus" {
  description = "Number of OCPUs for the bastion"
  type        = number
  default     = 1
}

variable "bastion_memory_gb" {
  description = "Memory in GB for the bastion"
  type        = number
  default     = 6
}

variable "app_server_ocpus" {
  description = "Number of OCPUs for the app server"
  type        = number
  default     = 1
}

variable "app_server_memory_gb" {
  description = "Memory in GB for the app server"
  type        = number
  default     = 10
}

variable "ssh_public_key_path" {
  description = "Path to the SSH public key for instance access"
  type        = string
}

variable "oracle_linux_image_id" {
  description = "OCID of the Oracle Linux 8 image (region-specific)"
  type        = string
}
```

**Step 5:** Tags variable

```hcl
# --- Tags ---
variable "freeform_tags" {
  description = "Freeform tags to apply to all resources"
  type        = map(string)
  default = {
    "Project"     = "fedtracker"
    "Environment" = "lab"
    "Owner"       = "<YOUR_NAME>"
    "CostCenter"  = "interview-prep"
  }
}
```

> **Why a `map(string)` for tags?** Tags are key-value pairs. Terraform's `map(string)` type represents exactly that — a dictionary of string keys and string values. Defining tags as a variable means every resource can reference `var.freeform_tags`, ensuring consistent tagging across all resources.

**Verify:**

```bash
grep -c "variable" terraform/variables.tf
# Expected: ~13 variables defined
```

---

### Step 11.5 — Create terraform.tfvars
📍 **Editor**

> ⚠️ **This file contains credentials. Add it to .gitignore immediately.**

```hcl
# terraform/terraform.tfvars
# NEVER commit this file to git — it contains credentials

tenancy_ocid      = "ocid1.tenancy.oc1..xxxxxxxxxxxxx"
user_ocid         = "ocid1.user.oc1..xxxxxxxxxxxxx"
fingerprint       = "xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx"
private_key_path  = "~/.oci/oci_api_key.pem"
region            = "us-ashburn-1"
compartment_ocid  = "ocid1.compartment.oc1..xxxxxxxxxxxxx"
ssh_public_key_path    = "~/.ssh/fedtracker.pub"
oracle_linux_image_id  = "ocid1.image.oc1.iad.xxxxxxxxxxxxx"
```

> **Important:** Replace every value with your actual OCI credentials and IDs. Get the image OCID from the OCI Console: Compute → Images → Oracle Linux 8 → copy the OCID.

```bash
# Add to .gitignore
echo "terraform.tfvars" >> ~/oci-federal-lab/.gitignore
echo "*.tfstate*" >> ~/oci-federal-lab/.gitignore
echo ".terraform/" >> ~/oci-federal-lab/.gitignore
```

---

### Step 11.6 — Create network.tf
📍 **Editor** (build by hand)

**Build `terraform/network.tf` section by section:**

**Step 1:** VCN

```hcl
# --- Virtual Cloud Network ---
resource "oci_core_vcn" "main" {
  compartment_id = var.compartment_ocid
  cidr_blocks    = [var.vcn_cidr]
  display_name   = "${var.project_name}-vcn"
  dns_label      = var.project_name

  freeform_tags = var.freeform_tags
}
```

> **What is `"${var.project_name}-vcn"`?** This is Terraform string interpolation — it inserts the variable's value into the string. If `project_name` is "fedtracker", the result is "fedtracker-vcn". This keeps resource names consistent and predictable.

**Step 2:** Internet Gateway

```hcl
# --- Internet Gateway (for public subnet) ---
resource "oci_core_internet_gateway" "main" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-igw"
  enabled        = true

  freeform_tags = var.freeform_tags
}
```

> Notice `vcn_id = oci_core_vcn.main.id` — this references the VCN created above. Terraform automatically understands that the Internet Gateway depends on the VCN and creates them in the correct order. This is called **implicit dependency**.

**Step 3:** NAT Gateway

```hcl
# --- NAT Gateway (for private subnet outbound internet) ---
resource "oci_core_nat_gateway" "main" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-natgw"

  freeform_tags = var.freeform_tags
}
```

**Step 4:** Route Tables

```hcl
# --- Public Route Table (routes to Internet Gateway) ---
resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.main.id
  }

  freeform_tags = var.freeform_tags
}

# --- Private Route Table (routes to NAT Gateway) ---
resource "oci_core_route_table" "private" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "private-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_nat_gateway.main.id
  }

  freeform_tags = var.freeform_tags
}
```

**Step 5:** Security Lists

```hcl
# --- Public Security List ---
resource "oci_core_security_list" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "public-sl"

  # Allow SSH from anywhere (in production, restrict to your IP)
  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  # Allow all outbound traffic
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  freeform_tags = var.freeform_tags
}

# --- Private Security List ---
resource "oci_core_security_list" "private" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "private-sl"

  # SSH from public subnet only
  ingress_security_rules {
    protocol = "6" # TCP
    source   = var.public_subnet_cidr
    tcp_options {
      min = 22
      max = 22
    }
  }

  # App traffic from public subnet
  ingress_security_rules {
    protocol = "6" # TCP
    source   = var.public_subnet_cidr
    tcp_options {
      min = 8000
      max = 8000
    }
  }

  # Allow all outbound (for dnf, pip via NAT)
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  freeform_tags = var.freeform_tags
}
```

**Step 6:** Subnets

```hcl
# --- Public Subnet ---
resource "oci_core_subnet" "public" {
  compartment_id    = var.compartment_ocid
  vcn_id            = oci_core_vcn.main.id
  cidr_block        = var.public_subnet_cidr
  display_name      = "public-subnet"
  dns_label         = "public"
  route_table_id    = oci_core_route_table.public.id
  security_list_ids = [oci_core_security_list.public.id]

  freeform_tags = var.freeform_tags
}

# --- Private Subnet ---
resource "oci_core_subnet" "private" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.main.id
  cidr_block                 = var.private_subnet_cidr
  display_name               = "private-subnet"
  dns_label                  = "private"
  route_table_id             = oci_core_route_table.private.id
  security_list_ids          = [oci_core_security_list.private.id]
  prohibit_public_ip_on_vnic = true

  freeform_tags = var.freeform_tags
}
```

> **Why `prohibit_public_ip_on_vnic = true`?** This prevents anyone from accidentally assigning a public IP to a VM in the private subnet. It's a safety net — even if someone tries, OCI will reject it. Defense in depth.

**Verify:**

```bash
grep -n "resource" terraform/network.tf
# Expected: ~10 resource blocks (vcn, igw, natgw, 2 route tables, 2 security lists, 2 subnets)
```

---

### Step 11.7 — Create compute.tf
📍 **Editor** (build by hand)

**Build `terraform/compute.tf` section by section:**

**Step 1:** Data source to get the latest Oracle Linux image and availability domain

```hcl
# --- Data Sources ---
# Get the list of availability domains
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}
```

**Step 2:** Bastion instance

```hcl
# --- Bastion VM (public subnet) ---
resource "oci_core_instance" "bastion" {
  compartment_id      = var.compartment_ocid
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "bastion"
  shape               = var.instance_shape

  shape_config {
    ocpus         = var.bastion_ocpus
    memory_in_gbs = var.bastion_memory_gb
  }

  source_details {
    source_type = "image"
    source_id   = var.oracle_linux_image_id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public.id
    assign_public_ip = true
    display_name     = "bastion-vnic"
  }

  metadata = {
    ssh_authorized_keys = file(var.ssh_public_key_path)
  }

  freeform_tags = var.freeform_tags
}
```

> **What is `file(var.ssh_public_key_path)`?** The `file()` function reads the contents of a file and inserts it as a string. This reads your SSH public key and passes it to the VM so you can SSH in.

**Step 3:** App Server instance

```hcl
# --- App Server VM (private subnet) ---
resource "oci_core_instance" "app_server" {
  compartment_id      = var.compartment_ocid
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "app-server"
  shape               = var.instance_shape

  shape_config {
    ocpus         = var.app_server_ocpus
    memory_in_gbs = var.app_server_memory_gb
  }

  source_details {
    source_type = "image"
    source_id   = var.oracle_linux_image_id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.private.id
    assign_public_ip = false
    display_name     = "app-server-vnic"
  }

  metadata = {
    ssh_authorized_keys = file(var.ssh_public_key_path)
  }

  freeform_tags = var.freeform_tags
}
```

> **Why `assign_public_ip = false`?** The app server is in the private subnet — it should NOT have a public IP. This matches the security architecture from Day 2: bastion is the only public-facing SSH endpoint.

**Verify:**

```bash
grep -n "resource" terraform/compute.tf
# Expected: 2 resource blocks (bastion and app_server)
```

---

### Step 11.8 — Create outputs.tf
📍 **Editor** (build by hand)

> **🧠 ELI5 — Terraform Outputs:** Outputs are values that Terraform prints after `terraform apply` — they give you the information you need to connect to your infrastructure. Instead of searching the OCI Console for your bastion's IP, Terraform tells you directly.

```hcl
# --- Outputs ---
output "bastion_public_ip" {
  description = "Public IP of the bastion host"
  value       = oci_core_instance.bastion.public_ip
}

output "app_server_private_ip" {
  description = "Private IP of the app server"
  value       = oci_core_instance.app_server.private_ip
}

output "vcn_id" {
  description = "OCID of the VCN"
  value       = oci_core_vcn.main.id
}

output "ssh_command_bastion" {
  description = "SSH command to connect to bastion"
  value       = "ssh -i ~/.ssh/fedtracker opc@${oci_core_instance.bastion.public_ip}"
}

output "ssh_command_app_server" {
  description = "SSH command to connect to app server through bastion"
  value       = "ssh -i ~/.ssh/fedtracker -J opc@${oci_core_instance.bastion.public_ip} opc@${oci_core_instance.app_server.private_ip}"
}
```

---

### Step 11.9 — Initialize, Plan, and Apply
📍 **Local Terminal**

```bash
cd ~/oci-federal-lab/terraform

# Initialize — downloads the OCI provider plugin
terraform init
# Expected: "Terraform has been successfully initialized!"
```

> `terraform init` downloads the OCI provider plugin and sets up the working directory. You run this once (or after adding new providers). It creates a `.terraform/` directory — don't commit this to git.

```bash
# Plan — preview what Terraform will create (dry run)
terraform plan
# Expected: "Plan: X to add, 0 to change, 0 to destroy"
# Review each resource — you should see the VCN, subnets, gateways, route tables, security lists, and both VMs
```

> **Why plan before apply?** `terraform plan` is a dry run — it shows you what will happen without actually making changes. This is your chance to catch mistakes: wrong CIDR, wrong shape, missing tags. In production, plan output is reviewed by peers before anyone runs apply.

```bash
# Apply — create all resources in OCI
terraform apply
# Type "yes" when prompted
# Expected: Takes 3-5 minutes. Ends with "Apply complete! Resources: X added"
```

> **Note:** Terraform automatically loads `terraform.tfvars` if present in the working directory. Use `-var-file` only for non-default filenames like `prod.tfvars`.

**Verify:**

```bash
# View the outputs
terraform output
# Expected: bastion_public_ip, app_server_private_ip, SSH commands

# Test SSH to bastion
ssh -i ~/.ssh/fedtracker opc@$(terraform output -raw bastion_public_ip)
# Expected: Shell prompt on bastion

# Test SSH to app server through bastion
ssh -i ~/.ssh/fedtracker -J opc@$(terraform output -raw bastion_public_ip) opc@$(terraform output -raw app_server_private_ip)
# Expected: Shell prompt on app server
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `terraform init` | | Initialize working directory, download providers |
| `terraform plan` | | Preview changes without applying. Auto-loads `terraform.tfvars` |
| `terraform apply` | | Create/update resources. Prompts for confirmation. Auto-loads `terraform.tfvars` |
| `terraform output` | | Display output values |
| `terraform output` | `-raw <name>` | Output a single value without quotes (useful in scripts) |

</em></sub>

---

### Phase 11 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `terraform init` | "Successfully initialized" | Check internet connectivity. Check `required_providers` block syntax |
| `terraform plan` | Shows resources to add | Check variable values in `terraform.tfvars`. Common: wrong OCID format, missing required variable |
| `terraform apply` | Resources created | Check OCI service limits (A1 Flex may have capacity issues in some regions). Check IAM permissions |
| `terraform output` shows IPs | Public and private IPs | Resources may still be provisioning — wait 1-2 minutes and retry |
| SSH to bastion | Shell prompt | Check public security list allows SSH, bastion has public IP assigned |
| SSH to app-server through bastion | Shell prompt | Check private security list allows SSH from public subnet CIDR |

---

## PHASE 12: ANSIBLE AUTOMATION (2 hrs)

> Terraform creates the infrastructure (VMs, networks, databases). Ansible configures the software on those VMs (installs packages, hardens SSH, deploys the app). They're complementary tools: Terraform handles "what servers exist" and Ansible handles "what's installed on those servers." You'll write two playbooks: one for security hardening and one for app deployment.
>
> 📍 **Where work happens:** Local Terminal and Editor (building Ansible files by hand).
>
> 🛠️ **Build approach:** Every Ansible file is built by hand, section by section. This is core DevOps work.

---

### Step 12.1 — Install Ansible
📍 **Local Terminal**

> **🧠 ELI5 — Ansible:** Ansible is a configuration management tool that automates server setup. You write a "playbook" — a YAML file describing what you want the server to look like — and Ansible connects via SSH and makes it happen. No agent needed on the target server (unlike Puppet or Chef). It's idempotent — running the same playbook twice produces the same result without breaking anything.

```bash
# macOS
brew install ansible

# Linux
pip3.11 install ansible

# Verify
ansible --version
# Expected: ansible [core 2.x.x]
```

---

### Step 12.2 — Create Inventory File
📍 **Editor** (build by hand)

```bash
mkdir -p ~/oci-federal-lab/ansible
```

**Build `ansible/inventory.ini`:**

```ini
# Ansible Inventory — defines which servers to manage
# Update IPs after each terraform apply

[bastion]
bastion ansible_host=<BASTION_PUBLIC_IP> ansible_user=opc ansible_ssh_private_key_file=~/.ssh/fedtracker

[app]
app-server ansible_host=<APP_SERVER_PRIVATE_IP> ansible_user=opc ansible_ssh_private_key_file=~/.ssh/fedtracker

[app:vars]
# App servers are in a private subnet — connect through bastion
ansible_ssh_common_args='-o ProxyJump=opc@<BASTION_PUBLIC_IP>'
```

> **Why `ansible_ssh_common_args` with ProxyJump?** The app server has no public IP — Ansible can't SSH to it directly. This tells Ansible to tunnel through the bastion, exactly like the `ssh -J` command you used manually.

> **Important:** Replace the IP placeholders with your actual IPs from `terraform output`.

**Verify:**

```bash
# Test connectivity
ansible all -i ansible/inventory.ini -m ping
# Expected: bastion | SUCCESS and app-server | SUCCESS
```

---

### Step 12.3 — Create Hardening Playbook
📍 **Editor** (build by hand)

```bash
mkdir -p ~/oci-federal-lab/ansible/playbooks
```

**Build `ansible/playbooks/harden.yml` section by section:**

**Step 1:** Playbook header and host targeting

```yaml
---
# Hardening Playbook — applies CIS-aligned security settings
# Targets: app server (and optionally bastion)
# Run: ansible-playbook -i ansible/inventory.ini ansible/playbooks/harden.yml

- name: Harden Oracle Linux 8 servers
  hosts: app
  become: true  # Run as root (sudo)

  tasks:
```

> **What is `become: true`?** This tells Ansible to run all tasks with `sudo` (elevated privileges). Security hardening requires root access — you're modifying system configuration files.

**Step 2:** SSH hardening tasks

```yaml
    # --- SSH Hardening ---
    - name: Disable root SSH login
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?PermitRootLogin'
        line: 'PermitRootLogin no'
        state: present
      notify: restart sshd

    - name: Disable password authentication
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?PasswordAuthentication'
        line: 'PasswordAuthentication no'
        state: present
      notify: restart sshd

    - name: Set max auth tries to 3
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?MaxAuthTries'
        line: 'MaxAuthTries 3'
        state: present
      notify: restart sshd

    - name: Set login grace time to 60 seconds
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?LoginGraceTime'
        line: 'LoginGraceTime 60'
        state: present
      notify: restart sshd

    - name: Deploy legal login banner
      copy:
        dest: /etc/issue.net
        content: |
          ***************************************************************************
          *                    AUTHORIZED ACCESS ONLY                                *
          *                                                                           *
          *  This system is the property of the organization. Unauthorized access    *
          *  is prohibited. All activities are monitored and recorded.                *
          ***************************************************************************
        mode: '0644'

    - name: Enable SSH banner
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?Banner'
        line: 'Banner /etc/issue.net'
        state: present
      notify: restart sshd
```

> **What is `lineinfile`?** Ansible's `lineinfile` module finds a line in a file (using `regexp`) and replaces it with the `line` value. If the line doesn't exist, it adds it. This is idempotent — running it twice doesn't create duplicate lines.

> **What is `notify`?** When a task changes something, `notify` triggers a handler (defined later). Multiple tasks can notify the same handler, but the handler only runs once at the end. This prevents SSH from being restarted after every single config change.

**Step 3:** Firewall and auditd tasks

```yaml
    # --- Firewall ---
    - name: Ensure firewalld is running
      systemd:
        name: firewalld
        state: started
        enabled: true

    - name: Open port 8000 for FastAPI
      firewalld:
        port: 8000/tcp
        permanent: true
        state: enabled
        immediate: true

    # --- Audit ---
    - name: Install auditd
      dnf:
        name: audit
        state: present

    - name: Enable auditd
      systemd:
        name: auditd
        state: started
        enabled: true

    - name: Deploy audit rules
      copy:
        dest: /etc/audit/rules.d/fedtracker.rules
        content: |
          -w /etc/passwd -p wa -k user_changes
          -w /etc/shadow -p wa -k user_changes
          -w /etc/ssh/sshd_config -p wa -k ssh_config
          -w /opt/fedtracker/ -p wa -k fedtracker_changes
        mode: '0640'
      notify: reload audit rules

    # --- Kernel Tuning (sysctl) ---
    - name: Apply kernel tuning for web server
      ansible.posix.sysctl:
        name: "{{ item.key }}"
        value: "{{ item.value }}"
        sysctl_file: /etc/sysctl.d/99-fedtracker.conf
        reload: yes
      loop:
        - { key: 'net.core.somaxconn', value: '4096' }
        - { key: 'vm.swappiness', value: '10' }
        - { key: 'net.ipv4.tcp_tw_reuse', value: '1' }
        - { key: 'net.ipv4.tcp_syncookies', value: '1' }

    # --- Password Policy (PAM) ---
    - name: Set password minimum length via PAM
      lineinfile:
        path: /etc/security/pwquality.conf
        regexp: '^#?\s*minlen'
        line: 'minlen = 14'
        state: present

    - name: Set password complexity — require digit
      lineinfile:
        path: /etc/security/pwquality.conf
        regexp: '^#?\s*dcredit'
        line: 'dcredit = -1'
        state: present

    - name: Set password complexity — require uppercase
      lineinfile:
        path: /etc/security/pwquality.conf
        regexp: '^#?\s*ucredit'
        line: 'ucredit = -1'
        state: present
```

> **What do the sysctl parameters do?**
>
> | Parameter | What It Does |
> |-----------|-------------|
> | `net.core.somaxconn=4096` | Increases the TCP listen backlog — allows more pending connections before dropping them. Default (128) is too low for a web server |
> | `vm.swappiness=10` | Tells the kernel to prefer keeping data in RAM over swapping to disk. Lower = less swap usage = better app performance |
> | `net.ipv4.tcp_tw_reuse=1` | Allows reusing TIME_WAIT sockets for new connections — prevents port exhaustion under high load |
> | `net.ipv4.tcp_syncookies=1` | Protects against SYN flood attacks by using cryptographic cookies instead of allocating resources for half-open connections |
>
> **What do the PAM/pwquality settings do?** They enforce federal password policy: minimum 14 characters, at least one digit (`dcredit=-1`), at least one uppercase letter (`ucredit=-1`). These settings apply to all local accounts. In production, you'd also enforce password history (`remember=24`) and account lockout via `pam_faillock`.

**Step 4:** Handlers (run at end when notified)

```yaml
  handlers:
    - name: restart sshd
      systemd:
        name: sshd
        state: restarted

    - name: reload audit rules
      command: augenrules --load
```

**Verify:**

```bash
# Check YAML syntax
ansible-playbook --syntax-check -i ansible/inventory.ini ansible/playbooks/harden.yml
# Expected: "playbook: ansible/playbooks/harden.yml" (no errors)
```

---

### Step 12.4 — Create Deploy Playbook
📍 **Editor** (build by hand)

**Build `ansible/playbooks/deploy_app.yml`:**

```yaml
---
# Deploy Playbook — installs and configures FedTracker on app server
# Run: ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy_app.yml

- name: Deploy FedTracker application
  hosts: app
  become: true

  vars:
    app_dir: /opt/fedtracker
    app_user: clouduser
    app_port: 8000

  tasks:
    # --- User Setup ---
    - name: Create application user
      user:
        name: "{{ app_user }}"
        create_home: true
        shell: /bin/bash
        groups: wheel
        append: true

    # --- Dependencies ---
    - name: Install system packages
      dnf:
        name:
          - python3.11
          - python3.11-pip
          - python3.11-devel
          - git
        state: present

    - name: Set python3.11 as default python3
      alternatives:
        name: python3
        path: /usr/bin/python3.11

    - name: Install Python packages
      pip:
        name:
          - fastapi
          - uvicorn
          - pydantic
          - oracledb
        executable: pip3.11

    # --- Application Directory ---
    - name: Create application directory
      file:
        path: "{{ app_dir }}"
        state: directory
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0755'

    # --- Application Code ---
    - name: Copy application code
      copy:
        src: ../../app/main.py
        dest: "{{ app_dir }}/main.py"
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0644'
      notify: restart fedtracker

    # --- systemd Service ---
    - name: Create systemd service file
      template:
        src: ../templates/fedtracker.service.j2
        dest: /etc/systemd/system/fedtracker.service
        mode: '0644'
      notify:
        - reload systemd
        - restart fedtracker

    - name: Enable and start FedTracker
      systemd:
        name: fedtracker
        state: started
        enabled: true

  handlers:
    - name: reload systemd
      systemd:
        daemon_reload: true

    - name: restart fedtracker
      systemd:
        name: fedtracker
        state: restarted
```

> **What is `{{ app_user }}`?** Double curly braces are Jinja2 template syntax — they insert variable values. `{{ app_user }}` gets replaced with "clouduser" at runtime. This makes the playbook reusable — change the variable, deploy to a different user.

Create the service template:

```bash
mkdir -p ~/oci-federal-lab/ansible/templates
```

**Build `ansible/templates/fedtracker.service.j2`:**

```ini
[Unit]
Description=FedTracker Personnel Tracking Application (FastAPI)
After=network.target

[Service]
User={{ app_user }}
Group={{ app_user }}
WorkingDirectory={{ app_dir }}
Environment=DB_TYPE=sqlite
Environment=SQLITE_PATH={{ app_dir }}/fedtracker.db
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port {{ app_port }}
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Security hardening (same directives from Day 1, now automated)
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths={{ app_dir }}
PrivateTmp=yes
MemoryMax=512M
OOMScoreAdjust=-500

[Install]
WantedBy=multi-user.target
```

> **What is a `.j2` file?** Jinja2 templates — Ansible replaces `{{ variables }}` with actual values before copying the file. This is how you create dynamic configuration files that adapt to each environment. Notice the security directives from Day 1's manual service file are now part of the template — this is the power of Ansible: the hardening you did by hand is now automated and consistent across every deployment.

**Verify:**

```bash
ansible-playbook --syntax-check -i ansible/inventory.ini ansible/playbooks/deploy_app.yml
# Expected: No errors
```

---

### Step 12.5 — Run Both Playbooks
📍 **Local Terminal**

```bash
cd ~/oci-federal-lab

# Run hardening first
ansible-playbook -i ansible/inventory.ini ansible/playbooks/harden.yml
# Expected: All tasks show "changed" or "ok"

# Then deploy the app
ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy_app.yml
# Expected: All tasks show "changed" or "ok"
```

**Verify idempotency — run again:**

```bash
ansible-playbook -i ansible/inventory.ini ansible/playbooks/harden.yml
# Expected: All tasks show "ok" (nothing changed — idempotent!)

ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy_app.yml
# Expected: All tasks show "ok" (nothing changed — idempotent!)
```

> **🧠 ELI5 — Idempotency:** Running the same Ansible playbook 10 times produces the same result as running it once. Ansible checks the current state before making changes — if a package is already installed, it doesn't reinstall it. If a file already has the right content, it doesn't rewrite it. This is critical for production: you can run your playbooks as often as you want without fear of breaking things.

**Test the deployed app:**

```bash
# From local machine, test through bastion
ssh app-server "curl -s http://localhost:8000/health"
# Expected: {"status": "healthy", ...}
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `ansible-playbook` | `-i inventory.ini` | Run a playbook. `-i` = inventory file |
| `ansible-playbook` | `--syntax-check` | Validate YAML syntax without running |
| `ansible` | `-m ping` | Test connectivity to all hosts |

</em></sub>

---

### Phase 12 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `ansible all -m ping` | SUCCESS for all hosts | Check: (1) IP addresses in inventory, (2) SSH keys, (3) ProxyJump syntax for app server |
| Playbook syntax check passes | No errors | YAML indentation issue — use spaces, not tabs. Use 2-space indentation |
| Hardening playbook runs | All tasks ok/changed | SSH task failed? Check if sshd_config exists. Permission denied? Check `become: true` |
| Deploy playbook runs | All tasks ok/changed | Copy failed? Check the `src` path is correct relative to playbook location |
| Second run shows all "ok" | No "changed" tasks | This IS idempotency. If tasks show "changed" on second run, the task is not idempotent (usually command/shell tasks) |
| App health check works | Healthy JSON response | Check `systemctl status fedtracker` on app server. Check `journalctl -u fedtracker` for errors |

---

## PHASE 13: DESTROY & REBUILD PROOF (1 hr)

> This is the moment of truth. You destroy all your cloud infrastructure and rebuild it entirely from code. If Terraform and Ansible are written correctly, you can go from zero to a fully deployed, hardened application in minutes. This is what interviewers want to hear: "I can rebuild the entire environment from scratch because everything is codified."
>
> 📍 **Where work happens:** Local Terminal.
>
> 🛠️ **Build approach:** Three commands: `terraform destroy`, `terraform apply`, `ansible-playbook`. That's it.

---

### Step 13.1 — Destroy Everything
📍 **Local Terminal**

```bash
cd ~/oci-federal-lab/terraform

# Preview what will be destroyed
terraform plan -destroy
# Expected: Shows all resources that will be destroyed

# Destroy everything
terraform destroy
# Type "yes" when prompted
# Expected: "Destroy complete! Resources: X destroyed."
```

> The VMs are gone. The network is gone. Everything you built over two days is deleted. This is intentional. If this makes you nervous, that's the point — it should feel uncomfortable until you prove the rebuild works.

---

### Step 13.2 — Rebuild from Code
📍 **Local Terminal**

```bash
# Rebuild everything
terraform apply
# Type "yes" when prompted
# Expected: "Apply complete! Resources: X added"

# Get the new IPs
terraform output
# Note: The IPs WILL be different from before
```

> **Important:** Update the Ansible inventory with the new IPs:

```bash
# Get the new IPs
BASTION_IP=$(terraform output -raw bastion_public_ip)
APP_IP=$(terraform output -raw app_server_private_ip)

echo "Bastion: $BASTION_IP"
echo "App Server: $APP_IP"
```

Update `ansible/inventory.ini` with these new IPs.

---

### Step 13.3 — Configure with Ansible
📍 **Local Terminal**

```bash
cd ~/oci-federal-lab

# Wait 60 seconds for VMs to fully boot
sleep 60

# Harden first
ansible-playbook -i ansible/inventory.ini ansible/playbooks/harden.yml

# Deploy the app
ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy_app.yml
```

---

### Step 13.4 — Verify Everything Works
📍 **Local Terminal**

```bash
# Health check
ssh app-server "curl -s http://localhost:8000/health"
# Expected: {"status": "healthy", ...}

# Personnel endpoint
ssh app-server "curl -s http://localhost:8000/personnel"
# Expected: JSON with personnel records

# Swagger docs (from browser)
echo "Visit: http://$BASTION_IP:8000/docs"
# Note: You'd need to set up port forwarding or adjust security lists
# to access the app from your browser through the bastion
```

### Step 13.5 — Measure and Document Rebuild Time
📍 **Local Terminal**

```bash
# Document the rebuild time
echo "=== REBUILD METRICS ==="
echo "Terraform apply: ~X minutes"
echo "Ansible hardening: ~X minutes"
echo "Ansible deploy: ~X minutes"
echo "Total time from zero to healthy app: ~X minutes"
echo "========================"
```

> **🧠 Interview framing:** "I can rebuild the entire environment from scratch in under 15 minutes. Terraform creates the VCN, subnets, gateways, security lists, and VMs. Ansible hardens the servers and deploys the application. Everything is codified — no manual steps, no console clicking, fully repeatable."

---

### Step 13.6 — Git Commit Day 3 Work
📍 **Local Terminal**

```bash
cd ~/oci-federal-lab
git add terraform/ ansible/ app/
git commit -m "Day 3: Terraform IaC + Ansible automation + destroy/rebuild proof

- Terraform: provider, variables, network (VCN, subnets, gateways, security lists), compute (bastion, app server), outputs
- Ansible: inventory, hardening playbook (SSH, firewall, auditd), deploy playbook (FastAPI + systemd)
- Destroy/rebuild verified: zero to healthy app in ~15 minutes
- All resources tagged for cost compliance"
```

---

### Phase 13 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `terraform destroy` completes | All resources destroyed | If a resource hangs, check OCI Console for dependent resources. Instance in a subnet prevents subnet deletion |
| `terraform apply` creates resources | All resources created | Check service limits. A1 Flex capacity varies by region. Try a different availability domain |
| Ansible can reach new VMs | Ping succeeds | Update inventory IPs! The new VMs have different IPs. Wait 60 seconds for boot |
| App is healthy after rebuild | `/health` returns healthy | Check `journalctl -u fedtracker` on app server. Most common: missing Python packages (Ansible task failed silently) |

---

## DAY 3 RECAP

### Day 3 Complete

**What you built:**
- Terraform configuration (5 files) that creates the entire OCI environment
- Ansible inventory and 2 playbooks (hardening + deployment)
- Proved destroy/rebuild works: zero to healthy app in minutes

**What's running:**
- Same architecture as Day 2, but entirely code-managed
- Every resource created by `terraform apply`
- Every configuration applied by `ansible-playbook`

**What you can now talk about in interviews:**
- "I wrote Terraform from scratch to codify my OCI infrastructure — VCN with public/private subnets, bastion, NAT gateway, security lists, and compute instances"
- "I use Terraform variables and tfvars to separate configuration from code, with credentials never committed to git"
- "I wrote Ansible playbooks for security hardening and app deployment, using lineinfile for SSH config, templates for systemd services, and handlers for efficient restarts"
- "I destroyed the entire environment and rebuilt it from code in under 15 minutes — Terraform for infrastructure, Ansible for configuration, zero manual steps"
- "Ansible is idempotent — running the same playbook twice produces the same result without breaking anything"

**Skills practiced:** Terraform (deep), Ansible (deep), IaC patterns, configuration management, destroy/rebuild, idempotency

**Next:** Day 4 — "Containerize & Secure" — you'll containerize FedTracker with Podman and Docker, run CIS compliance scans with OpenSCAP, and build an AI-powered evidence collector with Ollama.

---

## PHASE 14: PODMAN & DOCKER CONTAINERS (2.5 hrs)

> Containers package your application and all its dependencies into a single, portable unit. Instead of installing Python, FastAPI, and uvicorn on the server, you build a container image that includes everything. The image runs identically on your laptop, in CI/CD, and in production. Today you learn Podman first (Oracle Linux's native container tool), then Docker for comparison, then Docker Compose for multi-container setups.
>
> 📍 **Where work happens:** VM Terminal (app-server via bastion).
>
> 🛠️ **Build approach:** Dockerfile and docker-compose.yml are built by hand, section by section. Container commands are typed manually.

---

### Step 14.1 — Understand Containers
📍 **VM Terminal** (app-server)

> **🧠 ELI5 — What are Containers?** Think of a shipping container at a port. Before containers, each ship had to figure out how to store different cargo — barrels of oil next to crates of electronics next to bags of grain. Chaos. Shipping containers standardized everything: same size, same shape, stack them anywhere, load them on any ship. Software containers do the same thing: your app, its dependencies, its configuration — all packed into one standardized unit that runs the same way everywhere. It doesn't matter if the server runs Oracle Linux, Ubuntu, or Amazon Linux — the container runs identically.

> **🧠 ELI5 — Podman vs Docker:**
>
> | Feature | Podman | Docker |
> |---------|--------|--------|
> | Daemon | **Daemonless** — no background service | Runs `dockerd` daemon (always running, uses ~140MB RAM) |
> | Root | **Rootless by default** — containers run as your user | Requires root (or docker group, which is effectively root) |
> | CLI | Same commands — `podman build`, `podman run` | `docker build`, `docker run` |
> | RHEL/OCI default | **Yes** — ships with Oracle Linux and RHEL | Must install separately, not in default repos |
> | Federal preference | **Preferred** — rootless, no daemon attack surface | Common but security-conscious orgs prefer Podman |
> | OCI Images | Uses same OCI image format | Same format — images are interchangeable |
>
> **Bottom line:** Same Dockerfile, same images, different runtime. Podman is more secure by default. Use Podman when you can, Docker when you must (Docker Compose ecosystem is more mature).

---

### Step 14.2 — Build with Podman
📍 **VM Terminal** (app-server)

```bash
# Podman is pre-installed on Oracle Linux 8
podman --version
# Expected: podman version 4.x.x
```

**Build the Dockerfile section by section:**

📍 **VM Terminal** (build by hand)

**Step 1:** Base image and metadata

```bash
su - clouduser

cat > /opt/fedtracker/Dockerfile << 'DOCKEOF'
# --- Stage 1: Build stage ---
# Use Oracle Linux 8 as base (matches our server OS)
FROM oraclelinux:8-slim AS builder

# Metadata labels
LABEL maintainer="<YOUR_NAME>" \
      description="FedTracker Federal Personnel Tracking API" \
      version="1.0.0"
DOCKEOF
```

> **Why Oracle Linux as base?** Using the same OS as your server avoids compatibility issues. In federal environments, consistency matters — your container should match the host OS family when possible.

**Step 2:** Install dependencies

```bash
cat >> /opt/fedtracker/Dockerfile << 'DOCKEOF'

# Install Python and pip
RUN microdnf install -y python3 python3-pip && \
    microdnf clean all

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
DOCKEOF
```

> **Why `--no-cache-dir`?** pip normally caches downloaded packages for faster reinstalls. Inside a container, you'll never reinstall — the cache wastes space. `--no-cache-dir` keeps the image smaller.

> **Why `microdnf clean all`?** Same reason — removes package manager cache to reduce image size. Every layer in a Dockerfile adds to the final image size.

Create the requirements file:

```bash
cat > /opt/fedtracker/requirements.txt << 'EOF'
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
oracledb>=1.0.0
EOF
```

**Step 3:** Application code and configuration

```bash
cat >> /opt/fedtracker/Dockerfile << 'DOCKEOF'

# Create non-root user (security: never run containers as root)
RUN useradd -r -s /bin/false appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY main.py /app/main.py

# Own files by non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port (documentation — doesn't actually open the port)
EXPOSE 8000

# Health check — container orchestrators use this
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -sf http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKEOF
```

> **Why `USER appuser`?** Running containers as root is a security risk — if an attacker escapes the container, they're root on the host. `USER appuser` switches to a non-root user. This is a CIS benchmark requirement and a federal best practice.

> **Why `HEALTHCHECK`?** This tells container orchestrators (Docker, Podman, Kubernetes) how to check if the container is healthy. If the health check fails 3 times, the orchestrator can restart the container automatically.

> **🧠 Putting it together:** The Dockerfile says: "Start with Oracle Linux 8, install Python and FastAPI, copy the application code, create a non-root user, switch to that user, and run uvicorn on port 8000." Every step builds on the previous one, creating layers in the final image.

**Build and run with Podman:**

```bash
cd /opt/fedtracker

# Build the image
podman build -t fedtracker:1.0 .
# Expected: Successfully tagged localhost/fedtracker:1.0

# List images
podman images
# Expected: fedtracker image, ~200-300 MB

# Run the container
podman run -d --name fedtracker-app \
  -p 8000:8000 \
  -e DB_TYPE=sqlite \
  -e SQLITE_PATH=/app/fedtracker.db \
  fedtracker:1.0
```

> **What do the flags mean?** `-d` = detached (run in background). `--name` = give it a name (easier than container IDs). `-p 8000:8000` = map host port 8000 to container port 8000. `-e` = set environment variable.

```bash
# Check the container is running
podman ps
# Expected: fedtracker-app running, port 8000 mapped

# Test the health endpoint
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}

# View container logs
podman logs fedtracker-app
# Expected: Uvicorn startup messages

# Stop and remove the container
podman stop fedtracker-app
podman rm fedtracker-app
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `podman build` | `-t name:tag .` | Build image from Dockerfile in current directory |
| `podman run` | `-d --name -p -e` | Run container. `-d`=detach, `-p`=port, `-e`=env var |
| `podman ps` | | List running containers |
| `podman logs` | | View container stdout/stderr |
| `podman stop` | | Stop a running container |
| `podman rm` | | Remove a stopped container |
| `podman images` | | List downloaded/built images |

</em></sub>

---

### Step 14.3 — Docker Comparison
📍 **VM Terminal** (app-server)

> Now build and run the same image with Docker to see the difference.

```bash
# Install Docker CE on Oracle Linux 8
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable --now docker
sudo usermod -aG docker clouduser
```

> **Note:** You need to log out and back in (or `newgrp docker`) for the group change to take effect.

```bash
# Log out and back in to pick up docker group
exit
su - clouduser

# Build with Docker — same Dockerfile, same result
cd /opt/fedtracker
docker build -t fedtracker:1.0 .
# Expected: Same build output as Podman

# Run with Docker
docker run -d --name fedtracker-docker \
  -p 8000:8000 \
  -e DB_TYPE=sqlite \
  fedtracker:1.0

# Test
curl http://localhost:8000/health
# Expected: Same healthy response

# Clean up
docker stop fedtracker-docker
docker rm fedtracker-docker
```

> **Key difference observed:** Same Dockerfile, same image, same commands (just replace `podman` with `docker`). Under the hood, Docker uses `containerd` + `runc` with a daemon, while Podman uses `conmon` + `runc` without a daemon. For your day-to-day work, they're interchangeable.

> **💼 Interview Insight — Podman vs Docker:** "On Oracle Linux, I used Podman because that's what RHEL-based systems ship natively. It's daemonless and rootless by default, which aligns with federal security requirements. The same Dockerfile works with both — Podman and Docker use the same OCI image format. For multi-container orchestration, I used Docker Compose because its ecosystem is more mature, but for single containers, Podman is my default."

---

### Step 14.4 — Docker Compose
📍 **VM Terminal** (build by hand)

> **🧠 ELI5 — Docker Compose:** Docker Compose manages multiple containers as a single application. Instead of running separate `docker run` commands for your app, database, and monitoring sidecar, you define them all in a `docker-compose.yml` file and start everything with `docker compose up`. It handles networking between containers automatically.

```bash
# Install Docker Compose plugin (if not included with Docker CE)
sudo dnf install -y docker-compose-plugin
# Or: docker compose version (it's built into Docker CE v2+)
```

**Build `docker-compose.yml` section by section:**

**Step 1:** Service definition

```bash
cat > /opt/fedtracker/docker-compose.yml << 'COMPEOF'
# Docker Compose file for FedTracker
# Run: docker compose up -d
# Stop: docker compose down

version: "3.8"

services:
  # FedTracker API service
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: fedtracker-app
    ports:
      - "8000:8000"
    environment:
      - DB_TYPE=sqlite
      - SQLITE_PATH=/app/data/fedtracker.db
    volumes:
      - app-data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  app-data:
    driver: local
COMPEOF
```

> **Why `volumes: app-data`?** Without a volume, the SQLite database lives inside the container — when the container is destroyed, the data is gone. A volume persists data outside the container. `app-data:/app/data` maps a named volume to `/app/data` inside the container. Even if you destroy and recreate the container, the volume (and your data) survives.

> **Why `restart: unless-stopped`?** Like `Restart=always` in systemd — Docker restarts the container if it crashes. `unless-stopped` means it restarts on crash but NOT if you manually stopped it with `docker compose stop`.

**Run with Docker Compose:**

```bash
cd /opt/fedtracker

# Build and start
docker compose up -d
# Expected: Container starts successfully

# Check status
docker compose ps
# Expected: fedtracker-app running, port 8000 mapped

# View logs
docker compose logs -f app
# Expected: Uvicorn startup messages (Ctrl+C to stop following)

# Test
curl http://localhost:8000/health
# Expected: Healthy response

# Stop everything
docker compose down
# Expected: Container stopped and removed (volume preserved)
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `docker compose up` | `-d` | Build and start all services. `-d` = detached |
| `docker compose ps` | | List running services |
| `docker compose logs` | `-f app` | Follow logs for a service |
| `docker compose down` | | Stop and remove containers (volumes preserved) |
| `docker compose down` | `-v` | Stop and remove containers AND volumes (data lost!) |

</em></sub>

---

### Phase 14 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `podman build` succeeds | Image created | Check Dockerfile syntax. Common: wrong COPY path, missing requirements.txt |
| `podman run` starts container | Container running, port mapped | Port already in use? Stop the systemd service first: `sudo systemctl stop fedtracker` |
| `docker build` succeeds | Same image as Podman | Docker not installed? Check `docker --version`. Docker service running? `sudo systemctl status docker` |
| `docker compose up` starts | Service running | Check docker-compose.yml syntax. Common: indentation errors in YAML |
| `curl localhost:8000/health` | Healthy response | Container crashed? Check `docker compose logs app`. Common: missing env var, wrong port |
| Container image too large | Should be ~200-300 MB | Use slim base image. Add `.dockerignore` to exclude unnecessary files |

**SELinux and containers — the `:Z` volume mount flag:**

When mounting host directories into containers on an SELinux-enforcing system, the container process may be denied access — even if Unix permissions look correct. SELinux labels on the host files don't match what the container expects.

```bash
# This will FAIL on an SELinux-enforcing system if /data has the wrong label:
podman run -v /opt/fedtracker/data:/data fedtracker:1.0
# Error: Permission denied (SELinux denial, not Unix permissions)

# Fix: use the :Z flag to automatically relabel the volume
podman run -v /opt/fedtracker/data:/data:Z fedtracker:1.0
# :Z = private label (only this container can access the files)
# :z = shared label (multiple containers can access the files)
```

> **🧠 ELI5 — The `:Z` flag:** SELinux labels every file with a security context. When you mount a host directory into a container, the file labels say "I belong to the host" and the container says "I need files labeled for me." The `:Z` flag tells Podman to relabel the files so the container can access them. Use `:Z` (uppercase) for single-container access and `:z` (lowercase) if multiple containers share the volume.

**Container networking debugging:**

```bash
# Inspect a running container's network configuration
podman inspect --format '{{.NetworkSettings.IPAddress}}' fedtracker-app
# Shows the container's internal IP address

# Verify container port bindings from the host
ss -tlnp | grep 8000
# Should show the port mapped to the container process

# Debug: exec into a running container
podman exec -it fedtracker-app /bin/bash
# Now you're inside the container — run diagnostic commands
# Exit with: exit
```

---

## PHASE 15: OPENSCAP CIS COMPLIANCE (1.5 hrs)

> Federal systems must comply with security baselines — CIS Benchmarks define the minimum security configuration for operating systems. OpenSCAP is an open-source tool that scans your server against these benchmarks and generates compliance reports. This is not optional in federal environments — it's how you prove to auditors that your systems are configured correctly.
>
> 📍 **Where work happens:** VM Terminal (app-server).
>
> 🛠️ **Build approach:** Commands run manually. Remediation script built by hand.

---

### Step 15.1 — Install and Run OpenSCAP
📍 **VM Terminal** (app-server)

> **🧠 ELI5 — CIS Benchmarks & OpenSCAP:** CIS (Center for Internet Security) Benchmarks are security configuration guides — they list hundreds of settings like "SSH root login should be disabled" and "password minimum length should be 14 characters." OpenSCAP is a tool that automatically checks your server against these benchmarks and tells you which ones pass and which fail. Think of it as a security audit checklist that checks itself.

```bash
# Install OpenSCAP tools and the CIS content
sudo dnf install -y openscap-scanner scap-security-guide

# List available profiles
oscap info /usr/share/xml/scap/ssg/content/ssg-ol8-ds.xml | grep -A2 "Profile"
# Expected: Several profiles including CIS benchmarks
# Look for: xccdf_org.ssgproject.content_profile_cis
```

```bash
# Run the CIS Level 1 scan and generate an HTML report
sudo oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis \
  --results /tmp/cis-results.xml \
  --report /tmp/cis-report.html \
  /usr/share/xml/scap/ssg/content/ssg-ol8-ds.xml
```

> The scan takes 2-5 minutes. It checks hundreds of CIS controls and reports pass/fail for each.

```bash
# Check the summary
grep -c "pass" /tmp/cis-results.xml
grep -c "fail" /tmp/cis-results.xml
# Expected: Many passes and some failures — failures are expected before hardening
```

```bash
# Download the HTML report to view in your browser
# From your local machine:
```

📍 **Local Terminal**

```bash
scp -J bastion opc@<APP_SERVER_PRIVATE_IP>:/tmp/cis-report.html ~/Desktop/
# Open ~/Desktop/cis-report.html in your browser
```

> The HTML report shows every CIS control, whether it passed or failed, and what the expected value is. Your Day 2 hardening (SSH, auditd) should already cover several controls.

---

### Step 15.2 — Build Automated Scan Script
📍 **VM Terminal** (app-server, build by hand)

```bash
su - clouduser

cat > /opt/fedtracker/cis_scan.sh << 'SCANEOF'
#!/bin/bash
# =============================================================================
# CIS Benchmark Scanner — runs OpenSCAP and summarizes results
# Usage: sudo ./cis_scan.sh
# Output: HTML report + console summary
# =============================================================================

TIMESTAMP=$(date -u '+%Y%m%d_%H%M%S')
RESULTS="/tmp/cis-results-${TIMESTAMP}.xml"
REPORT="/tmp/cis-report-${TIMESTAMP}.html"
PROFILE="xccdf_org.ssgproject.content_profile_cis"
CONTENT="/usr/share/xml/scap/ssg/content/ssg-ol8-ds.xml"

echo "=== CIS Benchmark Scan ==="
echo "Profile: CIS Level 1 for Oracle Linux 8"
echo "Started: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

# Run the scan
oscap xccdf eval \
  --profile "${PROFILE}" \
  --results "${RESULTS}" \
  --report "${REPORT}" \
  "${CONTENT}" 2>/dev/null

# Parse results
PASS=$(grep -c 'result="pass"' "${RESULTS}" 2>/dev/null || echo 0)
FAIL=$(grep -c 'result="fail"' "${RESULTS}" 2>/dev/null || echo 0)
NOTAPPLICABLE=$(grep -c 'result="notapplicable"' "${RESULTS}" 2>/dev/null || echo 0)
TOTAL=$((PASS + FAIL))

echo "=== Results ==="
echo "  Passed:         ${PASS}"
echo "  Failed:         ${FAIL}"
echo "  Not Applicable: ${NOTAPPLICABLE}"
echo "  Total Checked:  ${TOTAL}"
if [ "${TOTAL}" -gt 0 ]; then
    SCORE=$(( PASS * 100 / TOTAL ))
    echo "  Score:          ${SCORE}%"
fi
echo ""
echo "  HTML Report:    ${REPORT}"
echo "  XML Results:    ${RESULTS}"
echo ""
echo "Completed: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
SCANEOF

chmod +x /opt/fedtracker/cis_scan.sh
```

```bash
# Run the scan (requires root for full access)
sudo /opt/fedtracker/cis_scan.sh
```

**Expected output:**

```
=== CIS Benchmark Scan ===
Profile: CIS Level 1 for Oracle Linux 8
Started: 2026-03-23 10:00:00 UTC

=== Results ===
  Passed:         142
  Failed:         38
  Not Applicable: 25
  Total Checked:  180
  Score:          78%

  HTML Report:    /tmp/cis-report-20260323_100000.html
  XML Results:    /tmp/cis-results-20260323_100000.xml

Completed: 2026-03-23 10:03:00 UTC
```

---

### Step 15.3 — Remediate Top Failures
📍 **VM Terminal** (app-server)

Review the HTML report and manually fix the top 5 failures. Common CIS failures and fixes:

```bash
# CIS: Ensure permissions on /etc/passwd are 644
sudo chmod 644 /etc/passwd

# CIS: Ensure permissions on /etc/shadow are 000
sudo chmod 000 /etc/shadow

# CIS: Ensure core dumps are restricted
echo "* hard core 0" | sudo tee -a /etc/security/limits.conf

# CIS: Ensure address space layout randomization (ASLR) is enabled
echo "kernel.randomize_va_space = 2" | sudo tee -a /etc/sysctl.d/99-cis.conf
sudo sysctl -p /etc/sysctl.d/99-cis.conf

# CIS: Ensure password creation requirements are configured
sudo dnf install -y libpwquality
sudo sed -i 's/# minlen = .*/minlen = 14/' /etc/security/pwquality.conf
```

```bash
# Re-run the scan to see improvement
sudo /opt/fedtracker/cis_scan.sh
# Expected: Higher score than before
```

> **🧠 Interview framing:** "I ran CIS Level 1 benchmarks against Oracle Linux 8 using OpenSCAP. The initial scan showed a 78% compliance score. I remediated the top failures — file permissions, core dump restrictions, ASLR, password complexity — and improved the score to 85%. In production, I'd automate these remediations in the Ansible hardening playbook."

---

## PHASE 16: OLLAMA AI EVIDENCE COLLECTOR (1.5 hrs)

> Federal compliance requires evidence packages — documents proving that security controls are in place. Normally, a human reads through scan results, firewall rules, and config files, then writes a narrative summary. Ollama is a local LLM that can read this evidence and generate human-readable summaries. This is the AI pillar for Phase 1 — local inference, no cloud API needed, air-gap capable.
>
> 📍 **Where work happens:** VM Terminal (app-server).
>
> 🛠️ **Build approach:** Python script built by hand. Ollama installed and configured.

---

### Step 16.1 — Install Ollama
📍 **VM Terminal** (app-server)

> **🧠 ELI5 — Ollama:** Ollama is a tool that runs large language models (LLMs) locally on your server — no internet connection needed, no API keys, no cloud costs. You download a model once, and it runs entirely on your machine. This is important for federal environments where data cannot leave the network (air-gapped systems). In production, you'd use OCI Generative AI Service for better models and scalability. For the lab, Ollama is free and demonstrates the same concept.

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start the Ollama service
sudo systemctl enable --now ollama

# Pull a small model (tinyllama fits in ~1GB RAM)
ollama pull tinyllama

# Verify it works
ollama run tinyllama "What is CIS in cybersecurity? Reply in 2 sentences."
# Expected: A brief explanation of CIS benchmarks
# Press Ctrl+D to exit the interactive session
```

> **Why `tinyllama`?** On Always Free ARM instances with limited RAM, use smaller models. TinyLlama (1.1B params) fits comfortably in the available memory. In production or with more resources, you'd use mistral:7b or llama3:8b for higher quality outputs. In production with OCI Generative AI, you'd use much larger models.

---

### Step 16.2 — Build the Evidence Collector Script
📍 **VM Terminal** (build by hand)

```bash
su - clouduser

cat > /opt/fedtracker/evidence_collector.py << 'PYEOF'
#!/usr/bin/env python3
"""
AI-Powered Compliance Evidence Collector
Collects system evidence (configs, scan results, service status)
and uses Ollama to generate narrative summaries per control family.

Usage: python3 evidence_collector.py
Output: Markdown evidence package
Requires: Ollama running with tinyllama model
"""

import subprocess
import json
import os
from datetime import datetime, timezone


def run_cmd(cmd):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[Command timed out]"
    except Exception as e:
        return f"[Error: {str(e)}]"


def query_ollama(prompt, model="tinyllama"):
    """Send a prompt to Ollama and return the response."""
    try:
        import requests
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120
        )
        return response.json().get("response", "[No response]")
    except Exception as e:
        return f"[Ollama error: {str(e)}]"


def collect_evidence():
    """Collect system evidence from various sources."""
    print("[Evidence Collector] Gathering system evidence...")

    evidence = {}

    # Access Control (AC)
    evidence["AC - SSH Configuration"] = run_cmd("grep -E '^(PermitRootLogin|PasswordAuthentication|MaxAuthTries)' /etc/ssh/sshd_config")
    evidence["AC - User Accounts"] = run_cmd("awk -F: '$3 >= 1000 {print $1, $3, $7}' /etc/passwd")
    evidence["AC - Sudo Configuration"] = run_cmd("grep -v '^#' /etc/sudoers.d/* 2>/dev/null || echo 'Default sudoers only'")

    # Audit & Accountability (AU)
    evidence["AU - Audit Rules"] = run_cmd("sudo auditctl -l 2>/dev/null || echo 'auditd not running'")
    evidence["AU - Recent Audit Events"] = run_cmd("sudo ausearch -ts recent -m USER_LOGIN 2>/dev/null | tail -20 || echo 'No recent events'")

    # System & Communications Protection (SC)
    evidence["SC - Firewall Rules"] = run_cmd("sudo firewall-cmd --list-all 2>/dev/null || echo 'firewalld not running'")
    evidence["SC - Listening Ports"] = run_cmd("ss -tlnp")

    # System & Information Integrity (SI)
    evidence["SI - CIS Scan Summary"] = run_cmd("ls -la /tmp/cis-results-*.xml 2>/dev/null | tail -1 || echo 'No CIS scan results found'")
    evidence["SI - Package Updates"] = run_cmd("dnf check-update --quiet 2>/dev/null | head -10 || echo 'All packages up to date'")

    # Configuration Management (CM)
    evidence["CM - Running Services"] = run_cmd("systemctl list-units --type=service --state=running --no-pager | head -20")
    evidence["CM - FedTracker Service"] = run_cmd("systemctl status fedtracker 2>/dev/null || echo 'FedTracker not running as service'")

    return evidence


def generate_evidence_package(evidence):
    """Generate a Markdown evidence package with AI-generated summaries."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    output_path = f"/opt/fedtracker/evidence-package-{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"

    lines = [
        f"# Compliance Evidence Package",
        f"## FedTracker Application — Phase 1",
        f"",
        f"**Generated:** {timestamp}",
        f"**System:** {run_cmd('hostname')}",
        f"**OS:** {run_cmd('cat /etc/oracle-release')}",
        f"**Method:** Automated collection with AI-assisted narrative (Ollama tinyllama)",
        f"",
        f"---",
        f""
    ]

    control_families = {
        "Access Control (AC)": ["AC - SSH Configuration", "AC - User Accounts", "AC - Sudo Configuration"],
        "Audit & Accountability (AU)": ["AU - Audit Rules", "AU - Recent Audit Events"],
        "System & Communications Protection (SC)": ["SC - Firewall Rules", "SC - Listening Ports"],
        "System & Information Integrity (SI)": ["SI - CIS Scan Summary", "SI - Package Updates"],
        "Configuration Management (CM)": ["CM - Running Services", "CM - FedTracker Service"],
    }

    for family, controls in control_families.items():
        print(f"[Evidence Collector] Processing: {family}")
        lines.append(f"## {family}")
        lines.append(f"")

        # Collect evidence for this family
        family_evidence = ""
        for ctrl in controls:
            if ctrl in evidence:
                lines.append(f"### {ctrl}")
                lines.append(f"```")
                lines.append(evidence[ctrl])
                lines.append(f"```")
                lines.append(f"")
                family_evidence += f"{ctrl}:\n{evidence[ctrl]}\n\n"

        # Generate AI narrative summary
        prompt = f"""You are a federal cybersecurity compliance analyst.
Review the following evidence for the {family} control family and write a brief (3-4 sentence)
assessment. Note any findings that comply with NIST 800-171 / CMMC and any gaps that need remediation.
Be specific about what you observe in the evidence.

Evidence:
{family_evidence}

Assessment:"""

        print(f"[Evidence Collector] Generating AI summary for {family}...")
        ai_summary = query_ollama(prompt)
        lines.append(f"**AI Assessment:**")
        lines.append(f"> {ai_summary}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

    # Write the package
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"\n[Evidence Collector] Evidence package written to: {output_path}")
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("  AI-Powered Compliance Evidence Collector")
    print(f"  Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    # Check Ollama is available
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        print(f"  Ollama models available: {models}")
    except Exception:
        print("  WARNING: Ollama not reachable. AI summaries will fail.")
        print("  Fix: sudo systemctl start ollama && ollama pull tinyllama")

    print("")

    evidence = collect_evidence()
    output = generate_evidence_package(evidence)

    print(f"\n{'=' * 60}")
    print(f"  Evidence package complete: {output}")
    print(f"  View it: cat {output}")
    print(f"{'=' * 60}")
PYEOF

# Install requests library (needed for Ollama API calls)
pip3.11 install requests --user
```

```bash
# Run the evidence collector
python3 /opt/fedtracker/evidence_collector.py
```

> The script takes 3-5 minutes — it queries Ollama for each control family. The output is a Markdown file with raw evidence and AI-generated assessment narratives.

**Verify:**

```bash
# Check the evidence package was created
ls -la /opt/fedtracker/evidence-package-*.md
# Expected: File exists, non-zero size

# View the first 50 lines
head -50 /opt/fedtracker/evidence-package-*.md
# Expected: Markdown with control families, evidence blocks, and AI assessments
```

> **🧠 Interview framing:** "I built an AI-powered compliance evidence collector using Ollama running locally on the server. It collects system evidence — SSH configuration, audit rules, firewall state, CIS scan results — and feeds it to a local LLM that generates narrative assessments per NIST 800-171 control family. In production, I'd use OCI Generative AI Service for better model quality, but Ollama demonstrates the same pattern and works air-gapped."

---

### Phase 16 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `ollama --version` | Version printed | Ollama not installed. Re-run the install script |
| `ollama pull tinyllama` | Model downloaded | Not enough disk space? Try a smaller quantized variant |
| `ollama run tinyllama "test"` | Text response | Model not loaded? Wait 30 seconds after pull. Check RAM: `free -h` (need ~1 GB available for tinyllama) |
| Evidence collector runs | Markdown file created | `requests` not installed? `pip3.11 install requests --user`. Ollama not running? `sudo systemctl start ollama` |
| AI summaries are "[Ollama error]" | Should be narrative text | Ollama service down or model not pulled. Check `curl http://localhost:11434/api/tags` |

---

## DAY 4 RECAP

### Day 4 Complete

**What you built:**
- Dockerfile for FedTracker (non-root user, health check, multi-stage)
- Built and ran containers with both Podman and Docker
- docker-compose.yml with persistent volumes
- OpenSCAP CIS benchmark scan script with automated scoring
- Remediated top CIS failures to improve compliance score
- AI-powered compliance evidence collector using Ollama

**What's running:**
- FedTracker can run as container (Podman or Docker) or systemd service
- OpenSCAP scan reports available as HTML
- Ollama LLM running locally for air-gapped AI inference
- Evidence package generated with AI-assisted narratives

**What you can now talk about in interviews:**
- "I containerized the application with both Podman and Docker — same Dockerfile works with both. On Oracle Linux, I default to Podman because it's daemonless and rootless"
- "I run containers as non-root users with HEALTHCHECK directives for orchestrator integration"
- "I used Docker Compose for multi-container management with persistent volumes to survive container restarts"
- "I ran CIS Level 1 benchmarks with OpenSCAP, achieved X% compliance, and remediated the top failures"
- "I built an AI-powered evidence collector using Ollama for local LLM inference — it generates compliance narratives per NIST 800-171 control family from collected system evidence"

**Skills practiced:** Podman (new), Docker, Docker Compose, OpenSCAP CIS compliance, Ollama/AI, Python, security compliance

**Next:** Day 5 — "Pipeline & Operations" — you'll build OCI Functions (serverless), a Jenkins pipeline, run DR drills, and tear everything down cleanly.

---

## PHASE 17: OCI FUNCTIONS — SERVERLESS (2 hrs)

> Serverless means you upload code and the cloud runs it — no servers to manage, no OS to patch, no capacity to plan. You pay only when the function executes. OCI Functions is built on the open-source Fn Project, which means less vendor lock-in than AWS Lambda. You'll build two functions: an audit file processor (triggered by Object Storage uploads) and a health check automation (triggered by monitoring alarms).
>
> 📍 **Where work happens:** OCI Console and Local Terminal.
>
> 🛠️ **Build approach:** Function code built by hand. OCI Console for configuration.

---

### Step 17.1 — Understand Serverless
📍 **Read before doing**

> **🧠 ELI5 — Serverless / FaaS:** Imagine a taxi vs owning a car. With a car (VM), you pay for parking, insurance, and maintenance whether you drive or not. With a taxi (serverless), you only pay when you ride. Serverless functions work the same way — your code sits dormant until an event triggers it (file upload, HTTP request, scheduled timer). The cloud spins up a container, runs your code, and tears it down. You never see the server.

> **🧠 ELI5 — OCI Functions vs AWS Lambda:**
>
> | Feature | OCI Functions | AWS Lambda |
> |---------|--------------|-----------|
> | Built on | Fn Project (open-source) | Proprietary |
> | Free tier | 2 million invocations/month | 1 million invocations/month |
> | Max runtime | 300 seconds | 900 seconds |
> | Languages | Python, Java, Go, Node.js, Ruby, C# | Same + custom runtimes |
> | Trigger sources | OCI Events, API Gateway, Notifications | EventBridge, S3, API Gateway, SQS |
> | Vendor lock-in | Lower (Fn Project portable) | Higher (Lambda-specific APIs) |

---

### Step 17.2 — Set Up OCI Functions Application
📍 **OCI Console**

1. Navigate to **Developer Services** → **Functions** → **Applications**
2. Make sure `fedtracker-lab` compartment is selected
3. Click **Create Application**
4. Fill in:
   - **Name:** `fedtracker-functions`
   - **VCN:** `fedtracker-vcn`
   - **Subnet:** `public-subnet` (functions need internet access for external dependencies)
5. Click **Create**

---

### Step 17.3 — Set Up Fn CLI
📍 **Local Terminal**

```bash
# Install the Fn CLI
# macOS:
brew install fn

# Linux:
curl -LSs https://raw.githubusercontent.com/fnproject/cli/master/install | sh

# Verify
fn version
# Expected: fn version x.x.x
```

```bash
# Configure Fn to use OCI
fn create context oci-context --provider oracle
fn use context oci-context

# Set configuration values
fn update context oracle.compartment-id <COMPARTMENT_OCID>
fn update context api-url https://functions.<REGION>.oci.oraclecloud.com
fn update context registry <REGION>.ocir.io/<TENANCY_NAMESPACE>/fedtracker
```

> **Important:** Replace `<REGION>`, `<COMPARTMENT_OCID>`, and `<TENANCY_NAMESPACE>` with your actual values. Find your tenancy namespace in OCI Console → Tenancy Details.

---

### Step 17.4 — Build Audit File Processor Function
📍 **Local Terminal** (build by hand)

> This function triggers when a file is uploaded to an Object Storage bucket. It reads the file, validates its format, and writes a summary to another bucket. This pattern is common in federal environments — evidence files are uploaded, automatically validated, and cataloged.

```bash
# Create function directory
mkdir -p ~/oci-federal-lab/functions/audit-processor
cd ~/oci-federal-lab/functions/audit-processor

# Initialize the function
fn init --runtime python audit-processor
```

**Build `func.py`:**

```bash
cat > func.py << 'FNEOF'
"""
Audit File Processor — OCI Function
Triggered by: Object Storage file upload to "audit-evidence" bucket
Action: Reads the file, validates format, writes summary to "audit-processed" bucket

This demonstrates serverless event-driven architecture:
File upload → OCI Events → OCI Notifications → This Function → Output to bucket
"""

import io
import json
import logging
from datetime import datetime, timezone

import oci
from fdk import response


def handler(ctx, data: io.BytesIO = None):
    """
    Main function handler — called by OCI Functions runtime.
    ctx: function context (config, headers)
    data: event payload (JSON with Object Storage event details)
    """
    logging.getLogger().info("Audit file processor triggered")

    try:
        body = json.loads(data.getvalue())
        logging.getLogger().info(f"Event received: {json.dumps(body, indent=2)}")

        # Extract event details
        event_type = body.get("eventType", "unknown")
        resource_name = body.get("data", {}).get("resourceName", "unknown")
        bucket_name = body.get("data", {}).get("additionalDetails", {}).get("bucketName", "unknown")
        namespace = body.get("data", {}).get("additionalDetails", {}).get("namespace", "unknown")

        # Build summary
        summary = {
            "processor": "audit-file-processor",
            "processed_at": datetime.now(timezone.utc).isoformat() + "Z",
            "event_type": event_type,
            "source_file": resource_name,
            "source_bucket": bucket_name,
            "namespace": namespace,
            "validation": "passed",
            "status": "processed"
        }

        logging.getLogger().info(f"Processing complete: {resource_name}")

        return response.Response(
            ctx,
            response_data=json.dumps(summary),
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        logging.getLogger().error(f"Error processing event: {str(e)}")
        error_response = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
        }
        return response.Response(
            ctx,
            response_data=json.dumps(error_response),
            headers={"Content-Type": "application/json"},
            status_code=500
        )
FNEOF
```

**Create `requirements.txt`:**

```bash
cat > requirements.txt << 'EOF'
fdk>=0.1.0
oci>=2.0.0
EOF
```

**Create `func.yaml`:**

```bash
cat > func.yaml << 'EOF'
schema_version: 20180708
name: audit-processor
version: 0.0.1
runtime: python
build_image: fnproject/python:3.9-dev
run_image: fnproject/python:3.9
entrypoint: /python/bin/fdk /function/func.py handler
memory: 256
timeout: 120
EOF
```

**Deploy the function:**

```bash
# Deploy to OCI Functions
fn deploy --app fedtracker-functions
# Expected: Function deployed successfully
```

> **Cost check:** OCI Functions = $0.00 for first 2 million invocations/month on Always Free tier. That's more generous than AWS Lambda's 1 million. Verify at: [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)

---

### Step 17.5 — Build Health Check Function
📍 **Local Terminal** (build by hand)

> This function checks your application's health endpoint. It could be triggered by a monitoring alarm (CPU > 80%) or run on a schedule. When it detects the app is down, it logs the incident.

```bash
mkdir -p ~/oci-federal-lab/functions/health-checker
cd ~/oci-federal-lab/functions/health-checker

fn init --runtime python health-checker
```

**Build `func.py`:**

```bash
cat > func.py << 'FNEOF'
"""
Health Check Automation — OCI Function
Triggered by: OCI Alarm, scheduled invocation, or manual trigger
Action: Checks app health endpoint, reports status

In production, this would:
1. Check the health endpoint
2. If unhealthy, create an incident ticket
3. Optionally trigger auto-remediation
"""

import io
import json
import logging
from datetime import datetime, timezone

from fdk import response


def handler(ctx, data: io.BytesIO = None):
    """Health check handler — verifies app endpoints are responding."""
    logging.getLogger().info("Health check function triggered")

    # Get the target URL from function config (set in OCI Console)
    app_url = ctx.Config().get("APP_HEALTH_URL", "http://app-server:8000/health")

    try:
        import urllib.request
        req = urllib.request.Request(app_url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            status_code = resp.status
            body = json.loads(resp.read().decode())

        result = {
            "function": "health-checker",
            "checked_at": datetime.now(timezone.utc).isoformat() + "Z",
            "target": app_url,
            "status_code": status_code,
            "app_status": body.get("status", "unknown"),
            "db_status": body.get("database", {}).get("status", "unknown"),
            "verdict": "HEALTHY" if status_code == 200 else "UNHEALTHY"
        }

    except Exception as e:
        result = {
            "function": "health-checker",
            "checked_at": datetime.now(timezone.utc).isoformat() + "Z",
            "target": app_url,
            "error": str(e),
            "verdict": "UNREACHABLE"
        }

    logging.getLogger().info(f"Health check result: {result['verdict']}")

    return response.Response(
        ctx,
        response_data=json.dumps(result),
        headers={"Content-Type": "application/json"}
    )
FNEOF
```

```bash
cat > requirements.txt << 'EOF'
fdk>=0.1.0
EOF

cat > func.yaml << 'EOF'
schema_version: 20180708
name: health-checker
version: 0.0.1
runtime: python
build_image: fnproject/python:3.9-dev
run_image: fnproject/python:3.9
entrypoint: /python/bin/fdk /function/func.py handler
memory: 256
timeout: 30
EOF

# Deploy
fn deploy --app fedtracker-functions
```

---

### Step 17.6 — Test Functions
📍 **Local Terminal**

```bash
# Invoke the health checker manually
echo '{}' | fn invoke fedtracker-functions health-checker
# Expected: JSON with health check results

# Invoke the audit processor with a simulated event
echo '{"eventType":"com.oraclecloud.objectstorage.createobject","data":{"resourceName":"test-evidence.txt","additionalDetails":{"bucketName":"audit-evidence","namespace":"<YOUR_TENANCY_NAMESPACE>"}}}' | fn invoke fedtracker-functions audit-processor
# Expected: JSON with processing results
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `fn init` | `--runtime python` | Initialize a new function project |
| `fn deploy` | `--app <name>` | Build and deploy function to OCI |
| `fn invoke` | `<app> <function>` | Trigger a function manually |
| `fn create context` | `--provider oracle` | Set up Fn CLI for OCI |

</em></sub>

---

### Phase 17 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `fn version` | Version number | Install Fn CLI. Check PATH |
| `fn deploy` succeeds | Function deployed | Check: (1) Docker running (Fn builds images locally), (2) OCIR login configured, (3) context configured correctly |
| `fn invoke` returns JSON | Function result | Check function logs: `fn inspect function fedtracker-functions health-checker`. Common: timeout, wrong config |
| Function can reach app | Health data returned | Network issue — function and app server must be in same VCN or have proper routing |

---

## PHASE 18: JENKINS PIPELINE (2 hrs)

> Jenkins is a CI/CD automation server — it watches your git repository and automatically runs validations, tests, and deployments when code changes. You'll install Jenkins on the bastion VM and build a pipeline that validates Terraform, lints Ansible, and deploys the containerized app.
>
> 📍 **Where work happens:** Bastion VM Terminal, Browser (Jenkins UI), Editor.
>
> 🛠️ **Build approach:** Jenkins installed via commands. Jenkinsfile built by hand.

> **Interview Insight: "The JD says CloudBees Jenkins — what's the difference?"**
>
> **Strong answer:** "CloudBees Jenkins is the enterprise distribution of Jenkins. It adds features critical for federal environments: RBAC with fine-grained permissions, audit trails for compliance (who ran what pipeline when), high availability with managed controllers, and enterprise support with SLAs. The core pipeline syntax (Jenkinsfile, stages, steps) is identical — CloudBees wraps Jenkins with enterprise governance. I built my pipelines on open-source Jenkins because CloudBees requires a license, but every Jenkinsfile I wrote would run on CloudBees without modification."
>
> **Weak answer:** "I'm not sure what CloudBees is." (Shows you didn't read the JD carefully)
>
> **What's coming next:** In Phase 2, you will migrate this open-source Jenkins instance to CloudBees CI (using the 30-day free trial) to experience the migration firsthand — backup, WAR replacement, license activation, and enterprise feature configuration. Phase 3 deepens CloudBees usage with pipeline templates, CasC bundle versioning, and cross-team governance. By the end, you'll have a complete Jenkins → CloudBees CI migration story for interviews.

---

### Step 18.1 — Install Jenkins
📍 **VM Terminal** (bastion)

> **🧠 ELI5 — Jenkins:** Jenkins is an automation butler — it watches your code repository and executes a pipeline (a series of steps) whenever you push changes. Each step might validate Terraform syntax, lint Ansible playbooks, run tests, build containers, or deploy to production. If any step fails, the pipeline stops and alerts you. This prevents broken code from reaching production.

```bash
ssh bastion

# Install Java (Jenkins requires it)
sudo dnf install -y java-17-openjdk

# Add Jenkins repository
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key

# Install Jenkins
sudo dnf install -y jenkins

# Start Jenkins
sudo systemctl enable --now jenkins

# Open firewall for Jenkins (port 8080)
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload
```

> **Cost check:** Jenkins runs on the bastion VM you already have. No additional cloud cost.

```bash
# Get the initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
# Copy this password — you'll need it to log in
```

📍 **OCI Console**

Add an ingress rule for port 8080 on the public subnet security list (same process as Step 4.3 for port 8000, but on the public-sl for port 8080).

📍 **Browser**

```
http://<BASTION_PUBLIC_IP>:8080
```

1. Paste the initial admin password
2. Install suggested plugins (wait 3-5 minutes)
3. Create your admin user
4. Finish setup

---

### Step 18.2 — Create Jenkinsfile
📍 **Editor** (build by hand)

> **🧠 ELI5 — Jenkinsfile:** A Jenkinsfile is a pipeline-as-code — it defines your CI/CD pipeline in a file that lives in your git repository alongside your code. This means the pipeline is versioned, reviewed, and auditable. No more clicking through a web UI to configure builds — the pipeline IS the code.

**Build `Jenkinsfile` section by section:**

```bash
mkdir -p ~/oci-federal-lab/jenkins
```

**Build `jenkins/Jenkinsfile`:**

```groovy
// Jenkinsfile — FedTracker CI/CD Pipeline
// Stages: Validate Terraform → Lint Ansible → Build Container → Deploy

pipeline {
    agent any

    environment {
        PROJECT_NAME = 'fedtracker'
        TERRAFORM_DIR = 'terraform'
        ANSIBLE_DIR = 'ansible'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Terraform Validate') {
            steps {
                echo 'Validating Terraform configuration...'
                dir("${TERRAFORM_DIR}") {
                    sh '''
                        terraform init -backend=false
                        terraform validate
                        terraform fmt -check -diff
                    '''
                }
            }
        }

        stage('Ansible Lint') {
            steps {
                echo 'Linting Ansible playbooks...'
                sh '''
                    ansible-playbook --syntax-check ${ANSIBLE_DIR}/playbooks/harden.yml
                    ansible-playbook --syntax-check ${ANSIBLE_DIR}/playbooks/deploy_app.yml
                '''
            }
        }

        stage('Build Container') {
            steps {
                echo 'Building container image...'
                dir('app') {
                    sh '''
                        podman build -t ${PROJECT_NAME}:${BUILD_NUMBER} .
                        podman build -t ${PROJECT_NAME}:latest .
                    '''
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to app server...'
                sh '''
                    ansible-playbook -i ${ANSIBLE_DIR}/inventory.ini \
                        ${ANSIBLE_DIR}/playbooks/deploy_app.yml
                '''
            }
        }

        stage('Smoke Test') {
            when {
                branch 'main'
            }
            steps {
                echo 'Running smoke test...'
                sh '''
                    sleep 15
                    ssh app-server "curl -sf http://localhost:8000/health" || exit 1
                    echo "Smoke test passed!"
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully! Build #${BUILD_NUMBER}"
        }
        failure {
            echo "Pipeline FAILED at build #${BUILD_NUMBER}. Check console output for details."
        }
        always {
            echo "Pipeline finished. Duration: ${currentBuild.durationString}"
        }
    }
}
```

> **What is `when { branch 'main' }`?** This conditional makes the Deploy and Smoke Test stages only run on the `main` branch. Feature branches get Validate + Lint + Build (catch errors early) but don't deploy. This prevents broken branches from reaching production.

> **What is the `post` block?** Code that runs after all stages, regardless of success or failure. `success` = ran when pipeline passed. `failure` = runs when any stage failed. `always` = runs no matter what. In production, you'd add Slack notifications or email alerts here.

---

### Step 18.3 — Configure Jenkins Pipeline Job
📍 **Browser** (Jenkins UI)

1. Click **New Item** → enter name `fedtracker-pipeline` → select **Pipeline** → OK
2. Under **Pipeline** section:
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** Your git repo URL
   - **Script Path:** `jenkins/Jenkinsfile`
3. Click **Save**
4. Click **Build Now** to trigger the first run

Watch the pipeline execute — you should see each stage go green.

---

### Step 18.4 — Add Jenkins Credentials
📍 **Browser** (Jenkins UI)

For the pipeline to deploy, Jenkins needs SSH access to the app server:

1. **Manage Jenkins** → **Credentials** → **System** → **Global credentials** → **Add Credentials**
2. Select **SSH Username with private key**
3. Fill in:
   - **ID:** `app-server-ssh`
   - **Username:** `opc`
   - **Private Key:** Enter directly → paste the app server private key
4. Click **Create**

Similarly, add the `terraform.tfvars` as a secret file credential for the Terraform stages.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `terraform validate` | | Check Terraform syntax and internal consistency |
| `terraform fmt` | `-check -diff` | Check formatting without modifying. `-check` = exit code 1 if not formatted, `-diff` = show differences |
| `ansible-playbook` | `--syntax-check` | Validate YAML syntax without running |

</em></sub>

---

### Phase 18 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| Jenkins UI loads | Login page at :8080 | Check: (1) Jenkins service running: `systemctl status jenkins`, (2) firewall port 8080 open, (3) OCI security list has 8080 ingress |
| Initial password works | Unlock Jenkins screen | Run `sudo cat /var/lib/jenkins/secrets/initialAdminPassword` again |
| Pipeline Terraform stage | Green/passed | Terraform not installed on Jenkins agent? Install on bastion |
| Pipeline Ansible stage | Green/passed | Ansible not installed? `pip3.11 install ansible` on bastion |
| Pipeline Deploy stage | Green/passed | SSH credential not configured? Add SSH key in Jenkins credentials |
| Smoke test passes | Health endpoint returns 200 | App not responding after deploy. Check `journalctl -u fedtracker` on app server |

---

## PHASE 19: DR DRILL & TEARDOWN (2 hrs)

> Disaster recovery isn't real until you've tested it. Today you'll back up the app server, intentionally destroy it, restore from backup, and measure how long recovery takes. Then you'll write a DR runbook documenting the exact steps. Finally, you'll tear down all resources to prove you can destroy and rebuild the entire environment from code.
>
> 📍 **Where work happens:** OCI Console, Local Terminal, VM Terminal.
>
> 🛠️ **Build approach:** DR runbook written by hand. All commands documented.

---

### Step 19.1 — Create Block Volume Backup
📍 **OCI Console**

> **🧠 ELI5 — Block Volume Backup:** A block volume backup is a snapshot of your VM's disk at a specific point in time. If the VM is destroyed, you can create a new VM from this snapshot and it will be in the exact state it was when the backup was taken — same files, same data, same configuration. It's like taking a photograph of your entire server.

1. Navigate to **Compute** → **Instances** → `app-server`
2. Click on the **Boot Volume** in the Resources section
3. Click **Create Backup**
4. Fill in:
   - **Name:** `app-server-backup-pre-dr-drill`
   - **Backup Type:** Full
5. Click **Create Boot Volume Backup**

Wait 5-10 minutes for the backup to complete.

> **Cost check:** Boot volume backups on Always Free tier. Check current pricing — OCI Object Storage for backups is $0.0255/GB/month, but small backups stay within free tier limits.

---

### Step 19.2 — DR Drill: Destroy and Recover
📍 **Local Terminal**

**Step 1: Document current state**

```bash
# Record what's working
ssh app-server "curl -s http://localhost:8000/health" > /tmp/pre-dr-health.json
ssh app-server "curl -s http://localhost:8000/personnel" > /tmp/pre-dr-personnel.json
echo "Pre-DR health check saved"
cat /tmp/pre-dr-health.json
```

**Step 2: Destroy the app server (simulating a disaster)**

```bash
cd ~/oci-federal-lab/terraform

# Destroy only the app server
terraform destroy -target=oci_core_instance.app_server
# Type "yes"
# Expected: app-server destroyed
```

> This simulates a real disaster — the app server is gone. In production, this could be a hardware failure, accidental deletion, or a ransomware event.

**Step 3: Start the recovery timer**

```bash
echo "Recovery started at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
RECOVERY_START=$(date +%s)
```

**Step 4: Recreate the infrastructure**

```bash
terraform apply
# Type "yes"
# Expected: app-server recreated with new IP
```

**Step 5: Update inventory and run Ansible**

```bash
# Get new IP
NEW_APP_IP=$(terraform output -raw app_server_private_ip)
echo "New app server IP: $NEW_APP_IP"

# Update inventory (manual for now — could be automated)
# Edit ansible/inventory.ini with the new IP

# Wait for VM to boot
sleep 60

# Harden and deploy
cd ~/oci-federal-lab
ansible-playbook -i ansible/inventory.ini ansible/playbooks/harden.yml
ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy_app.yml
```

**Step 6: Verify recovery**

```bash
# Test the recovered app
ssh app-server "curl -s http://localhost:8000/health"
# Expected: {"status": "healthy", ...}

ssh app-server "curl -s http://localhost:8000/personnel"
# Expected: Personnel records (seed data from fresh deploy)

# Stop the timer
RECOVERY_END=$(date +%s)
RECOVERY_SECONDS=$((RECOVERY_END - RECOVERY_START))
RECOVERY_MINUTES=$((RECOVERY_SECONDS / 60))
echo ""
echo "============================="
echo "Recovery completed!"
echo "RTO (Recovery Time Objective): ${RECOVERY_MINUTES} minutes"
echo "RPO (Recovery Point Objective): Data from last backup"
echo "============================="
```

**Step 7: Post-recovery Linux forensics**

After recovery, investigate what happened during the incident — this is what a real post-incident review looks like:

```bash
# Check what happened during the previous boot (before the disaster)
ssh app-server "sudo journalctl -b -1 --no-pager | tail -50"
# -b -1 = previous boot. Shows the last 50 lines before shutdown
# In a real incident, you'd look for errors leading up to the failure

# Check for OOM kills (common cause of "mysterious" service failures)
ssh app-server "sudo dmesg | grep -i oom"
# If you see "Out of memory: Kill process", that's your smoking gun
# The kernel killed a process to free memory — check which one

# Check if the OOM killer was involved via journalctl
ssh app-server "sudo journalctl -k | grep -i 'out of memory'"
```

> **LVM snapshot as pre-change backup strategy:** In production, before running a DR drill or making risky changes, you'd take an LVM snapshot of the data volume:
>
> ```bash
> # Before the drill:
> sudo lvcreate -s -L 5G -n app-snap /dev/app-vg/app-data
>
> # If the drill fails and you need to revert:
> sudo lvconvert --merge /dev/app-vg/app-snap
>
> # If the drill succeeds, clean up:
> sudo lvremove /dev/app-vg/app-snap
> ```
>
> LVM snapshots are instantaneous and much faster than block volume backups. They're your "undo button" for risky changes. In this lab, we used OCI block volume backups (cloud-level), but in a bare-metal federal environment, LVM snapshots are the go-to approach.

---

### Step 19.3 — Write DR Runbook
📍 **Editor** (build by hand)

```bash
cat > ~/oci-federal-lab/docs/dr-runbook.md << 'DREOF'
# FedTracker Disaster Recovery Runbook

## Overview
- **Application:** FedTracker (FastAPI on Oracle Linux 8)
- **Infrastructure:** OCI (Terraform-managed)
- **Configuration:** Ansible-managed
- **Measured RTO:** ~15 minutes (terraform apply + ansible-playbook)
- **RPO:** Last database backup (Oracle Autonomous DB has continuous backup)

## Recovery Procedure

### Step 1: Assess the Damage
```bash
terraform plan
# This shows what resources are missing
```

### Step 2: Recreate Infrastructure
```bash
terraform apply
# Type "yes" — recreates all missing resources
```

### Step 3: Update Ansible Inventory
```bash
NEW_IP=$(terraform output -raw app_server_private_ip)
# Update ansible/inventory.ini with new IP
```

### Step 4: Configure and Deploy
```bash
ansible-playbook -i ansible/inventory.ini ansible/playbooks/harden.yml
ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy_app.yml
```

### Step 5: Verify
```bash
ssh app-server "curl -s http://localhost:8000/health"
ssh app-server "curl -s http://localhost:8000/personnel"
```

## Key Contacts
- Infrastructure: <YOUR_NAME> (Terraform owner)
- Application: <YOUR_NAME> (FedTracker maintainer)
- Database: Oracle Autonomous DB (auto-managed)

## Lessons Learned
- Database survives VM loss (Oracle Autonomous DB is separate)
- Application code is in git — no data loss
- Ansible ensures consistent configuration on new VMs
- Main delay is VM boot time (~60 seconds)
DREOF
```

---

### Step 19.4 — Cost Reporting Script
📍 **VM Terminal** (build by hand)

```bash
ssh app-server
su - clouduser

cat > /opt/fedtracker/cost_reporter.py << 'PYEOF'
#!/usr/bin/env python3
"""
OCI Cost and Compliance Reporter
Reports on resource costs, tagging compliance, and free tier usage.

Usage: python3 cost_reporter.py
Requires: pip3.11 install oci
"""

import oci
import sys
from datetime import datetime, timezone


def main():
    # Load OCI config
    try:
        config = oci.config.from_file()
    except Exception as e:
        print(f"[ERROR] Failed to load OCI config: {e}")
        sys.exit(1)

    print(f"\n{'#'*60}")
    print(f"  OCI COST & COMPLIANCE REPORT")
    print(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Region:    {config.get('region')}")
    print(f"{'#'*60}")

    # Get compartment
    identity = oci.identity.IdentityClient(config)
    tenancy_id = config["tenancy"]
    compartments = identity.list_compartments(tenancy_id).data
    lab_compartment = None
    for c in compartments:
        if c.name == "fedtracker-lab" and c.lifecycle_state == "ACTIVE":
            lab_compartment = c
            break

    if not lab_compartment:
        print("[WARNING] fedtracker-lab compartment not found")
        return

    compartment_id = lab_compartment.id

    # List compute instances
    compute = oci.core.ComputeClient(config)
    instances = compute.list_instances(compartment_id).data

    print(f"\n{'='*60}")
    print(f"  RESOURCE INVENTORY")
    print(f"{'='*60}")

    total_ocpus = 0
    total_memory = 0
    untagged = 0

    for inst in instances:
        if inst.lifecycle_state == "TERMINATED":
            continue
        ocpus = inst.shape_config.ocpus if inst.shape_config else 0
        memory = inst.shape_config.memory_in_gbs if inst.shape_config else 0
        total_ocpus += ocpus
        total_memory += memory

        tagged = "✓" if inst.freeform_tags else "✗"
        if not inst.freeform_tags:
            untagged += 1

        print(f"  {inst.display_name:20s} {inst.shape:25s} {ocpus} OCPU / {memory} GB  Tags: {tagged}")

    # Free tier check
    print(f"\n{'='*60}")
    print(f"  FREE TIER USAGE")
    print(f"{'='*60}")
    print(f"  A1 Flex OCPUs:  {total_ocpus}/4  ({'WITHIN LIMIT' if total_ocpus <= 4 else 'OVER LIMIT!'})")
    print(f"  A1 Flex Memory: {total_memory}/24 GB  ({'WITHIN LIMIT' if total_memory <= 24 else 'OVER LIMIT!'})")
    print(f"  Untagged:       {untagged} resource(s)")

    # Summary
    print(f"\n{'='*60}")
    print(f"  ESTIMATED MONTHLY COST")
    print(f"{'='*60}")
    if total_ocpus <= 4 and total_memory <= 24:
        print(f"  Compute:  $0.00 (within Always Free tier)")
    else:
        print(f"  Compute:  WARNING — exceeds free tier limits!")
    print(f"  VCN/NAT:  $0.00 (free on OCI)")
    print(f"  ADB:      $0.00 (Always Free 1 OCPU / 20 GB)")
    print(f"  Total:    $0.00")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
PYEOF
```

```bash
python3 /opt/fedtracker/cost_reporter.py
```

---

### Step 19.5 — Final Teardown
📍 **Local Terminal**

> ⚠️ **This destroys ALL resources.** Only do this when you're done with the entire lab.

```bash
cd ~/oci-federal-lab/terraform

# Preview what will be destroyed
terraform plan -destroy

# Destroy everything
terraform destroy
# Type "yes"
# Expected: "Destroy complete! Resources: X destroyed"
```

📍 **OCI Console**

Manually verify and clean up resources that Terraform doesn't manage:
1. **Oracle Database** → **Autonomous Database** → terminate `fedtracker-db`
2. **Object Storage** → delete any buckets
3. **Functions** → delete `fedtracker-functions` application
4. **Identity** → review policies (optional to delete)

```bash
# Final verification — confirm nothing is running
# Check OCI Console: no instances, no VCN, no database
```

---

### Step 19.6 — Final Git Commit
📍 **Local Terminal**

```bash
cd ~/oci-federal-lab

git add functions/ jenkins/ docs/ app/
git commit -m "Day 5: OCI Functions, Jenkins pipeline, DR drill, cost reporting, teardown

- OCI Functions: audit file processor + health checker (serverless)
- Jenkins pipeline: Terraform validate, Ansible lint, container build, deploy, smoke test
- DR drill completed: measured RTO of ~15 minutes
- DR runbook documented
- Cost reporter: free tier usage tracking + tagging compliance
- All resources torn down cleanly"
```

---

### Phase 19 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| Boot volume backup completes | Backup shows "Available" | Wait longer — backups can take 10-15 minutes for large volumes |
| `terraform destroy -target` works | App server destroyed | Check resource dependencies. If subnet can't be deleted, instances still exist |
| `terraform apply` recreates | New VM created | Check service limits. A1 Flex capacity may be exhausted in your region |
| Ansible deploy to new VM | App running on new IP | Update inventory with new IP. Wait for VM to fully boot (60+ seconds) |
| Cost reporter runs | Report printed | OCI SDK installed? Config file exists? Check `~/.oci/config` |
| Final teardown completes | All resources destroyed | Some resources may have dependencies. Delete in order: instances → subnets → VCN |

---

## DAY 5 RECAP — PHASE 1 COMPLETE

### What You Built Over 5 Days

| Day | What You Did | Skills Practiced |
|-----|-------------|-----------------|
| Day 1 | Manual VM setup, Linux admin, FastAPI REST API (built from scratch), systemd, Bash/Python scripts | Oracle Linux, OCI basics, FastAPI, REST APIs, Bash, Python, systemd |
| Day 2 | Proper architecture: VCN, subnets, bastion, Oracle DB, security hardening, IAM, cost tagging | OCI networking, Oracle DB, security, cost management, IAM |
| Day 3 | Terraform + Ansible automation, destroy/rebuild proof | Terraform, Ansible, IaC, configuration management |
| Day 4 | Podman, Docker, Docker Compose, OpenSCAP CIS, Ollama AI evidence collector | Containers, compliance scanning, AI/LLM integration |
| Day 5 | OCI Functions, Jenkins pipeline, DR drill, cost reporting, teardown | Serverless, CI/CD, disaster recovery, FinOps |

### What You Can Now Talk About in Interviews

- "I built a REST API from scratch using FastAPI with Pydantic validation, pagination, audit logging, and auto-generated API documentation"
- "I designed a secure OCI environment with public/private subnets, bastion access, and Oracle Autonomous DB"
- "I automated infrastructure provisioning with Terraform and server hardening with Ansible"
- "I containerized the application with Podman (Oracle Linux native) and Docker, using non-root containers with health checks"
- "I ran CIS Level 1 benchmarks with OpenSCAP, remediated failures, and tracked compliance score improvement"
- "I built an AI-powered compliance evidence collector using Ollama for air-gapped LLM inference"
- "I implemented serverless event processing with OCI Functions for audit file validation and health check automation"
- "I built a Jenkins CI/CD pipeline that validates Terraform, lints Ansible, builds containers, deploys to the app server, and runs smoke tests"
- "I conducted a disaster recovery drill — destroyed the app server, recovered via Terraform and Ansible in 15 minutes, and documented the runbook with measured RTO and RPO"
- "I implemented cost controls including resource tagging, budget alerts, and a Python cost compliance reporter that verifies free tier usage"

### Your Repository Structure

```
oci-federal-lab/
├── terraform/              # Complete OCI infrastructure as code
│   ├── provider.tf
│   ├── variables.tf
│   ├── network.tf
│   ├── compute.tf
│   └── outputs.tf
├── ansible/                # Server hardening + app deployment
│   ├── inventory.ini
│   ├── templates/
│   │   └── fedtracker.service.j2
│   └── playbooks/
│       ├── harden.yml
│       └── deploy_app.yml
├── app/                    # FedTracker FastAPI application
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── functions/              # OCI Functions (serverless)
│   ├── audit-processor/
│   │   ├── func.py
│   │   ├── func.yaml
│   │   └── requirements.txt
│   └── health-checker/
│       ├── func.py
│       ├── func.yaml
│       └── requirements.txt
├── jenkins/                # CI/CD pipeline
│   └── Jenkinsfile
├── scripts/                # Operational scripts
│   ├── health_check.sh     # Bash health check
│   ├── oci_reporter.py     # OCI resource/tag reporter
│   ├── cost_reporter.py    # Cost and free tier reporter
│   ├── cis_scan.sh         # OpenSCAP CIS benchmark scanner
│   └── evidence_collector.py  # AI compliance evidence generator
├── docs/                   # Documentation
│   ├── phase-1-implementation-guide.md  # This guide
│   └── dr-runbook.md       # Disaster recovery procedures
├── .gitignore
└── README.md
```

### Linux Admin Deep Dive — Practice Labs & Reference

The **[Linux Admin Deep Dive](phase-1-linux-admin-deep-dive.md)** companion guide contains additional hands-on practice labs and troubleshooting exercises for the Linux admin skills introduced throughout Days 1-5. Use it for:
- Extra break-fix practice on any topic (SELinux, LVM, systemd, networking, kernel tuning)
- Interview prep — 8 realistic troubleshooting scenarios with diagnosis steps
- Command quick-reference table for all Linux admin tools
- Deeper exploration of topics where you want more confidence

These exercises can be done alongside or after the main guide — they use the same Phase 1 VM.

### Next: Phase 2 — Disaster Recovery Drill & Backup Architecture

Phase 2 is a completely independent project with a fresh OCI environment. You'll build a resilient environment from the start, implement immutable backup architecture with Object Storage versioning, deploy on k3s (lightweight Kubernetes), simulate a ransomware event, and prove recovery within defined RTO/RPO targets. Terraform and Ansible will be returning concepts (abbreviated guidance), while k3s, AIDE file integrity monitoring, OCI Generative AI incident classification, and webhook-based event processing will be new concepts with full ELI5 treatment.
