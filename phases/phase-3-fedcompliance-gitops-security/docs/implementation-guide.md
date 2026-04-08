# Federal Cloud Engineer Lab — Phase 3 Implementation Guide
## CI/CD Pipeline Modernization & AI-Augmented Operations on OCI

**Goal:** Build a production-grade CI/CD pipeline with security scanning and SBOM generation, deploy to Kubernetes via Helm and ArgoCD GitOps, implement API authentication, and add AI-powered security pattern detection.
**Total Cost:** $0.00 (OCI Always Free tier)
**Primary Tool:** SSH Terminal + OCI Console
**Prerequisite:** Phase 1 and Phase 2 completed

---

## WHAT YOU'RE BUILDING

Over 5 days you transform a manually-deployed compliance tool into a fully automated, security-scanned, GitOps-delivered application with AI-powered operations. Day 1 rebuilds infrastructure using Terraform modules and secrets management. Day 2 builds the CI/CD pipeline with container scanning and SBOM generation. Day 3 upgrades to Helm packaging and ArgoCD GitOps delivery. Day 4 adds AI-augmented security analysis and compliance-as-code. Day 5 validates everything end-to-end and tears down.

| Component | Before (Phase 2) | After (Phase 3) |
|-----------|-------------------|------------------|
| Infrastructure | Flat Terraform files | Terraform modules (network/compute/database) |
| Secrets | Environment variables, plaintext | OCI Vault + Ansible Vault integration |
| Deployment | kubectl apply raw manifests | Helm charts + ArgoCD GitOps auto-sync |
| Pipeline | Jenkins: build + deploy | Jenkins: scan + SBOM + approve + build + deploy |
| Security Scanning | None | Trivy container scan + Syft SBOM (EO 14028) |
| API Auth | None | API key validation + auth middleware |
| K8s Delivery | Manual kubectl | ArgoCD watches git, auto-syncs to cluster |
| AI/ML | Ollama LLM (Phase 1) | scikit-learn IsolationForest anomaly detection |
| Compliance | OpenSCAP manual scan | Compliance-as-code evidence collector in pipeline |
| Application | IncidentResponse API | FedCompliance API (compliance scanning + reporting) |

---

## ARCHITECTURE OVERVIEW

**Day 1 — Secure Foundations:**

```
Internet
    │
┌───▼──────────────────────────────────────────────────────┐
│  OCI VCN: fedcompliance-vcn (10.0.0.0/16)                │
│  (Terraform MODULES — network/compute/database)           │
│                                                            │
│  ┌─────────────────────────────┐                          │
│  │ Public Subnet (10.0.1.0/24) │                          │
│  │  Bastion / Jenkins VM       │                          │
│  │  (Oracle Linux 9)           │                          │
│  └──────────────┬──────────────┘                          │
│                 │ SSH tunnel                               │
│  ┌──────────────▼──────────────┐                          │
│  │ Private Subnet (10.0.2.0/24)│                          │
│  │                              │                          │
│  │  ┌────────────────────────┐ │                          │
│  │  │  k3s Server (node-1)   │ │                          │
│  │  │  + k3s Agent (node-2)  │ │                          │
│  │  │                        │ │                          │
│  │  │  ┌──────────────────┐  │ │                          │
│  │  │  │ FedCompliance    │  │ │                          │
│  │  │  │ (Helm + ArgoCD)  │  │ │                          │
│  │  │  │ Port 8000        │  │ │                          │
│  │  │  └──────────────────┘  │ │                          │
│  │  └────────────────────────┘ │                          │
│  └──────────────┬──────────────┘                          │
│                 │                                          │
│  ┌──────────────▼──────────────┐                          │
│  │ Oracle Autonomous DB         │                          │
│  │ (Always Free, 20 GB)        │                          │
│  └─────────────────────────────┘                          │
│                                                            │
│  OCI Vault: secrets management (API keys, DB creds)       │
│  OCI Functions: log processor, compliance collector        │
│  OCIR: container image registry                            │
│  Object Storage: SBOMs, compliance evidence, backups       │
└────────────────────────────────────────────────────────────┘
```

**Day 5 — Full Pipeline Architecture:**

```
Developer pushes code
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  Jenkins Pipeline                                        │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Checkout  │─▶│ TF Plan  │─▶│ Trivy    │              │
│  │          │  │ Validate │  │ Scan     │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│       │                            │                     │
│       │              ┌─────────────▼─────────┐          │
│       │              │ Syft SBOM Generation   │          │
│       │              │ (EO 14028 compliance)  │          │
│       │              └─────────────┬─────────┘          │
│       │                            │                     │
│       │              ┌─────────────▼─────────┐          │
│       │              │ Ansible Lint           │          │
│       │              └─────────────┬─────────┘          │
│       │                            │                     │
│       │              ┌─────────────▼─────────┐          │
│       │              │ MANUAL APPROVAL GATE   │          │
│       │              │ (federal change mgmt)  │          │
│       │              └─────────────┬─────────┘          │
│       │                            │                     │
│       │              ┌─────────────▼─────────┐          │
│       │              │ Build + Push to OCIR   │          │
│       │              └─────────────┬─────────┘          │
│       │                            │                     │
│       │              ┌─────────────▼─────────┐          │
│       │              │ Update Helm values.yaml│          │
│       │              │ (image tag in git)     │          │
│       │              └─────────────┬─────────┘          │
│       │                            │                     │
│       │              ┌─────────────▼─────────┐          │
│       │              │ Compliance Evidence    │          │
│       │              │ Collection             │          │
│       │              └─────────────┬─────────┘          │
└───────│────────────────────────────│─────────────────────┘
        │                            │
        │              ┌─────────────▼─────────┐
        │              │ ArgoCD (GitOps)        │
        │              │ Watches git repo       │
        │              │ Auto-syncs to k3s      │
        │              └─────────────┬─────────┘
        │                            │
        │              ┌─────────────▼─────────┐
        │              │ k3s Cluster            │
        │              │ FedCompliance running  │
        │              │ via Helm chart          │
        │              └───────────────────────┘
```

**Full Request Path — API Authentication Flow:**

```
Client (curl/browser)
    │
    │  GET /compliance/status
    │  Header: X-API-Key: fc_live_abc123...
    │
    ▼
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│ OCI API      │────▶│ k3s Ingress/ │────▶│ FedCompliance│
│ Gateway      │     │ NodePort     │     │ Pod (FastAPI) │
│ (rate limit) │     │ Service      │     │              │
└─────────────┘     └─────────────┘     │ ┌──────────┐ │
                                         │ │ Auth     │ │
                                         │ │Middleware│ │
                                         │ │          │ │
                                         │ │ Check    │ │
                                         │ │ X-API-Key│ │
                                         │ │ header   │ │
                                         │ └────┬─────┘ │
                                         │      │       │
                                         │      ▼       │
                                         │ ┌──────────┐ │
                                         │ │ Endpoint  │ │
                                         │ │ Handler   │ │
                                         │ └────┬─────┘ │
                                         │      │       │
                                         └──────│───────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │ Oracle        │
                                         │ Autonomous DB │
                                         │ (compliance   │
                                         │  data)        │
                                         └──────┬───────┘
                                                │
                                                ▼
                                         JSON Response
                                         back through
                                         the same path
```

> **🧠 ELI5 — Reading the Request Path:** Follow the arrows from top to bottom — this is what happens every time someone calls your API:
>
> | Step | Component | What Happens | Phase Where You Built This |
> |------|-----------|-------------|---------------------------|
> | 1 | **Client** | Sends HTTP request with `X-API-Key` header | — |
> | 2 | **OCI API Gateway** | Receives request, applies rate limiting (e.g., 100 req/min per client). If over limit, returns `429 Too Many Requests` without ever hitting your app | Phase 2 |
> | 3 | **k3s NodePort/Ingress** | Routes traffic from the gateway to the correct pod inside the Kubernetes cluster | Phase 2 (k3s setup) → Phase 3 (Helm) |
> | 4 | **Auth Middleware** | FastAPI middleware reads `X-API-Key` header, validates it against the database. Invalid key = `401 Unauthorized` | Phase 3 (this phase) |
> | 5 | **Endpoint Handler** | Business logic runs — compliance scan, report generation, control listing | Phase 3 (this phase) |
> | 6 | **Oracle Autonomous DB** | Reads/writes compliance data, API key records, audit log entries | Phase 2 (Terraform) |
> | 7 | **Response** | JSON response flows back through the same path to the client | — |
>
> **Why layered security matters:** Each layer catches different threats. The API Gateway stops abuse (DDoS, rate limit violations) before your app sees it. The auth middleware stops unauthorized access. The endpoint handler validates business logic. The DB enforces data integrity. No single layer handles everything — defense in depth.

> **Why this progression?** Phase 1 deployed manually (SSH + systemctl). Phase 2 deployed to k3s with raw manifests. Phase 3 starts the same way (Day 2), then upgrades to Helm + ArgoCD (Day 3). Each phase adds a layer of abstraction — but you always build the lower layer first so you understand what the abstraction replaces. An interviewer who asks "what does Helm actually do?" will get a real answer because you deployed without it first.

---

## WHERE AM I? — LOCATION GUIDE

Watch for these location tags throughout the guide. They tell you exactly where to type each command.

| Tag | Where | What It Looks Like |
|-----|-------|-------------------|
| 📍 **OCI Console** | Oracle Cloud web UI | cloud.oracle.com — clicking buttons, navigating menus |
| 📍 **Local Terminal** | Your machine's terminal | WSL2 on your laptop |
| 📍 **Bastion Terminal** | SSH into bastion/Jenkins VM | `ssh opc@<bastion_ip>` — public subnet jump box |
| 📍 **App Node Terminal** | SSH into k3s node via bastion | `ssh -J opc@<bastion_ip> opc@<private_ip>` — private subnet |
| 📍 **Editor** | Your text editor | VS Code, nano, vim — editing files |
| 📍 **Browser** | Web browser | Testing endpoints, Jenkins UI, ArgoCD UI, Swagger docs |

---

## API PILLAR — PHASE 3: API AUTHENTICATION & REQUEST LIFECYCLE

> Phase 1 taught REST fundamentals (HTTP verbs, Pydantic, status codes). Phase 2 introduced webhooks (event-driven API patterns with HMAC signature validation) and OCI API Gateway (managed entry point with rate limiting). Phase 3 completes the API pillar with **authentication** — how APIs verify who is calling them and what they're allowed to do. The full request path diagram above shows all three phases working together: API Gateway (Phase 2) → k3s routing (Phase 2/3) → auth middleware (Phase 3) → endpoint logic. This is the most interview-relevant API topic for federal/enterprise roles.

### API Authentication Methods — ELI5

> **🧠 ELI5 — API Keys:** Imagine a library card. When you walk into the library, you show your card. The librarian checks the number against their system — if it's valid, you can borrow books. An API key works the same way: the client sends a unique string (the key) with every request, and the server checks it against a list of valid keys. If the key is valid, the request proceeds. If not, the server returns `401 Unauthorized`. API keys are the simplest form of API authentication — no login flow, no tokens to refresh. You generate a key, give it to the client, and they include it in every request header.

> **🧠 ELI5 — JWT (JSON Web Tokens):** If API keys are library cards, JWTs are concert wristbands. When you check in at the gate (login), they give you a wristband (token) that contains your name, ticket type, and expiration time — all encoded and signed so nobody can tamper with it. The bouncer at each stage (API endpoint) can read the wristband without calling back to the box office (auth server). JWTs are **self-contained** — the token itself carries the user's identity and permissions. The server doesn't need to look anything up in a database; it just verifies the signature. This is why JWTs are popular for microservices — each service can independently verify the token without a shared database.
>
> *In this lab, we implement API keys (simpler, appropriate for service-to-service auth). JWT is covered conceptually for interview readiness.*

> **🧠 ELI5 — mTLS (Mutual TLS):** Normal HTTPS is one-way trust — your browser verifies the server's certificate ("yes, this really is google.com"), but the server doesn't verify your browser. mTLS adds the reverse: the server also verifies the client's certificate. Both sides prove their identity. Think of it like two diplomats at a border crossing — each shows their passport to the other before either crosses. In federal environments, mTLS is the gold standard for service-to-service communication because it doesn't rely on shared secrets (like API keys) that could be stolen. Each service has its own certificate issued by a trusted Certificate Authority (CA).
>
> *mTLS is covered conceptually here. Full implementation requires a certificate infrastructure (PKI) that's beyond this lab's scope, but understanding the concept is critical for federal interviews.*

> **💼 Interview Insight — API Authentication:** When interviewers ask "how do you secure APIs?", they're testing whether you understand the spectrum of options and when each is appropriate. A strong answer: "It depends on the context. For simple service-to-service calls within a trusted network, API keys work — they're easy to implement and rotate. For user-facing APIs with identity and permissions, JWT tokens are standard because they're self-contained and don't require a session store. For zero-trust federal environments, mTLS provides mutual authentication at the transport layer — both sides prove identity via certificates, and no shared secret can be stolen." A weak answer picks one method and doesn't explain trade-offs.

> **💼 Interview Insight — JWT in Practice:** "JWTs carry claims — user ID, roles, expiration — in a base64-encoded payload signed with a secret or private key. The server validates the signature without hitting a database. The trade-off is revocation: once issued, a JWT is valid until it expires. You can't 'log out' a JWT without maintaining a blacklist, which partially defeats the stateless advantage. Short expiration times (15 minutes) plus refresh tokens are the standard mitigation."

> **💼 Interview Insight — mTLS in Federal Environments:** "In federal systems, mTLS is often required for east-west traffic (service-to-service within the data center). Tools like Istio service mesh automate mTLS between pods in Kubernetes — each pod gets a certificate automatically, and all pod-to-pod traffic is encrypted and mutually authenticated. This is part of a zero-trust architecture where no network path is inherently trusted."

### API Authentication Pattern Comparison

| Aspect | API Keys | JWT | mTLS |
|--------|----------|-----|------|
| **Complexity** | Simple — generate, store, validate | Medium — login flow, token issuance, refresh | Complex — PKI, certificate management |
| **Where stored** | Header (`X-API-Key`) or query param | Header (`Authorization: Bearer <token>`) | TLS handshake (client certificate) |
| **Server-side** | Database lookup per request | Signature verification (no DB needed) | Certificate chain verification |
| **Revocation** | Delete key from database — instant | Blacklist or wait for expiry | Revoke certificate via CRL/OCSP |
| **Best for** | Service-to-service, internal APIs | User-facing APIs, microservices | Zero-trust, federal, high-security |
| **Federal use** | Internal tooling, CI/CD tokens | User auth, SSO integration | Service mesh, east-west traffic |
| **This lab** | Implemented (POST /auth/validate) | Conceptual (Interview Insight) | Conceptual (Interview Insight) |

---

## PHASE 22: ENVIRONMENT & SECURE FOUNDATIONS (6–8 hrs)

> Day 1 of Phase 3 rebuilds your OCI environment from scratch using Terraform modules — a major step up from the flat `.tf` files used in Phases 1 and 2. You'll learn three new concepts today: Terraform modules (organizing infrastructure into reusable, composable units), OCI Vault (storing secrets outside your code), and Ansible Vault integration (pulling those secrets securely into playbooks). By the end of the day, you'll have a hardened 2-node k3s cluster running the FedCompliance app with zero secrets stored in plaintext.
>
> 📍 **Work happens across: Local Terminal, OCI Console, Bastion Terminal, App Node Terminal, Editor.**
>
> 🛠️ **Build approach:** Terraform modules built by hand (section-by-section, full ELI5). FedCompliance FastAPI app built by hand (section-by-section). SQL schema is copy-paste with inline comments. Ansible playbooks built by hand (abbreviated — returning concept). OCI Vault configured via Console + CLI.

---

### Step 22.1 — Create Project Directory Structure
📍 **Local Terminal**

```bash
mkdir -p ~/oci-federal-lab-phase3/terraform/modules/network
mkdir -p ~/oci-federal-lab-phase3/terraform/modules/compute
mkdir -p ~/oci-federal-lab-phase3/terraform/modules/database
mkdir -p ~/oci-federal-lab-phase3/terraform/environments/lab
mkdir -p ~/oci-federal-lab-phase3/ansible/roles/hardening
mkdir -p ~/oci-federal-lab-phase3/ansible/roles/deploy
mkdir -p ~/oci-federal-lab-phase3/ansible/playbooks
mkdir -p ~/oci-federal-lab-phase3/app/fedcompliance
mkdir -p ~/oci-federal-lab-phase3/app/scripts
mkdir -p ~/oci-federal-lab-phase3/k8s
mkdir -p ~/oci-federal-lab-phase3/docs
cd ~/oci-federal-lab-phase3
git init
```

Create `.gitignore` immediately — before any sensitive files are created:

📍 **Editor** — create `~/oci-federal-lab-phase3/.gitignore`

```
# Terraform state and credentials — NEVER commit these
*.tfstate
*.tfstate.backup
*.tfstate.lock.info
.terraform/
terraform.tfvars
*.tfvars

# Ansible Vault password file
.vault_pass
.vault_password

# OCI credentials
*.pem
oci_api_key.pem
oci_config

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# App secrets
.env
secrets/
```

**Verify:**

```bash
ls ~/oci-federal-lab-phase3/terraform/modules/
# Expected: compute  database  network
```

---

### Step 22.2 — Understand Terraform Modules (New Concept)
📍 **Editor** (read this before writing any code)

> **🧠 ELI5 — Terraform Modules:** In Phases 1 and 2, all your Terraform resources lived in flat files in one directory — `network.tf`, `compute.tf`, `database.tf` all side by side. This works for small projects, but imagine handing your code to a teammate who needs to build a second environment. They'd have to copy every file, change variable names, and hope nothing breaks. A Terraform **module** is like a reusable recipe card. You write the recipe once (in a `modules/network/` folder), then "call" it from your environment config: "use the network recipe, but plug in these specific values." The module handles the details; the caller just provides ingredients. Now you can create dev, staging, and prod environments by calling the same modules with different values — no copy-paste, no drift.

> **💼 Interview Insight — Terraform Modules:** "Modules are the primary way teams enforce consistency at scale. In federal consulting, you would likely consume a pre-approved 'network module' that already has DISA STIG-compliant security group rules baked in. Your job is to call it with the right inputs, not reinvent the network every time. Flat files copied between projects lead to configuration drift where dev and prod gradually diverge in ways nobody notices until a security audit."

**Module anatomy — every module has exactly three files:**

```
modules/network/
├── main.tf        ← The actual resources (what gets built)
├── variables.tf   ← The inputs (what the caller must provide)
└── outputs.tf     ← The return values (what the caller can use)
```

**How the caller references a module (`environments/lab/main.tf`):**

```hcl
module "network" {
  source = "../../modules/network"   # path to the module folder

  # These match variable names declared in modules/network/variables.tf
  compartment_ocid = var.compartment_ocid
  vcn_cidr         = "10.0.0.0/16"
  project_name     = "fedcompliance"
}

# To USE a module output in another resource:
# module.network.public_subnet_id   ← module_name.output_name
```

> **Why three files?** `variables.tf` defines the interface (what callers must supply). `main.tf` is the implementation (the actual OCI resources). `outputs.tf` is what the module returns so other modules can reference its resources. Separating these makes the module self-documenting — you can read `variables.tf` to know exactly what a module needs without reading all resource code.

---

### Step 22.3 — Build Terraform Root Configuration
📍 **Editor** (build by hand)

The root configuration lives in `terraform/environments/lab/`. This is the "caller" that wires together all three modules.

**Build `terraform/environments/lab/provider.tf` section by section:**

**Section 1:** Terraform version and provider pin

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/environments/lab/provider.tf`

```hcl
# Provider configuration for fedcompliance lab environment
# Returning concept from Phases 1-2 — credentials via variables, never hardcoded

terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.5.0"
}

provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}
```

**Build `terraform/environments/lab/variables.tf`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/environments/lab/variables.tf`

```hcl
# Root variables — values you supply via terraform.tfvars (never committed to git)

# --- OCI Authentication ---
variable "tenancy_ocid" {
  description = "OCI tenancy OCID"
  type        = string
}

variable "user_ocid" {
  description = "OCI user OCID"
  type        = string
}

variable "fingerprint" {
  description = "API key fingerprint"
  type        = string
}

variable "private_key_path" {
  description = "Path to OCI API private key"
  type        = string
}

variable "region" {
  description = "OCI region (e.g., us-ashburn-1)"
  type        = string
  default     = "us-ashburn-1"
}

variable "compartment_ocid" {
  description = "Compartment OCID for all Phase 3 resources"
  type        = string
}

variable "availability_domain" {
  description = "Availability domain name (get from OCI Console > Governance > Limits)"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key content for VM access"
  type        = string
}

variable "image_ocid" {
  description = "Oracle Linux 9 ARM image OCID for your region"
  type        = string
}

variable "db_admin_password" {
  description = "Oracle Autonomous DB admin password (min 12 chars, mixed case + number + special)"
  type        = string
  sensitive   = true
}

variable "db_wallet_password" {
  description = "Oracle Autonomous DB wallet password"
  type        = string
  sensitive   = true
}
```

**Build `terraform/environments/lab/main.tf` — the module wiring file:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/environments/lab/main.tf`

**Section 1:** Network module call

```hcl
# Phase 3 — FedCompliance Lab Environment
# Uses Terraform modules to compose infrastructure from reusable components.
# Pattern: each module is called with inputs; outputs flow between modules.

# --- Network Module ---
# Creates: VCN, public subnet, private subnet, IGW, NAT GW, Service GW, route tables, security lists
module "network" {
  source = "../../modules/network"

  compartment_ocid = var.compartment_ocid
  vcn_cidr         = "10.0.0.0/16"
  public_cidr      = "10.0.1.0/24"
  private_cidr     = "10.0.2.0/24"
  project_name     = "fedcompliance"
  region           = var.region
}
```

**Section 2:** Compute module call — note the `depends_on`

```hcl
# --- Compute Module ---
# Creates: bastion VM (public subnet), k3s-node-1 (private), k3s-node-2 (private)
# depends_on ensures the network fully exists before any VM creation is attempted
module "compute" {
  source = "../../modules/compute"

  depends_on = [module.network]

  compartment_ocid    = var.compartment_ocid
  availability_domain = var.availability_domain
  ssh_public_key      = var.ssh_public_key
  image_ocid          = var.image_ocid
  project_name        = "fedcompliance"

  # Wire network outputs directly into compute inputs
  public_subnet_id  = module.network.public_subnet_id
  private_subnet_id = module.network.private_subnet_id
}
```

**Section 3:** Database module call

```hcl
# --- Database Module ---
# Creates: Oracle Autonomous DB Transaction Processing (Always Free, 20 GB)
module "database" {
  source = "../../modules/database"

  depends_on = [module.network]

  compartment_ocid   = var.compartment_ocid
  project_name       = "fedcompliance"
  db_admin_password  = var.db_admin_password
  db_wallet_password = var.db_wallet_password
}
```

> **Why `depends_on` on the compute module?** Terraform normally infers dependencies automatically when you reference one module's output in another module's argument — `module.network.public_subnet_id` is such a reference. The explicit `depends_on` is belt-and-suspenders: it makes the ordering unmistakably clear to any reader and prevents edge-case parallel execution bugs where Terraform tries to create a VM before the subnet is fully provisioned. In federal environments where Terraform applies are often audited, explicit intent is preferred over implicit inference.

**Build `terraform/environments/lab/outputs.tf`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/environments/lab/outputs.tf`

```hcl
# Root outputs — values you will use in Ansible inventory and app configuration

output "bastion_public_ip" {
  description = "Public IP of bastion/Jenkins VM — SSH entry point"
  value       = module.compute.bastion_public_ip
}

output "k3s_node1_private_ip" {
  description = "Private IP of k3s server node (node-1)"
  value       = module.compute.k3s_node1_private_ip
}

output "k3s_node2_private_ip" {
  description = "Private IP of k3s agent node (node-2)"
  value       = module.compute.k3s_node2_private_ip
}

output "db_connection_string" {
  description = "Oracle Autonomous DB connection string (low service)"
  value       = module.database.db_connection_string
  sensitive   = true   # won't print in terraform plan output
}

output "vcn_id" {
  description = "VCN OCID — needed when writing OCI Vault IAM policies"
  value       = module.network.vcn_id
}
```

**Verify root environment files:**

```bash
ls ~/oci-federal-lab-phase3/terraform/environments/lab/
# Expected: main.tf  outputs.tf  provider.tf  variables.tf
```

---

### Step 22.4 — Build the Network Module
📍 **Editor** (build by hand — new module pattern)

> **🧠 ELI5 — Module variables.tf vs root variables.tf:** The root `variables.tf` defines what *you* (the human running Terraform) must supply — your tenancy OCID, SSH key, etc. A module's `variables.tf` defines what the *module caller* must supply — in this case `environments/lab/main.tf` is the caller. Think of it as a function's parameter list. If `main.tf` forgets to pass a required variable, Terraform errors immediately with "variable X has no value." This contract-based approach is what makes modules safe to share across teams.

**Build `terraform/modules/network/variables.tf`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/modules/network/variables.tf`

```hcl
# Network module inputs
# These are the parameters that environments/lab/main.tf must provide when calling this module.

variable "compartment_ocid" {
  description = "OCI compartment OCID where network resources will be created"
  type        = string
}

variable "project_name" {
  description = "Project name — prefixes all resource display names (e.g., 'fedcompliance')"
  type        = string
}

variable "region" {
  description = "OCI region — used for Service Gateway lookup"
  type        = string
}

variable "vcn_cidr" {
  description = "CIDR block for the VCN"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_cidr" {
  description = "CIDR block for the public subnet (bastion lives here)"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_cidr" {
  description = "CIDR block for the private subnet (app nodes live here)"
  type        = string
  default     = "10.0.2.0/24"
}
```

**Build `terraform/modules/network/main.tf` section by section:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/modules/network/main.tf`

**Section 1:** VCN and data source

```hcl
# Network Module — main.tf
# Creates the full network topology: VCN, subnets, gateways, route tables, security lists.
# All display names are prefixed with var.project_name for easy identification in the Console.

# Data source: look up the OCI Services Network service CIDR for this region
# Used by the Service Gateway so private VMs can reach Vault/OCIR without internet
data "oci_core_services" "all_services" {
  filter {
    name   = "name"
    values = ["All .* Services In Oracle Services Network"]
    regex  = true
  }
}

# VCN — the private network container for all resources
resource "oci_core_vcn" "main" {
  compartment_id = var.compartment_ocid
  display_name   = "${var.project_name}-vcn"
  cidr_blocks    = [var.vcn_cidr]
  dns_label      = var.project_name   # enables internal DNS: host.fedcompliance.oraclevcn.com

  freeform_tags = {
    "Project"     = var.project_name
    "Environment" = "lab"
    "Phase"       = "3"
    "ManagedBy"   = "terraform-modules"
  }
}
```

**Section 2:** Gateways

```hcl
# Internet Gateway — public subnet VMs can be reached from, and reach, the internet
resource "oci_core_internet_gateway" "igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-igw"
  enabled        = true
}

# NAT Gateway — private subnet VMs can make outbound internet calls; no inbound allowed
resource "oci_core_nat_gateway" "natgw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-natgw"
}

# Service Gateway — private subnet reaches OCI-managed services (Vault, OCIR, Object Storage)
# Traffic stays on Oracle's backbone network; never traverses the public internet
resource "oci_core_service_gateway" "svcgw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-svcgw"

  services {
    service_id = data.oci_core_services.all_services.services[0].id
  }
}
```

> **Why a Service Gateway alongside a NAT Gateway?** The NAT Gateway handles general internet traffic (dnf updates, git clones). The Service Gateway creates a direct path to OCI-managed services that stays entirely within Oracle's network. In federal environments, this separation is often required by policy: internal service communication (your VM talking to OCI Vault) must not route through the public internet even if NAT is available. Security scanners can tell the difference.

**Section 3:** Route tables

```hcl
# Public route table: all traffic goes through the Internet Gateway
resource "oci_core_route_table" "public_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.igw.id
  }
}

# Private route table: outbound internet through NAT; OCI services through Service GW
resource "oci_core_route_table" "private_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-private-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_nat_gateway.natgw.id
  }

  route_rules {
    destination_type  = "SERVICE_CIDR_BLOCK"
    destination       = data.oci_core_services.all_services.services[0].cidr_block
    network_entity_id = oci_core_service_gateway.svcgw.id
  }
}
```

**Section 4:** Security lists

```hcl
# Public security list — bastion/Jenkins VM access
resource "oci_core_security_list" "public_sl" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-public-sl"

  ingress_security_rules {
    protocol    = "6"   # TCP
    source      = "0.0.0.0/0"
    description = "SSH to bastion from internet"
    tcp_options { min = 22; max = 22 }
  }

  ingress_security_rules {
    protocol    = "6"
    source      = "0.0.0.0/0"
    description = "Jenkins UI (Day 2)"
    tcp_options { min = 8080; max = 8080 }
  }

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
    description = "Allow all outbound"
  }
}

# Private security list — k3s nodes
resource "oci_core_security_list" "private_sl" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-private-sl"

  ingress_security_rules {
    protocol    = "6"
    source      = var.public_cidr
    description = "SSH from bastion"
    tcp_options { min = 22; max = 22 }
  }

  ingress_security_rules {
    protocol    = "6"
    source      = var.private_cidr
    description = "k3s API server (cluster internal)"
    tcp_options { min = 6443; max = 6443 }
  }

  ingress_security_rules {
    protocol    = "17"   # UDP — Flannel VXLAN overlay network
    source      = var.private_cidr
    description = "k3s Flannel VXLAN overlay"
    udp_options { min = 8472; max = 8472 }
  }

  ingress_security_rules {
    protocol    = "6"
    source      = var.private_cidr
    description = "FedCompliance app port"
    tcp_options { min = 8000; max = 8000 }
  }

  ingress_security_rules {
    protocol    = "1"   # ICMP — for troubleshooting connectivity within private subnet
    source      = var.private_cidr
    description = "ICMP within private subnet"
  }

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
    description = "Allow all outbound"
  }
}
```

**Section 5:** Subnets

```hcl
# Public subnet — bastion and Jenkins VM
resource "oci_core_subnet" "public" {
  compartment_id    = var.compartment_ocid
  vcn_id            = oci_core_vcn.main.id
  display_name      = "${var.project_name}-public-subnet"
  cidr_block        = var.public_cidr
  dns_label         = "public"
  route_table_id    = oci_core_route_table.public_rt.id
  security_list_ids = [oci_core_security_list.public_sl.id]

  # false = VMs in this subnet CAN receive public IPs
  prohibit_public_ip_on_vnic = false
}

# Private subnet — k3s nodes
resource "oci_core_subnet" "private" {
  compartment_id    = var.compartment_ocid
  vcn_id            = oci_core_vcn.main.id
  display_name      = "${var.project_name}-private-subnet"
  cidr_block        = var.private_cidr
  dns_label         = "private"
  route_table_id    = oci_core_route_table.private_rt.id
  security_list_ids = [oci_core_security_list.private_sl.id]

  # true = VMs in this subnet CANNOT receive public IPs — enforced at the subnet level
  prohibit_public_ip_on_vnic = true
}
```

**Build `terraform/modules/network/outputs.tf`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/modules/network/outputs.tf`

```hcl
# Network module outputs
# Referenced in environments/lab/main.tf as: module.network.<output_name>

output "vcn_id" {
  description = "VCN OCID — used when writing OCI Vault IAM policies"
  value       = oci_core_vcn.main.id
}

output "public_subnet_id" {
  description = "Public subnet OCID — passed to compute module for bastion VM"
  value       = oci_core_subnet.public.id
}

output "private_subnet_id" {
  description = "Private subnet OCID — passed to compute module for k3s nodes"
  value       = oci_core_subnet.private.id
}

output "vcn_cidr" {
  description = "VCN CIDR block"
  value       = var.vcn_cidr
}
```

**Verify network module:**

```bash
ls ~/oci-federal-lab-phase3/terraform/modules/network/
# Expected: main.tf  outputs.tf  variables.tf
```

---

### Step 22.5 — Build the Compute Module
📍 **Editor** (build by hand)

The compute module creates three VMs: one bastion (public subnet) and two k3s nodes (private subnet). Returning concept from Phase 2 — same VM shapes, abbreviated ELI5.

**Build `terraform/modules/compute/variables.tf`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/modules/compute/variables.tf`

```hcl
# Compute module inputs

variable "compartment_ocid" {
  description = "OCI compartment OCID"
  type        = string
}

variable "availability_domain" {
  description = "Availability domain for VM placement"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key content for opc user"
  type        = string
}

variable "image_ocid" {
  description = "Oracle Linux 9 ARM image OCID"
  type        = string
}

variable "project_name" {
  description = "Project name — prefixes display names"
  type        = string
}

variable "public_subnet_id" {
  description = "Public subnet OCID — from network module output"
  type        = string
}

variable "private_subnet_id" {
  description = "Private subnet OCID — from network module output"
  type        = string
}
```

**Build `terraform/modules/compute/main.tf` section by section:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/modules/compute/main.tf`

**Section 1:** Bastion VM (public subnet, Jenkins will install here on Day 2)

```hcl
# Compute Module — main.tf
# Creates three VMs: bastion (public), k3s-node-1 (private), k3s-node-2 (private)
# All use ARM shapes (VM.Standard.A1.Flex) — Always Free tier

# Bastion / Jenkins VM — lives in public subnet, reachable from internet via SSH
resource "oci_core_instance" "bastion" {
  compartment_id      = var.compartment_ocid
  availability_domain = var.availability_domain
  display_name        = "${var.project_name}-bastion"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 1
    memory_in_gbs = 6
  }

  source_details {
    source_type = "image"
    source_id   = var.image_ocid
  }

  create_vnic_details {
    subnet_id        = var.public_subnet_id
    display_name     = "${var.project_name}-bastion-vnic"
    assign_public_ip = true   # bastion needs a public IP — this is the SSH entry point
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data = base64encode(<<-USERDATA
      #!/bin/bash
      # Install OCI CLI on first boot — needed for Vault secret retrieval
      dnf install -y python3-pip
      python3 -m pip install oci-cli
      USERDATA
    )
  }

  freeform_tags = {
    "Project"     = var.project_name
    "Role"        = "bastion"
    "Phase"       = "3"
    "ManagedBy"   = "terraform-modules"
  }
}
```

**Section 2:** k3s server node (private subnet)

```hcl
# k3s server node — runs the k3s control plane + kubelet
# Lives in private subnet — reachable only via bastion SSH jump
resource "oci_core_instance" "k3s_node1" {
  compartment_id      = var.compartment_ocid
  availability_domain = var.availability_domain
  display_name        = "${var.project_name}-k3s-node-1"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 1
    memory_in_gbs = 6
  }

  source_details {
    source_type = "image"
    source_id   = var.image_ocid
  }

  create_vnic_details {
    subnet_id        = var.private_subnet_id
    display_name     = "${var.project_name}-k3s-node1-vnic"
    assign_public_ip = false   # private subnet — no public IP
    hostname_label   = "k3s-node1"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
  }

  freeform_tags = {
    "Project"     = var.project_name
    "Role"        = "k3s-server"
    "Phase"       = "3"
    "ManagedBy"   = "terraform-modules"
  }
}
```

**Section 3:** k3s agent node (private subnet)

```hcl
# k3s agent node — runs workloads only; no control plane
resource "oci_core_instance" "k3s_node2" {
  compartment_id      = var.compartment_ocid
  availability_domain = var.availability_domain
  display_name        = "${var.project_name}-k3s-node-2"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 1
    memory_in_gbs = 6
  }

  source_details {
    source_type = "image"
    source_id   = var.image_ocid
  }

  create_vnic_details {
    subnet_id        = var.private_subnet_id
    display_name     = "${var.project_name}-k3s-node2-vnic"
    assign_public_ip = false
    hostname_label   = "k3s-node2"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
  }

  freeform_tags = {
    "Project"     = var.project_name
    "Role"        = "k3s-agent"
    "Phase"       = "3"
    "ManagedBy"   = "terraform-modules"
  }
}
```

> **Cost check:** Three `VM.Standard.A1.Flex` instances at 1 OCPU / 6 GB each = 3 OCPU / 18 GB total. Always Free allows 4 OCPU + 24 GB across all ARM instances. You're within limits. Verify at: https://www.oracle.com/cloud/free/#always-free

**Build `terraform/modules/compute/outputs.tf`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/modules/compute/outputs.tf`

```hcl
# Compute module outputs
# Referenced in environments/lab/outputs.tf and ansible inventory

output "bastion_public_ip" {
  description = "Bastion public IP — your SSH entry point"
  value       = oci_core_instance.bastion.public_ip
}

output "k3s_node1_private_ip" {
  description = "k3s server node private IP — SSH via bastion jump"
  value       = oci_core_instance.k3s_node1.private_ip
}

output "k3s_node2_private_ip" {
  description = "k3s agent node private IP — SSH via bastion jump"
  value       = oci_core_instance.k3s_node2.private_ip
}

output "bastion_instance_id" {
  description = "Bastion instance OCID — needed for IAM policy granting Vault access"
  value       = oci_core_instance.bastion.id
}

output "k3s_node1_instance_id" {
  description = "k3s node-1 instance OCID — needed for IAM policy granting Vault access"
  value       = oci_core_instance.k3s_node1.id
}
```

---

### Step 22.6 — Build the Database Module
📍 **Editor** (build by hand)

> Returning concept from Phases 1 and 2 — Oracle Autonomous DB setup. Abbreviated here: same resource type, new variable names.

**Build `terraform/modules/database/variables.tf`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/modules/database/variables.tf`

```hcl
# Database module inputs

variable "compartment_ocid" {
  description = "OCI compartment OCID"
  type        = string
}

variable "project_name" {
  description = "Project name — prefixes display names"
  type        = string
}

variable "db_admin_password" {
  description = "Admin password for Autonomous DB (min 12 chars, mixed case + number + special)"
  type        = string
  sensitive   = true
}

variable "db_wallet_password" {
  description = "Password for the wallet zip file"
  type        = string
  sensitive   = true
}
```

**Build `terraform/modules/database/main.tf`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/modules/database/main.tf`

```hcl
# Database Module — main.tf
# Creates Oracle Autonomous Database (Transaction Processing, Always Free)

resource "oci_database_autonomous_database" "main" {
  compartment_id           = var.compartment_ocid
  display_name             = "${var.project_name}-adb"
  db_name                  = "FEDCOMP"   # max 14 chars, alphanumeric only
  admin_password           = var.db_admin_password
  db_workload              = "OLTP"      # Transaction Processing workload type
  cpu_core_count           = 1
  data_storage_size_in_tbs = 0           # 0 = use GB instead of TB
  data_storage_size_in_gbs = 20          # Always Free limit is 20 GB
  is_free_tier             = true        # marks this as Always Free — prevents accidental paid upgrades
  is_auto_scaling_enabled  = false       # Always Free cannot use auto-scaling

  freeform_tags = {
    "Project"     = var.project_name
    "Environment" = "lab"
    "Phase"       = "3"
    "ManagedBy"   = "terraform-modules"
  }
}
```

> **Cost check:** `is_free_tier = true` locks this database to the Always Free tier. OCI will refuse any configuration change that would move it to paid. Always Free Autonomous DB = $0.00/month. Verify at: https://www.oracle.com/cloud/free/#always-free

**Build `terraform/modules/database/outputs.tf`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/modules/database/outputs.tf`

```hcl
# Database module outputs

output "db_id" {
  description = "Autonomous DB OCID"
  value       = oci_database_autonomous_database.main.id
}

output "db_connection_string" {
  description = "DB connection string for low-priority service (use for app connections)"
  value       = oci_database_autonomous_database.main.connection_strings[0].low
  sensitive   = true
}

output "db_name" {
  description = "DB name (used in wallet configuration)"
  value       = oci_database_autonomous_database.main.db_name
}
```

**Verify all three modules are complete:**

```bash
ls ~/oci-federal-lab-phase3/terraform/modules/network/
# Expected: main.tf  outputs.tf  variables.tf

ls ~/oci-federal-lab-phase3/terraform/modules/compute/
# Expected: main.tf  outputs.tf  variables.tf

ls ~/oci-federal-lab-phase3/terraform/modules/database/
# Expected: main.tf  outputs.tf  variables.tf
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `ls ~/path/` | Verify module files exist after creation |
| `terraform init` | (next step) Downloads providers and resolves module paths |
| `terraform plan` | (next step) Shows what will be created without making changes |

</em></sub>

---

### Step 22.7 — Create terraform.tfvars and Deploy Infrastructure
📍 **Editor** then **Local Terminal**

Create `terraform/environments/lab/terraform.tfvars` — this file is in `.gitignore` and must never be committed.

📍 **Editor** — create `~/oci-federal-lab-phase3/terraform/environments/lab/terraform.tfvars`

```hcl
# terraform.tfvars — YOUR ACTUAL VALUES GO HERE
# This file is gitignored. Never commit it.

tenancy_ocid        = "ocid1.tenancy.oc1..YOUR_TENANCY_OCID"
user_ocid           = "ocid1.user.oc1..YOUR_USER_OCID"
fingerprint         = "xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx"
private_key_path    = "~/.oci/oci_api_key.pem"
region              = "us-ashburn-1"
compartment_ocid    = "ocid1.compartment.oc1..YOUR_COMPARTMENT_OCID"
availability_domain = "YOUR-AD-NAME"   # e.g., "XgvI:US-ASHBURN-AD-1"
ssh_public_key      = "ssh-rsa AAAA... your-key-here"
image_ocid          = "ocid1.image.oc1.iad.YOUR_OL9_ARM_IMAGE_OCID"
db_admin_password   = "YourStrongP@ssw0rd1!"
db_wallet_password  = "WalletP@ssw0rd1!"
```

> **Finding your values:**
> - **tenancy_ocid / user_ocid / fingerprint:** OCI Console → top-right profile icon → "My profile" → "Tokens and keys" tab → "API keys" (older tenancies: "User Settings" → scroll to "API Keys")
> - **availability_domain:** OCI Console → Governance & Administration → Limits, Quotas and Usage → filter "Availability Domain"
> - **image_ocid:** OCI Console → Compute → Images → Platform Images → filter "Oracle Linux 9" + "aarch64" → copy OCID for your region
> - **compartment_ocid:** OCI Console → Identity & Security → Compartments → click your compartment → copy OCID

**Initialize and apply:**

📍 **Local Terminal**

```bash
cd ~/oci-federal-lab-phase3/terraform/environments/lab

# Initialize — downloads the OCI provider and resolves module source paths
terraform init

# Plan — shows exactly what will be created (4 network resources, 3 VMs, 1 DB)
terraform plan

# Apply — creates all resources; type 'yes' when prompted
terraform apply
```

Terraform will output your IPs when complete. Save them:

```bash
# After apply completes, capture outputs to a file for use in Ansible
terraform output -json > ~/oci-federal-lab-phase3/docs/tf_outputs.json

# Display the IPs you need
terraform output bastion_public_ip
terraform output k3s_node1_private_ip
terraform output k3s_node2_private_ip
```

**Verify SSH access:**

```bash
# Test bastion access
ssh -i ~/.ssh/id_rsa opc@$(terraform output -raw bastion_public_ip)
# Expected: Oracle Linux 9 welcome banner, opc@fedcompliance-bastion prompt

# Test k3s node access via bastion jump (from local terminal)
BASTION_IP=$(terraform output -raw bastion_public_ip)
NODE1_IP=$(terraform output -raw k3s_node1_private_ip)
ssh -J opc@${BASTION_IP} opc@${NODE1_IP}
# Expected: opc@fedcompliance-k3s-node-1 prompt
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `terraform init` | — | Downloads provider plugins; resolves module `source` paths |
| `terraform plan` | — | Dry run — shows what will be created/changed/destroyed |
| `terraform apply` | — | Creates all resources; prompts for confirmation |
| `terraform output` | `-json` | Prints all outputs as JSON; `-raw` prints a single value without quotes |
| `ssh` | `-J user@host` | Jump proxy — SSH through bastion to reach private VMs |

</em></sub>

---

### Step 22.8 — Run Ansible Hardening
📍 **Local Terminal** → **Bastion Terminal**

> Returning concept from Phases 1 and 2 — Ansible hardening. Abbreviated: same playbook structure, new inventory IPs. Full ELI5 skipped.

**Build the Ansible inventory:**

📍 **Editor** — create `~/oci-federal-lab-phase3/ansible/inventory.ini`

```ini
# Ansible inventory for Phase 3
# IPs come from terraform output — update with your actual values

[bastion]
fedcompliance-bastion ansible_host=BASTION_PUBLIC_IP ansible_user=opc ansible_ssh_private_key_file=~/.ssh/id_rsa

[k3s_servers]
k3s-node-1 ansible_host=K3S_NODE1_PRIVATE_IP ansible_user=opc ansible_ssh_private_key_file=~/.ssh/id_rsa ansible_ssh_common_args='-J opc@BASTION_PUBLIC_IP'

[k3s_agents]
k3s-node-2 ansible_host=K3S_NODE2_PRIVATE_IP ansible_user=opc ansible_ssh_private_key_file=~/.ssh/id_rsa ansible_ssh_common_args='-J opc@BASTION_PUBLIC_IP'

[k3s_cluster:children]
k3s_servers
k3s_agents

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

> Replace `BASTION_PUBLIC_IP`, `K3S_NODE1_PRIVATE_IP`, `K3S_NODE2_PRIVATE_IP` with the values from `terraform output`.

**Build `ansible/playbooks/harden.yml`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/ansible/playbooks/harden.yml`

```yaml
---
# Hardening playbook — runs on all nodes
# Returning concept from Phase 1. Abbreviated — same tasks, new project paths.

- name: Harden all OCI nodes
  hosts: all
  become: true

  tasks:
    - name: Install security tools
      dnf:
        name:
          - firewalld
          - fail2ban
          - auditd
          - python3-pip
        state: present

    - name: Enable and start firewalld
      systemd:
        name: firewalld
        enabled: true
        state: started

    - name: Allow SSH through firewall
      firewalld:
        service: ssh
        permanent: true
        state: enabled
        immediate: true

    - name: Allow app port on k3s nodes
      firewalld:
        port: 8000/tcp
        permanent: true
        state: enabled
        immediate: true
      when: inventory_hostname in groups['k3s_cluster']

    - name: Allow k3s API port on server node
      firewalld:
        port: 6443/tcp
        permanent: true
        state: enabled
        immediate: true
      when: inventory_hostname in groups['k3s_servers']

    - name: Disable root SSH login
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PermitRootLogin'
        line: 'PermitRootLogin no'
        backup: true
      notify: Restart sshd

    - name: Set SSH idle timeout (10 minutes)
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^ClientAliveInterval'
        line: 'ClientAliveInterval 600'
      notify: Restart sshd

    - name: Enable and start auditd
      systemd:
        name: auditd
        enabled: true
        state: started

    - name: Install OCI CLI (needed for Vault access)
      pip:
        name: oci-cli
        executable: /usr/bin/python3 -m pip

    - name: Verify OCI CLI importable
      command: python3 -c "import oci; print('oci OK')"
      changed_when: false

  handlers:
    - name: Restart sshd
      systemd:
        name: sshd
        state: restarted
```

**Run the hardening playbook:**

📍 **Local Terminal**

```bash
cd ~/oci-federal-lab-phase3

# Test connectivity first
ansible all -i ansible/inventory.ini -m ping

# Run hardening
ansible-playbook -i ansible/inventory.ini ansible/playbooks/harden.yml

# Verify SSH lockdown on node-1
ssh -J opc@<BASTION_PUBLIC_IP> opc@<NODE1_PRIVATE_IP> "sudo sshd -T | grep permitrootlogin"
# Expected: permitrootlogin no
```

---

### Step 22.9 — Set Up OCI Vault for Secrets Management (New Concept)
📍 **OCI Console** then **Bastion Terminal**

> **🧠 ELI5 — OCI Vault:** Right now, your database password lives in `terraform.tfvars` on your laptop. If a teammate clones the repo and you accidentally committed that file — or if your laptop is stolen — the password is exposed. OCI Vault is a dedicated secrets locker. You store the password in Vault (encrypted, access-controlled), and instead of passing the password in a config file, your application asks Vault "give me the DB password" at runtime. Vault checks whether that application (identified by its OCI Instance Principal — like a VM's built-in badge) has permission to read that secret. If yes, the secret is returned. If no, the request is denied and logged. The password never sits in a file.

> **💼 Interview Insight — Secrets Management:** "The progression from hardcoded → environment variables → secrets manager is one of the most common security improvement conversations in federal cloud work. Hardcoded is always wrong. Environment variables are better but still expose secrets in process listings, container inspect output, and CI/CD logs. A dedicated secrets manager like OCI Vault, AWS Secrets Manager, or HashiCorp Vault adds access control (who can read which secret), audit logging (who read it and when), automatic rotation, and encryption at rest. In CMMC Level 2+, secret management is a control requirement — you need to demonstrate that credentials are protected and access is logged."

**Step 22.9a — Create the Vault:**

📍 **OCI Console** → Identity & Security → Vault → Create Vault

```
Name:          fedcompliance-vault
Compartment:   [your compartment]
Vault type:    Virtual Private Vault (DO NOT select "Default Shared" — it has lower security guarantees)
```

> **Cost check:** Virtual Private Vault = $0.00 for the first vault under Always Free. Keys and secret versions have minimal costs only beyond free tier limits. For this lab (< 20 secrets, < 1000 API calls/month) = $0.00. Verify at: https://www.oracle.com/security/cloud-security/key-management/pricing/

Wait for vault status to show "Active" before proceeding (~2 minutes).

**Step 22.9b — Create an Encryption Key:**

📍 **OCI Console** → Identity & Security → Vault → [your vault] → Keys → Create Key

```
Protection mode:   Software (HSM costs extra; Software is sufficient for lab)
Name:              fedcompliance-master-key
Key shape:         AES, 256 bits
```

**Step 22.9c — Store Secrets in Vault:**

📍 **OCI Console** → Identity & Security → Vault → [your vault] → Secrets → Create Secret

Create each secret one at a time:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `fedcompliance-db-password` | Your ADB admin password | Autonomous DB admin credential |
| `fedcompliance-db-wallet-password` | Your wallet password | ADB wallet decryption |
| `fedcompliance-api-key` | `fc_live_phase3_lab_key_001` | FedCompliance API key (Phase 3 auth) |

For each secret:
1. Click "Create Secret"
2. Name: (from table above)
3. Encryption Key: select `fedcompliance-master-key`
4. Secret Type: Plain-Text
5. Secret Contents: (your actual value)
6. Click "Create Secret"

Note the OCID of each secret after creation — you will reference them in Ansible.

**Step 22.9d — Create IAM Policy Granting VM Access to Vault:**

> **🧠 ELI5 — Instance Principals:** When a VM needs to call OCI APIs (like reading a Vault secret), it needs credentials. But you can not store OCI credentials on the VM — that's the whole problem you're solving. OCI solves this with **Instance Principals**: every OCI VM automatically has a cryptographic identity issued by Oracle. Think of it as a company badge that gets assigned when the VM is created. You write an IAM policy saying "any VM in this dynamic group can read secrets in this vault" — the VM proves its identity automatically via the instance principal, no password needed.

📍 **OCI Console** → Identity & Security → Dynamic Groups → Create Dynamic Group

```
Name:        fedcompliance-compute-dg
Description: k3s nodes and bastion that need Vault access

Matching Rule:
  Any {instance.compartment.id = 'YOUR_COMPARTMENT_OCID'}
```

> This rule matches all VMs in your compartment. In production you would scope this to specific instance OCIDs for least privilege: `instance.id = 'ocid1.instance...'`

📍 **OCI Console** → Identity & Security → Policies → Create Policy

```
Name:        fedcompliance-vault-read-policy
Description: Allow Phase 3 compute instances to read Vault secrets

Statements:
  Allow dynamic-group fedcompliance-compute-dg to read secret-family in compartment YOUR_COMPARTMENT_NAME
  Allow dynamic-group fedcompliance-compute-dg to use vaults in compartment YOUR_COMPARTMENT_NAME
  Allow dynamic-group fedcompliance-compute-dg to use keys in compartment YOUR_COMPARTMENT_NAME
```

**Verify OCI CLI can read a secret from the bastion:**

📍 **Bastion Terminal**

```bash
# SSH into bastion
ssh -i ~/.ssh/<YOUR_BASTION_KEY> opc@<BASTION_PUBLIC_IP>

# Test that the instance principal can authenticate to OCI CLI
oci iam region list --auth instance_principal
# Expected: JSON list of OCI regions — proves Instance Principal auth works

# Read a secret by OCID (use your actual secret OCID from the Console)
SECRET_OCID="ocid1.vaultsecret.oc1.iad.YOUR_SECRET_OCID"
oci secrets secret-bundle get \
  --secret-id ${SECRET_OCID} \
  --auth instance_principal \
  --query 'data."secret-bundle-content".content' \
  --raw-output | base64 -d
# Expected: the plaintext value you stored (e.g., fc_live_phase3_lab_key_001)
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `oci iam region list` | `--auth instance_principal` | Uses VM's built-in OCI identity instead of config file credentials |
| `oci secrets secret-bundle get` | `--secret-id` | Retrieves the latest version of a secret by OCID |
| `--query` | `'data."secret-bundle-content".content'` | JMESPath query to extract just the base64-encoded content |
| `base64 -d` | — | Decodes the base64 string to plaintext |

</em></sub>

---

### Step 22.10 — Integrate Ansible with OCI Vault (New Concept)
📍 **Local Terminal** then **Bastion Terminal**

> **🧠 ELI5 — Ansible Vault Integration:** Ansible has its own "Ansible Vault" feature (confusingly named) that encrypts variables inside your playbook files. But today you're doing something more powerful: pulling secrets directly from OCI Vault at playbook runtime. The pattern is: Ansible runs a lookup plugin that calls the OCI API to retrieve the secret value, and injects it into the playbook as a variable. Your playbook file contains only the secret's OCID — not the value. An attacker who gets your playbook sees only `ocid1.vaultsecret.oc1...` — useless without OCI credentials and the vault access policy.

> **💼 Interview Insight — Ansible Vault vs OCI Vault:** "These are two different tools that complement each other. Ansible Vault encrypts files and variables locally using a password — it's good for checking encrypted secrets into git. OCI Vault is a cloud-based secrets management service with access control, audit logging, and automatic rotation — it's better for production because the secret never lives in your repo at all, even encrypted. The enterprise pattern is often both: OCI Vault holds the real secrets, and Ansible Vault protects the password that unlocks your OCI CLI credentials on the control node."

**Install the OCI Ansible collection on the control node:**

📍 **Local Terminal**

> **Prerequisite:** Ansible must be installed on your local machine. If you installed it in Phase 1 or 2, skip the install. **Windows users:** Run all commands from WSL2 — Ansible does not run in PowerShell or Git Bash. See Phase 1 Step 12.1 for WSL2 setup instructions.

```bash
# Install Ansible if not already installed:
# pip install ansible   (WSL2/Linux)
# brew install ansible  (macOS)

# Install the OCI Ansible collection (includes the oci_secret lookup plugin)
ansible-galaxy collection install oracle.oci

# Verify installation
ansible-galaxy collection list | grep oracle
# Expected: oracle.oci   X.X.X
```

**Build `ansible/playbooks/deploy_fedcompliance.yml`:**

This playbook retrieves secrets from OCI Vault at runtime and uses them to configure the application — no secrets in the playbook file.

📍 **Editor** — create `~/oci-federal-lab-phase3/ansible/playbooks/deploy_fedcompliance.yml`

**Section 1:** Play header and OCI Vault secret lookups

```yaml
---
# Deploy FedCompliance — pulls secrets from OCI Vault at runtime
# Pattern: secret OCIDs are in the playbook; values are never stored locally
#
# Prerequisites:
#   - OCI Vault created with secrets: fedcompliance-db-password, fedcompliance-api-key
#   - IAM policy grants instance principal read access to the vault
#   - oracle.oci Ansible collection installed

- name: Deploy FedCompliance with secrets from OCI Vault
  hosts: k3s_servers
  become: true

  vars:
    # Secret OCIDs — these are NOT sensitive (they're just identifiers, not values)
    # Replace with your actual OCIDs from OCI Console → Vault → Secrets
    db_password_secret_ocid: "ocid1.vaultsecret.oc1.iad.YOUR_DB_PASSWORD_OCID"
    api_key_secret_ocid:     "ocid1.vaultsecret.oc1.iad.YOUR_API_KEY_OCID"
    app_dir: "/opt/fedcompliance"
    app_user: "fedcompliance"
```

**Section 2:** Pre-tasks — retrieve secrets from OCI Vault

```yaml
  pre_tasks:
    # Retrieve DB password from OCI Vault using instance principal auth
    # The lookup plugin contacts the OCI API; the VM's instance principal badge grants access
    - name: Retrieve DB password from OCI Vault
      set_fact:
        db_password: "{{ lookup('oracle.oci.oci_secret',
                          secret_id=db_password_secret_ocid,
                          auth_type='instance_principal') }}"
      no_log: true   # CRITICAL: prevents the retrieved secret value from appearing in logs

    - name: Retrieve API key from OCI Vault
      set_fact:
        fedcompliance_api_key: "{{ lookup('oracle.oci.oci_secret',
                                    secret_id=api_key_secret_ocid,
                                    auth_type='instance_principal') }}"
      no_log: true

    - name: Confirm secrets retrieved (without exposing values)
      debug:
        msg: "Secrets retrieved successfully. DB password length: {{ db_password | length }}"
```

> **Why `no_log: true`?** Ansible logs every task's arguments and return values to stdout and its log file by default. Without `no_log: true`, the retrieved secret value would appear in plaintext in your terminal output and in Jenkins logs. `no_log: true` suppresses all output for that task — the task still runs and the variable is set, but no values are logged.

**Section 3:** Application deployment tasks

```yaml
  tasks:
    - name: Create application user (non-root, no shell)
      user:
        name: "{{ app_user }}"
        system: true
        shell: /sbin/nologin
        home: "{{ app_dir }}"
        create_home: true

    - name: Create application directory structure
      file:
        path: "{{ item }}"
        state: directory
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0755'
      loop:
        - "{{ app_dir }}"
        - "{{ app_dir }}/app"
        - "{{ app_dir }}/logs"

    - name: Copy FedCompliance application files
      copy:
        src: "{{ item.src }}"
        dest: "{{ item.dest }}"
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0644'
      loop:
        - { src: "../../app/fedcompliance/", dest: "{{ app_dir }}/app/" }

    - name: Install Python dependencies
      pip:
        requirements: "{{ app_dir }}/app/requirements.txt"
        executable: /usr/bin/python3 -m pip

    - name: Verify Python dependencies are importable
      command: python3 -c "import fastapi; import uvicorn; print('deps OK')"
      changed_when: false

    - name: Write .env file with secrets from OCI Vault
      template:
        src: "../templates/fedcompliance.env.j2"
        dest: "{{ app_dir }}/.env"
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0600'   # owner-read-only — other users cannot read this file
      no_log: true     # template contains secret values

    - name: Deploy systemd service file
      template:
        src: "../templates/fedcompliance.service.j2"
        dest: /etc/systemd/system/fedcompliance.service
        mode: '0644'

    - name: Reload systemd and restart service
      systemd:
        name: fedcompliance
        daemon_reload: true
        enabled: true
        state: restarted

    - name: Wait for service to be ready
      uri:
        url: "http://localhost:8000/health"
        method: GET
        status_code: 200
      register: health_check
      retries: 10
      delay: 3
      until: health_check.status == 200

    - name: Report deployment success
      debug:
        msg: "FedCompliance deployed successfully. Health: {{ health_check.json }}"
```

**Build `ansible/templates/fedcompliance.env.j2`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/ansible/templates/fedcompliance.env.j2`

```ini
# FedCompliance environment variables
# Generated by Ansible at deploy time — secrets sourced from OCI Vault
# File permissions: 0600 (owner read-only)

DATABASE_URL=oracle+cx_oracle://ADMIN:{{ db_password }}@{{ db_connection_string }}
FEDCOMPLIANCE_API_KEY={{ fedcompliance_api_key }}
APP_ENV=lab
APP_PORT=8000
LOG_LEVEL=INFO
```

**Build `ansible/templates/fedcompliance.service.j2`:**

📍 **Editor** — create `~/oci-federal-lab-phase3/ansible/templates/fedcompliance.service.j2`

```ini
# systemd service file for FedCompliance
# Managed by Ansible — do not edit manually on the server

[Unit]
Description=FedCompliance FastAPI Service
After=network.target
Wants=network.target

[Service]
Type=simple
User={{ app_user }}
WorkingDirectory={{ app_dir }}/app
EnvironmentFile={{ app_dir }}/.env
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=fedcompliance

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths={{ app_dir }}/logs
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

---

### Step 22.11 — Build the FedCompliance FastAPI Application
📍 **Editor** (build by hand — new application, full section-by-section)

> **🧠 ELI5 — FedCompliance:** This is the application that will travel through the entire Phase 3 pipeline. It simulates a compliance management tool: it tracks security controls, runs compliance scans, and generates reports — the kind of tool a cloud engineer in federal consulting might build for a federal client who needs to demonstrate CMMC or NIST compliance. Today you build it manually and deploy it with Ansible. Days 2–4 will scan it for vulnerabilities, package it in a Helm chart, and deliver it via GitOps.

**Project structure for FedCompliance:**

```
app/fedcompliance/
├── main.py           ← FastAPI app entry point + middleware
├── database.py       ← Database connection and session management
├── models.py         ← SQLAlchemy ORM models
├── schemas.py        ← Pydantic request/response schemas
├── routers/
│   ├── compliance.py ← /compliance/* endpoints
│   └── auth.py       ← /auth/* endpoints
├── services/
│   └── scanner.py    ← Compliance scan logic
├── requirements.txt  ← Python dependencies
└── sql/
    └── seed.sql      ← Initial compliance control data (copy-paste)
```

Create the directory structure:

```bash
mkdir -p ~/oci-federal-lab-phase3/app/fedcompliance/routers
mkdir -p ~/oci-federal-lab-phase3/app/fedcompliance/services
mkdir -p ~/oci-federal-lab-phase3/app/fedcompliance/sql
```

---

#### Step 22.11a — Build requirements.txt
📍 **Editor** — create `~/oci-federal-lab-phase3/app/fedcompliance/requirements.txt`

```
fastapi==0.110.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.28
cx_Oracle==8.3.0
pydantic==2.6.3
pydantic-settings==2.2.1
python-dotenv==1.0.1
httpx==0.27.0
```

> **Why `cx_Oracle`?** Oracle Autonomous DB requires the Oracle client library. `cx_Oracle` is the Python adapter for Oracle databases. In newer projects `python-oracledb` replaces it, but `cx_Oracle` has broader documentation for ADB wallet-based connections — which is what Autonomous DB uses.

---

#### Step 22.11b — Build database.py
📍 **Editor** — create `~/oci-federal-lab-phase3/app/fedcompliance/database.py`

**Section 1:** Imports and configuration

```python
# database.py — Oracle Autonomous DB connection management
# Uses SQLAlchemy as the ORM; cx_Oracle as the Oracle database adapter
# Connection string and credentials come from environment variables (set by Ansible from OCI Vault)

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load .env file — written by Ansible with secrets from OCI Vault
load_dotenv()
```

**Section 2:** Database engine creation

```python
# Read DATABASE_URL from environment (injected by Ansible, sourced from OCI Vault)
# Format: oracle+cx_oracle://USER:PASSWORD@(description=(address=...))
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Ensure Ansible has written the .env file from OCI Vault secrets."
    )

# Create SQLAlchemy engine
# pool_size=5: maintain 5 persistent connections (reduces connection overhead)
# max_overflow=10: allow up to 10 additional connections under load
# pool_pre_ping=True: test connections before use — handles Autonomous DB idle disconnects
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False  # Set to True during debugging to log all SQL queries
)

# Session factory — each request gets its own session (connection lease)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()
```

**Section 3:** Database dependency for FastAPI

```python
def get_db():
    """
    FastAPI dependency that yields a database session per request.
    The 'finally' block ensures the session is always closed,
    even if the request handler raises an exception.

    Usage in a route:
        @router.get("/example")
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_health() -> dict:
    """Quick connectivity check for the /health endpoint."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM DUAL"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
```

---

#### Step 22.11c — Build models.py
📍 **Editor** — create `~/oci-federal-lab-phase3/app/fedcompliance/models.py`

**Section 1:** Imports

```python
# models.py — SQLAlchemy ORM models
# Defines the database table structure as Python classes.
# SQLAlchemy maps these classes to Oracle DB tables automatically.

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.sql import func
from database import Base
```

**Section 2:** Control and Scan models

```python
class ComplianceControl(Base):
    """
    A single compliance control from a framework (CMMC or NIST).
    Example: CMMC AC.1.001 — "Limit information system access to authorized users."
    """
    __tablename__ = "compliance_controls"

    id          = Column(Integer, primary_key=True, index=True)
    control_id  = Column(String(50), unique=True, nullable=False, index=True)
    framework   = Column(String(20), nullable=False)   # "CMMC" or "NIST"
    category    = Column(String(100), nullable=False)
    title       = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority    = Column(String(10), nullable=False, default="MEDIUM")  # HIGH / MEDIUM / LOW
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class ComplianceScan(Base):
    """
    A record of a compliance scan run.
    When POST /compliance/scan is called, a new scan record is created here.
    """
    __tablename__ = "compliance_scans"

    id              = Column(Integer, primary_key=True, index=True)
    scan_id         = Column(String(50), unique=True, nullable=False, index=True)
    framework       = Column(String(20), nullable=False)
    status          = Column(String(20), nullable=False, default="PENDING")  # PENDING / RUNNING / COMPLETE / FAILED
    controls_total  = Column(Integer, default=0)
    controls_passed = Column(Integer, default=0)
    controls_failed = Column(Integer, default=0)
    score           = Column(Float, default=0.0)   # compliance percentage 0.0-100.0
    findings        = Column(Text, nullable=True)   # JSON string of finding details
    started_at      = Column(DateTime(timezone=True), server_default=func.now())
    completed_at    = Column(DateTime(timezone=True), nullable=True)


class ApiKey(Base):
    """
    API keys for POST /auth/validate.
    In production, keys would be hashed (bcrypt). For this lab, stored as-is for simplicity.
    """
    __tablename__ = "api_keys"

    id          = Column(Integer, primary_key=True, index=True)
    key_value   = Column(String(100), unique=True, nullable=False, index=True)
    key_name    = Column(String(100), nullable=False)   # human-readable label
    is_active   = Column(Boolean, default=True)
    permissions = Column(String(200), default="read")   # comma-separated: read,write,admin
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    last_used   = Column(DateTime(timezone=True), nullable=True)
```

---

#### Step 22.11d — Build schemas.py
📍 **Editor** — create `~/oci-federal-lab-phase3/app/fedcompliance/schemas.py`

```python
# schemas.py — Pydantic request/response models
# Pydantic validates incoming request data and structures outgoing responses.
# Every API endpoint's input and output is defined here — nothing passes unvalidated.

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone


# --- Compliance Control Schemas ---

class ComplianceControlResponse(BaseModel):
    """Response schema for a single compliance control."""
    id:          int
    control_id:  str
    framework:   str
    category:    str
    title:       str
    description: Optional[str] = None
    priority:    str
    created_at:  datetime

    model_config = {"from_attributes": True}   # allows creating from SQLAlchemy model


class ControlsListResponse(BaseModel):
    """Response schema for GET /compliance/controls/{framework}."""
    framework:      str
    total_controls: int
    controls:       List[ComplianceControlResponse]


# --- Compliance Scan Schemas ---

class ScanRequest(BaseModel):
    """Request body for POST /compliance/scan."""
    framework: str = Field(
        ...,
        description="Framework to scan against",
        pattern="^(CMMC|NIST)$"   # only accept these two values
    )
    scope: Optional[str] = Field(
        default="full",
        description="Scan scope: 'full' or 'quick'"
    )


class ScanResponse(BaseModel):
    """Response schema for POST /compliance/scan."""
    scan_id:         str
    framework:       str
    status:          str
    message:         str
    estimated_seconds: int


class ScanStatusResponse(BaseModel):
    """Response schema for a completed scan."""
    scan_id:          str
    framework:        str
    status:           str
    controls_total:   int
    controls_passed:  int
    controls_failed:  int
    score:            float
    started_at:       datetime
    completed_at:     Optional[datetime] = None

    model_config = {"from_attributes": True}


# --- Compliance Dashboard Schemas ---

class ComplianceStatusResponse(BaseModel):
    """Response schema for GET /compliance/status."""
    overall_status:  str   # "COMPLIANT", "AT_RISK", "NON_COMPLIANT"
    cmmc_score:      float
    nist_score:      float
    last_scan_date:  Optional[datetime] = None
    open_findings:   int
    total_controls:  int


# --- Report Schemas ---

class ComplianceReportResponse(BaseModel):
    """Response schema for GET /compliance/report."""
    generated_at:     datetime
    reporting_period: str
    frameworks:       List[str]
    summary:          dict
    controls_by_category: dict
    recent_scans:     List[ScanStatusResponse]


# --- Auth Schemas ---

class ApiKeyValidateRequest(BaseModel):
    """Request body for POST /auth/validate."""
    api_key: str = Field(..., description="API key to validate", min_length=10)


class ApiKeyValidateResponse(BaseModel):
    """Response schema for POST /auth/validate."""
    valid:       bool
    key_name:    Optional[str] = None
    permissions: Optional[List[str]] = None
    message:     str


# --- Health Schema ---

class HealthResponse(BaseModel):
    """Response schema for GET /health."""
    status:    str
    service:   str
    version:   str
    database:  dict
    timestamp: datetime
```

---

#### Step 22.11e — Build services/scanner.py
📍 **Editor** — create `~/oci-federal-lab-phase3/app/fedcompliance/services/scanner.py`

```python
# services/scanner.py — Compliance scan business logic
# Simulates running a compliance scan against CMMC or NIST controls.
# In a real system this would call OpenSCAP, run shell checks, or call audit APIs.
# For this lab, it runs deterministic checks against the controls table.

import uuid
import json
import random
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models import ComplianceControl, ComplianceScan


def run_compliance_scan(db: Session, framework: str, scope: str = "full") -> ComplianceScan:
    """
    Execute a compliance scan for the given framework.

    1. Creates a scan record (status=RUNNING)
    2. Queries all controls for the framework
    3. Simulates check results (deterministic for repeatability in demos)
    4. Updates the scan record with results (status=COMPLETE)

    Returns the completed ComplianceScan record.
    """
    # Create the scan record
    scan_id = f"SCAN-{framework[:4].upper()}-{uuid.uuid4().hex[:8].upper()}"

    scan = ComplianceScan(
        scan_id=scan_id,
        framework=framework,
        status="RUNNING",
        started_at=datetime.now(timezone.utc)
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Retrieve controls for this framework
    controls = db.query(ComplianceControl).filter(
        ComplianceControl.framework == framework
    ).all()

    if not controls:
        scan.status = "FAILED"
        scan.findings = json.dumps({"error": f"No controls found for framework: {framework}"})
        db.commit()
        return scan

    # Simulate compliance checks
    # Deterministic based on control_id so results are consistent in demos
    findings = []
    passed = 0
    failed = 0

    for control in controls:
        # Use control_id hash for deterministic pass/fail (not random each run)
        # HIGH priority controls fail more often (simulates harder requirements)
        fail_threshold = {"HIGH": 0.35, "MEDIUM": 0.20, "LOW": 0.10}.get(control.priority, 0.20)

        # Seed random with control_id for repeatability
        rng = random.Random(hash(control.control_id) % 10000)
        check_failed = rng.random() < fail_threshold

        if check_failed:
            failed += 1
            findings.append({
                "control_id": control.control_id,
                "status": "FAIL",
                "severity": control.priority,
                "finding": f"Control {control.control_id} check did not pass automated verification",
                "remediation": f"Review {control.title} implementation and verify against {framework} requirements"
            })
        else:
            passed += 1

    # Calculate compliance score
    total = len(controls)
    score = round((passed / total) * 100, 2) if total > 0 else 0.0

    # Update scan record with results
    scan.status = "COMPLETE"
    scan.controls_total  = total
    scan.controls_passed = passed
    scan.controls_failed = failed
    scan.score           = score
    scan.findings        = json.dumps(findings)
    scan.completed_at    = datetime.now(timezone.utc)

    db.commit()
    db.refresh(scan)
    return scan


def get_latest_scan(db: Session, framework: str) -> ComplianceScan | None:
    """Return the most recent completed scan for a framework."""
    return (
        db.query(ComplianceScan)
        .filter(ComplianceScan.framework == framework, ComplianceScan.status == "COMPLETE")
        .order_by(ComplianceScan.completed_at.desc())
        .first()
    )
```

---

#### Step 22.11f — Build routers/auth.py
📍 **Editor** — create `~/oci-federal-lab-phase3/app/fedcompliance/routers/auth.py`

**Section 1:** Imports and router setup

```python
# routers/auth.py — POST /auth/validate endpoint
# Implements API key validation — the Phase 3 API authentication concept.
# This is the pattern you discuss when interviewers ask "how do you secure APIs?"

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db
from models import ApiKey
from schemas import ApiKeyValidateRequest, ApiKeyValidateResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
```

**Section 2:** Validation endpoint

```python
@router.post(
    "/validate",
    response_model=ApiKeyValidateResponse,
    summary="Validate an API key",
    description="Check whether an API key is valid and return its permissions. "
                "Used by services that need to verify caller identity before processing requests."
)
def validate_api_key(
    request: ApiKeyValidateRequest,
    db: Session = Depends(get_db)
):
    """
    Validate an API key against the database.

    Steps:
    1. Look up the key in the api_keys table
    2. Check that the key is active
    3. Update last_used timestamp (audit trail)
    4. Return validity and permissions

    Returns 200 with valid=True/False regardless of whether key exists.
    This prevents timing attacks that could enumerate valid key prefixes.
    """
    # Database lookup
    key_record = (
        db.query(ApiKey)
        .filter(ApiKey.key_value == request.api_key, ApiKey.is_active == True)
        .first()
    )

    if not key_record:
        # Return 200 with valid=False — NOT 401
        # Why? Returning 401 for invalid keys reveals that key validation happened.
        # Returning 200 with a validity field is safer for validation endpoints.
        # Endpoints that REQUIRE auth should return 401 — this endpoint CHECKS auth.
        return ApiKeyValidateResponse(
            valid=False,
            message="API key not found or inactive"
        )

    # Update last_used timestamp for audit trail
    key_record.last_used = datetime.now(timezone.utc)
    db.commit()

    return ApiKeyValidateResponse(
        valid=True,
        key_name=key_record.key_name,
        permissions=key_record.permissions.split(","),
        message="API key is valid"
    )
```

**Section 3:** Auth middleware helper (used by other routers)

```python
def require_api_key(
    api_key: str = None,
    db: Session = Depends(get_db)
) -> ApiKey:
    """
    FastAPI dependency for endpoints that REQUIRE authentication.

    Usage:
        @router.get("/protected")
        def protected_route(key: ApiKey = Depends(require_api_key)):
            ...

    How it works:
    - Client sends: Header X-API-Key: fc_live_...
    - FastAPI injects the header value as 'api_key' parameter
    - This function validates it and raises 401 if invalid
    - If valid, returns the ApiKey record so the route can check permissions
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    key_record = (
        db.query(ApiKey)
        .filter(ApiKey.key_value == api_key, ApiKey.is_active == True)
        .first()
    )

    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    # Update last_used
    key_record.last_used = datetime.now(timezone.utc)
    db.commit()

    return key_record
```

> **Why does `/auth/validate` return 200 with `valid=False` instead of 401?** This endpoint's purpose is to *check* a key, not *require* one. A service calling this endpoint isn't necessarily trying to authenticate itself — it may be validating a key on behalf of another request. Returning 401 for "key not found" would confuse clients because they'd think *their call to the validation endpoint* was unauthorized. The 200+`valid=false` pattern clearly communicates "your call succeeded; the key you asked about is invalid." Reserve 401 for endpoints that *require* the caller to be authenticated.

---

#### Step 22.11g — Build routers/compliance.py
📍 **Editor** — create `~/oci-federal-lab-phase3/app/fedcompliance/routers/compliance.py`

**Section 1:** Imports and router setup

```python
# routers/compliance.py — All /compliance/* endpoints
# GET  /compliance/status              — compliance dashboard
# GET  /compliance/controls/{framework} — list controls for a framework
# POST /compliance/scan                — trigger a compliance scan
# GET  /compliance/report              — generate compliance report

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
import json

from database import get_db
from models import ComplianceControl, ComplianceScan
from schemas import (
    ComplianceStatusResponse,
    ControlsListResponse,
    ScanRequest,
    ScanResponse,
    ComplianceReportResponse,
    ScanStatusResponse,
)
from services.scanner import run_compliance_scan, get_latest_scan

router = APIRouter(prefix="/compliance", tags=["Compliance"])
```

**Section 2:** Status endpoint

```python
@router.get(
    "/status",
    response_model=ComplianceStatusResponse,
    summary="Compliance dashboard",
    description="Returns overall compliance posture based on the most recent scans for each framework."
)
def get_compliance_status(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Returns the overall compliance status dashboard.
    Pulls the most recent completed scan for each framework and computes overall status.
    No authentication required (public status dashboard).
    """
    cmmc_scan = get_latest_scan(db, "CMMC")
    nist_scan  = get_latest_scan(db, "NIST")

    cmmc_score = cmmc_scan.score if cmmc_scan else 0.0
    nist_score = nist_scan.score if nist_scan else 0.0

    # Determine overall status based on scores
    avg_score = (cmmc_score + nist_score) / 2 if (cmmc_scan or nist_scan) else 0.0

    if avg_score >= 85.0:
        overall_status = "COMPLIANT"
    elif avg_score >= 70.0:
        overall_status = "AT_RISK"
    else:
        overall_status = "NON_COMPLIANT"

    # Count open findings across all frameworks
    open_findings = 0
    for scan in [cmmc_scan, nist_scan]:
        if scan and scan.findings:
            try:
                findings = json.loads(scan.findings)
                open_findings += len([f for f in findings if f.get("status") == "FAIL"])
            except (json.JSONDecodeError, TypeError):
                pass

    total_controls = db.query(ComplianceControl).count()

    return ComplianceStatusResponse(
        overall_status=overall_status,
        cmmc_score=cmmc_score,
        nist_score=nist_score,
        last_scan_date=cmmc_scan.completed_at if cmmc_scan else None,
        open_findings=open_findings,
        total_controls=total_controls,
    )
```

**Section 3:** Controls list endpoint

```python
@router.get(
    "/controls/{framework}",
    response_model=ControlsListResponse,
    summary="List compliance controls",
    description="Returns all controls for the specified framework (CMMC or NIST)."
)
def get_controls(
    framework: str,
    db: Session = Depends(get_db)
):
    """
    List all controls for a given compliance framework.
    framework must be 'CMMC' or 'NIST' (case-insensitive — normalized to uppercase).
    """
    framework = framework.upper()

    if framework not in ("CMMC", "NIST"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown framework '{framework}'. Supported: CMMC, NIST"
        )

    controls = (
        db.query(ComplianceControl)
        .filter(ComplianceControl.framework == framework)
        .order_by(ComplianceControl.control_id)
        .all()
    )

    return ControlsListResponse(
        framework=framework,
        total_controls=len(controls),
        controls=controls,
    )
```

**Section 4:** Scan trigger endpoint

```python
@router.post(
    "/scan",
    response_model=ScanResponse,
    status_code=status.HTTP_202_ACCEPTED,   # 202 = request accepted, processing async
    summary="Trigger compliance scan",
    description="Initiates a compliance scan for the specified framework. "
                "Requires X-API-Key header with write permissions."
)
def trigger_scan(
    scan_request: ScanRequest,
    x_api_key: str = Header(..., alias="X-API-Key", description="API key with write permissions"),
    db: Session = Depends(get_db)
):
    """
    Trigger a compliance scan. Protected by API key (requires write permission).

    Note: In a production system, scans would run asynchronously (Celery, async background task).
    For this lab, the scan runs synchronously — the response returns after the scan completes.
    The 202 status code signals "accepted for processing" as a forward-compatible design choice.
    """
    from routers.auth import require_api_key
    from fastapi import Request

    # Validate API key inline (would normally be a Depends() but keeping it explicit for clarity)
    from models import ApiKey
    key_record = db.query(ApiKey).filter(
        ApiKey.key_value == x_api_key, ApiKey.is_active == True
    ).first()

    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid X-API-Key header required to trigger scans"
        )

    # Check write permission
    if "write" not in key_record.permissions.split(",") and "admin" not in key_record.permissions.split(","):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not have write permissions required to trigger scans"
        )

    # Run the scan (synchronous for simplicity)
    try:
        scan = run_compliance_scan(db, scan_request.framework, scan_request.scope)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scan failed: {str(e)}"
        )

    return ScanResponse(
        scan_id=scan.scan_id,
        framework=scan.framework,
        status=scan.status,
        message=f"Scan completed: {scan.controls_passed}/{scan.controls_total} controls passed ({scan.score}%)",
        estimated_seconds=0,  # already complete
    )
```

**Section 5:** Report endpoint

```python
@router.get(
    "/report",
    response_model=ComplianceReportResponse,
    summary="Generate compliance report",
    description="Generates a comprehensive compliance report across all frameworks."
)
def get_compliance_report(db: Session = Depends(get_db)):
    """
    Generate a compliance report aggregating results from all recent scans.
    """
    # Get recent scans for both frameworks
    recent_scans = (
        db.query(ComplianceScan)
        .filter(ComplianceScan.status == "COMPLETE")
        .order_by(ComplianceScan.completed_at.desc())
        .limit(10)
        .all()
    )

    # Build controls-by-category breakdown
    controls_by_category: dict = {}
    all_controls = db.query(ComplianceControl).all()
    for control in all_controls:
        key = f"{control.framework}:{control.category}"
        controls_by_category[key] = controls_by_category.get(key, 0) + 1

    # Summary statistics
    cmmc_scan = get_latest_scan(db, "CMMC")
    nist_scan  = get_latest_scan(db, "NIST")

    summary = {
        "cmmc": {
            "score":    cmmc_scan.score if cmmc_scan else None,
            "status":   cmmc_scan.status if cmmc_scan else "NO_SCAN",
            "findings": cmmc_scan.controls_failed if cmmc_scan else 0,
        },
        "nist": {
            "score":    nist_scan.score if nist_scan else None,
            "status":   nist_scan.status if nist_scan else "NO_SCAN",
            "findings": nist_scan.controls_failed if nist_scan else 0,
        },
    }

    return ComplianceReportResponse(
        generated_at=datetime.now(timezone.utc),
        reporting_period="Last 30 days",
        frameworks=["CMMC", "NIST"],
        summary=summary,
        controls_by_category=controls_by_category,
        recent_scans=recent_scans,
    )
```

---

#### Step 22.11h — Build main.py (Application Entry Point)
📍 **Editor** — create `~/oci-federal-lab-phase3/app/fedcompliance/main.py`

**Section 1:** Imports and app configuration

```python
# main.py — FedCompliance FastAPI application entry point
# Wires together all routers, configures middleware, and sets up the database.
# This is the file that uvicorn loads: uvicorn main:app --host 0.0.0.0 --port 8000

import os
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import Base, engine, check_db_health
from routers import compliance, auth
from schemas import HealthResponse

# Configure structured logging — output to stdout for systemd/journald capture
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("fedcompliance")
```

**Section 2:** Lifespan handler (startup / shutdown)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on application startup and shutdown.
    On startup: creates database tables if they don't exist.
    On shutdown: logs graceful shutdown (good practice for audit trails).

    asynccontextmanager pattern replaces the old @app.on_event("startup") decorator
    which was deprecated in FastAPI 0.95+.
    """
    # Startup
    logger.info("FedCompliance starting up...")
    logger.info(f"Environment: {os.getenv('APP_ENV', 'unknown')}")

    # Create all tables defined in models.py if they don't already exist
    # In production, use Alembic migrations instead — but table creation is fine for labs
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created")

    yield  # Application runs here

    # Shutdown
    logger.info("FedCompliance shutting down gracefully")
```

**Section 3:** App instance and middleware

```python
app = FastAPI(
    title="FedCompliance API",
    description=(
        "Compliance management API for federal environments. "
        "Tracks CMMC and NIST controls, runs compliance scans, and generates reports. "
        "Phase 3 of the Federal Cloud Engineer Lab."
    ),
    version="3.0.0",
    docs_url="/docs",        # Swagger UI at /docs
    redoc_url="/redoc",      # ReDoc at /redoc
    lifespan=lifespan,
)

# CORS middleware — allow all origins in lab (would restrict to specific domains in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Section 4:** Request logging middleware

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log every incoming request with method, path, and response status.
    Runs for EVERY request before it reaches a route handler.

    This is how federal audit logs work: every API call is recorded with
    timestamp, method, path, and status code. The X-API-Key header value
    is intentionally NOT logged — logging secrets is a security violation.
    """
    start_time = datetime.now(timezone.utc)

    # Log the incoming request (mask API key if present)
    has_key = "X-API-Key" in request.headers
    logger.info(
        f"REQUEST {request.method} {request.url.path} "
        f"[api_key={'present' if has_key else 'absent'}]"
    )

    response = await call_next(request)

    # Log the response
    duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
    logger.info(
        f"RESPONSE {request.method} {request.url.path} "
        f"status={response.status_code} duration={duration_ms:.1f}ms"
    )

    return response
```

**Section 5:** Router registration and health endpoint

```python
# Register routers — each router handles a URL prefix
app.include_router(compliance.router)
app.include_router(auth.router)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Service health check",
    description="Returns service health including database connectivity. "
                "Used by k3s liveness probes and the Ansible deploy playbook."
)
def health_check():
    """
    Health check endpoint — no authentication required.
    Returns 200 if healthy, 503 if any critical dependency is down.

    k3s uses this endpoint for liveness and readiness probes.
    Ansible's uri module calls this to verify deployment success.
    """
    db_health = check_db_health()

    overall_healthy = db_health.get("status") == "healthy"

    if not overall_healthy:
        # Return 503 Service Unavailable so k3s restarts the pod
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {db_health}"
        )

    return HealthResponse(
        status="healthy",
        service="fedcompliance",
        version="3.0.0",
        database=db_health,
        timestamp=datetime.now(timezone.utc),
    )
```

> **🧠 Putting it together:** `main.py` is the wiring layer. It creates the FastAPI app, attaches the logging middleware (which runs for every request), registers the two routers (which own the actual endpoint logic), and provides the `/health` endpoint. When uvicorn starts, it imports `main.py`, calls the `lifespan` startup function to create database tables, then begins accepting HTTP requests. When a request arrives, the middleware logs it, the appropriate router handles it, and the middleware logs the response.

---

#### Step 22.11i — Create SQL Schema and Seed Data (Copy-Paste)
📍 **Editor** — create `~/oci-federal-lab-phase3/app/fedcompliance/sql/seed.sql`

> This file is copy-paste — it's data, not logic. Read the inline comments to understand the structure.

```sql
-- seed.sql — Initial compliance control data for FedCompliance
-- Run once after database creation to populate the compliance_controls table.
-- Ansible's deploy playbook runs this via sqlplus after the app tables are created.
--
-- Data represents a subset of real CMMC Level 2 and NIST SP 800-171 controls.
-- Used for demo purposes — not authoritative compliance guidance.

-- ============================================================
-- CMMC Level 2 Controls (subset)
-- Domain areas: AC (Access Control), IA (Identification & Auth),
--               CM (Configuration Mgmt), SC (System & Comms Protection)
-- ============================================================

-- Access Control domain
INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('AC.L2-3.1.1', 'CMMC', 'Access Control',
        'Limit system access to authorized users',
        'Limit information system access to authorized users, processes acting on behalf of authorized users, and devices (including other information systems).',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('AC.L2-3.1.2', 'CMMC', 'Access Control',
        'Limit system access to permitted transactions',
        'Limit information system access to the types of transactions and functions that authorized users are permitted to execute.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('AC.L2-3.1.3', 'CMMC', 'Access Control',
        'Control CUI flow',
        'Control the flow of CUI in accordance with approved authorizations.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('AC.L2-3.1.5', 'CMMC', 'Access Control',
        'Employ principle of least privilege',
        'Employ the principle of least privilege, including for specific security functions and privileged accounts.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('AC.L2-3.1.6', 'CMMC', 'Access Control',
        'Use non-privileged accounts for non-security functions',
        'Use non-privileged accounts or roles when accessing non-security functions.',
        'MEDIUM');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('AC.L2-3.1.12', 'CMMC', 'Access Control',
        'Monitor and control remote access sessions',
        'Monitor and control remote access sessions.',
        'HIGH');

-- Identification and Authentication domain
INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('IA.L2-3.5.1', 'CMMC', 'Identification & Authentication',
        'Identify information system users',
        'Identify information system users, processes acting on behalf of users, and devices.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('IA.L2-3.5.2', 'CMMC', 'Identification & Authentication',
        'Authenticate users before allowing access',
        'Authenticate (or verify) the identities of those users, processes, or devices as a prerequisite to allowing access.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('IA.L2-3.5.3', 'CMMC', 'Identification & Authentication',
        'Use multifactor authentication',
        'Use multifactor authentication for local and network access to privileged accounts and for network access to non-privileged accounts.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('IA.L2-3.5.7', 'CMMC', 'Identification & Authentication',
        'Enforce minimum password complexity',
        'Enforce a minimum password complexity and change of characters when new passwords are created.',
        'MEDIUM');

-- Configuration Management domain
INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('CM.L2-3.4.1', 'CMMC', 'Configuration Management',
        'Establish baseline configurations',
        'Establish and maintain baseline configurations and inventories of organizational information systems.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('CM.L2-3.4.2', 'CMMC', 'Configuration Management',
        'Establish security configuration settings',
        'Establish and enforce security configuration settings for IT products employed in organizational information systems.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('CM.L2-3.4.6', 'CMMC', 'Configuration Management',
        'Employ principle of least functionality',
        'Employ the principle of least functionality by configuring organizational information systems to provide only essential capabilities.',
        'MEDIUM');

-- System and Communications Protection domain
INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('SC.L2-3.13.1', 'CMMC', 'System & Communications Protection',
        'Monitor communications at external boundaries',
        'Monitor, control, and protect organizational communications at the external boundaries and key internal boundaries of information systems.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('SC.L2-3.13.5', 'CMMC', 'System & Communications Protection',
        'Implement subnetworks for publicly accessible components',
        'Implement subnetworks for publicly accessible system components that are physically or logically separated from internal networks.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('SC.L2-3.13.8', 'CMMC', 'System & Communications Protection',
        'Implement cryptographic mechanisms for CUI transmission',
        'Implement cryptographic mechanisms to prevent unauthorized disclosure of CUI during transmission.',
        'HIGH');

-- Audit and Accountability domain
INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('AU.L2-3.3.1', 'CMMC', 'Audit & Accountability',
        'Create and retain system audit logs',
        'Create and retain system audit logs and records to the extent needed to enable the monitoring, analysis, investigation, and reporting of unlawful or unauthorized system activity.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('AU.L2-3.3.2', 'CMMC', 'Audit & Accountability',
        'Ensure individual accountability',
        'Ensure that the actions of individual information system users can be uniquely traced to those users.',
        'HIGH');

-- ============================================================
-- NIST SP 800-171 Controls (subset)
-- Mirrors CMMC Level 2 but uses NIST numbering
-- ============================================================

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.1.1', 'NIST', 'Access Control',
        'Limit system access to authorized users and processes',
        'Limit information system access to authorized users, processes acting on behalf of authorized users, and devices.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.1.2', 'NIST', 'Access Control',
        'Limit access to permitted transaction types',
        'Limit information system access to types of transactions and functions authorized users are permitted to execute.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.3.1', 'NIST', 'Audit & Accountability',
        'Create audit logs sufficient for monitoring',
        'Create and retain system audit logs to enable monitoring, analysis, investigation, and reporting of unlawful activity.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.3.2', 'NIST', 'Audit & Accountability',
        'Ensure user actions are uniquely traceable',
        'Ensure the actions of individual system users can be uniquely traced to those users.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.4.1', 'NIST', 'Configuration Management',
        'Establish and maintain baseline configurations',
        'Establish and maintain baseline configurations and inventories of organizational systems.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.4.2', 'NIST', 'Configuration Management',
        'Enforce security configuration settings',
        'Establish and enforce security configuration settings for IT products employed in systems.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.5.1', 'NIST', 'Identification & Authentication',
        'Identify system users and devices',
        'Identify information system users, processes acting on behalf of users, and devices.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.5.2', 'NIST', 'Identification & Authentication',
        'Authenticate users before granting access',
        'Authenticate the identities of users, processes, or devices before allowing access.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.5.3', 'NIST', 'Identification & Authentication',
        'Require MFA for privileged accounts',
        'Use multifactor authentication for local and network access to privileged accounts.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.13.1', 'NIST', 'System & Communications Protection',
        'Monitor and control communications at system boundaries',
        'Monitor, control, and protect communications at external boundaries and key internal boundaries.',
        'HIGH');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.13.5', 'NIST', 'System & Communications Protection',
        'Separate publicly accessible components',
        'Implement subnetworks for publicly accessible components separated from internal networks.',
        'MEDIUM');

INSERT INTO compliance_controls (control_id, framework, category, title, description, priority)
VALUES ('NIST-3.13.8', 'NIST', 'System & Communications Protection',
        'Encrypt CUI in transit',
        'Implement cryptographic mechanisms to prevent unauthorized disclosure of CUI during transmission.',
        'HIGH');

-- ============================================================
-- API Keys — initial key for lab testing
-- In production: keys would be bcrypt-hashed. Lab uses plaintext for simplicity.
-- The actual key value is stored in OCI Vault as 'fedcompliance-api-key'
-- ============================================================

INSERT INTO api_keys (key_value, key_name, is_active, permissions)
VALUES ('fc_live_phase3_lab_key_001', 'Phase 3 Lab Key', 1, 'read,write');

-- Read-only key for monitoring/reporting
INSERT INTO api_keys (key_value, key_name, is_active, permissions)
VALUES ('fc_readonly_phase3_monitor_001', 'Phase 3 Monitor Key', 1, 'read');

COMMIT;
```

**Verify app file structure:**

```bash
find ~/oci-federal-lab-phase3/app/fedcompliance -type f | sort
# Expected:
#   .../fedcompliance/database.py
#   .../fedcompliance/main.py
#   .../fedcompliance/models.py
#   .../fedcompliance/requirements.txt
#   .../fedcompliance/routers/auth.py
#   .../fedcompliance/routers/compliance.py
#   .../fedcompliance/schemas.py
#   .../fedcompliance/services/scanner.py
#   .../fedcompliance/sql/seed.sql
```

---

### Step 22.12 — Set Up 2-Node k3s Cluster
📍 **App Node Terminal** (abbreviated — returning concept from Phase 2)

> Returning concept from Phase 2. Same server + agent pattern. Abbreviated — commands listed, ELI5 skipped.

**Install k3s server on node-1:**

📍 **App Node Terminal (node-1)** — SSH in via bastion jump

```bash
ssh -J opc@BASTION_IP opc@NODE1_PRIVATE_IP

# Install k3s server (control plane + worker)
# --disable traefik: we will use nginx ingress instead (Day 3)
curl -sfL https://get.k3s.io | sh -s - server \
  --disable traefik \
  --node-name k3s-node-1 \
  --write-kubeconfig-mode 644

sudo systemctl status k3s
# Expected: active (running)

# Get the node token — needed for the agent join command
sudo cat /var/lib/rancher/k3s/server/node-token
# Save this value — referred to as YOUR_NODE_TOKEN below
```

**Join k3s agent on node-2:**

📍 **App Node Terminal (node-2)**

```bash
ssh -J opc@BASTION_IP opc@NODE2_PRIVATE_IP

curl -sfL https://get.k3s.io | sh -s - agent \
  --server https://NODE1_PRIVATE_IP:6443 \
  --token YOUR_NODE_TOKEN \
  --node-name k3s-node-2

sudo systemctl status k3s-agent
# Expected: active (running)
```

**Verify cluster and copy kubeconfig to bastion:**

📍 **App Node Terminal (node-1)**

```bash
kubectl get nodes
# Expected:
# NAME          STATUS   ROLES                  AGE   VERSION
# k3s-node-1   Ready    control-plane,master   Xm    v1.29.x+k3s1
# k3s-node-2   Ready    <none>                 Xm    v1.29.x+k3s1
```

📍 **Bastion Terminal**

```bash
# Copy kubeconfig from node-1
# Replace <NODE1_PRIVATE_IP> with your actual node-1 private IP
# Find it with: terraform output -raw k3s_node1_private_ip
scp opc@<NODE1_PRIVATE_IP>:/etc/rancher/k3s/k3s.yaml ~/.kube/config

# Point kubeconfig at node-1's real IP (default is 127.0.0.1)
sed -i "s/127.0.0.1/<NODE1_PRIVATE_IP>/g" ~/.kube/config

# Install kubectl (ARM binary)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/arm64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

kubectl get nodes
# Expected: both nodes Ready
```

---

### Step 22.13 — Deploy FedCompliance via Ansible
📍 **Local Terminal**

```bash
cd ~/oci-federal-lab-phase3

# Run the deploy playbook — pulls secrets from OCI Vault at runtime
ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy_fedcompliance.yml

# Watch for the debug task output — confirms Vault integration worked:
# "Secrets retrieved successfully. DB password length: 18"
# The actual password is never shown in output

# Seed the database with compliance control data
ssh -J opc@BASTION_IP opc@NODE1_PRIVATE_IP \
  "sqlplus ADMIN/YOUR_DB_PASSWORD@FEDCOMP_low @/opt/fedcompliance/app/sql/seed.sql"
```

**Verify the application:**

📍 **Bastion Terminal**

```bash
# Health check
curl http://NODE1_PRIVATE_IP:8000/health
# Expected: {"status":"healthy","service":"fedcompliance",...,"database":{"status":"healthy",...}}

# Compliance dashboard (no scan run yet)
curl http://NODE1_PRIVATE_IP:8000/compliance/status
# Expected: {"overall_status":"NON_COMPLIANT","cmmc_score":0.0,"nist_score":0.0,...}

# Trigger a CMMC scan (requires API key)
curl -X POST http://NODE1_PRIVATE_IP:8000/compliance/scan \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fc_live_phase3_lab_key_001" \
  -d '{"framework": "CMMC", "scope": "full"}'
# Expected: {"scan_id":"SCAN-CMMC-XXXXXXXX","status":"COMPLETE","score":...}

# Validate an API key (the Phase 3 auth concept in action)
curl -X POST http://NODE1_PRIVATE_IP:8000/auth/validate \
  -H "Content-Type: application/json" \
  -d '{"api_key": "fc_live_phase3_lab_key_001"}'
# Expected: {"valid":true,"key_name":"Phase 3 Lab Key","permissions":["read","write"],...}

# Test with an invalid key — should return 200 with valid=false (not 401)
curl -X POST http://NODE1_PRIVATE_IP:8000/auth/validate \
  -H "Content-Type: application/json" \
  -d '{"api_key": "not_a_real_key"}'
# Expected: {"valid":false,"message":"API key not found or inactive"}
```

Open Swagger UI to explore all endpoints interactively:

```bash
# Create SSH tunnel from your local machine
ssh -L 8000:NODE1_PRIVATE_IP:8000 -J opc@BASTION_IP opc@NODE1_PRIVATE_IP -N &
# Then open: http://localhost:8000/docs
```

---

### Step 22.14 — Git Commit
📍 **Local Terminal**

```bash
cd ~/oci-federal-lab-phase3

git add phases/phase-3-fedcompliance-gitops-security/
git add .gitignore

git commit -m "Phase 22: Terraform modules, OCI Vault secrets, FedCompliance app

- Refactored flat Terraform into network/compute/database modules
- Added Service Gateway for private subnet OCI Vault access
- OCI Vault with 3 secrets; IAM Instance Principal policy grants VM read access
- Ansible deploy playbook retrieves secrets from OCI Vault at runtime
- FedCompliance FastAPI: compliance scan, report, API key auth endpoints
- 2-node k3s cluster (server + agent) deployed and verified"

git push origin main
```

---

### Phase 22 Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `terraform apply` fails: `missing required attribute "public_subnet_id"` | Output variable name mismatch between `modules/network/outputs.tf` and `environments/lab/main.tf` | Open `modules/network/outputs.tf` — confirm the output block is named `public_subnet_id`. Open `environments/lab/main.tf` — confirm `public_subnet_id = module.network.public_subnet_id` matches exactly |
| `terraform plan` error: `This object does not have an attribute named "public_subnet_id"` | Same mismatch — Terraform can not find the output | Check `modules/network/outputs.tf` output block name. The name after `output "` must match what `main.tf` references after `module.network.` |
| Compute creates before network finishes — VMs fail to attach to subnet | Missing `depends_on` in compute module call | Add `depends_on = [module.network]` inside both the `module "compute"` and `module "database"` blocks in `environments/lab/main.tf` |
| App fails to start; systemd logs show `Authorization failed or requested resource not found` | Vault IAM policy does not grant the VM's instance principal read access | Console → Identity & Security → Policies → `fedcompliance-vault-read-policy` → verify the statement says `read secret-family in compartment YOUR_COMPARTMENT_NAME` (exact name, not OCID). Verify the dynamic group rule matches the compartment OCID where the VMs live |
| `oci secrets secret-bundle get` returns 404 from bastion | Secret OCID in the command is wrong, or secret is in a different compartment | Console → Vault → Secrets → click the secret → copy OCID from the detail panel. Re-run the command with the copied OCID |
| `oci iam region list --auth instance_principal` fails | Instance principal not enabled, or OCI CLI version too old | Run `python3 -m pip install --upgrade oci-cli` on bastion. Verify the bastion VM is in the dynamic group: Console → Identity → Dynamic Groups → view matching rules |
| Ansible `lookup('oracle.oci.oci_secret')` fails: `ModuleNotFoundError: No module named 'oci'` | OCI Python SDK missing from Ansible's Python environment | Run `python3 -m pip install oci` on the Ansible control node. Verify: `python3 -c "import oci; print(oci.__version__)"` |
| FedCompliance `/health` returns `database: connection refused` | ADB wallet not installed or `DATABASE_URL` malformed in `.env` | Verify wallet was extracted to the wallet directory. Check `/opt/fedcompliance/.env` — the connection string must use the tnsnames format, not a simple host:port |
| k3s node-2 shows `NotReady` | Flannel VXLAN UDP 8472 blocked by OCI private security list | In `modules/network/main.tf`, verify the private security list has `protocol = "17"` (UDP) ingress rule for port 8472. Run `terraform apply` to push the update |

---

### Phase 22 Complete

**What you built:**

- Terraform module architecture: `modules/network`, `modules/compute`, `modules/database` — each with `main.tf`, `variables.tf`, `outputs.tf` — called from `environments/lab/main.tf`
- OCI network with Service Gateway routing private subnet traffic to OCI Vault without internet traversal
- OCI Vault with AES-256 encryption key and three secrets; IAM Instance Principal dynamic group + policy grants VMs access at runtime with no stored credentials
- Ansible deploy playbook using the `oracle.oci` lookup plugin to pull secrets from Vault — zero plaintext secrets in code or config files
- FedCompliance FastAPI application: 6 endpoints covering compliance dashboards, control listing, scan triggering, report generation, API key validation, and health checking
- Oracle Autonomous DB seeded with 20+ real CMMC Level 2 and NIST SP 800-171 control records
- 2-node k3s cluster on Oracle Linux 9 ARM, with kubeconfig on bastion for remote management

**What's running:**

- OCI Vault: `fedcompliance-vault` with `fedcompliance-master-key`, 3 active secrets
- Oracle Autonomous DB `FEDCOMP` (Always Free, 20 GB): compliance_controls, compliance_scans, api_keys tables populated
- k3s cluster: node-1 (control-plane + worker), node-2 (worker) — both Ready
- FedCompliance API: port 8000 on node-1, systemd-managed, secrets sourced from OCI Vault at deploy time

**Total Phase 22 cost: $0.00** (3 Always Free ARM VMs + Always Free Autonomous DB + Always Free Vault)

**Next phase:** Phase 23 installs Jenkins on the bastion and builds the CI/CD pipeline. The pipeline will check out FedCompliance, validate the Terraform modules, scan the container image with Trivy for CVEs, generate an SBOM with Syft (Executive Order 14028 compliance), pass through a manual approval gate, build and push the container to OCIR, and deploy to the k3s cluster via raw kubectl manifests. Everything built today — the modules, the app, the cluster — feeds directly into that pipeline.

---

## PHASE 23: THE PIPELINE + RAW K8S DEPLOY (6–8 hrs)

> You have infrastructure standing from Day 1 (Terraform modules, OCI Vault, k3s cluster). Today you build the CI/CD pipeline that makes every future change automated, auditable, and security-gated. You install Jenkins, write a multi-stage Jenkinsfile by hand, add container security scanning with Trivy, generate a software bill of materials with Syft, wire up a manual approval gate, and end the day with your FedCompliance app running on k3s — deployed entirely through the pipeline via raw `kubectl apply`.
>
> Why raw manifests before Helm? Because Day 3 introduces Helm, and the best way to understand what Helm abstracts is to do it without Helm first. Today you feel the friction of managing individual YAML files and sed-based image tag substitution. Tomorrow you will understand exactly what Helm fixes.
>
> 📍 **Most work happens on the Bastion Terminal (Jenkins VM). Jenkins UI setup uses the Browser. K8s verification uses the App Node Terminal.**
>
> 🛠️ **Build approach:** Jenkinsfile — built by hand, section by section with full explanation. K8s manifests (Deployment, Service, ConfigMap, Namespace) — built by hand, abbreviated (returning from Phase 2). Trivy and Syft — installed via commands, called from Jenkinsfile. Jenkins credentials — configured via Jenkins UI.

---

### Phase 23 Architecture — What You're Building Today

```
Your Laptop (git push)
        │
        ▼
┌───────────────────────────────────────────────────────┐
│  Bastion VM / Jenkins Server (Oracle Linux 9)          │
│  Public Subnet — 10.0.1.x                              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Jenkins Pipeline (Jenkinsfile)                  │   │
│  │                                                   │   │
│  │  Stage 1: Checkout                               │   │
│  │      ▼                                            │   │
│  │  Stage 2: Terraform Validate + Plan              │   │
│  │      ▼                                            │   │
│  │  Stage 3: Trivy Scan ← BLOCKS on CRITICAL CVEs  │   │
│  │      ▼                                            │   │
│  │  Stage 4: Syft SBOM Generation (EO 14028)        │   │
│  │      ▼                                            │   │
│  │  Stage 5: Ansible Lint                           │   │
│  │      ▼                                            │   │
│  │  Stage 6: MANUAL APPROVAL GATE (human clicks)   │   │
│  │      ▼  [pauses — waits for approval]            │   │
│  │  Stage 7: Docker Build + Push to OCIR            │   │
│  │      ▼                                            │   │
│  │  Stage 8: kubectl apply -f k8s/                  │   │
│  │      ▼                                            │   │
│  │  Stage 9: Smoke Test (curl /health)              │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Tools on this VM:                                      │
│    Jenkins (returning)  Trivy (NEW)  Syft (NEW)         │
│    Docker  kubectl  Terraform  Ansible                  │
└───────────────────────┬───────────────────────────────┘
                        │ kubectl apply
                        │ (kubeconfig secret)
                        ▼
┌───────────────────────────────────────────────────────┐
│  k3s Cluster — Private Subnet 10.0.2.x                 │
│                                                         │
│  Namespace: fedcompliance                               │
│    ConfigMap: fedcompliance-config                      │
│    Deployment: fedcompliance (2 replicas)               │
│      Image: <region>.ocir.io/<ns>/fedcompliance:<sha>   │
│    Service: fedcompliance-svc (NodePort 30080)          │
│                                                         │
│  Build artifacts per run (Jenkins):                     │
│    trivy-report.json + fedcompliance-sbom-N.spdx.json  │
└───────────────────────────────────────────────────────┘
```

---

### Step 23.1 — Install Jenkins (Returning Concept — Abbreviated)

📍 **Bastion Terminal**

> **CloudBees CI — Returning from Phase 2 Migration**
>
> In Phase 2, you migrated from open-source Jenkins to CloudBees CI (or the open-source plugin equivalent). You configured RBAC, CasC, and audit trails. Phase 3 starts with a fresh environment, so you'll do a speed-run of that setup, then go deeper with **pipeline templates**, **cross-team visibility**, and **CasC bundle versioning** in Step 23.13.
>
> Your Jenkinsfile syntax is 100% compatible — CloudBees runs standard Jenkins pipelines. The difference is the governance wrapper around it.

> This is a fresh Phase 3 environment. Follow the abbreviated install below, then apply your CloudBees CI trial WAR (or install the plugin stack) as you did in Phase 2.

**Install Java 17:**

```bash
sudo dnf install -y java-17-openjdk java-17-openjdk-devel
java -version
# Expected: openjdk version "17.x.x"
```

**Add Jenkins repository and install:**

```bash
sudo wget -O /etc/yum.repos.d/jenkins.repo \
  https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo dnf install -y jenkins
```

**Enable and start Jenkins:**

```bash
sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins
# Expected: Active: active (running)
```

> **Federal Reality Check: SELinux**
>
> Oracle Linux 9 ships with SELinux in enforcing mode. If your service fails to start, check SELinux first:
> ```bash
> # Check if SELinux is blocking your service
> sudo ausearch -m avc -ts recent
>
> # If you see denials for your app, create a custom policy:
> sudo ausearch -m avc -ts recent | audit2allow -M fedcompliance
> sudo semodule -i fedcompliance.pp
>
> # NEVER run setenforce 0 in a federal environment — that's an automatic audit failure
> getenforce  # Should always say "Enforcing"
> ```
>
> **Interview Insight:** "Is SELinux enforcing?" is the first question a federal auditor asks. The answer must always be "Yes, with custom policies for our applications."

**Open firewall port:**

```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

**Get the initial admin password:**

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
# Copy this value
```

**Verify:**

📍 **Browser**

```
http://<BASTION_PUBLIC_IP>:8080
```

> Expected: Jenkins unlock screen (paste password above) or Jenkins dashboard if already configured. Install suggested plugins and create an admin user if prompted.

> **OCI Security List:** Port 8080 must be open in the Public Subnet Ingress rules. If set up in Phase 18, it is already open. Verify: OCI Console → Networking → VCN → Security Lists → Public Subnet.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `sudo dnf install -y java-17-openjdk` | Installs Java 17 (Jenkins requires Java 11+) |
| `sudo systemctl enable jenkins` | Configures Jenkins to start on boot |
| `sudo systemctl start jenkins` | Starts the Jenkins service immediately |
| `sudo cat /var/lib/jenkins/secrets/initialAdminPassword` | Prints the one-time unlock password |
| `sudo firewall-cmd --permanent --add-port=8080/tcp` | Opens Jenkins port in Oracle Linux firewalld |

</em></sub>

---

### Step 23.2 — Install Trivy (Container Security Scanner)

📍 **Bastion Terminal**

> **🧠 ELI5 — Trivy:** Imagine you ordered a sandwich and before the deli hands it to you, a food inspector scans every ingredient for contamination. Trivy does that for container images. Before you deploy your Docker image to Kubernetes, Trivy scans every package inside it — the OS packages, the Python libraries, everything — against a database of known vulnerabilities (CVEs). If it finds a `CRITICAL` severity vulnerability, the pipeline stops. You cannot deploy contaminated software. This is how professional teams catch issues like Log4Shell before they ever reach a server.

**Add the Trivy repository:**

```bash
cat << 'EOF' | sudo tee /etc/yum.repos.d/trivy.repo
[trivy]
name=Trivy repository
baseurl=https://aquasecurity.github.io/trivy-repo/rpm/releases/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://aquasecurity.github.io/trivy-repo/rpm/public.key
EOF
```

**Install Trivy:**

```bash
sudo dnf install -y trivy
trivy --version
# Expected: Version: 0.5x.x (current stable)
```

**Download the CVE database and run a test scan:**

```bash
# First run downloads the vulnerability DB (~100 MB) — takes 1-2 minutes
trivy image --severity CRITICAL,HIGH python:3.11-slim
# Expected: table showing CVE findings, or "No Vulnerabilities Found"
# The database is cached at ~/.cache/trivy/db/ for subsequent runs
```

> **Why `--severity CRITICAL,HIGH`?** In a pipeline you want to fail fast on the most dangerous vulnerabilities. CRITICAL and HIGH represent known exploits and high-impact weaknesses. MEDIUM and LOW generate reports but typically do not block deployment — they go into a remediation backlog. Federal security policy (referencing NIST SP 800-190, Container Security Guide) commonly sets the pipeline-blocking threshold at CRITICAL.

**Verify:**

```bash
trivy --version
# Expected: Version: 0.5x.x

ls ~/.cache/trivy/db/
# Expected: trivy.db present (CVE database downloaded and cached)
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `trivy image` | `--severity CRITICAL,HIGH` | Scans a container image, reporting only CRITICAL and HIGH CVEs |
| `trivy image` | `--exit-code 1` | Returns non-zero exit code on findings — used in pipeline to fail the build |
| `trivy image` | `--format json` | Outputs results as JSON for archiving as evidence |
| `trivy image` | `--output <file>` | Writes results to a file instead of stdout |

</em></sub>

---

### Step 23.3 — Install Syft (SBOM Generator)

📍 **Bastion Terminal**

> **🧠 ELI5 — SBOM (Software Bill of Materials):** When you buy a packaged food product, the label lists every ingredient. A Software Bill of Materials does the same thing for software — it lists every library, package, and component inside your application and its container image. Why does this matter? In 2021, Log4Shell showed that organizations had no idea which of their systems contained the vulnerable Log4j library. Executive Order 14028 (signed by President Biden, May 2021) now requires that all software provided to the federal government must include an SBOM — so agencies can immediately search "do we have Log4j 2.14?" and get a definitive answer.

> **🧠 ELI5 — Syft:** Syft is the tool that generates SBOMs. Point it at a container image, and it crawls every installed package, language library, and dependency, then outputs a structured document listing all of them with names, versions, and licenses. Think of it as the automated ingredient label writer.

> **🧠 ELI5 — SPDX Format:** SPDX (Software Package Data Exchange) is an open standard for SBOMs — a universal ingredient label format that any compliance tool can read. It is an ISO standard (ISO/IEC 5962:2021). The federal government prefers SPDX because it is vendor-neutral and machine-readable. When you generate `sbom.spdx.json`, any security scanner or compliance dashboard can ingest it and search for specific packages. CycloneDX is the other accepted format — both satisfy EO 14028.

**Install Syft:**

```bash
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh \
  | sudo sh -s -- -b /usr/local/bin
syft --version
# Expected: syft 1.x.x
```

**Run a test SBOM generation:**

```bash
syft python:3.11-slim -o spdx-json > /tmp/test-sbom.spdx.json
# Takes 30-60 seconds as Syft pulls and inspects the image

python3 -c "
import json
with open('/tmp/test-sbom.spdx.json') as f:
    sbom = json.load(f)
print('SPDX version:', sbom.get('spdxVersion'))
print('Package count:', len(sbom.get('packages', [])))
"
# Expected:
# SPDX version: SPDX-2.3
# Package count: 80-200 (varies by image)
```

> **💼 Interview Insight — SBOM and EO 14028:** Executive Order 14028 Section 4(e) requires vendors providing software to the federal government to include SBOMs in machine-readable format. The two accepted formats are SPDX (ISO/IEC 5962:2021) and CycloneDX. NIST SP 800-218 (Secure Software Development Framework) provides the implementation guidance. A strong interview answer: "We generate SBOMs with every build using Syft, store them as Jenkins build artifacts indexed by build number and Git commit SHA, and maintain them in object storage for the retention period required by the contract. If a new CVE is disclosed — like Log4Shell — we query our SBOM archive to immediately identify every deployed container version that contains the affected package version, down to the specific commit hash." This answer demonstrates direct EO 14028 compliance awareness, specific tooling knowledge, and practical incident response application. Most candidates have never heard of SBOMs. Knowing this distinguishes you as someone who has actually worked on federal software delivery.

**Verify:**

```bash
syft --version
# Expected: syft 1.x.x

ls -lh /tmp/test-sbom.spdx.json
# Expected: file exists, size > 100KB
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `curl -sSfL .../install.sh \| sudo sh -s -- -b /usr/local/bin` | Downloads and installs Syft binary to `/usr/local/bin` |
| `syft <image> -o spdx-json` | Generates SBOM in SPDX JSON format for a container image |
| `syft <image> -o cyclonedx-json` | Alternative: generates SBOM in CycloneDX format (also accepted by EO 14028) |
| `syft <directory> -o spdx-json` | Can also scan a local source code directory instead of a container image |

</em></sub>

---

### Step 23.4 — Configure Jenkins Credentials

📍 **Browser → Jenkins UI**

> **🧠 ELI5 — Pipeline Credentials Management:** Your pipeline needs to authenticate to four systems: OCI (to push Docker images to OCIR), Kubernetes (to deploy with kubectl), SSH (for Ansible), and OCI CLI (for Terraform). You cannot hard-code passwords or keys in the Jenkinsfile — anyone who reads your git repository would see them, and they would appear in build logs. Jenkins has a built-in **Credentials Store** that encrypts secrets and makes them available to pipelines by reference ID only. The pipeline says "give me the credential named `ocir-credentials`" — Jenkins injects it as an environment variable or temporary file. The actual value never appears in the Jenkinsfile or build logs.

Navigate to: **Jenkins → Manage Jenkins → Credentials → System → Global credentials (unrestricted) → Add Credentials**

Add the following five credentials one at a time:

---

**Credential 1 — OCIR Docker Login (Username + Password)**

| Field | Value |
|-------|-------|
| Kind | Username with password |
| Username | `<tenancy_namespace>/oracleidentitycloudservice/<your_email>` |
| Password | Your OCI Auth Token (not your console password — see note) |
| ID | `ocir-credentials` |
| Description | OCIR container registry login for Docker push |

> **How to generate an OCI Auth Token:** OCI Console → top-right profile icon → My Profile → Auth Tokens → Generate Token → copy immediately. This token is displayed only once. It is the password for Docker login to OCIR.

---

**Credential 2 — kubeconfig for k3s (Secret File)**

| Field | Value |
|-------|-------|
| Kind | Secret file |
| File | Upload your kubeconfig file (instructions below) |
| ID | `k3s-kubeconfig` |
| Description | kubeconfig for k3s cluster kubectl access from Jenkins pipeline |

> **How to get the kubeconfig from k3s:** On your k3s server node, run `sudo cat /etc/rancher/k3s/k3s.yaml`. Copy the output. Replace the `server: https://127.0.0.1:6443` line with `server: https://<k3s_private_ip>:6443` (use the actual private IP of your k3s node). Save to a file and upload it here. The pipeline writes this file to a temp path and sets `KUBECONFIG` to point to it.

---

**Credential 3 — SSH Private Key for Ansible (SSH Username with Private Key)**

| Field | Value |
|-------|-------|
| Kind | SSH Username with private key |
| Username | `opc` |
| Private Key | Paste the full contents of your OCI instance SSH private key |
| ID | `bastion-ssh-key` |
| Description | SSH key for Ansible to connect to OCI VM instances |

---

**Credential 4 — OCI CLI Config (Secret File)**

| Field | Value |
|-------|-------|
| Kind | Secret file |
| File | Upload `~/.oci/config` from your bastion VM |
| ID | `oci-cli-config` |
| Description | OCI CLI config file for Terraform and OCI CLI commands in pipeline |

---

**Credential 5 — OCI Vault OCID (Secret Text)**

| Field | Value |
|-------|-------|
| Kind | Secret text |
| Secret | The OCID of your OCI Vault from Day 1 (format: `ocid1.vault.oc1...`) |
| ID | `oci-vault-ocid` |
| Description | OCI Vault OCID for runtime secret retrieval |

---

**Verify all five credentials are registered:**

📍 **Browser**

```
Jenkins → Manage Jenkins → Credentials → System → Global credentials (unrestricted)
```

> Expected: five rows with IDs `ocir-credentials`, `k3s-kubeconfig`, `bastion-ssh-key`, `oci-cli-config`, `oci-vault-ocid`. The actual secret values are masked — you only see IDs and descriptions.

> **💼 Interview Insight — Pipeline Security in Federal Environments:** When asked "how do you handle secrets in CI/CD pipelines?", a weak answer is "environment variables." A strong answer: "We store secrets in Jenkins Credentials Store — they are encrypted at rest using Jenkins's built-in AES-256 encryption, and referenced in the Jenkinsfile by ID only. The values are automatically masked in build logs. For higher-assurance environments we integrate with an external vault — HashiCorp Vault or OCI Vault — so secrets are fetched at pipeline runtime via authenticated API calls, used for the duration of the stage, and then discarded. Jenkins stores nothing. The audit trail records which pipeline, build number, and user triggered the credential access." This maps directly to NIST 800-53 IA-5 (Authenticator Management), SC-28 (Protection of Information at Rest), and AU-2 (Audit Events).

---

### Step 23.5 — Create the K8s Raw Manifests (Returning Concept — Abbreviated)

📍 **Bastion Terminal** then 📍 **Editor**

> K8s manifests were introduced in Phase 2. You built Deployment, Service, and ConfigMap YAML by hand. Same structure here. What is new is that these files are applied by the **pipeline** (Stage 8) rather than by your hands at the terminal. The YAML pattern is returning — explanation is abbreviated — but read the inline comments for anything specific to this pipeline integration.

**Create the directory:**

```bash
mkdir -p ~/fedcompliance/k8s
```

**Create `k8s/namespace.yaml`:**

```yaml
# k8s/namespace.yaml
# Creates the fedcompliance namespace to isolate all Phase 3 resources.
# Applied first by the pipeline — all other resources reference this namespace.
apiVersion: v1
kind: Namespace
metadata:
  name: fedcompliance
  labels:
    app: fedcompliance
    environment: lab
    phase: "3"
```

**Create `k8s/configmap.yaml`:**

```yaml
# k8s/configmap.yaml
# Non-sensitive configuration — injected as environment variables into the pod.
# Sensitive values (DB password, API keys) come from OCI Vault at runtime. Never here.
apiVersion: v1
kind: ConfigMap
metadata:
  name: fedcompliance-config
  namespace: fedcompliance
data:
  APP_ENV: "production"
  APP_PORT: "8000"
  LOG_LEVEL: "INFO"
  COMPLIANCE_FRAMEWORK: "NIST-800-53"
  API_VERSION: "v1"
```

**Create `k8s/deployment.yaml`:**

```yaml
# k8s/deployment.yaml
# Defines desired state: 2 replicas of FedCompliance, always running.
# IMAGE_TAG is a placeholder — the pipeline replaces it with the Git commit SHA
# using: sed -i 's|IMAGE_TAG|<actual_sha>|g' k8s/deployment.yaml
# IMPORTANT: Replace <REGION> and <NAMESPACE> with your actual values before committing.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fedcompliance
  namespace: fedcompliance
  labels:
    app: fedcompliance
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fedcompliance
  template:
    metadata:
      labels:
        app: fedcompliance
    spec:
      # Pull secret lets k3s authenticate to your private OCIR repository
      imagePullSecrets:
        - name: ocir-pull-secret
      containers:
        - name: fedcompliance
          # IMAGE_TAG replaced by pipeline Stage 8 with real Git commit SHA
          image: <REGION>.ocir.io/<NAMESPACE>/fedcompliance:IMAGE_TAG
          ports:
            - containerPort: 8000
          # All keys from the ConfigMap become environment variables in the pod
          envFrom:
            - configMapRef:
                name: fedcompliance-config
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"    # Hard limit — pod is OOM-killed if exceeded
              cpu: "250m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
```

> **Why `IMAGE_TAG` as a string placeholder?** In Stage 8 the pipeline runs `sed -i 's|IMAGE_TAG|<sha>|g' k8s/deployment.yaml` to substitute the real Git commit SHA before running `kubectl apply`. This is the standard raw-manifest approach to image versioning — no templating engine, just string substitution. Day 3 replaces this pattern with Helm's `values.yaml` image tag field, which is purpose-built for this use case and eliminates the need to restore the placeholder between pipeline runs.

> ⚠️ **Important:** Replace `<REGION>` with your OCI region (e.g., `us-ashburn-1`) and `<NAMESPACE>` with your tenancy namespace before committing to git.

**Create `k8s/service.yaml`:**

```yaml
# k8s/service.yaml
# Exposes FedCompliance pods on NodePort 30080.
# NodePort makes the service reachable at <any_node_ip>:30080 from within the VCN.
# The bastion VM (running Jenkins) uses this to reach the app for smoke tests.
apiVersion: v1
kind: Service
metadata:
  name: fedcompliance-svc
  namespace: fedcompliance
spec:
  type: NodePort
  selector:
    app: fedcompliance          # Routes traffic to pods matching this label
  ports:
    - protocol: TCP
      port: 8000                # Port within the cluster
      targetPort: 8000          # Port the container listens on
      nodePort: 30080           # Port exposed on the node IP (range: 30000-32767)
```

**Create the OCIR image pull secret on k3s:**

📍 **App Node Terminal** (k3s server)

```bash
# This secret lets k3s nodes authenticate to OCIR to pull your private image.
# Replace placeholders with your actual values.
kubectl create secret docker-registry ocir-pull-secret \
  --docker-server=<REGION>.ocir.io \
  --docker-username='<TENANCY_NAMESPACE>/oracleidentitycloudservice/<YOUR_EMAIL>' \
  --docker-password='<YOUR_OCI_AUTH_TOKEN>' \
  --namespace=fedcompliance \
  --dry-run=client -o yaml | kubectl apply -f -
# --dry-run=client -o yaml | kubectl apply -f - makes this idempotent
# (succeeds even if the secret already exists)
```

**Verify manifest files:**

📍 **Bastion Terminal**

```bash
ls -la ~/fedcompliance/k8s/
# Expected: namespace.yaml  configmap.yaml  deployment.yaml  service.yaml

# Quick YAML syntax check before the pipeline runs
for f in ~/fedcompliance/k8s/*.yaml; do
  python3 -c "import yaml, sys; yaml.safe_load(open('$f'))" \
    && echo "$f — OK" \
    || echo "$f — SYNTAX ERROR"
done
# Expected: four lines, each ending in OK
```

> **Why check YAML syntax with Python before committing?** YAML is whitespace-sensitive. A single indentation error causes `kubectl apply` to fail with a cryptic message. Catching it here saves a failed pipeline run and the time to diagnose it.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `kubectl create secret docker-registry` | Creates an image pull secret for authenticating to a private registry |
| `--dry-run=client -o yaml \| kubectl apply -f -` | Generates the manifest and applies it — idempotent, no error if secret exists |
| `python3 -c "import yaml; yaml.safe_load(open(...))"` | Validates YAML syntax without running kubectl |

</em></sub>

---

### Step 23.6 — Build the Jenkinsfile (NEW CONCEPT — Multi-Stage Pipeline with Approval Gate)

📍 **Editor** (build by hand — section by section)

> **🧠 ELI5 — Jenkinsfile:** A Jenkinsfile is a recipe card that tells Jenkins exactly how to handle your code. It lives in your git repository (pipeline-as-code), so the pipeline definition is version-controlled just like your application. Every time Jenkins runs the pipeline, it reads this file and executes each stage in order. If any stage fails, the pipeline stops. This makes your entire delivery process reproducible, reviewable, and auditable — anyone can read the Jenkinsfile to understand exactly what happens to code before it reaches production.

> **🧠 ELI5 — Declarative Pipeline Syntax:** Jenkinsfiles can be written in two styles: Scripted (raw Groovy code) or Declarative (structured with required blocks). Declarative uses a defined skeleton — `pipeline { agent {} stages {} post {} }` — that Jenkins validates before running. Think of it like filling out a structured government form versus writing a freehand letter. Declarative is harder to break accidentally, easier to read, and the style Jenkins recommends for new pipelines.

> **🧠 ELI5 — Multi-Stage Pipeline:** Each `stage` in a Jenkinsfile is a labeled checkpoint. Jenkins displays each stage as a column in its Stage View UI — green means passed, red means failed, blue means running. When Stage 3 (Trivy Scan) turns red, you know immediately that the container security check failed without digging through logs. Multi-stage pipelines make the health of your delivery process visible at a glance.

> **🧠 ELI5 — The Approval Gate (`input` step):** The `input` step pauses the pipeline completely and waits for a human to click "Proceed" in the Jenkins UI. Think of it like a checkpoint on a military base — the vehicle stops, a guard verifies credentials, then waves it through. The pipeline releases its build executor while waiting (so other builds can use it), and holds until someone approves or the timeout expires. This is how automated pipelines implement human change-management oversight — all pre-checks run automatically, but a human makes the final deployment decision.

**Create the Jenkinsfile:**

```bash
touch ~/fedcompliance/Jenkinsfile
```

Open `~/fedcompliance/Jenkinsfile` in your editor and build it section by section:

---

**Build `Jenkinsfile` — Section 1 of 11: Pipeline Declaration and Environment**

> The outer shell of every Declarative Jenkinsfile. The `environment` block defines variables available to all stages. Credentials are referenced by ID — the actual values never appear here.

```groovy
// Jenkinsfile
// FedCompliance CI/CD Pipeline — Phase 3 Day 2
// 9 stages: Checkout → TF Validate → Trivy Scan → SBOM Generation →
//           Ansible Lint → Approval Gate → Docker Build/Push →
//           kubectl apply → Smoke Test

pipeline {
  // 'any' = run on any available Jenkins executor
  // Production: agent { label 'oracle-linux-8' } to target specific node types
  agent any

  environment {
    // OCI region — used in OCIR image URL
    OCI_REGION      = 'us-ashburn-1'

    // OCI tenancy namespace — find it: OCI Console → Tenancy Details → Object Storage Namespace
    OCI_NAMESPACE   = '<YOUR_TENANCY_NAMESPACE>'

    // Full OCIR image path without tag
    IMAGE_NAME      = "${OCI_REGION}.ocir.io/${OCI_NAMESPACE}/fedcompliance"

    // Image tag = first 7 characters of the Git commit SHA
    // GIT_COMMIT is a Jenkins built-in variable set during the Checkout stage
    // ?.take(7) = safe Groovy navigation: if GIT_COMMIT is null, fall back to 'latest'
    IMAGE_TAG       = "${env.GIT_COMMIT?.take(7) ?: 'latest'}"

    // Temp path for the kubeconfig secret file — deleted in post.always
    KUBECONFIG_PATH = '/tmp/k3s-kubeconfig'

    // SBOM filename includes build number so each run gets a unique artifact name
    SBOM_FILE       = "fedcompliance-sbom-${env.BUILD_NUMBER}.spdx.json"
  }
```

---

**Build `Jenkinsfile` — Section 2 of 11: Stage 1 — Checkout**

> Checkout pulls the latest code and sets `GIT_COMMIT`. Print the SHA to the build log — this is the audit trail entry that links every build artifact back to the exact code version.

```groovy
  stages {

    // ─────────────────────────────────────────────────────────────
    // STAGE 1: CHECKOUT
    // Pulls code from the SCM configured in the Jenkins job.
    // Sets GIT_COMMIT, GIT_BRANCH (used in IMAGE_TAG and approval summary).
    // ─────────────────────────────────────────────────────────────
    stage('Checkout') {
      steps {
        checkout scm
        sh 'echo "Building commit: ${GIT_COMMIT}"'
        sh 'echo "Branch: ${GIT_BRANCH}"'
        sh 'echo "Build number: ${BUILD_NUMBER}"'
      }
    }
```

---

**Build `Jenkinsfile` — Section 3 of 11: Stage 2 — Terraform Validate + Plan**

> Validates Terraform syntax and generates a plan without applying. Catches IaC configuration errors before any infrastructure is touched. The plan file is archived as a build artifact for audit review.

```groovy
    // ─────────────────────────────────────────────────────────────
    // STAGE 2: TERRAFORM VALIDATE + PLAN
    // Catches infrastructure config errors without making any changes.
    // Plan file is archived — auditors can review what TF would change.
    // ─────────────────────────────────────────────────────────────
    stage('Terraform Validate + Plan') {
      steps {
        dir('terraform') {
          sh 'terraform init -input=false'
          sh 'terraform validate'
          // || true: prevents plan from blocking build if remote state is unavailable
          // Remove || true in production where state backend is reliable
          sh 'terraform plan -out=tfplan -input=false || true'
        }
      }
      post {
        always {
          archiveArtifacts artifacts: 'terraform/tfplan', allowEmptyArchive: true
        }
      }
    }
```

---

**Build `Jenkinsfile` — Section 4 of 11: Stage 3 — Trivy Security Scan**

> Trivy scans the container image for CVEs. `--exit-code 1` makes Trivy return a non-zero exit if findings exist — this fails the stage and stops the pipeline. The image is never pushed to OCIR if this stage fails.

```groovy
    // ─────────────────────────────────────────────────────────────
    // STAGE 3: TRIVY CONTAINER SECURITY SCAN
    // Scans the Docker image BEFORE pushing to OCIR.
    // --exit-code 1 fails the build on CRITICAL or HIGH CVEs.
    // Image is NEVER pushed if this stage fails.
    // ─────────────────────────────────────────────────────────────
    stage('Trivy Security Scan') {
      steps {
        script {
          // Build image with temp tag for scanning
          // Real tag (Git SHA) is applied in Stage 7 after approval
          sh "docker build -t ${IMAGE_NAME}:scan-temp ."

          // Scan the temp image
          // --exit-code 1  : non-zero exit on findings (fails the stage)
          // --severity     : only CRITICAL and HIGH block the pipeline
          // --format json  : machine-readable output for archiving
          // --output       : write to file for artifact archiving
          sh """
            trivy image \
              --exit-code 1 \
              --severity CRITICAL,HIGH \
              --format json \
              --output trivy-report.json \
              ${IMAGE_NAME}:scan-temp
          """
        }
      }
      post {
        always {
          // Archive report regardless of pass/fail
          // Federal auditors need the report even when the build is blocked
          archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
        }
        failure {
          echo '================================================'
          echo 'SECURITY GATE BLOCKED: CRITICAL or HIGH CVEs found by Trivy'
          echo 'Required action: Update base image or patch vulnerable packages'
          echo 'Review trivy-report.json in Build Artifacts for CVE details'
          echo '================================================'
        }
      }
    }
```

> **Why scan before pushing?** If you scan after pushing, you have already uploaded a vulnerable image to the registry. In a federal environment the registry may trigger automated compliance alerts on vulnerable image uploads, creating an incident before you can remediate. Scan before pushing — only clean images enter OCIR.

---

**Build `Jenkinsfile` — Section 5 of 11: Stage 4 — Syft SBOM Generation**

> Syft generates the SBOM only after Trivy passes. The SBOM is archived as a build artifact. Together with the Trivy report, they form the security evidence package for this build.

```groovy
    // ─────────────────────────────────────────────────────────────
    // STAGE 4: SBOM GENERATION (EO 14028 COMPLIANCE)
    // Generates Software Bill of Materials in SPDX JSON format.
    // Runs only after Trivy passes — clean image gets inventoried.
    // Archived per build for supply chain audit trail.
    // ─────────────────────────────────────────────────────────────
    stage('SBOM Generation') {
      steps {
        script {
          echo "Generating SBOM for ${IMAGE_NAME}:scan-temp"

          // syft <image> -o spdx-json outputs SPDX JSON to stdout
          sh "syft ${IMAGE_NAME}:scan-temp -o spdx-json > ${SBOM_FILE}"

          // Print package count to build log for visibility
          sh """
            PKGS=\$(python3 -c "
import json, sys
d = json.load(open('${SBOM_FILE}'))
print(len(d.get('packages', [])))
")
            echo "SBOM generated: ${SBOM_FILE}"
            echo "Packages inventoried: \$PKGS"
          """
        }
      }
      post {
        always {
          archiveArtifacts artifacts: "${SBOM_FILE}", allowEmptyArchive: true
          echo "SBOM archived: ${SBOM_FILE} (build #${BUILD_NUMBER})"
        }
      }
    }
```

---

**Build `Jenkinsfile` — Section 6 of 11: Stage 5 — Ansible Lint**

> Ansible lint checks playbooks for deprecated syntax, missing task names, and best-practice violations — before they run against real infrastructure.

```groovy
    // ─────────────────────────────────────────────────────────────
    // STAGE 5: ANSIBLE LINT
    // Validates Ansible playbooks for syntax errors and best practices.
    // || true: warnings don't block the build in this lab environment.
    // Remove || true in production to enforce lint compliance.
    // ─────────────────────────────────────────────────────────────
    stage('Ansible Lint') {
      steps {
        script {
          sh 'ansible-lint --version || python3 -m pip install ansible-lint'
          sh 'ansible-lint -p ansible/*.yml || true'
        }
      }
    }
```

---

**Build `Jenkinsfile` — Section 7 of 11: Stage 6 — Manual Approval Gate**

> The pipeline pauses here and waits for human approval. A `timeout` wrapper auto-aborts the build if no decision is made within 2 hours — preventing a stale pipeline from sitting open indefinitely.

```groovy
    // ─────────────────────────────────────────────────────────────
    // STAGE 6: MANUAL APPROVAL GATE
    // Pipeline PAUSES here — waits for authorized human approval.
    // Implements federal change management gate (NIST 800-53 CM-3).
    // Auto-aborts after 2 hours if no decision is made.
    // ─────────────────────────────────────────────────────────────
    stage('Approval Gate') {
      steps {
        script {
          // Print deployment summary for the approver to review in the build log
          echo '================================================'
          echo 'DEPLOYMENT SUMMARY — AWAITING APPROVAL'
          echo '================================================'
          echo "Image:    ${IMAGE_NAME}:${IMAGE_TAG}"
          echo "Commit:   ${env.GIT_COMMIT}"
          echo "Branch:   ${env.GIT_BRANCH}"
          echo "Build:    #${env.BUILD_NUMBER}"
          echo "Trivy:    PASSED (no CRITICAL/HIGH CVEs found)"
          echo "SBOM:     Generated — ${SBOM_FILE}"
          echo "Target:   k3s cluster / namespace: fedcompliance"
          echo "Port:     NodePort 30080"
          echo '================================================'
          echo 'Review build artifacts (trivy-report.json, SBOM) before approving.'
        }

        // timeout wraps input — build auto-aborts if not approved within 2 hours
        timeout(time: 2, unit: 'HOURS') {
          input(
            message: "Deploy ${IMAGE_NAME}:${IMAGE_TAG} to k3s cluster?",
            ok: 'Approve Deployment',
            // submitter restricts who can approve — change to your Jenkins username
            // Remove submitter line to allow any authenticated Jenkins user to approve
            submitter: 'admin',
            parameters: [
              string(
                name: 'CHANGE_TICKET',
                defaultValue: '',
                description: 'Optional: change management ticket number for audit trail'
              )
            ]
          )
        }

        echo 'Deployment APPROVED. Proceeding to build and deploy.'
      }
    }
```

> **💼 Interview Insight — Approval Gates and Federal Change Management:** Federal agencies follow change management frameworks (ITIL, agency-specific Change Advisory Board processes). Production deployments require documented human approval. A strong interview answer: "We implement an `input` step in Jenkins that pauses the pipeline after all automated checks — Trivy scan, SBOM generation, Ansible lint — pass. The pipeline prints a deployment summary showing the exact image tag, Git commit SHA, and scan results. An authorized approver reviews the summary and artifacts in the Jenkins UI, optionally enters a change ticket number, and clicks Approve. Jenkins records the approver's username and the exact approval timestamp in the build log. The 2-hour timeout means no approval window stays open indefinitely — auto-abort prevents stale deployments from accidentally proceeding days later." Then connect to the framework: "This satisfies NIST 800-53 CM-3 (Configuration Change Control) — the control that requires documented authorization for changes to information systems. The Jenkins build log is the CM-3 audit record." Most candidates can describe automated pipelines. Knowing how and why to add a human gate — and being able to cite the specific NIST control it satisfies — is what distinguishes a federal-environment engineer.

---

**Build `Jenkinsfile` — Section 8 of 11: Stage 7 — Docker Build + Push to OCIR**

> With approval granted, the pipeline builds the final tagged image and pushes it to OCIR. Credentials are injected by `withCredentials` — the username and password never appear in the Jenkinsfile.

```groovy
    // ─────────────────────────────────────────────────────────────
    // STAGE 7: DOCKER BUILD + PUSH TO OCIR
    // Builds with the real Git SHA tag and pushes to OCIR.
    // Runs only AFTER: Trivy passed AND human approval granted.
    // ─────────────────────────────────────────────────────────────
    stage('Build + Push to OCIR') {
      steps {
        // withCredentials injects DOCKER_CREDS_USR and DOCKER_CREDS_PSW
        // Variables exist only within this block — values are masked in logs
        withCredentials([
          usernamePassword(
            credentialsId: 'ocir-credentials',
            usernameVariable: 'DOCKER_CREDS_USR',
            passwordVariable: 'DOCKER_CREDS_PSW'
          )
        ]) {
          script {
            // Log in to OCIR
            // --password-stdin: reads from pipe — never exposes password in process list
            sh """
              echo "${DOCKER_CREDS_PSW}" | docker login \
                ${OCI_REGION}.ocir.io \
                -u "${DOCKER_CREDS_USR}" \
                --password-stdin
            """

            // Build with the real image tag (Git commit SHA)
            sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."

            // Tag as latest for convenience
            sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest"

            // Push both tags
            sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
            sh "docker push ${IMAGE_NAME}:latest"

            // Remove temp scan image — no longer needed
            sh "docker rmi ${IMAGE_NAME}:scan-temp || true"

            echo "Successfully pushed: ${IMAGE_NAME}:${IMAGE_TAG}"
          }
        }
      }
    }
```

> **Why `--password-stdin`?** Passing the password via stdin (pipe) prevents it from appearing in the process list (`ps aux`) or shell history. Jenkins also masks `DOCKER_CREDS_PSW` in build logs automatically, but using stdin adds a second layer of protection at the OS level.

---

**Build `Jenkinsfile` — Section 9 of 11: Stage 8 — kubectl apply (Raw Manifest Deploy)**

> This is the raw-manifest deployment. The pipeline writes the kubeconfig secret to a temp file, sets `KUBECONFIG`, substitutes the real image tag into the deployment manifest with `sed`, then applies all four manifests. After apply, it waits for the rollout to complete before proceeding to the smoke test.

```groovy
    // ─────────────────────────────────────────────────────────────
    // STAGE 8: kubectl apply — RAW MANIFEST DEPLOY TO k3s
    // Writes kubeconfig to temp path, substitutes IMAGE_TAG placeholder,
    // applies all k8s manifests, waits for rollout to complete.
    // Day 3 replaces this stage with Helm upgrade + ArgoCD sync.
    // ─────────────────────────────────────────────────────────────
    stage('Deploy to k3s') {
      steps {
        // withCredentials writes the kubeconfig secret file to a temp path
        // Jenkins sets KUBECONFIG_FILE to that temp path
        withCredentials([
          file(credentialsId: 'k3s-kubeconfig', variable: 'KUBECONFIG_FILE')
        ]) {
          script {
            // Copy to a stable path and lock down permissions
            sh "cp \${KUBECONFIG_FILE} ${KUBECONFIG_PATH}"
            sh "chmod 600 ${KUBECONFIG_PATH}"  // Note: chmod works on Linux Jenkins agents only

            // withEnv sets KUBECONFIG for all kubectl commands in this block
            withEnv(["KUBECONFIG=${KUBECONFIG_PATH}"]) {

              // Verify kubectl can reach the cluster before applying
              sh 'kubectl cluster-info'
              sh 'kubectl get nodes'

              // Replace IMAGE_TAG placeholder with the actual Git commit SHA
              // sed -i modifies the file in the Jenkins workspace (not the git repo)
              sh "sed -i 's|IMAGE_TAG|${IMAGE_TAG}|g' k8s/deployment.yaml"

              // Verify the substitution before applying
              sh "grep 'image:' k8s/deployment.yaml"
              // Expected: image: us-ashburn-1.ocir.io/myns/fedcompliance:a3f91c2

              // Apply manifests — namespace first (must exist before other resources)
              sh 'kubectl apply -f k8s/namespace.yaml'
              sh 'kubectl apply -f k8s/configmap.yaml'
              sh 'kubectl apply -f k8s/deployment.yaml'
              sh 'kubectl apply -f k8s/service.yaml'

              // Wait for rollout to complete
              // --timeout=120s: fail stage if rollout takes more than 2 minutes
              sh 'kubectl rollout status deployment/fedcompliance \
                    -n fedcompliance --timeout=120s'

              // Print current state for build log and audit trail
              sh 'kubectl get pods -n fedcompliance'
              sh 'kubectl get svc  -n fedcompliance'
            }
          }
        }
      }
      post {
        always {
          // Delete kubeconfig temp file — it contains cluster admin credentials
          sh "rm -f ${KUBECONFIG_PATH}"
        }
      }
    }
```

> **Why `rm -f ${KUBECONFIG_PATH}` in `post.always`?** The kubeconfig file grants administrative access to your Kubernetes cluster. Leaving it on disk after the build — even on a trusted server — is a security risk. `post.always` runs whether the stage passed or failed, so the file is removed in all outcomes.

---

**Build `Jenkinsfile` — Section 10 of 11: Stage 9 — Smoke Test**

> The smoke test is final proof that the deployment worked. `kubectl rollout status` confirmed pods became ready — the smoke test confirms the application inside the pods is responding correctly on the expected endpoint.

```groovy
    // ─────────────────────────────────────────────────────────────
    // STAGE 9: SMOKE TEST
    // Hits /health on the deployed app via NodePort 30080.
    // Proves the application is running, not just that pods are scheduled.
    // ─────────────────────────────────────────────────────────────
    stage('Smoke Test') {
      steps {
        script {
          // Replace <K3S_SERVER_PRIVATE_IP> with the actual private IP of your k3s server node
          // Find it with: terraform output -raw k3s_node1_private_ip
          // The bastion VM can reach k3s nodes via the VCN private subnet
          def K3S_NODE_IP = '<K3S_SERVER_PRIVATE_IP>'

          // Give pods a moment to finish startup before hitting them
          sleep(time: 15, unit: 'SECONDS')

          // -s: silent (suppress progress bar)
          // -f: fail on HTTP 4xx/5xx (non-zero exit = stage failure)
          sh """
            curl -sf http://${K3S_NODE_IP}:30080/health \
              || (echo 'SMOKE TEST FAILED: /health did not return HTTP 200' && exit 1)
          """

          echo "Smoke test PASSED — FedCompliance is responding on k3s"
          echo "Deployed: ${IMAGE_NAME}:${IMAGE_TAG}"
          echo "Access URL (from bastion): http://${K3S_NODE_IP}:30080"
        }
      }
    }

  } // end stages
```

---

**Build `Jenkinsfile` — Section 11 of 11: Post Block**

> The `post` block runs after all stages complete, regardless of outcome. Handles notifications and cleanup.

```groovy
  // ─────────────────────────────────────────────────────────────
  // POST BLOCK
  // Runs after all stages — pass, fail, or abort.
  // ─────────────────────────────────────────────────────────────
  post {
    success {
      echo '================================================'
      echo 'PIPELINE SUCCEEDED'
      echo "Image:   ${IMAGE_NAME}:${IMAGE_TAG}"
      echo "Trivy:   PASSED — no CRITICAL/HIGH CVEs"
      echo "SBOM:    ${SBOM_FILE} archived"
      echo "Deploy:  FedCompliance running on k3s (NodePort 30080)"
      echo '================================================'
    }
    failure {
      echo '================================================'
      echo 'PIPELINE FAILED'
      echo 'Check the red stage in Stage View for the failure reason.'
      echo 'Build artifacts: trivy-report.json and SBOM provide security context.'
      echo '================================================'
    }
    aborted {
      echo 'Pipeline ABORTED — approval gate timed out or manually stopped.'
    }
    always {
      // Clean up local Docker images to reclaim disk space on the build server
      sh "docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true"
      sh "docker rmi ${IMAGE_NAME}:latest || true"
      sh "docker rmi ${IMAGE_NAME}:scan-temp || true"
      // Belt-and-suspenders: ensure kubeconfig temp file is gone
      sh "rm -f ${KUBECONFIG_PATH} || true"
    }
  }

} // end pipeline
```

**Verify the complete Jenkinsfile:**

```bash
wc -l ~/fedcompliance/Jenkinsfile
# Expected: 220+ lines

grep -n "stage('" ~/fedcompliance/Jenkinsfile
# Expected: 9 lines, one per stage name

grep -n "withCredentials" ~/fedcompliance/Jenkinsfile
# Expected: 2 occurrences (Stage 7 OCIR login, Stage 8 kubeconfig)

grep -n "archiveArtifacts" ~/fedcompliance/Jenkinsfile
# Expected: 3 occurrences (tfplan, trivy-report.json, SBOM file)

grep -n "input(" ~/fedcompliance/Jenkinsfile
# Expected: 1 occurrence in the Approval Gate stage
```

> **🧠 Putting it together:** The Jenkinsfile is the single document that defines your entire delivery process. Code enters at Stage 1 (Checkout) and — if all nine gates pass — exits as a running container on k3s at Stage 9 (Smoke Test). Security (Trivy), compliance (Syft SBOM), quality (Ansible Lint), and governance (Approval Gate) are baked into the pipeline. Not bolted on. Not optional. This is what "shift-left security" and "security-by-design" mean in practice — enforcement at the pipeline level before software ever reaches infrastructure.

---

### Step 23.7 — Configure the Jenkins Pipeline Job

📍 **Browser → Jenkins UI**

> **🧠 ELI5 — Jenkins Pipeline Job:** A Jenkins job is the standing configuration that tells Jenkins where your code lives and which Jenkinsfile to run. Create it once. After that, Jenkins executes the Jenkinsfile on every Build Now click (or on webhook trigger from git). The job is the doorbell; the Jenkinsfile is the instruction manual that answers the door.

**Create a new Pipeline job:**

1. Jenkins home → **New Item**
2. Enter item name: `fedcompliance-pipeline`
3. Select type: **Pipeline** → click **OK**

**Configure the Pipeline section:**

- **Definition:** `Pipeline script from SCM`
- **SCM:** `Git`
- **Repository URL:** `<your-git-repo-url>`
- **Credentials:** Add git credentials if the repo is private
- **Branch Specifier:** `*/main`
- **Script Path:** `Jenkinsfile`

Click **Save**.

**Verify:**

```
Jenkins → fedcompliance-pipeline → Configure → Pipeline section
```

> Expected: Definition = "Pipeline script from SCM", SCM = Git, Branch = `*/main`, Script Path = `Jenkinsfile`.

---

### Step 23.8 — Commit All Files and Trigger the First Pipeline Run

📍 **Bastion Terminal**

**Update the two placeholder values before committing:**

```bash
# 1. Update deployment.yaml — replace <REGION> and <NAMESPACE>
nano ~/fedcompliance/k8s/deployment.yaml
# Find:    image: <REGION>.ocir.io/<NAMESPACE>/fedcompliance:IMAGE_TAG
# Replace: image: us-ashburn-1.ocir.io/<YOUR_TENANCY_NAMESPACE>/fedcompliance:IMAGE_TAG

# 2. Update Jenkinsfile — replace OCI_NAMESPACE and K3S_SERVER_PRIVATE_IP
nano ~/fedcompliance/Jenkinsfile
# Find:    OCI_NAMESPACE = '<YOUR_TENANCY_NAMESPACE>'
# Replace with your actual namespace
# Find:    K3S_NODE_IP = '<K3S_SERVER_PRIVATE_IP>'
# Replace with your actual k3s server private IP
```

**Commit and push:**

```bash
cd ~/fedcompliance

git add Jenkinsfile k8s/
git status
# Expected: staged — Jenkinsfile, k8s/namespace.yaml, k8s/configmap.yaml,
#           k8s/deployment.yaml, k8s/service.yaml

git commit -m "phase-23: add multi-stage Jenkinsfile and raw k8s manifests

Jenkinsfile: 9-stage pipeline
  Stage 1: Checkout
  Stage 2: Terraform validate + plan (artifact: tfplan)
  Stage 3: Trivy scan CRITICAL/HIGH — blocks on findings (artifact: trivy-report.json)
  Stage 4: Syft SBOM generation SPDX JSON (artifact: fedcompliance-sbom-N.spdx.json)
  Stage 5: Ansible lint (warnings allowed, errors blocked)
  Stage 6: Manual approval gate — 2hr timeout, admin submitter
  Stage 7: Docker build + push to OCIR (Git SHA tag + latest)
  Stage 8: kubectl apply raw manifests to k3s namespace fedcompliance
  Stage 9: Smoke test curl /health NodePort 30080

k8s/: Namespace, ConfigMap, Deployment (2 replicas + resource limits + health probes),
      Service (NodePort 30080)
Credentials: 5 Jenkins credentials configured (ocir, kubeconfig, ssh, oci-cli, vault)"

git push origin main
```

**Trigger the first pipeline run:**

📍 **Browser**

```
Jenkins → fedcompliance-pipeline → Build Now
```

> A build entry appears in the Build History. Click the build number to open it. Click **Stage View** to watch stages execute in real time — each stage lights up as it runs.

---

### Step 23.9 — Walk Through the Approval Gate

📍 **Browser → Jenkins UI**

> Stages 1–5 run automatically (roughly 3–8 minutes depending on Trivy database download and Docker build time). The pipeline pauses at Stage 6 (Approval Gate). You will see a blue spinner on that stage — it is waiting.

**To approve:**

1. Click into the running build (`fedcompliance-pipeline → #1`)
2. In Stage View or Console Output, look for the approval dialog:
   ```
   Deploy us-ashburn-1.ocir.io/<YOUR_TENANCY_NAMESPACE>/fedcompliance:a3f91c2 to k3s cluster?
   [Approve Deployment] [Abort]
   ```
3. Before approving, review:
   - The deployment summary in the console (image tag, branch, commit, Trivy PASSED, SBOM file)
   - Click **Build Artifacts** → download and spot-check `trivy-report.json`
4. Optionally enter a change ticket number
5. Click **Approve Deployment**

> The pipeline resumes. Stage 7 (Docker Build + Push) starts immediately.

**Verify the approval was recorded:**

```
Build #1 → Console Output → search for "Deployment APPROVED"
```

> Expected: `Deployment APPROVED. Proceeding to build and deploy.`
> The log includes the Jenkins username and exact timestamp — this is the audit record.

**Watch Stages 7–9 complete:**

| Stage | Expected Duration | Success Indicator |
|-------|------------------|-------------------|
| Build + Push to OCIR | 2–5 min | "Successfully pushed: ...fedcompliance:a3f91c2" |
| Deploy to k3s | 1–2 min | "successfully rolled out" from rollout status |
| Smoke Test | ~30 sec | "Smoke test PASSED — FedCompliance is responding on k3s" |

---

### Step 23.10 — Verify the Deployment on k3s

📍 **App Node Terminal** (SSH to k3s server via bastion)

```bash
# Verify namespace was created by the pipeline
kubectl get namespace fedcompliance
# Expected: NAME            STATUS   AGE
#           fedcompliance   Active   Xm

# Verify both pods are Running
kubectl get pods -n fedcompliance
# Expected: two pods, STATUS=Running, RESTARTS=0

# Verify service and NodePort
kubectl get svc -n fedcompliance
# Expected: fedcompliance-svc   NodePort   10.x.x.x   <none>   8000:30080/TCP

# Confirm what image is actually running (should match the pipeline's Git SHA tag)
kubectl get deployment fedcompliance -n fedcompliance \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
# Expected: us-ashburn-1.ocir.io/<YOUR_TENANCY_NAMESPACE>/fedcompliance:a3f91c2
# (where a3f91c2 is the short SHA from the build)

# Check application logs — confirm clean startup
kubectl logs -n fedcompliance -l app=fedcompliance --tail=20
# Expected: Uvicorn running on port 8000, no ERROR or CRITICAL lines
```

**Verify the application responds from the bastion:**

📍 **Bastion Terminal**

```bash
K3S_IP=<k3s_server_private_ip>

# Health check
curl http://${K3S_IP}:30080/health
# Expected: {"status": "healthy", "version": "1.0.0"} (or similar)

# Confirm FastAPI is running (OpenAPI spec)
curl -s http://${K3S_IP}:30080/openapi.json | python3 -m json.tool | head -10
# Expected: OpenAPI spec JSON {"openapi": "3.x.x", "info": {...}}
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `kubectl get pods -n fedcompliance` | Shows pod status — both should be Running |
| `kubectl get svc -n fedcompliance` | Shows service type and NodePort assignment |
| `kubectl get deployment ... -o jsonpath=...` | Extracts the exact running image tag — confirms pipeline deployed the right SHA |
| `kubectl logs -n fedcompliance -l app=fedcompliance` | Streams logs from all pods matching the label selector |
| `kubectl rollout status deployment/fedcompliance -n fedcompliance` | Confirms the rollout completed — all replicas are updated and healthy |

</em></sub>

---

### Step 23.11 — Review the Build Artifacts (Security Evidence Package)

📍 **Browser → Jenkins UI**

> Every pipeline run produces a security evidence package. Review it now — this is what you would present to a federal auditor or security review board.

```
Jenkins → fedcompliance-pipeline → Build #1 → Build Artifacts
```

> Expected artifacts:
> - `trivy-report.json` — CVE scan results for this exact image version
> - `fedcompliance-sbom-1.spdx.json` — SBOM in SPDX JSON format
> - `terraform/tfplan` — Terraform plan from Stage 2

**Inspect the SBOM structure** — download and open `fedcompliance-sbom-1.spdx.json`:

```json
{
  "spdxVersion": "SPDX-2.3",
  "dataLicense": "CC0-1.0",
  "name": "...",
  "packages": [
    {
      "name": "python",
      "versionInfo": "3.11.x",
      "licenseConcluded": "PSF-2.0",
      ...
    }
  ]
}
```

Key SBOM fields to know for interviews:

| Field | Meaning |
|-------|---------|
| `spdxVersion` | SPDX-2.3 = current standard (ISO/IEC 5962:2021) |
| `dataLicense` | CC0-1.0 = the SBOM document itself is public domain |
| `packages[]` | Full inventory — every package with name, version, license |
| `licenseConcluded` | License for each package — critical for open-source compliance review |
| `externalRefs[]` | Links packages to known CVE records for cross-referencing with Trivy |

**Inspect the Trivy report** — download `trivy-report.json`:

```json
{
  "SchemaVersion": 2,
  "Results": [
    {
      "Target": "fedcompliance:scan-temp",
      "Type": "python-pkg",
      "Vulnerabilities": null
    }
  ]
}
```

> `Vulnerabilities: null` or empty array = the image passed the CRITICAL/HIGH gate. Any entries with `"Severity": "CRITICAL"` would have caused Stage 3 to fail before this artifact was even created (but the report is archived regardless, per `post.always`).

---

### Step 23.12 — Git Commit Final Phase 23 Work

📍 **Bastion Terminal**

```bash
cd ~/fedcompliance

# The sed in Stage 8 modified deployment.yaml in the Jenkins workspace,
# but if your git repo is on the same machine, check if the placeholder was changed:
grep "IMAGE_TAG\|image:" k8s/deployment.yaml
# If IMAGE_TAG is missing (replaced with a SHA), restore the placeholder:
git checkout k8s/deployment.yaml
grep "IMAGE_TAG" k8s/deployment.yaml
# Expected: image: us-ashburn-1.ocir.io/<YOUR_TENANCY_NAMESPACE>/fedcompliance:IMAGE_TAG

git status
# If deployment.yaml was restored, commit it:
git add k8s/deployment.yaml
git commit -m "phase-23: restore IMAGE_TAG placeholder in deployment.yaml

sed in Stage 8 replaces IMAGE_TAG in the Jenkins workspace, not the git repo.
Restoring placeholder so future pipeline runs have a string to substitute.
Day 3 (Helm) eliminates this sed pattern — values.yaml handles image tags cleanly."

git push origin main
```

> **Important:** The `sed -i` in Stage 8 modifies the file in Jenkins's build **workspace** — a temporary copy of your repo on the Jenkins server. It does not modify your actual git repository. The workspace is wiped on the next build checkout. However, if your git repository and Jenkins workspace share the same directory (common in single-VM lab setups), `sed -i` will modify the working tree. The `git checkout k8s/deployment.yaml` command restores it from git history.

---

### Step 23.13 — Advanced CloudBees CI Governance (1.5 hrs)

You migrated from open-source Jenkins to CloudBees CI in Phase 2 — you configured RBAC, CasC, and audit trails. Phase 3 goes deeper into the enterprise governance features that differentiate CloudBees from open-source Jenkins. These are the features that hiring managers ask about.

> **Returning concept:** RBAC, CasC, and audit trail were set up in Phase 2. This phase assumes they're already configured (Phase 3 starts from a fresh environment, so you'll do a speed-run of the Phase 2 CloudBees install first — same WAR replacement or plugin install, abbreviated). Focus here is on **advanced patterns**, not re-doing the basics.

**[BASTION TERMINAL]**

#### Speed-Run: CloudBees CI Setup (15 min, abbreviated)

Repeat the Phase 2 migration on your fresh Phase 3 environment. This is muscle memory — you've done it before.

```bash
# Install Java 17 + Jenkins (same as Phase 1/2)
sudo dnf install -y java-17-openjdk java-17-openjdk-devel
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo dnf install -y jenkins

# If using CloudBees CI trial (Path A from Phase 2):
# Replace WAR before first start
sudo cp /home/opc/cloudbees-core.war /usr/share/java/jenkins.war

# If using plugin stack (Path B from Phase 2):
# Start Jenkins, then install plugins (JCasC, Role Strategy, Audit Trail, Folder)

sudo systemctl enable --now jenkins
sudo firewall-cmd --permanent --add-port=8080/tcp && sudo firewall-cmd --reload

# Apply CasC config (copy from Phase 2 or git repo)
sudo mkdir -p /var/lib/jenkins/casc_configs
# Copy your jenkins.yaml from git
echo 'CASC_JENKINS_CONFIG=/var/lib/jenkins/casc_configs' | sudo tee -a /etc/sysconfig/jenkins
sudo systemctl restart jenkins
```

Set up folders (`platform-team/`, `app-team/`) and roles as you did in Phase 2. This should take 10-15 minutes since you've done it before.

---

#### 1. Pipeline Templates — Enforced Organizational Standards (30 min)

CloudBees CI's Pipeline Templates are locked-down, parameterized pipeline definitions that teams consume but cannot modify. This is the #1 differentiator from open-source shared libraries. With shared libraries, teams CAN choose not to import them. With templates, the structure is enforced.

In open-source Jenkins, we simulate templates using a shared library that **requires** certain stages:

```bash
# Create the shared library (or extend from Phase 2)
mkdir -p ~/jenkins-shared-lib/vars
cd ~/jenkins-shared-lib

# Create an enforced pipeline template
cat > vars/federalPipeline.groovy << 'TEMPLATEEOF'
// federalPipeline — Enforced pipeline template
// Teams call this instead of writing their own pipeline structure.
// Security stages (Trivy, SBOM) CANNOT be skipped.
//
// Usage in Jenkinsfile:
//   @Library('oci-shared-lib') _
//   federalPipeline(
//     appName: 'fedcompliance',
//     terraformDir: 'terraform/',
//     environment: 'lab'
//   )

def call(Map config) {
    def appName = config.get('appName', 'app')
    def terraformDir = config.get('terraformDir', 'terraform/')
    def environment = config.get('environment', 'dev')
    def skipDeploy = config.get('skipDeploy', false)

    pipeline {
        agent any

        environment {
            IMAGE_TAG = "${appName}:${BUILD_NUMBER}"
        }

        stages {
            // === MANDATORY STAGES (teams cannot skip these) ===

            stage('Checkout') {
                steps {
                    checkout scm
                }
            }

            stage('Terraform Validate') {
                steps {
                    dir(terraformDir) {
                        sh 'terraform init -backend=false'
                        sh 'terraform validate'
                    }
                }
            }

            stage('Security: Trivy Scan') {
                // This stage is MANDATORY — templates enforce it
                steps {
                    sh "docker build -t ${IMAGE_TAG} ."
                    sh "trivy image --exit-code 1 --severity CRITICAL ${IMAGE_TAG}"
                    sh "trivy image --format json --output trivy-report.json ${IMAGE_TAG}"
                    archiveArtifacts artifacts: 'trivy-report.json'
                }
            }

            stage('Security: SBOM Generation') {
                // This stage is MANDATORY — EO 14028 compliance
                steps {
                    sh "syft ${IMAGE_TAG} -o spdx-json > sbom.json"
                    archiveArtifacts artifacts: 'sbom.json'
                }
            }

            stage('Ansible Lint') {
                steps {
                    sh 'ansible-lint ansible/ || echo "Lint warnings (non-blocking)"'
                }
            }

            // === APPROVAL GATE (governed by RBAC) ===

            stage('Approval') {
                steps {
                    timeout(time: 30, unit: 'MINUTES') {
                        input message: "Deploy ${appName} to ${environment}?",
                              submitter: 'admin,deployer'
                    }
                }
            }

            // === DEPLOYMENT (optional, controlled by parameter) ===

            stage('Deploy') {
                when { expression { !skipDeploy } }
                steps {
                    sh "echo 'Deploying ${IMAGE_TAG} to ${environment}'"
                    // Actual deployment commands go here
                }
            }
        }

        post {
            always {
                echo "Pipeline complete for ${appName} — build #${BUILD_NUMBER}"
            }
            failure {
                echo "ALERT: Pipeline failed for ${appName}"
            }
        }
    }
}
TEMPLATEEOF

git init
git add .
git commit -m "Add federalPipeline template — enforced security stages"
```

Configure in Jenkins UI: Manage Jenkins → System → Global Pipeline Libraries:
- Name: `oci-shared-lib`
- Default version: `main`
- Source: Git, point to `~/jenkins-shared-lib`

**Now create a Jenkinsfile that uses the template:**

```groovy
// This is what a team's Jenkinsfile looks like when using the template.
// The team specifies parameters but CANNOT skip the Trivy/SBOM stages.
@Library('oci-shared-lib') _

federalPipeline(
    appName: 'fedcompliance',
    terraformDir: 'terraform/',
    environment: 'lab'
)
```

> **That's it.** The entire team's Jenkinsfile is 4 lines. The security scanning, SBOM generation, approval gates, and deployment logic are all enforced by the template. Teams can't bypass them.

**Create a second pipeline to prove the template works for multiple teams:**

In Jenkins UI: New Item → Pipeline in `app-team/` folder → name: `app-team-service`

```groovy
@Library('oci-shared-lib') _

federalPipeline(
    appName: 'app-team-service',
    terraformDir: 'terraform/',
    environment: 'dev',
    skipDeploy: true  // This team just wants CI, not CD
)
```

Run both pipelines. Both execute the same security stages. Neither team can skip Trivy or SBOM.

> **Interview Insight: "How do you enforce security standards across multiple teams' pipelines?"**
>
> **Strong answer:** "I use pipeline templates — a shared library that defines the entire pipeline structure including mandatory security stages. Teams consume the template with 4 lines of Jenkinsfile, specifying only their app name and environment. They cannot skip the Trivy scan or SBOM generation. In CloudBees CI, this is formalized as Pipeline Templates with a locked-down structure and parameterized inputs. The open-source equivalent uses shared libraries with the same pattern. Either way, organizational security standards are enforced, not optional."
>
> **Weak answer:** "We trust teams to add security scanning to their pipelines." (In federal environments, trust is not a compliance strategy.)

---

#### 2. Cross-Team Pipeline Visibility (15 min)

In an enterprise with multiple teams, leadership needs a dashboard showing all teams' pipeline health — without having access to modify anything.

**Set up the `auditor` view:**

1. Log in as `admin`
2. Create a new View: Jenkins → New View → name: `all-teams-dashboard` → select "List View"
3. Add all pipelines from both `platform-team/` and `app-team/` folders
4. Save

Now log in as `auditor` (read-only role from RBAC setup):
- `auditor` can see the dashboard, all pipeline statuses, build history
- `auditor` CANNOT build, configure, or modify anything
- This maps to NIST AC-3 (access enforcement) and AU-6 (audit review)

```bash
# Verify via audit trail that the auditor's login was logged
sudo grep "auditor" /var/log/jenkins/audit.log
```

> **CloudBees extends this:** Operations Center provides a single dashboard across ALL managed controllers — not just one Jenkins instance. A federal program with 5 teams on 5 separate controllers gets one unified view. Open-source Jenkins limits visibility to a single controller.

---

#### 3. CasC Bundle Versioning — GitOps for Jenkins (20 min)

In Phase 2, you created a CasC YAML file. Now practice the GitOps workflow: change the YAML in git → Jenkins config updates.

```bash
cd ~/fedcompliance-project  # or your repo directory

# Edit the CasC config — change the system message
cat > phases/phase-3-fedcompliance-gitops-security/jenkins/casc/jenkins.yaml << 'CASCEOF'
jenkins:
  systemMessage: "FedCompliance Lab v3 — Managed by CasC + GitOps (Phase 3)"
  numExecutors: 3
  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "admin"
          name: "Admin"
        - id: "deployer"
          name: "Deploy Service Account"
        - id: "auditor"
          name: "Audit Viewer"
        - id: "app-deployer"
          name: "App Team Deployer"
  authorizationStrategy:
    roleBased:
      roles:
        global:
          - name: "admin"
            permissions:
              - "Overall/Administer"
            entries:
              - user: "admin"
          - name: "viewer"
            permissions:
              - "Overall/Read"
              - "Job/Read"
            entries:
              - user: "auditor"

unclassified:
  audit-trail:
    logBuildCause: true
    pattern: ".*/(?:configSubmit|doDelete|postBuildResult|enable|disable|cancelQueue|stop|toggleLogKeep|doWipeOutWorkspace|createItem|createView|toggleOffline|cancelQuietDown|quietDown|restart|exit|safeRestart).*"
CASCEOF

git add phases/phase-3-fedcompliance-gitops-security/jenkins/casc/jenkins.yaml
git commit -m "CasC v3: add app-deployer user, increase executors to 3"
```

Now apply the updated CasC:

```bash
# Copy updated config to Jenkins
sudo cp jenkins/casc/jenkins.yaml /var/lib/jenkins/casc_configs/jenkins.yaml

# Reload CasC without restarting Jenkins
curl -X POST "http://localhost:8080/configuration-as-code/reload" \
  --user admin:YOUR_PASSWORD
```

**Verify:**
1. Jenkins UI → system message should say "FedCompliance Lab v3"
2. Manage Jenkins → Users → `app-deployer` should exist
3. Number of executors should be 3

> **The workflow:** Code change → git commit → deploy CasC YAML → Jenkins updates. This is GitOps for Jenkins configuration. In CloudBees CI, Operations Center pushes CasC bundles to all managed controllers automatically — you don't even need to `curl` a reload endpoint. But the principle is identical: Jenkins config is code, versioned in git, deployed via automation.

---

#### 4. Shared Library as Governance Enforcement (15 min)

The shared library from the pipeline template enforces that every pipeline MUST call `securityScan()`. A pipeline that doesn't use the template is non-compliant.

Create a governance check that validates all pipelines use the template:

```bash
cat > phases/phase-3-fedcompliance-gitops-security/scripts/validate-pipelines.sh << 'VALIDATEEOF'
#!/bin/bash
# validate-pipelines.sh — Check that all Jenkinsfiles use the federal template
# This is compliance-as-code for CI/CD pipelines

echo "=== Pipeline Governance Validation ==="
echo "Checking all Jenkinsfiles use the federalPipeline template..."

FAIL=0
for jenkinsfile in $(find . -name "Jenkinsfile" -not -path "./.git/*"); do
    if grep -q "federalPipeline" "$jenkinsfile"; then
        echo "  PASS: $jenkinsfile uses federalPipeline template"
    elif grep -q "@Library('oci-shared-lib')" "$jenkinsfile"; then
        echo "  WARN: $jenkinsfile uses shared library but not the template"
    else
        echo "  FAIL: $jenkinsfile does NOT use approved pipeline pattern"
        FAIL=1
    fi
done

if [ $FAIL -eq 1 ]; then
    echo ""
    echo "GOVERNANCE VIOLATION: Some pipelines do not use the approved template."
    echo "All pipelines must use federalPipeline() for NIST 800-53 compliance."
    exit 1
fi

echo ""
echo "All pipelines compliant."
VALIDATEEOF

chmod +x phases/phase-3-fedcompliance-gitops-security/scripts/validate-pipelines.sh
git add phases/phase-3-fedcompliance-gitops-security/scripts/validate-pipelines.sh
git commit -m "Add pipeline governance validation script"

git push origin main
```

> **Interview talking point:** "I built a governance layer around Jenkins pipelines. The shared library enforces that every pipeline runs Trivy scanning and SBOM generation. A validation script checks that all Jenkinsfiles in the repo use the approved template. Non-compliant pipelines are flagged. This is compliance-as-code for CI/CD — it ties into the compliance-as-code evidence collector we build later in Phase 25."

---

## PHASE 23 TROUBLESHOOTING

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| **Stage 3 fails: "CRITICAL CVE found"** | Base image contains a known critical vulnerability | Update `Dockerfile`: change `FROM python:3.11-slim` to `FROM python:3.12-slim` or `FROM python:3.11-slim-bookworm`. Commit and re-run pipeline. This is the intended behavior — Trivy is working correctly |
| **Stage 3 fails: "trivy: command not found"** | Jenkins executor runs with a PATH that does not include Trivy's install location | Add `export PATH=$PATH:/usr/local/bin` at the top of the Trivy `sh` block, or install Trivy to `/usr/bin/trivy` with `sudo mv /usr/local/bin/trivy /usr/bin/trivy` |
| **Stage 3 fails: "Cannot connect to Docker daemon"** | Jenkins service user (`jenkins`) is not in the `docker` group | `sudo usermod -aG docker jenkins && sudo systemctl restart jenkins` — then re-run the pipeline |
| **Stage 4: SBOM file is empty (0 bytes)** | Syft could not find the `scan-temp` image locally | Confirm Stage 3 successfully built `${IMAGE_NAME}:scan-temp` before Stage 4 runs. Review Stage 3 console output for Docker build errors |
| **Stage 6: No input prompt appears in Jenkins UI** | Pipeline does not have permission to pause for input | Jenkins → Manage Jenkins → Configure Global Security → verify your admin user has Job/Build permission on `fedcompliance-pipeline` |
| **Stage 6: Approval gate times out immediately** | Timeout value or unit is misconfigured | Verify exact syntax: `timeout(time: 2, unit: 'HOURS')` — capital HOURS, no typos. Check Jenkins server system time: `date` on the bastion VM |
| **Stage 6: "No valid submitter found for admin"** | Your Jenkins user account is not named `admin` | Change `submitter: 'admin'` to match your actual Jenkins username. To find it: Jenkins → top-right username dropdown. Or remove the `submitter` line entirely to allow any user to approve |
| **Stage 7 fails: "unauthorized: authentication required"** | Wrong credential ID or expired OCI Auth Token | Verify `credentialsId: 'ocir-credentials'` matches exactly. Regenerate OCI Auth Token: OCI Console → Profile → Auth Tokens → Generate Token. Update the Jenkins credential with the new token |
| **Stage 7 fails: "denied: requested access to resource is denied"** | OCIR username format is wrong | Correct OCIR username format: `<tenancy_namespace>/oracleidentitycloudservice/<your_email>` — not your console login username |
| **Stage 8 fails: "unable to connect to the server"** | kubeconfig has `127.0.0.1` as the server address | Re-generate kubeconfig from k3s: `sudo cat /etc/rancher/k3s/k3s.yaml` → replace `127.0.0.1` with the k3s node private IP → re-upload to Jenkins credential `k3s-kubeconfig` |
| **Stage 8 fails: "namespace fedcompliance not found"** | Deployment manifest applied before namespace was created | Verify Stage 8 applies `namespace.yaml` first: `kubectl apply -f k8s/namespace.yaml` must precede `kubectl apply -f k8s/deployment.yaml`. Check the ordering in your Jenkinsfile |
| **Stage 8: pods stuck in `ImagePullBackOff`** | k3s nodes cannot authenticate to OCIR to pull the image | Create the OCIR pull secret in the namespace (see Step 23.5). Verify: `kubectl get secret ocir-pull-secret -n fedcompliance` |
| **Stage 8: `sed` did not replace IMAGE_TAG** | The placeholder was already replaced in a previous run | Restore it: `git checkout k8s/deployment.yaml` in the repo directory. Then verify: `grep 'IMAGE_TAG' k8s/deployment.yaml` should show the placeholder. Commit the restored file |
| **Stage 8: rollout status times out (pods stay Pending)** | Node resource limits exceeded, or image pull failing | Check: `kubectl describe pod -n fedcompliance -l app=fedcompliance` — look for Events section. Common causes: ImagePullBackOff (fix pull secret) or Insufficient memory (reduce `resources.requests.memory`) |
| **Stage 9: smoke test fails "Connection refused"** | Application pod not fully ready when curl runs | Increase sleep: `sleep(time: 30, unit: 'SECONDS')`. Or add before curl: `kubectl wait --for=condition=ready pod -l app=fedcompliance -n fedcompliance --timeout=60s` |
| **Stage 9: smoke test fails "HTTP 422 Unprocessable Entity"** | The `/health` endpoint requires a request body or query parameter it is not receiving | Verify FastAPI has `@app.get("/health")` with no required parameters. Check pod logs: `kubectl logs -n fedcompliance -l app=fedcompliance --tail=50` |
| **Next pipeline run: IMAGE_TAG already replaced in deployment.yaml** | `sed -i` ran in a shared workspace or working tree | Run `git checkout k8s/deployment.yaml` and commit the restored file. For a permanent fix, modify Stage 8 to work on a copy: `cp k8s/deployment.yaml /tmp/deploy.yaml && sed -i ... /tmp/deploy.yaml && kubectl apply -f /tmp/deploy.yaml` |

---

### Phase 23 Complete

**What you built:**
- A 9-stage Jenkins pipeline written entirely by hand as a `Jenkinsfile` (pipeline-as-code, version-controlled)
- Container security gate: Trivy scans for CRITICAL/HIGH CVEs and blocks the pipeline before any image reaches OCIR
- SBOM generation: Syft produces a SPDX JSON software bill of materials for every build, archived as a Jenkins artifact (EO 14028 compliance)
- Manual approval gate: pipeline pauses after automated checks, requires authorized human approval before deploying — with 2-hour auto-abort and optional change ticket field
- Pipeline credentials management: OCI auth token, kubeconfig, SSH key, OCI CLI config — all encrypted in Jenkins Credentials Store, referenced by ID only
- Raw K8s manifests: Namespace, ConfigMap, Deployment (2 replicas with resource limits and health probes), Service (NodePort 30080) — applied via `kubectl apply`
- Image tag strategy: Git commit SHA (short form) used as Docker image tag — every running container is traceable back to its exact source commit and build

**What's running:**
- Jenkins on the bastion VM (port 8080)
- FedCompliance API on k3s: 2 pods in the `fedcompliance` namespace, accessible on NodePort 30080 from within the VCN
- Trivy and Syft installed on the bastion VM, callable from any future pipeline stage
- Per-build security evidence package: `trivy-report.json` + `fedcompliance-sbom-N.spdx.json` + `terraform/tfplan` archived in Jenkins

**Why this matters for the interview:**
- You can describe a real multi-stage pipeline with security gates — not a toy two-step "build and push"
- You understand the approval gate's purpose and can cite the federal control it satisfies (NIST 800-53 CM-3) with a clear explanation
- You can explain SBOM generation with specific tooling (Syft, SPDX JSON) and tie it to EO 14028 requirements
- You deployed to Kubernetes with raw `kubectl apply` first — so when Day 3 introduces Helm, you can explain precisely what Helm's `values.yaml` image tag field replaces (the `sed -i IMAGE_TAG` pattern) and why Helm's approach is cleaner at scale
- You know the difference between scanning before vs. after push, and why scan-before-push is the correct approach in regulated environments

**Next phase (Day 3 — Phase 24):** Upgrade the deployment from raw `kubectl apply` to Helm. Write `Chart.yaml`, `values.yaml`, and templated K8s manifests by hand. Replace Stage 8's `kubectl apply` + `sed` with `helm upgrade --install`. Then add ArgoCD: install it on k3s, write an `Application` manifest pointing at your git repo, and watch ArgoCD auto-sync the cluster on every git push — making the pipeline's deploy stage itself optional.

---

## PHASE 24: HELM + ARGOCD — PRODUCTION-GRADE DELIVERY (6-8 hrs)

> **What this phase builds:** You will replace the raw `kubectl apply` + `sed -i IMAGE_TAG` pattern from Phase 23 with a proper Helm chart you write from scratch. Then you will install ArgoCD on k3s, write an Application manifest by hand, and establish a full GitOps loop: push a change to git → ArgoCD detects it → cluster auto-syncs. Finally you will update the Jenkins pipeline so it only handles build + push + git commit; ArgoCD owns the K8s deployment from that point forward.

> **Why this order matters:** You built with raw kubectl in Phase 23 deliberately. Now every Helm concept has a direct comparison. When an interviewer asks "what does Helm actually do?" you can say "it replaces my `sed -i IMAGE_TAG` one-liner with a typed `values.yaml` field, and wraps all my manifests in a versioned, rollback-able release" — because you lived the before state.

---

> **🧠 ELI5 — Helm (the big picture):** Imagine you have five YAML files for your app — Deployment, Service, ConfigMap, Secret, Namespace. Every time you deploy to a new environment (dev, staging, prod) you have to change values scattered across all five files: image tags, replica counts, resource limits, environment names. Without Helm you either copy-paste and manually edit, or write fragile `sed` commands like the one in Phase 23's Stage 8. Helm solves this by letting you write your YAML once as templates with `{{ .Values.something }}` placeholders, then define the actual values per environment in a `values.yaml` file. When you run `helm install`, Helm fills in all the templates and sends the result to Kubernetes — like a mail-merge for YAML. Bonus: Helm tracks every install and upgrade as a numbered "release" in Kubernetes secrets, so `helm rollback` can restore any previous state in seconds.

> **🧠 ELI5 — ArgoCD and GitOps:** GitOps says "your git repository is the single source of truth for what should be running in your cluster." ArgoCD is the agent that enforces this. You tell ArgoCD: "watch this git repo, specifically this path, and keep the cluster matching it." Whenever you push a commit, ArgoCD sees the diff between what is in git and what is in the cluster, and syncs the cluster to match. No human runs `kubectl apply` or `helm upgrade` — git push is the deployment action. For federal environments, this is powerful: every change to the cluster is a git commit, meaning every deployment has a full audit trail (who, what, when) in git history — not just in a CI log that might get rotated.

---

### Step 24.1 — Understand What Helm Replaces (The Before/After Mental Model)

📍 **Bastion Terminal** — no commands yet, just analysis

Before you write a single Helm file, internalize exactly what you are replacing. Pull up the Phase 23 Jenkinsfile Stage 8 in your head:

```
# Phase 23 Stage 8 approach:
sed -i "s|IMAGE_TAG|${IMAGE_TAG}|g" k8s/deployment.yaml
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/configmap.yaml
```

Problems with this approach at scale:

| Problem | Why It Hurts |
|---------|-------------|
| `sed -i IMAGE_TAG` is a string replacement hack | Fragile — breaks if placeholder appears elsewhere, no type safety, no validation |
| Applying 4 separate files in order | You must know the correct apply order; a missing file causes a confusing error |
| No release history | There is no record of "what was deployed at 14:32 on Tuesday" — only the current state |
| No rollback primitive | To roll back you must re-run the pipeline or manually apply an old manifest |
| Values scattered across files | Changing replicas means editing `deployment.yaml`; changing the port means editing both `deployment.yaml` and `service.yaml` |
| No multi-environment support | Dev and prod require separate manifest directories or more `sed` hacks |

Helm's answer to every row:

| Problem | Helm Solution |
|---------|--------------|
| `sed -i` hack | `{{ .Values.image.tag }}` in `deployment.yaml` template; set via `--set` or `values.yaml` |
| Apply order | `helm install` sends all templates atomically; Helm handles ordering for CRDs |
| No release history | Every `helm install`/`helm upgrade` creates a numbered release stored in a K8s secret |
| No rollback | `helm rollback <release> <revision>` — single command, tested in Step 24.6 |
| Values scattered | All tunable values in one `values.yaml`; templates reference them by path |
| Multi-environment | Override values per environment: `helm upgrade --install -f values-prod.yaml` |

> **💼 Interview Insight — "What does Helm actually do?":** The answer interviewers want is not "it's a package manager." Say: "Helm separates the structure of your Kubernetes manifests from the values that change between deployments. I built without it in Phase 23 using raw kubectl apply and a sed substitution for the image tag. Helm replaces that with a typed values.yaml and Go templates in the manifests. On top of that it tracks every install and upgrade as a versioned release, so rollback is a single command rather than re-running a pipeline or manually applying old YAML." Then mention you have actually run `helm rollback` in your lab.

---

### Step 24.2 — Install Helm on the Bastion VM

📍 **Bastion Terminal**

```bash
# Check if Helm is already installed
helm version 2>/dev/null && echo "Helm already installed" || echo "Need to install"

# Install Helm via the official installer script
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version
# Expected output (version numbers may vary):
# version.BuildInfo{Version:"v3.14.x", GitCommit:"...", GitTreeState:"clean", GoVersion:"go1.22.x"}

# Confirm helm is on PATH for all shells
which helm
# Expected: /usr/local/bin/helm
```

> If the curl installer is blocked (air-gapped lab), use the binary install:

```bash
# Alternative: direct binary download
HELM_VERSION="v3.14.4"
curl -LO "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz"
tar -zxvf "helm-${HELM_VERSION}-linux-amd64.tar.gz"
sudo mv linux-amd64/helm /usr/local/bin/helm
helm version
```

```bash
# Add the stable Helm repo (useful for pulling community charts later)
helm repo add stable https://charts.helm.sh/stable
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
# Expected: "Update Complete. Happy Helming!"
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `helm version` | Shows the installed Helm client version |
| `helm repo add` | Registers a chart repository by name and URL |
| `helm repo update` | Refreshes the local cache of all registered repos (like `apt update`) |

</em></sub>

---

### Step 24.3 — Understand Helm Chart Structure Before Writing Anything

📍 **Bastion Terminal** — read the scaffold first

```bash
# Create a throwaway chart to see the default structure
cd ~
helm create example-chart
find example-chart -type f | sort
```

Expected output:
```
example-chart/Chart.yaml
example-chart/charts/
example-chart/templates/NOTES.txt
example-chart/templates/_helpers.tpl
example-chart/templates/deployment.yaml
example-chart/templates/hpa.yaml
example-chart/templates/ingress.yaml
example-chart/templates/service.yaml
example-chart/templates/serviceaccount.yaml
example-chart/templates/tests/test-connection.yaml
example-chart/values.yaml
```

**What each file does:**

| File / Directory | Role |
|-----------------|------|
| `Chart.yaml` | Chart metadata: name, version, app version, description, maintainers |
| `values.yaml` | Default values for all template variables — this is what you override per deployment |
| `templates/` | Directory of Go-templated Kubernetes YAML files |
| `templates/_helpers.tpl` | Named template partials (reusable snippets, like a function library) |
| `templates/NOTES.txt` | Text printed to the terminal after `helm install` — instructions for the user |
| `charts/` | Sub-charts (dependencies) — empty for now |

```bash
# Remove the throwaway chart — you will write yours from scratch
rm -rf ~/example-chart
```

> **Why write from scratch instead of using `helm create`?** The scaffold includes HPA, Ingress, ServiceAccount, and test templates you do not need yet. Writing from scratch means you understand every line. For the interview, "I generated a scaffold" is weaker than "I wrote Chart.yaml, values.yaml, and each template by hand."

---

### Step 24.4 — Create the FedCompliance Helm Chart By Hand

📍 **Bastion Terminal**

```bash
# Create the chart directory structure inside your repo
cd ~/fedcompliance
mkdir -p helm/fedcompliance/templates

# Verify the structure
find helm/ -type d
# Expected:
# helm/
# helm/fedcompliance/
# helm/fedcompliance/templates/
```

**Write Chart.yaml:**

```bash
cat > helm/fedcompliance/Chart.yaml << 'EOF'
# Chart.yaml — Helm chart metadata
# chartVersion vs appVersion: chart version tracks the Helm packaging;
# appVersion tracks the version of the application being deployed.
# They move independently: chart v1.2.0 can package app v2.0.0.

apiVersion: v2          # v2 = Helm 3 chart format
name: fedcompliance     # Must match the directory name by convention
description: >
  FedCompliance FastAPI application — federal policy compliance checker
  deployed on OCI k3s via GitOps (ArgoCD) with Helm templating.
type: application       # "application" = runnable workload; "library" = reusable templates only
version: 0.1.0          # Chart version — increment when chart structure changes
appVersion: "1.0.0"     # Application version — informational; image tag controls actual version
maintainers:
  - name: <YOUR_NAME>       # e.g., "Jane Smith"
    email: <YOUR_EMAIL>      # e.g., "you@example.com"
EOF
```

Verify:
```bash
cat helm/fedcompliance/Chart.yaml
```

---

**Write values.yaml — the single source of tunable configuration:**

```bash
cat > helm/fedcompliance/values.yaml << 'EOF'
# values.yaml — Default values for the FedCompliance Helm chart.
# Override any value with: helm upgrade --install -f values-prod.yaml
# or inline: helm upgrade --install --set image.tag=abc1234
#
# Every {{ .Values.X }} in the templates refers back to a path here.

# Image configuration
image:
  repository: us-ashburn-1.ocir.io/<YOUR_TENANCY_NAMESPACE>/fedcompliance
  # tag defaults to "latest" — the CI pipeline overrides this with a Git SHA
  tag: "latest"
  # IfNotPresent: only pull if the tag is not already on the node
  # Use Always for "latest" tags; IfNotPresent is safe for SHA-tagged images
  pullPolicy: IfNotPresent

# OCIR pull secret — created manually with kubectl create secret docker-registry
imagePullSecrets:
  - name: ocir-pull-secret

# Number of replicas — override to 1 for dev, 3+ for production
replicaCount: 2

# Kubernetes Service configuration
service:
  type: NodePort        # NodePort for lab access without a LoadBalancer
  port: 8000            # Port the FastAPI app listens on inside the container
  nodePort: 30080       # External port on every k3s node (30000-32767 range)

# Target namespace — Helm creates this via templates/namespace.yaml
namespace: fedcompliance

# Resource requests and limits
# Requests: what Kubernetes reserves on the node for scheduling
# Limits: hard cap — container is OOMKilled or CPU-throttled if exceeded
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"         # 100 millicores = 0.1 vCPU
  limits:
    memory: "256Mi"
    cpu: "500m"         # 500 millicores = 0.5 vCPU

# Application environment variables — become the ConfigMap
env:
  appEnv: "production"
  logLevel: "INFO"
  dbConnectionString: "localhost:1521/atp"

# Health probe configuration — liveness restarts unhealthy pods;
# readiness gates traffic — pod does not receive requests until passing
probes:
  liveness:
    path: /health
    initialDelaySeconds: 15
    periodSeconds: 20
  readiness:
    path: /health
    initialDelaySeconds: 10
    periodSeconds: 10
EOF
```

---

**Write templates/deployment.yaml:**

> Go template syntax reference:
> - `{{ .Values.X }}` — substitute the value at path X from values.yaml
> - `{{ .Release.Name }}` — the Helm release name (set at install time)
> - `{{ .Release.Namespace }}` — the namespace Helm is deploying into
> - `{{ .Chart.AppVersion }}` — the appVersion from Chart.yaml
> - `| quote` — wraps the value in double quotes (safe for strings in YAML)
> - `{{- range .Values.list }}` / `{{- end }}` — loop over a list

```bash
cat > helm/fedcompliance/templates/deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
  namespace: {{ .Values.namespace }}
  labels:
    app: {{ .Release.Name }}
    chart: {{ .Chart.Name }}-{{ .Chart.Version }}
    release: {{ .Release.Name }}
    heritage: {{ .Release.Service }}
    app.kubernetes.io/managed-by: Helm
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
        version: {{ .Values.image.tag | quote }}
    spec:
      imagePullSecrets:
        {{- range .Values.imagePullSecrets }}
        - name: {{ .name }}
        {{- end }}
      containers:
        - name: {{ .Release.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.port }}
              protocol: TCP
          envFrom:
            - configMapRef:
                name: {{ .Release.Name }}-config
          resources:
            requests:
              memory: {{ .Values.resources.requests.memory | quote }}
              cpu: {{ .Values.resources.requests.cpu | quote }}
            limits:
              memory: {{ .Values.resources.limits.memory | quote }}
              cpu: {{ .Values.resources.limits.cpu | quote }}
          livenessProbe:
            httpGet:
              path: {{ .Values.probes.liveness.path }}
              port: {{ .Values.service.port }}
            initialDelaySeconds: {{ .Values.probes.liveness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.liveness.periodSeconds }}
          readinessProbe:
            httpGet:
              path: {{ .Values.probes.readiness.path }}
              port: {{ .Values.service.port }}
            initialDelaySeconds: {{ .Values.probes.readiness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.readiness.periodSeconds }}
EOF
```

---

**Write templates/service.yaml:**

```bash
cat > helm/fedcompliance/templates/service.yaml << 'EOF'
# Routes external traffic to pods selected by app={{ .Release.Name }}.
# NodePort exposes the service on a static port on every k3s node.
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-svc
  namespace: {{ .Values.namespace }}
  labels:
    app: {{ .Release.Name }}
    release: {{ .Release.Name }}
    app.kubernetes.io/managed-by: Helm
spec:
  type: {{ .Values.service.type }}
  selector:
    app: {{ .Release.Name }}
  ports:
    - name: http
      protocol: TCP
      port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.port }}
      nodePort: {{ .Values.service.nodePort }}
EOF
```

---

**Write templates/configmap.yaml:**

```bash
cat > helm/fedcompliance/templates/configmap.yaml << 'EOF'
# Stores non-sensitive environment configuration.
# The Deployment references this via envFrom.configMapRef.
# ConfigMap changes require a pod restart — handled automatically
# by Helm upgrade since it updates the Deployment spec (triggering a rollout).
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
  namespace: {{ .Values.namespace }}
  labels:
    app: {{ .Release.Name }}
    release: {{ .Release.Name }}
    app.kubernetes.io/managed-by: Helm
data:
  APP_ENV: {{ .Values.env.appEnv | quote }}
  LOG_LEVEL: {{ .Values.env.logLevel | quote }}
  DB_CONNECTION_STRING: {{ .Values.env.dbConnectionString | quote }}
EOF
```

---

**Write templates/secret.yaml:**

```bash
cat > helm/fedcompliance/templates/secret.yaml << 'EOF'
# IMPORTANT: In production, do NOT store actual secret values in values.yaml.
# Use External Secrets Operator (OCI Vault), Sealed Secrets, or Helm Secrets plugin.
# This is a placeholder secret for lab purposes only.
# The real OCI Vault integration was built in Phase 20.
#
# b64enc is a Helm/Sprig template function — not a shell command.
# Usage: {{ "plaintext value" | b64enc }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Release.Name }}-secret
  namespace: {{ .Values.namespace }}
  labels:
    app: {{ .Release.Name }}
    release: {{ .Release.Name }}
    app.kubernetes.io/managed-by: Helm
  annotations:
    # Documents that this secret's values come from OCI Vault in production.
    oci-vault-source: "ocid1.vault.oc1.iad.placeholder"
type: Opaque
data:
  API_KEY: {{ "placeholder-rotate-before-prod" | b64enc | quote }}
EOF
```

---

**Write templates/namespace.yaml:**

```bash
cat > helm/fedcompliance/templates/namespace.yaml << 'EOF'
# Creates the namespace if it does not already exist.
# Helm applies Namespace resources before other resource types automatically.
# If the namespace was manually created (Phase 23), delete it first:
#   kubectl delete namespace fedcompliance
apiVersion: v1
kind: Namespace
metadata:
  name: {{ .Values.namespace }}
  labels:
    app.kubernetes.io/managed-by: Helm
    environment: {{ .Values.env.appEnv | quote }}
EOF
```

---

**Write templates/NOTES.txt:**

```bash
cat > helm/fedcompliance/templates/NOTES.txt << 'EOF'
FedCompliance has been deployed successfully.

Release:   {{ .Release.Name }}
Namespace: {{ .Values.namespace }}
Image:     {{ .Values.image.repository }}:{{ .Values.image.tag }}
Replicas:  {{ .Values.replicaCount }}

Access the application from within the VCN (bastion):
  curl http://<k3s-node-private-ip>:{{ .Values.service.nodePort }}/health

Helm release history:
  helm history {{ .Release.Name }} -n {{ .Values.namespace }}

Roll back to previous version:
  helm rollback {{ .Release.Name }} -n {{ .Values.namespace }}
EOF
```

Verify the complete chart structure:
```bash
find ~/fedcompliance/helm -type f | sort
```

Expected:
```
/home/opc/fedcompliance/helm/fedcompliance/Chart.yaml
/home/opc/fedcompliance/helm/fedcompliance/templates/NOTES.txt
/home/opc/fedcompliance/helm/fedcompliance/templates/configmap.yaml
/home/opc/fedcompliance/helm/fedcompliance/templates/deployment.yaml
/home/opc/fedcompliance/helm/fedcompliance/templates/namespace.yaml
/home/opc/fedcompliance/helm/fedcompliance/templates/secret.yaml
/home/opc/fedcompliance/helm/fedcompliance/templates/service.yaml
/home/opc/fedcompliance/helm/fedcompliance/values.yaml
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Files created:

| File | Role |
|------|------|
| `Chart.yaml` | Chart identity and versioning metadata |
| `values.yaml` | All tunable defaults — the only file you edit per environment |
| `templates/deployment.yaml` | Templated Deployment — image, replicas, probes, resources |
| `templates/service.yaml` | NodePort Service — routes traffic to pods |
| `templates/configmap.yaml` | Non-sensitive env vars fed into containers via envFrom |
| `templates/secret.yaml` | Placeholder secret with note on production Vault integration |
| `templates/namespace.yaml` | Creates the namespace as a Helm-managed resource |
| `templates/NOTES.txt` | Post-install instructions printed to terminal |

</em></sub>

---

### Step 24.5 — Lint and Dry-Run the Chart Before Installing

📍 **Bastion Terminal**

```bash
# helm lint: checks template syntax and Chart.yaml validity
# Catches: undefined values, malformed YAML, missing required fields
helm lint ~/fedcompliance/helm/fedcompliance
# Expected: ==> Linting fedcompliance
#           [INFO] Chart.yaml: icon is recommended
#           1 chart(s) linted, 0 chart(s) failed
```

If lint fails, the error message includes the file and line number. Common errors:

| Lint Error | Cause | Fix |
|-----------|-------|-----|
| `parse error at (deployment.yaml:N)` | Missing closing `}}` in a template expression | Count `{{` and `}}` — they must be balanced |
| `values don't meet the specifications of the schema` | `values.schema.json` present but values mismatch | Remove the schema file or correct the value type |
| `[ERROR] Chart.yaml: apiVersion is required` | `Chart.yaml` is missing the `apiVersion: v2` line | Add it |

```bash
# helm template: renders all templates locally without connecting to K8s
# Use this to verify what Helm will actually send to kubectl
helm template fedcompliance ~/fedcompliance/helm/fedcompliance \
  --namespace fedcompliance \
  --set image.tag=a3f91c2 \
  | head -80
```

Expected: raw Kubernetes YAML with all `{{ }}` expressions replaced by actual values. Look for:
- `image: us-ashburn-1.ocir.io/<YOUR_TENANCY_NAMESPACE>/fedcompliance:a3f91c2` — confirms `--set image.tag` worked
- `replicas: 2` — from `values.yaml`
- `namespace: fedcompliance` — from `values.namespace`

```bash
# Full rendered output to a file for review
helm template fedcompliance ~/fedcompliance/helm/fedcompliance \
  --namespace fedcompliance \
  --set image.tag=a3f91c2 \
  > /tmp/helm-rendered-output.yaml

# Count the Kubernetes objects that would be created
grep "^kind:" /tmp/helm-rendered-output.yaml
# Expected:
# kind: Namespace
# kind: ConfigMap
# kind: Secret
# kind: Deployment
# kind: Service
```

```bash
# helm install --dry-run --debug: renders AND validates against the cluster API
# Does not actually create resources
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
helm install fedcompliance ~/fedcompliance/helm/fedcompliance \
  --namespace fedcompliance \
  --set image.tag=a3f91c2 \
  --dry-run \
  --debug 2>&1 | tail -30
# Expected: STATUS: pending-install — nothing hits the cluster
```

---

### Step 24.6 — Install the Helm Chart and Verify

📍 **Bastion Terminal**

```bash
# Delete the Phase 23 resources so Helm can manage them cleanly
# (Helm cannot adopt resources it did not create without annotation patching)
kubectl delete namespace fedcompliance 2>/dev/null || echo "Namespace did not exist — clean slate"

# Wait for namespace termination
kubectl get namespace fedcompliance 2>/dev/null && sleep 10 || echo "Namespace gone"

# Install the chart
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
CURRENT_SHA=$(cd ~/fedcompliance && git rev-parse --short HEAD)
echo "Deploying image tag: ${CURRENT_SHA}"

helm install fedcompliance ~/fedcompliance/helm/fedcompliance \
  --namespace fedcompliance \
  --set image.tag=${CURRENT_SHA}
```

Expected output:
```
NAME: fedcompliance
LAST DEPLOYED: <timestamp>
NAMESPACE: fedcompliance
STATUS: deployed
REVISION: 1
NOTES:
FedCompliance has been deployed successfully.
...
```

```bash
# Verify pods are running
kubectl get pods -n fedcompliance
# Expected: two pods, STATUS=Running

# Verify the release is tracked by Helm
helm list -n fedcompliance
# NAME           NAMESPACE      REVISION  STATUS    CHART                    APP VERSION
# fedcompliance  fedcompliance  1         deployed  fedcompliance-0.1.0      1.0.0

# Verify the image tag in the running Deployment
kubectl get deployment fedcompliance -n fedcompliance \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
# Expected: us-ashburn-1.ocir.io/<YOUR_TENANCY_NAMESPACE>/fedcompliance:<CURRENT_SHA>

# Test application response
K3S_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
curl http://${K3S_IP}:30080/health
# Expected: {"status": "healthy", ...}
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `helm install <name> <chart>` | Installs the chart as a new named release; fails if release already exists |
| `helm list -n <namespace>` | Lists all Helm releases in the namespace with status and revision |
| `helm status <name> -n <namespace>` | Shows detailed status of a specific release |

</em></sub>

---

### Step 24.7 — Helm Upgrade: Deploy a New Image Tag

📍 **Bastion Terminal**

> This simulates what the Jenkins pipeline will do in Step 24.13 — build a new image, push to OCIR, then run `helm upgrade` to deploy it.

```bash
# Simulate pushing a new build by using a demo tag
NEW_TAG="v1.1.0-demo"

helm upgrade fedcompliance ~/fedcompliance/helm/fedcompliance \
  --namespace fedcompliance \
  --set image.tag=${NEW_TAG}
# Expected: Release "fedcompliance" has been upgraded. Happy Helming!
# REVISION: 2
```

```bash
# Verify revision incremented to 2
helm list -n fedcompliance

# Verify rollout completed
kubectl rollout status deployment/fedcompliance -n fedcompliance

# Confirm new image tag is in the running spec
kubectl get deployment fedcompliance -n fedcompliance \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
# Expected: ...fedcompliance:v1.1.0-demo

# View full release history
helm history fedcompliance -n fedcompliance
# REVISION  STATUS      DESCRIPTION
# 1         superseded  Install complete
# 2         deployed    Upgrade complete
```

---

### Step 24.8 — Helm Rollback: Restore the Previous State

📍 **Bastion Terminal**

> This is the demo an interviewer wants to hear about. Push a bad config (wrong image tag → pods crash), then roll back in seconds.

```bash
# Simulate a bad deployment — non-existent image tag
helm upgrade fedcompliance ~/fedcompliance/helm/fedcompliance \
  --namespace fedcompliance \
  --set image.tag=BAD-TAG-DOES-NOT-EXIST
# Helm considers this a "deployed" release — it successfully sent the spec to K8s.
# But pods will fail because the image does not exist in OCIR.

# Watch pods fail
sleep 30
kubectl get pods -n fedcompliance
# Expected: ImagePullBackOff or ErrImagePull on one or both pods

# Confirm revision 3 is the bad one
helm history fedcompliance -n fedcompliance
```

```bash
# ROLLBACK — restore revision 2 (last known-good state)
helm rollback fedcompliance 2 -n fedcompliance
# Expected: Rollback was a success! Happy Helming!

# Watch pods recover
kubectl rollout status deployment/fedcompliance -n fedcompliance
# Expected: "successfully rolled out"

kubectl get pods -n fedcompliance
# Expected: both pods Running

# Confirm image tag restored
kubectl get deployment fedcompliance -n fedcompliance \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
# Expected: ...fedcompliance:v1.1.0-demo

# History after rollback — revision 4 records the rollback
helm history fedcompliance -n fedcompliance
# REVISION  STATUS      DESCRIPTION
# 1         superseded  Install complete
# 2         superseded  Upgrade complete
# 3         superseded  Upgrade complete (the bad one)
# 4         deployed    Rollback to 2
```

> **💼 Interview Insight — "Have you ever had to roll back a deployment?":** Yes. "In my lab I demonstrated a bad image tag scenario. I used `helm rollback` which restored the previous Deployment spec in under 60 seconds — no pipeline re-run required, no manually applying old YAML. Kubernetes performed a rolling update back to the previous replica set. The important distinction is that Helm rollback restores the entire release state across all resources, not just the Deployment — the ConfigMap, Service, and Secret all revert too. `kubectl rollout undo` only reverts the Deployment."

---

### Step 24.9 — Install ArgoCD on k3s

📍 **Bastion Terminal**

> **🧠 ELI5 — ArgoCD Installation:** ArgoCD is itself a set of Kubernetes workloads — several controllers, a server, a Redis instance, and a Dex OIDC provider. You install it into its own namespace. Once running, ArgoCD watches Application custom resources you create, and for each one it compares the desired state (your Helm chart in git) with the actual state (what is in the cluster), then syncs the difference.

```bash
# Create the ArgoCD namespace
kubectl create namespace argocd

# Install ArgoCD using the official manifest
# This is the non-HA install — suitable for a lab/single-node setup
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

> If internet access is restricted, download the manifest first:
```bash
curl -LO https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl apply -n argocd -f install.yaml
```

```bash
# Watch ArgoCD pods come up (takes 2-5 minutes for all images to pull)
kubectl get pods -n argocd --watch &
WATCH_PID=$!
sleep 180
kill $WATCH_PID 2>/dev/null

# Verify all ArgoCD pods are Running
kubectl get pods -n argocd
```

Expected pods (all should show Running or Completed):
```
argocd-application-controller-0       Running
argocd-applicationset-controller-xxx  Running
argocd-dex-server-xxx                 Running
argocd-notifications-controller-xxx   Running
argocd-redis-xxx                      Running
argocd-repo-server-xxx                Running
argocd-server-xxx                     Running
```

```bash
# Install ArgoCD CLI on the bastion
ARGOCD_VERSION=$(curl -s https://api.github.com/repos/argoproj/argo-cd/releases/latest \
  | grep tag_name | cut -d'"' -f4)
echo "Installing ArgoCD CLI ${ARGOCD_VERSION}"

curl -sSL -o /usr/local/bin/argocd \
  "https://github.com/argoproj/argo-cd/releases/download/${ARGOCD_VERSION}/argocd-linux-amd64"
chmod +x /usr/local/bin/argocd

argocd version --client
# Expected: argocd: v2.x.x
```

```bash
# Get the initial admin password (auto-generated on first install)
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d)
echo "ArgoCD initial admin password: ${ARGOCD_PASSWORD}"
# SAVE THIS — you will need it to log in to the UI and CLI
```

```bash
# Expose the ArgoCD server via NodePort
kubectl patch svc argocd-server -n argocd \
  -p '{"spec": {"type": "NodePort"}}'

# Get the assigned NodePort
kubectl get svc argocd-server -n argocd
ARGOCD_PORT=$(kubectl get svc argocd-server -n argocd \
  -o jsonpath='{.spec.ports[?(@.port==80)].nodePort}')
K3S_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
echo "ArgoCD UI available at: http://${K3S_IP}:${ARGOCD_PORT}"
```

```bash
# Patch argocd-server to allow HTTP (lab only — not for production)
kubectl patch deployment argocd-server -n argocd \
  --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--insecure"}]'

kubectl rollout status deployment/argocd-server -n argocd

# Log in via CLI
argocd login ${K3S_IP}:${ARGOCD_PORT} \
  --username admin \
  --password ${ARGOCD_PASSWORD} \
  --insecure
# Expected: 'admin:login' logged in successfully
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `kubectl apply -n argocd -f <url>` | Installs ArgoCD by applying all its manifests into the argocd namespace |
| `kubectl -n argocd get secret argocd-initial-admin-secret` | Retrieves the auto-generated admin password |
| `kubectl patch svc argocd-server -n argocd -p '{"spec":{"type":"NodePort"}}'` | Changes service type to NodePort for external access |
| `argocd login` | Authenticates the CLI to the ArgoCD API server |

</em></sub>

---

### Step 24.10 — Add Your Git Repository to ArgoCD

📍 **Bastion Terminal**

> ArgoCD needs to read your git repository to watch for changes. For a private GitHub repo, provide a Deploy Key or Personal Access Token.

```bash
cd ~/fedcompliance
git remote -v
# Note the URL — this is what you will register with ArgoCD
```

**If using a private GitHub repository:**

```bash
# Option A: Register with HTTPS + Personal Access Token
# First, set your username variable:
# YOUR_GITHUB_USERNAME="your-actual-github-username"
argocd repo add https://github.com/YOUR_GITHUB_USERNAME/fedcompliance.git \
  --username YOUR_GITHUB_USERNAME \
  --password YOUR_PAT \
  --insecure-skip-server-verification

# Option B: Register with SSH deploy key
ssh-keygen -t ed25519 -f ~/.ssh/argocd_deploy_key -N "" -C "argocd@fedcompliance"

# Add the PUBLIC key to GitHub:
# GitHub → your repo → Settings → Deploy keys → Add deploy key → Allow read access
cat ~/.ssh/argocd_deploy_key.pub

# Register the repo with ArgoCD using the private key
argocd repo add git@github.com:YOUR_GITHUB_USERNAME/fedcompliance.git \
  --ssh-private-key-path ~/.ssh/argocd_deploy_key \
  --insecure-skip-server-verification
```

```bash
# Verify the repository is registered and reachable
argocd repo list
# Expected:
# TYPE  REPO                                              STATUS      MESSAGE
# git   https://github.com/.../fedcompliance.git         Successful
```

If STATUS is `Failed`, the MESSAGE column shows the specific error:
- PAT permissions: must have `repo` scope (read access to the repository)
- SSH key: confirm the public key is in GitHub Deploy Keys and marked "Allow read access"

---

### Step 24.11 — Create the ArgoCD Application Manifest By Hand

📍 **Bastion Terminal**

> **🧠 ELI5 — ArgoCD Application:** An ArgoCD "Application" is a custom Kubernetes resource (CRD) that tells ArgoCD: "the desired state of THIS cluster namespace should always match THIS path in THIS git repo." You write it as YAML (like any other K8s manifest), apply it to the cluster, and ArgoCD's application controller picks it up and starts watching.

```bash
mkdir -p ~/fedcompliance/argocd
```

Now create the Application manifest. Every field is explained inline:

```bash
cat > ~/fedcompliance/argocd/application.yaml << 'EOF'
# argocd/application.yaml — ArgoCD Application custom resource.
# Tells ArgoCD: watch this git repo at this path and keep
# the fedcompliance namespace in sync with it at all times.

apiVersion: argoproj.io/v1alpha1   # ArgoCD's API group — installed by the ArgoCD manifests
kind: Application
metadata:
  name: fedcompliance              # Name of this ArgoCD application (shown in the UI)
  namespace: argocd                # MUST be argocd — this is where ArgoCD watches for Applications
  labels:
    app: fedcompliance
    managed-by: argocd
spec:
  # Project groups applications for RBAC and access control.
  # "default" project allows all source repos and all destination clusters.
  # In production: create a named project with restricted permissions per team/environment.
  project: default

  source:
    # Your git repository URL — must match exactly what you registered in Step 24.10
    repoURL: https://github.com/YOUR_GITHUB_USERNAME/fedcompliance.git

    # Branch, tag, or commit SHA to track.
    # HEAD = always sync the latest commit on the default branch.
    # Pin to a tag (e.g., "v1.2.0") for production deployments that need explicit promotion.
    targetRevision: HEAD

    # Path within the repo where the Helm chart lives
    path: helm/fedcompliance

    # Helm-specific source configuration
    helm:
      # Values files to apply (in addition to the chart's default values.yaml).
      # Layer environment-specific overrides here without modifying the base chart.
      valueFiles:
        - values.yaml

      # Individual value overrides — equivalent to --set on the CLI.
      # image.tag is managed by Jenkins writing to values.yaml in git.
      # ArgoCD reads the tag from values.yaml — it does not set it here.
      parameters: []

  destination:
    # "https://kubernetes.default.svc" = the cluster where ArgoCD itself is running.
    # For multi-cluster setups, this would be an external cluster API server URL.
    server: https://kubernetes.default.svc
    # Target namespace — ArgoCD creates it if CreateNamespace=true is in syncOptions
    namespace: fedcompliance

  syncPolicy:
    automated:
      # prune: true = ArgoCD DELETES resources from the cluster that no longer exist in git.
      # This enforces git as the strict source of truth — no orphaned resources.
      # prune: false (default) = ArgoCD adds/updates but never deletes automatically.
      prune: true

      # selfHeal: true = if someone manually changes a resource in the cluster
      # (kubectl edit, kubectl scale, kubectl delete), ArgoCD reverts it to match git.
      # This is the enforcement mechanism for immutable GitOps infrastructure.
      selfHeal: true

    syncOptions:
      # Create destination namespace if it does not already exist
      - CreateNamespace=true
      # Use kubectl server-side apply — handles field ownership conflicts cleanly
      - ServerSideApply=true

  # Retry failed syncs with exponential backoff
  # Protects against transient API server errors or brief network issues
  retryStrategy:
    limit: 5
    backoff:
      duration: 5s        # Initial retry delay
      factor: 2           # Multiply delay by this factor each retry (5s, 10s, 20s, 40s, 80s)
      maxDuration: 3m     # Never wait longer than 3 minutes between retries
EOF
```

```bash
# Update the repoURL placeholder with your actual GitHub username
YOUR_GITHUB_USERNAME="your-actual-github-username"
sed -i "s|YOUR_GITHUB_USERNAME|${YOUR_GITHUB_USERNAME}|g" \
  ~/fedcompliance/argocd/application.yaml

grep "repoURL" ~/fedcompliance/argocd/application.yaml
# Verify it shows your actual repo URL
```

```bash
# Apply the Application manifest to the cluster
kubectl apply -f ~/fedcompliance/argocd/application.yaml
# Expected: application.argoproj.io/fedcompliance created

# Check initial status
argocd app get fedcompliance

# Wait for healthy status (first sync may take 30-60 seconds)
argocd app wait fedcompliance --health --timeout 120
# Expected: application 'fedcompliance' health is 'Healthy'

# Final status check
argocd app get fedcompliance
# SyncStatus:   Synced
# HealthStatus: Healthy
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Key ArgoCD Application fields:

| Field | What It Controls |
|-------|-----------------|
| `spec.source.repoURL` | The git repository ArgoCD watches |
| `spec.source.targetRevision` | Branch/tag/commit — HEAD = latest on the default branch |
| `spec.source.path` | Directory within the repo containing the Helm chart |
| `spec.destination.server` | Which Kubernetes cluster to deploy to |
| `spec.syncPolicy.automated.prune` | Whether ArgoCD deletes resources removed from git |
| `spec.syncPolicy.automated.selfHeal` | Whether ArgoCD reverts manual cluster changes |
| `spec.retryStrategy` | How many times to retry a failed sync before giving up |

</em></sub>

---

### Step 24.12 — Demo the GitOps Loop: Push a Change, Watch ArgoCD Auto-Sync

📍 **Bastion Terminal**

> This is the core GitOps demo. Change one value in `values.yaml`, push to git, and watch ArgoCD update the cluster — without running any kubectl or helm command.

```bash
cd ~/fedcompliance

# Change the replica count from 2 to 3
sed -i 's/^replicaCount: 2/replicaCount: 3/' helm/fedcompliance/values.yaml
grep "replicaCount" helm/fedcompliance/values.yaml
# Expected: replicaCount: 3

# Commit and push
git add helm/fedcompliance/values.yaml
git commit -m "scale fedcompliance to 3 replicas via values.yaml

GitOps demo: ArgoCD will detect this commit and sync the cluster
without any manual kubectl or helm command.
Every scaling decision is now documented in git with author and timestamp."

git push origin main
echo "Pushed at: $(date)"
```

```bash
# Trigger immediate ArgoCD sync (skips the default 3-minute poll cycle)
argocd app sync fedcompliance

# Watch the rollout
kubectl rollout status deployment/fedcompliance -n fedcompliance

# Confirm 3 pods are now running
kubectl get pods -n fedcompliance
# Expected: 3 pods, all Running

# ArgoCD sync history shows the git commit that triggered it
argocd app history fedcompliance
# Expected: shows your "scale fedcompliance to 3 replicas" commit
# with timestamp and git SHA — this is the audit trail
```

> **💼 Interview Insight — "Explain GitOps":** GitOps means using git as the single source of truth for your infrastructure and application state, with an automated operator continuously reconciling the cluster to match git. In my lab I use ArgoCD. The workflow is: I change `values.yaml` in git (replica count, image tag, resource limits) and push. ArgoCD detects the diff between git and the cluster within minutes and applies the change. Nobody runs `kubectl apply` or `helm upgrade` manually. Every change to the cluster is traceable to a git commit — author, timestamp, message, diff — without relying on CI logs. For a federal environment this satisfies NIST 800-53 CM-3 (Configuration Change Control) and AU-2 (Audit Events). Every deployment decision has a permanent record in git history.

---

### Step 24.13 — Update the Jenkins Pipeline for Helm + GitOps

📍 **Bastion Terminal**

> In the GitOps model, Jenkins only needs to: build the image, scan it, push it to OCIR, then commit the new image tag to `values.yaml` in git. ArgoCD handles the K8s deployment. The pipeline no longer needs `kubectl` at all.
>
> **CloudBees CI note:** If you're running CloudBees CI (from Phase 2 migration), the approval gate in this pipeline is governed by your folder-based RBAC — only users with the `platform-deployer` role can approve deployments. The audit trail logs every approval with timestamp, user, and IP. Consider importing the shared library (`@Library('oci-shared-lib') _`) and using the `federalPipeline` template from Step 23.13 to enforce security stages.

Pipeline changes from Phase 23:
- **REMOVED:** Stage 8 (kubectl apply + sed IMAGE_TAG) — ArgoCD replaces this entirely
- **REMOVED:** Stage 9 (smoke test via kubectl rollout status) — ArgoCD health check replaces this
- **NEW Stage 7:** Writes the new `image.tag` to `helm/fedcompliance/values.yaml` and pushes to git
- **NEW Stage 8:** Calls `argocd app sync` + `argocd app wait --health` to confirm deployment success

```bash
cat > ~/fedcompliance/Jenkinsfile << 'EOF'
pipeline {
    agent any

    environment {
        REGISTRY      = "us-ashburn-1.ocir.io"
        TENANCY_NS    = "<YOUR_TENANCY_NAMESPACE>"
        IMAGE_NAME    = "${REGISTRY}/${TENANCY_NS}/fedcompliance"
        IMAGE_TAG     = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()

        // Git config for the values.yaml commit in Stage 7.
        // Add a GitHub PAT to Jenkins as Secret text with ID "github-pat"
        // PAT must have "repo" scope (write access).
        GIT_REPO_URL  = "https://github.com/YOUR_GITHUB_USERNAME/fedcompliance.git"
        GIT_BRANCH    = "main"

        // ArgoCD server address: k3s node IP + NodePort from Step 24.9
        ARGOCD_APP    = "fedcompliance"
        ARGOCD_SERVER = "YOUR_K3S_NODE_IP:YOUR_ARGOCD_NODEPORT"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }

    stages {

        stage('1 - Checkout') {
            steps {
                checkout scm
                sh 'git log --oneline -3'
            }
        }

        stage('2 - Terraform Plan') {
            steps {
                withCredentials([file(credentialsId: 'oci-config', variable: 'OCI_CONFIG')]) {
                    dir('terraform') {
                        sh '''
                            mkdir -p ~/.oci
                            cp "${OCI_CONFIG}" ~/.oci/config
                            terraform init -input=false
                            terraform plan -out=tfplan -input=false
                        '''
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'terraform/tfplan', allowEmptyArchive: true
                }
            }
        }

        stage('3 - Build + Scan') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:scan-temp .

                    trivy image \
                        --exit-code 1 \
                        --severity CRITICAL,HIGH \
                        --format json \
                        --output trivy-report.json \
                        ${IMAGE_NAME}:scan-temp

                    echo "Trivy scan passed — no CRITICAL or HIGH CVEs"
                    docker tag ${IMAGE_NAME}:scan-temp ${IMAGE_NAME}:${IMAGE_TAG}
                    echo "Image tagged: ${IMAGE_NAME}:${IMAGE_TAG}"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
                }
            }
        }

        stage('4 - Generate SBOM') {
            steps {
                sh '''
                    syft ${IMAGE_NAME}:scan-temp \
                        -o spdx-json \
                        --file fedcompliance-sbom-${BUILD_NUMBER}.spdx.json
                    wc -l fedcompliance-sbom-${BUILD_NUMBER}.spdx.json
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'fedcompliance-sbom-*.spdx.json',
                                     allowEmptyArchive: true
                }
            }
        }

        stage('5 - Push to OCIR') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'ocir-credentials',
                        usernameVariable: 'OCIR_USER',
                        passwordVariable: 'OCIR_PASS'
                    )
                ]) {
                    sh '''
                        echo "${OCIR_PASS}" | docker login ${REGISTRY} \
                            -u "${OCIR_USER}" --password-stdin
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker rmi ${IMAGE_NAME}:scan-temp || true
                        echo "Successfully pushed: ${IMAGE_NAME}:${IMAGE_TAG}"
                    '''
                }
            }
        }

        stage('6 - Approval Gate') {
            steps {
                timeout(time: 2, unit: 'HOURS') {
                    input(
                        message: "Approve deployment of ${IMAGE_NAME}:${IMAGE_TAG} to k3s via ArgoCD?",
                        ok: 'Deployment APPROVED',
                        submitter: 'admin',
                        parameters: [
                            string(
                                name: 'CHANGE_TICKET',
                                description: 'Change ticket number (e.g., CHG-1042)',
                                defaultValue: ''
                            )
                        ]
                    )
                }
                echo "Deployment APPROVED. Committing image tag to git."
            }
        }

        // GitOps deploy trigger.
        // Instead of kubectl apply, Jenkins writes the new image tag to values.yaml
        // and commits + pushes to git. ArgoCD detects the commit and deploys to K8s.
        // Jenkins no longer needs kubectl or kubeconfig at all.
        stage('7 - Update Helm values.yaml') {
            steps {
                withCredentials([string(credentialsId: 'github-pat', variable: 'GH_PAT')]) {
                    sh '''
                        git config user.email "jenkins@fedcompliance-lab"
                        git config user.name "Jenkins CI"

                        # Update image.tag in values.yaml
                        sed -i "s|^  tag: .*|  tag: \\"${IMAGE_TAG}\\"|" \
                            helm/fedcompliance/values.yaml

                        grep "tag:" helm/fedcompliance/values.yaml
                        echo "values.yaml updated: image.tag = ${IMAGE_TAG}"

                        git add helm/fedcompliance/values.yaml
                        git commit -m "ci: deploy fedcompliance:${IMAGE_TAG}

Build:     #${BUILD_NUMBER}
Image:     ${IMAGE_NAME}:${IMAGE_TAG}
Trivy:     PASSED (no CRITICAL/HIGH CVEs)
SBOM:      fedcompliance-sbom-${BUILD_NUMBER}.spdx.json
ArgoCD:    will auto-sync this commit to the fedcompliance namespace"

                        // NOTE: YOUR_GITHUB_USERNAME below is replaced by the sed command in Step 24.12
                        git remote set-url origin https://${GH_PAT}@github.com/YOUR_GITHUB_USERNAME/fedcompliance.git
                        git push origin ${GIT_BRANCH}
                        echo "Pushed to git. ArgoCD will detect and sync."
                    '''
                }
            }
        }

        // Trigger an immediate ArgoCD sync (do not wait 3 minutes for auto-poll).
        // Then wait for the application to reach Healthy status before marking the build green.
        stage('8 - ArgoCD Sync + Health Check') {
            steps {
                withCredentials([string(credentialsId: 'argocd-admin-password', variable: 'ARGOCD_PASS')]) {
                    sh '''
                        argocd login ${ARGOCD_SERVER} \
                            --username admin \
                            --password "${ARGOCD_PASS}" \
                            --insecure

                        argocd app sync ${ARGOCD_APP} --timeout 120

                        argocd app wait ${ARGOCD_APP} \
                            --health \
                            --timeout 180

                        argocd app get ${ARGOCD_APP}
                        echo "ArgoCD sync complete — FedCompliance is Healthy"
                    '''
                }
            }
        }

    }

    post {
        success {
            echo "Pipeline SUCCESS — FedCompliance deployed via GitOps. Image: ${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "Pipeline FAILED at build #${BUILD_NUMBER} — review console output"
        }
        always {
            sh "docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true"
        }
    }
}
EOF
```

Add the two new Jenkins credentials this pipeline requires:

```bash
# In Jenkins UI → Manage Jenkins → Credentials → Global → Add Credentials:

# 1. "github-pat"
#    Kind: Secret text
#    ID: github-pat
#    Secret: <your GitHub Personal Access Token with repo write scope>

# 2. "argocd-admin-password"
#    Kind: Secret text
#    ID: argocd-admin-password
#    Secret: <ARGOCD_PASSWORD from Step 24.9>
```

Update placeholder values in the Jenkinsfile (replace with your actual values):
```bash
YOUR_GITHUB_USERNAME="your-actual-username"  # <-- replace this
YOUR_K3S_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
YOUR_ARGOCD_PORT=$(kubectl get svc argocd-server -n argocd \
  -o jsonpath='{.spec.ports[?(@.port==80)].nodePort}')

sed -i "s|YOUR_GITHUB_USERNAME|${YOUR_GITHUB_USERNAME}|g" ~/fedcompliance/Jenkinsfile
sed -i "s|YOUR_K3S_NODE_IP|${YOUR_K3S_IP}|g" ~/fedcompliance/Jenkinsfile
sed -i "s|YOUR_ARGOCD_NODEPORT|${YOUR_ARGOCD_PORT}|g" ~/fedcompliance/Jenkinsfile

echo "Jenkinsfile updated:"
grep -E "GIT_REPO_URL|ARGOCD_SERVER" ~/fedcompliance/Jenkinsfile
```

```bash
# Commit all Phase 24 changes
cd ~/fedcompliance
git add helm/ argocd/ Jenkinsfile
git status
# Should show: helm/fedcompliance/* and argocd/application.yaml and Jenkinsfile

git commit -m "phase-24: add Helm chart, ArgoCD Application, GitOps Jenkinsfile

- helm/fedcompliance/: complete Helm chart written by hand
  Chart.yaml, values.yaml, templates/{deployment,service,configmap,
  secret,namespace,NOTES.txt} with inline comments on every field
- argocd/application.yaml: ArgoCD Application with automated sync,
  selfHeal=true, prune=true, retryStrategy
- Jenkinsfile: updated to GitOps model — Stage 7 commits new image.tag
  to values.yaml; Stage 8 triggers ArgoCD sync and waits for Healthy.
  kubectl no longer called anywhere in the pipeline."

git push origin main
```

---

### Step 24.14 — Explore the ArgoCD UI

📍 **Browser** → `http://<k3s-node-ip>:<argocd-nodeport>`

```
Login: admin / <password from Step 24.9>
```

**What to look at and what each section means:**

| UI Section | What It Shows | What to Look For |
|-----------|--------------|-----------------|
| **Applications view** | All ArgoCD-managed apps as status cards | `fedcompliance` card: green = Synced+Healthy |
| **App detail — Summary** | Source (repo, path, branch), Destination, sync policy | Confirm `automated.selfHeal: true` is shown |
| **App detail — Sync Status** | Whether git and cluster match right now | `Synced` = cluster matches HEAD commit exactly |
| **App detail — Health** | Whether all child resources are healthy | `Healthy` = all pods Running, all services exist |
| **App detail — Resources tree** | Visual graph of all K8s resources the app manages | Namespace → Deployment → ReplicaSet → Pods |
| **App detail — Diff** | Side-by-side diff between git and live cluster state | Empty when synced; shows field changes when OutOfSync |
| **App detail — History** | All sync records with git SHA and timestamp | Your complete deployment audit trail |
| **App detail — Events** | K8s events for the application's resources | Use this to debug failed syncs |

**Try a manual drift demo:**

```bash
# Put the cluster out of sync intentionally
kubectl scale deployment fedcompliance -n fedcompliance --replicas=1

# Refresh the ArgoCD UI — app should show "OutOfSync"
# The Diff tab shows: git says replicas=3, cluster has replicas=1
# selfHeal=true means ArgoCD will revert this within ~3 minutes automatically
# Or click "Sync" in the UI to trigger it immediately

# Watch ArgoCD restore the replica count
sleep 180
kubectl get deployment fedcompliance -n fedcompliance \
  -o jsonpath='{.spec.replicas}'
# Expected: 3 (ArgoCD restored it from git)
```

> **💼 Interview Insight — "What is drift detection in ArgoCD?":** ArgoCD continuously compares the desired state in git against the actual state in the cluster. If they diverge — because someone ran kubectl manually, or a node event changed a resource — ArgoCD calls this "drift." With `selfHeal: true`, it automatically corrects drift by re-applying the git state. I tested this by manually scaling a deployment to 1 replica and watching ArgoCD restore it to 3 within minutes. For compliance, this means no manual change can persist without either being reflected in git or being overwritten by the reconciler — satisfying NIST 800-53 CM-5 (Access Restrictions for Change) and CM-6 (Configuration Settings).

---

### Step 24.15 — Rolling Update via values.yaml Change

📍 **Bastion Terminal**

> Complete end-to-end GitOps workflow. Make a change in git, push it, watch ArgoCD sync — no manual kubectl or helm commands.

```bash
cd ~/fedcompliance

# Change the log level from INFO to WARNING
sed -i 's/logLevel: "INFO"/logLevel: "WARNING"/' helm/fedcompliance/values.yaml
grep "logLevel" helm/fedcompliance/values.yaml
# Expected: logLevel: "WARNING"

git add helm/fedcompliance/values.yaml
git commit -m "config: set log level to WARNING for production

Reducing log verbosity to decrease log volume.
ArgoCD will sync this ConfigMap change and trigger a pod restart."

git push origin main
```

```bash
# Trigger immediate ArgoCD sync
argocd app sync fedcompliance

# Watch the ConfigMap update and pods restart
kubectl get pods -n fedcompliance --watch &
WATCH_PID=$!
sleep 60
kill $WATCH_PID 2>/dev/null

# Verify the ConfigMap was updated
kubectl get configmap fedcompliance-config -n fedcompliance -o yaml | grep LOG_LEVEL
# Expected: LOG_LEVEL: WARNING

# Verify the running pod has the new env var
kubectl exec -n fedcompliance \
  $(kubectl get pod -n fedcompliance -l app=fedcompliance -o name | head -1) \
  -- env | grep LOG_LEVEL
# Expected: LOG_LEVEL=WARNING
```

---

## PHASE 24 COMMAND REFERENCE

### Helm Commands

| Command | What It Does |
|---------|-------------|
| `helm lint <chart-path>` | Validates chart syntax and structure |
| `helm template <name> <chart-path> [--set key=val]` | Renders templates locally without connecting to K8s |
| `helm install <name> <chart-path> -n <namespace>` | Installs a new release (fails if name already exists) |
| `helm upgrade <name> <chart-path> -n <namespace>` | Upgrades an existing release |
| `helm upgrade --install <name> <chart-path>` | Installs if not present, upgrades if already installed — idempotent |
| `helm list -n <namespace>` | Lists all releases in the namespace |
| `helm status <name> -n <namespace>` | Shows release status and NOTES |
| `helm history <name> -n <namespace>` | Shows all revisions (installs + upgrades + rollbacks) |
| `helm rollback <name> <revision> -n <namespace>` | Restores a specific previous revision |
| `helm get values <name> -n <namespace>` | Shows the values used for the current release |
| `helm get manifest <name> -n <namespace>` | Shows the rendered Kubernetes YAML for the current release |
| `helm uninstall <name> -n <namespace>` | Removes the release and all managed resources |
| `helm repo add <name> <url>` | Registers a chart repository |
| `helm repo update` | Refreshes local chart repository cache |
| `helm search repo <keyword>` | Searches registered repos for matching charts |

### ArgoCD Commands

| Command | What It Does |
|---------|-------------|
| `argocd login <server>` | Authenticates the CLI to an ArgoCD server |
| `argocd app list` | Lists all ArgoCD applications with status |
| `argocd app get <name>` | Shows detailed status of an application |
| `argocd app sync <name>` | Triggers an immediate sync |
| `argocd app wait <name> --health` | Blocks until the application reaches Healthy status |
| `argocd app diff <name>` | Shows the diff between git state and cluster state |
| `argocd app history <name>` | Shows all sync records with timestamps and git SHAs |
| `argocd app rollback <name> <id>` | Rolls back to a specific sync history entry |
| `argocd app set <name> --sync-policy automated` | Enables auto-sync on an existing application |
| `argocd repo add <url>` | Registers a git repository with ArgoCD |
| `argocd repo list` | Lists all registered repositories and their status |
| `argocd cluster list` | Lists all clusters ArgoCD is managing |

---

## PHASE 24 COMPARISON TABLE

> **💼 Interview Insight — "What is the difference between raw kubectl, Helm, and Helm+ArgoCD?":**

| Dimension | Raw kubectl apply | Helm | Helm + ArgoCD (GitOps) |
|-----------|------------------|------|------------------------|
| **Deployment mechanism** | Manually apply each YAML file | `helm upgrade --install` renders templates atomically | Git push → ArgoCD detects diff → applies Helm chart |
| **Image tag management** | `sed -i IMAGE_TAG` string replacement | `--set image.tag=<sha>` or values.yaml | values.yaml committed to git; ArgoCD reads it |
| **Rollback** | `kubectl rollout undo` (Deployment only) | `helm rollback <name> <revision>` (entire release) | ArgoCD rollback from sync history OR helm rollback |
| **Release history** | Not tracked (only K8s events) | Tracked per release in K8s secrets | Tracked in git commits AND ArgoCD sync history |
| **Drift detection** | None — manual `kubectl diff` | None — manual `helm diff` plugin needed | Automatic — ArgoCD continuously reconciles |
| **Drift correction** | Manual | Manual `helm upgrade` | Automatic if `selfHeal: true` |
| **Multi-environment** | Separate directories + `sed` | `-f values-prod.yaml` overlay files | Separate ArgoCD Applications per environment |
| **Audit trail** | CI log (may be rotated) | Helm release history (in-cluster secret) | Git commit history (permanent) + ArgoCD sync history |
| **NIST CM-3 alignment** | Weak — no formal change record | Moderate — release history exists | Strong — every change is a git commit with author |
| **Pipeline complexity** | High — pipeline manages K8s | Medium — pipeline manages Helm | Low — pipeline manages image only; ArgoCD manages K8s |

---

## PHASE 24 TROUBLESHOOTING

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| **`helm install` fails: "cannot re-use a name that is still in use"** | A release named `fedcompliance` already exists | Use `helm upgrade --install` instead, or `helm uninstall fedcompliance -n fedcompliance` first |
| **`helm lint` fails: "parse error at (deployment.yaml:N)"** | Malformed Go template — unmatched `{{` or `}}` | Count template delimiters in the failing file. Common issue: `{{- range }}` without closing `{{- end }}` |
| **`helm template` renders `<nil>` for a value** | The path in `{{ .Values.X }}` does not exist in `values.yaml` | Check spelling exactly — YAML is case-sensitive. Run `helm get values fedcompliance -n fedcompliance` |
| **Pods stuck in `ImagePullBackOff` after Helm install** | OCIR pull secret not in the namespace, or wrong secret name | `kubectl get secret ocir-pull-secret -n fedcompliance`. Verify `values.imagePullSecrets[0].name` matches exactly |
| **`helm rollback` succeeds but pods still failing** | The revision you rolled back to also had a bad image | Run `helm history fedcompliance -n fedcompliance` and roll back to an earlier known-good revision |
| **`helm history` shows no entries** | Wrong namespace specified | Always pass `-n <namespace>`: `helm history fedcompliance -n fedcompliance` |
| **ArgoCD app shows `OutOfSync` immediately after install** | Initial sync not yet completed | Wait 30 seconds, then run `argocd app sync fedcompliance`. Check `argocd app diff fedcompliance` for details |
| **ArgoCD shows `Unknown` health status** | Pods not yet running | `kubectl get pods -n fedcompliance`. ArgoCD derives health from K8s conditions — Pending pods = Progressing |
| **ArgoCD `ComparisonError`: "helm not found"** | Unusual — ArgoCD repo-server missing Helm | Verify ArgoCD version: `argocd version`. Standard ArgoCD v2.x includes Helm 3 |
| **ArgoCD SSH repo connection fails** | Deploy key not in GitHub or wrong key | `cat ~/.ssh/argocd_deploy_key.pub` — compare with GitHub → repo → Settings → Deploy keys |
| **Jenkins Stage 7 fails: "git push rejected"** | Jenkins PAT expired or missing `repo` scope | Regenerate the GitHub PAT with `repo` scope. Update the `github-pat` Jenkins credential |
| **Jenkins Stage 8 fails: "argocd: command not found"** | ArgoCD CLI not on Jenkins executor PATH | `which argocd` on the bastion. Add `export PATH=$PATH:/usr/local/bin` to the Jenkins executor shell init |
| **ArgoCD app stuck in `Progressing` for >5 minutes** | Pods crashing (CrashLoopBackOff) | `kubectl describe pod -n fedcompliance -l app=fedcompliance` — Events section shows OOMKilled or startup errors |
| **ArgoCD `selfHeal` not reverting manual changes** | Reconciliation loop delayed (3 min default) | Wait 3-5 minutes. If still not reverting: `argocd app get fedcompliance` — check Conditions section for sync errors |
| **Jenkins Stage 7 `sed` does not update image.tag** | The `tag:` field format in values.yaml changed | Verify exact format: `  tag: "latest"` (two-space indent). Adjust the sed pattern to match the current format |

---

## PHASE 24 COMPLETE ✅

**What you built:**

- **Helm chart written entirely by hand:** `Chart.yaml` (metadata + versioning), `values.yaml` (all tunable config in one place), `templates/deployment.yaml` (Go-templated with inline reference), `templates/service.yaml`, `templates/configmap.yaml`, `templates/secret.yaml` with Vault annotation, `templates/namespace.yaml`, `templates/NOTES.txt`
- **Helm lifecycle exercised end-to-end:** install → upgrade → bad deploy (ImagePullBackOff) → rollback → recovery. You ran `helm history` and read the revision table.
- **ArgoCD installed on k3s:** all pods running, server exposed via NodePort, admin password retrieved, CLI authenticated
- **ArgoCD Application manifest written by hand:** every field (`source`, `destination`, `syncPolicy.automated`, `prune`, `selfHeal`, `retryStrategy`) explained with inline comments. Applied to cluster and confirmed Synced+Healthy.
- **GitOps loop demonstrated:** committed a `values.yaml` change to git → ArgoCD detected diff → synced cluster without any kubectl or helm command
- **`selfHeal` demonstrated:** manually scaled the deployment → ArgoCD restored it to the git-defined replica count automatically
- **Jenkins pipeline updated to 8 stages:** Stage 7 commits the new `image.tag` to `values.yaml` and pushes to git. Stage 8 triggers `argocd app sync` and waits for `Healthy`. Pipeline no longer runs `kubectl apply` — ArgoCD owns all K8s changes.
- **Comparison table built:** raw kubectl vs Helm vs Helm+ArgoCD across 10 dimensions including NIST CM-3 alignment

**What is running:**

- Jenkins on bastion (port 8080) — updated 8-stage GitOps pipeline
- ArgoCD on k3s (argocd namespace, NodePort accessible from bastion)
- FedCompliance managed by ArgoCD: every `git push` to `main` triggers a sync; every manual cluster change is reverted within minutes
- Helm release `fedcompliance` tracked in the `fedcompliance` namespace with full revision history

**Why this matters for the interview:**

- You can explain the **GitOps pattern** with a concrete example: "I pushed a replica count change to `values.yaml`, ArgoCD detected the diff within minutes and scaled the Deployment — no manual kubectl." This is not a talking point, it is something you actually did.
- You can explain **what Helm solves** by contrast: "Before Helm I used `sed -i IMAGE_TAG` to inject the image tag. Helm replaced that with a typed `values.yaml` field and gave me rollback as a first-class operation."
- You can describe the **audit trail improvement** for federal environments: every deployment is a git commit with author, timestamp, and diff — satisfying NIST 800-53 CM-3 without relying on CI logs.
- You have run `helm rollback` in a real failure scenario (pods in ImagePullBackOff) and recovered the application in under 60 seconds. This is a specific, credible answer to "have you handled a failed deployment?"
- You understand **ArgoCD's selfHeal behavior** and its compliance implications: no manual change to the cluster persists without a corresponding git commit. This is continuously-enforced immutable infrastructure.

**Next phase (Day 3 — Phase 25):** Observability — install the kube-prometheus-stack via Helm (using the community chart this time), instrument FedCompliance with Prometheus metrics (`/metrics` endpoint), create a Grafana dashboard tracking request latency and error rate, and set up an alerting rule that fires when error rate exceeds 5% — completing the production-readiness picture alongside the security and delivery layers already in place.

---

---

## PHASE 25: AI-AUGMENTED OPERATIONS & COMPLIANCE (6-8 hrs)

**Day 4 - What you are building:** An AI layer on top of the pipeline and running cluster. You will write a Python OCI Function that ingests application logs, run classical machine-learning anomaly detection with scikit-learn IsolationForest, and build a compliance-as-code evidence collector that queries OCI APIs directly and outputs a CMMC control-mapping report. The compliance collector also becomes a new stage in your Jenkins pipeline.

> **Why this matters:** Federal cloud engineers are increasingly expected to automate evidence collection for audits and to instrument workloads with lightweight security analytics. This phase shows you can bridge DevSecOps tooling, cloud APIs, and ML-based pattern detection - all in Python, all auditable.

---

### Phase 25 Architecture - What You Are Building Today

```
app_logs (OCI Object Storage)
        |
        v
[OCI Function: log-processor]  <--- fn CLI invoke
        |  reads raw logs
        |  writes summary JSON back to Object Storage
        v
[security_detector.py]  (runs on bastion VM)
        |  pulls summary JSON
        |  IsolationForest anomaly scoring
        |  rule engine (brute-force, priv-esc patterns)
        |  writes security_digest.json
        v
[compliance_collector.py]  (runs on bastion VM + Jenkins stage)
        |  queries OCI IAM, VCN Security Lists, KMS, Audit
        |  maps findings to CMMC controls
        |  writes cmmc_evidence_report.json
        v
Jenkins Stage 10: Compliance Evidence
        |  runs compliance_collector.py
        |  archives report as build artifact
```

---

### Step 25.1 - Prepare the OCI Functions Application (Return Visit)

**Location:** Bastion VM - `~/oci-fn/`

You set up the fn CLI context in Phase 22. This step creates the application container and Python function skeleton.

```bash
# Confirm fn CLI context is set
fn list context

# Create the Functions application (one-time, per compartment)
fn create app log-processor-app \
  --annotation oracle.com/oci/subnetIds='["<your-private-subnet-ocid>"]'

# Create the function project directory
mkdir -p ~/oci-fn/log-processor
cd ~/oci-fn/log-processor

# Initialize a Python function
# Note: This is the OCI Functions platform runtime, separate from the VM's Python version
fn init --runtime python3.11 log-processor
cd log-processor
ls
# You should see: func.py  func.yaml  requirements.txt
```

> **What fn init gives you:** A `func.py` with a `handler(ctx, data)` entry point, a `func.yaml` declaring the function name/runtime/memory, and a `requirements.txt`. You will rewrite `func.py` entirely by hand.

---

### Step 25.2 - Write the Log Processor Function by Hand

**Location:** Bastion VM - `~/oci-fn/log-processor/log-processor/func.py`

Open `func.py` and replace its contents section by section.

**Section 1 - Imports and OCI client setup:**

```python
import io
import json
import logging
import os
from datetime import datetime, timezone

import oci
from fdk import response

logger = logging.getLogger(__name__)

def _get_object_storage_client():
    signer = oci.auth.signers.get_resource_principals_signer()
    return oci.object_storage.ObjectStorageClient({}, signer=signer)
```

**Section 2 - Log parsing helper:**

```python
def _parse_log_line(line: str) -> dict | None:
    # Expects: 2026-03-20T14:32:01Z INFO src=10.0.1.45 method=GET status=200 latency_ms=12
    # Returns a dict or None if the line cannot be parsed.
    parts = line.strip().split()
    if len(parts) < 5:
        return None
    try:
        record = {"timestamp": parts[0], "level": parts[1]}
        for token in parts[2:]:
            if "=" in token:
                k, v = token.split("=", 1)
                record[k] = v
        return record
    except Exception:
        return None
```

**Section 3 - Aggregation logic:**

```python
def _aggregate(records: list[dict]) -> dict:
    # Produce a summary dict from a list of parsed log records.
    total = len(records)
    errors = sum(1 for r in records if r.get("level") in ("ERROR", "WARN"))
    status_counts: dict[str, int] = {}
    source_ips: set[str] = set()
    latencies: list[float] = []

    for r in records:
        sc = r.get("status", "unknown")
        status_counts[sc] = status_counts.get(sc, 0) + 1
        if "src" in r:
            source_ips.add(r["src"])
        if "latency_ms" in r:
            try:
                latencies.append(float(r["latency_ms"]))
            except ValueError:
                pass

    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
    p95_latency = 0.0
    if latencies:
        latencies.sort()
        idx = int(len(latencies) * 0.95)
        p95_latency = round(latencies[min(idx, len(latencies) - 1)], 2)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_log_lines": total,
        "error_warn_count": errors,
        "error_rate_pct": round((errors / total * 100), 2) if total else 0.0,
        "status_code_counts": status_counts,
        "unique_source_ips": sorted(source_ips),
        "avg_latency_ms": avg_latency,
        "p95_latency_ms": p95_latency,
    }
```

**Section 4 - Handler entry point:**

```python
def handler(ctx, data: io.BytesIO = None):
    # Triggered by OCI Events rule or manual fn invoke.
    # Reads all logs/ prefix objects, aggregates, writes summary JSON.
    namespace = os.environ.get("OCI_NAMESPACE")
    bucket    = os.environ.get("LOG_BUCKET", "app_logs")
    client    = _get_object_storage_client()

    list_resp = client.list_objects(namespace, bucket, prefix="logs/")
    objects = list_resp.data.objects or []

    all_records: list[dict] = []
    for obj in objects:
        content = client.get_object(namespace, bucket, obj.name).data.text
        for line in content.splitlines():
            parsed = _parse_log_line(line)
            if parsed:
                all_records.append(parsed)

    summary = _aggregate(all_records)
    summary_bytes = json.dumps(summary, indent=2).encode("utf-8")
    output_name = f"summaries/summary_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}.json"
    client.put_object(namespace, bucket, output_name, io.BytesIO(summary_bytes))

    logger.info("Wrote summary to %s/%s/%s", bucket, namespace, output_name)
    return response.Response(
        ctx,
        response_data=json.dumps({"status": "ok", "output": output_name}),
        headers={"Content-Type": "application/json"},
    )
```

**Update `requirements.txt`:**

```
fdk>=0.1.67
oci>=2.126.0
```

---

### Step 25.3 - Configure func.yaml and Deploy

**Location:** Bastion VM - `~/oci-fn/log-processor/log-processor/func.yaml`

```yaml
schema_version: 20180708
name: log-processor
version: 0.0.1
runtime: python3.11          # Note: This is the OCI Functions platform runtime, separate from the VM's Python version
build_image: fnproject/python:3.11-dev
run_image: fnproject/python:3.11
entrypoint: /python/bin/fdk log_processor.func.handler
memory: 256
timeout: 120
config:
  OCI_NAMESPACE: <your-tenancy-namespace>
  LOG_BUCKET: app_logs
```

```bash
# Deploy - fn CLI builds the Docker image and pushes to OCIR
fn --verbose deploy --app log-processor-app

# Invoke manually to test
fn invoke log-processor-app log-processor
```

**Verification:**

```bash
oci os object list --bucket-name app_logs --prefix summaries/ --output table
```

---

### Step 25.4 - ELI5: What is IsolationForest?

> **ELI5 - IsolationForest**
>
> Imagine you have a bag full of marbles, and most are ordinary glass marbles - but a few are oddly shaped. If you reach in blindly and try to separate one marble from the others by drawing random lines, the weird ones are much easier to isolate (it takes fewer cuts) than the ordinary ones.
>
> IsolationForest does exactly that with data. It builds many random decision trees and counts how many "cuts" (splits) it takes to isolate each data point. Normal points blend in and need many cuts. Anomalies stick out and need very few.
>
> **In practice:** Each log record becomes a row of numbers (error count, latency, requests per minute, hour of day). IsolationForest scores every row. Scores close to -1 are anomalies; scores near +1 are normal. You set a threshold (e.g., score < -0.1 means flag it).
>
> **Why classical ML instead of an LLM here?** IsolationForest is deterministic, runs in milliseconds on a VM with no GPU, requires no internet call, produces auditable scores, and has no hallucination risk. For anomaly detection on structured numerical log features, it outperforms an LLM in every operational dimension that matters in a federal environment.

---

### Step 25.5 - Write the Security Pattern Detector by Hand

**Location:** Bastion VM - `~/scripts/security_detector.py`

```bash
mkdir -p ~/scripts
```

Write the script section by section.

**Section 1 - Imports and config:**

```python
#!/usr/bin/env python3
# security_detector.py
# Pulls log summaries from Object Storage, runs IsolationForest anomaly
# detection, applies a rule engine for known-bad patterns, writes a
# security digest back to Object Storage.
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import oci
from sklearn.ensemble import IsolationForest

NAMESPACE     = os.environ.get("OCI_NAMESPACE", "")
BUCKET        = os.environ.get("LOG_BUCKET", "app_logs")
DIGEST_KEY    = "digests/security_digest_latest.json"
CONTAMINATION = float(os.environ.get("IF_CONTAMINATION", "0.05"))
```

**Section 2 - OCI client (instance principal with config fallback):**

```python
def get_os_client() -> oci.object_storage.ObjectStorageClient:
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        return oci.object_storage.ObjectStorageClient({}, signer=signer)
    except Exception:
        return oci.object_storage.ObjectStorageClient(oci.config.from_file())
```

**Section 3 - Load all summaries from Object Storage:**

```python
def load_summaries(client, namespace: str, bucket: str) -> list[dict]:
    resp = client.list_objects(namespace, bucket, prefix="summaries/")
    summaries = []
    for obj in resp.data.objects or []:
        raw = client.get_object(namespace, bucket, obj.name).data.text
        summaries.append(json.loads(raw))
    return summaries
```

**Section 4 - Feature extraction (5 numerical features per summary):**

```python
def build_feature_matrix(summaries: list[dict]) -> tuple[np.ndarray, list[dict]]:
    # Features: [error_rate_pct, avg_latency_ms, p95_latency_ms,
    #            unique_ip_count, total_log_lines]
    rows, valid = [], []
    for s in summaries:
        try:
            rows.append([
                float(s.get("error_rate_pct", 0)),
                float(s.get("avg_latency_ms", 0)),
                float(s.get("p95_latency_ms", 0)),
                float(len(s.get("unique_source_ips", []))),
                float(s.get("total_log_lines", 0)),
            ])
            valid.append(s)
        except (TypeError, ValueError):
            continue
    return np.array(rows, dtype=float), valid
```

**Section 5 - IsolationForest scoring:**

```python
def run_isolation_forest(X: np.ndarray, contamination: float) -> np.ndarray:
    # score_samples() returns lower values for anomalies.
    # We negate so higher = more anomalous (easier threshold logic).
    # Returns zeros if fewer than 5 samples (not enough data to train).
    if len(X) < 5:
        return np.zeros(len(X))
    clf = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    clf.fit(X)
    return -clf.score_samples(X)
```

**Section 6 - Rule engine for known-bad patterns:**

```python
BRUTE_FORCE_THRESHOLD = 5     # distinct source IPs in one summary window
HIGH_ERROR_RATE       = 20.0  # percent

def apply_rule_engine(summary: dict) -> list[str]:
    alerts = []
    if summary.get("error_rate_pct", 0) >= HIGH_ERROR_RATE:
        alerts.append("HIGH_ERROR_RATE")
    if len(summary.get("unique_source_ips", [])) >= BRUTE_FORCE_THRESHOLD:
        alerts.append("POTENTIAL_BRUTE_FORCE")
    status_codes = summary.get("status_code_counts", {})
    forbidden = int(status_codes.get("403", 0)) + int(status_codes.get("401", 0))
    total     = max(summary.get("total_log_lines", 1), 1)
    if forbidden / total >= 0.10:
        alerts.append("PRIVILEGE_ESC_INDICATOR")
    return alerts
```

**Section 7 - Digest assembly and main:**

```python
def build_digest(summaries: list[dict], scores: np.ndarray) -> dict:
    ANOMALY_THRESHOLD = 0.55
    flagged = []
    for s, score in zip(summaries, scores):
        rules = apply_rule_engine(s)
        is_anomaly = float(score) > ANOMALY_THRESHOLD
        if is_anomaly or rules:
            flagged.append({
                "summary_generated_at": s.get("generated_at"),
                "anomaly_score": round(float(score), 4),
                "is_ml_anomaly": is_anomaly,
                "triggered_rules": rules,
                "error_rate_pct": s.get("error_rate_pct"),
                "unique_ip_count": len(s.get("unique_source_ips", [])),
            })
    return {
        "digest_generated_at": datetime.now(timezone.utc).isoformat(),
        "total_summaries_analyzed": len(summaries),
        "flagged_windows": len(flagged),
        "contamination_setting": CONTAMINATION,
        "findings": flagged,
    }

def main():
    if not NAMESPACE:
        sys.exit("ERROR: Set OCI_NAMESPACE environment variable")
    client = get_os_client()
    print("[*] Loading summaries from Object Storage...")
    summaries = load_summaries(client, NAMESPACE, BUCKET)
    if not summaries:
        print("[!] No summaries found. Run the log-processor function first.")
        sys.exit(0)
    print(f"[*] Loaded {len(summaries)} summaries. Building feature matrix...")
    X, valid_summaries = build_feature_matrix(summaries)
    print("[*] Running IsolationForest...")
    scores = run_isolation_forest(X, CONTAMINATION)
    digest = build_digest(valid_summaries, scores)
    import io as _io
    digest_bytes = json.dumps(digest, indent=2).encode("utf-8")
    client.put_object(NAMESPACE, BUCKET, DIGEST_KEY, _io.BytesIO(digest_bytes))
    print(f"[+] Security digest written to {BUCKET}/{DIGEST_KEY}")
    print(f"    Summaries analyzed : {digest['total_summaries_analyzed']}")
    print(f"    Flagged windows    : {digest['flagged_windows']}")

if __name__ == "__main__":
    main()
```

**Install dependencies:**

```bash
# Linux/macOS/WSL2:
python3 -m pip install scikit-learn numpy oci --user

# Windows (if python3 not found, use python):
# python -m pip install scikit-learn numpy oci --user
```

**Run and verify:**

```bash
export OCI_NAMESPACE=$(oci os ns get --query 'data' --raw-output)
export LOG_BUCKET=app_logs
python3 ~/scripts/security_detector.py
oci os object get --bucket-name app_logs \
  --name digests/security_digest_latest.json \
  --file /tmp/digest.json
cat /tmp/digest.json
```

---

### Step 25.6 - ELI5: What is Compliance-as-Code?

> **ELI5 - Compliance-as-Code**
>
> In traditional IT audits, a compliance officer walks through a checklist by hand: "Is encryption enabled? Show me a screenshot." This takes days, happens once a year, and the screenshots are outdated the moment the audit ends.
>
> Compliance-as-code means you write a program that asks the cloud APIs those same questions programmatically and records the answers as structured data. The program can run every day (or in every CI/CD pipeline run), so your evidence is always current.
>
> For example, instead of "log into the OCI console and screenshot the KMS vault," you write Python that calls `oci.key_management.KmsVaultClient.list_vaults()` and checks that at least one vault exists and is ACTIVE. The output is a JSON file that says "Control SC-28 (encryption at rest): PASS - vault ocid1.vault... is ACTIVE." That JSON file is your audit artifact.
>
> **CMMC context:** CMMC 2.0 Level 2 maps directly to NIST 800-171 practices. For a federal contractor cloud environment, you need evidence for controls like AC-2 (account management), SC-28 (protection at rest), AU-2 (audit events). Your compliance collector checks the OCI-side settings that satisfy these controls.

---

### Step 25.7 - Write the Compliance Evidence Collector by Hand

**Location:** Bastion VM - `~/scripts/compliance_collector.py`

Write section by section.

**Section 1 - Imports and control catalog:**

```python
#!/usr/bin/env python3
# compliance_collector.py
# Queries OCI APIs and maps findings to CMMC 2.0 / NIST 800-171 controls.
# Outputs a JSON evidence report.
import json
import os
import sys
from datetime import datetime, timezone
import oci

CONTROLS = {
    "AC.1.001": "Limit system access to authorized users",
    "AC.1.002": "Limit system access to permitted transactions",
    "AU.2.041": "Ensure audit log coverage for defined events",
    "IA.1.076": "Identify information system users",
    "SC.3.177": "Employ FIPS-validated cryptography",
    "SC.1.175": "Monitor, control, and protect communications",
    "CM.2.061": "Establish and maintain baseline configurations",
    "SI.1.210": "Identify, report, and correct information system flaws",
}
```

**Section 2 - OCI client factory with instance principal / config fallback:**

```python
COMPARTMENT_ID = os.environ.get("OCI_COMPARTMENT_ID", "")
REGION         = os.environ.get("OCI_REGION", "us-ashburn-1")
BUCKET         = os.environ.get("LOG_BUCKET", "app_logs")
NAMESPACE      = os.environ.get("OCI_NAMESPACE", "")

def _signer_and_config():
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        return {}, signer
    except Exception:
        return oci.config.from_file(), None

def make_client(ClientClass):
    cfg, signer = _signer_and_config()
    return ClientClass(cfg, signer=signer) if signer else ClientClass(cfg)
```

**Section 3 - IAM policy check (AC.1.001, AC.1.002):**

```python
def check_iam_policies() -> dict:
    # Detect overly-broad IAM statements. Maps to AC.1.001 / AC.1.002.
    client = make_client(oci.identity.IdentityClient)
    try:
        resp = client.list_policies(COMPARTMENT_ID)
        policies = resp.data or []
        overly_broad = []
        for p in policies:
            for stmt in (p.statements or []):
                lower = stmt.lower()
                if "any-user" in lower and "manage all-resources" in lower:
                    overly_broad.append({"policy_name": p.name, "statement": stmt})
        return {
            "control": "AC.1.001 / AC.1.002",
            "status": "FAIL" if overly_broad else "PASS",
            "policy_count": len(policies),
            "overly_broad_statements": overly_broad,
            "detail": f"Found {len(policies)} policies; {len(overly_broad)} overly-broad statements.",
        }
    except Exception as e:
        return {"control": "AC.1.001 / AC.1.002", "status": "ERROR", "detail": str(e)}
```

**Section 4 - Audit log retention check (AU.2.041):**

```python
def check_audit_config() -> dict:
    # Verify tenancy-level audit log retention >= 365 days. Maps to AU.2.041.
    client = make_client(oci.audit.AuditClient)
    try:
        cfg, _ = _signer_and_config()
        tenancy_id = cfg.get("tenancy", COMPARTMENT_ID)
        retention_days = client.get_configuration(tenancy_id).data.retention_period_days or 0
        return {
            "control": "AU.2.041",
            "status": "PASS" if retention_days >= 365 else "FAIL",
            "retention_period_days": retention_days,
            "detail": f"Audit log retention: {retention_days} days (required: >=365).",
        }
    except Exception as e:
        return {"control": "AU.2.041", "status": "ERROR", "detail": str(e)}
```

**Section 5 - KMS vault check (SC.3.177):**

```python
def check_kms_vaults() -> dict:
    # Verify at least one active KMS vault exists. Maps to SC.3.177.
    try:
        cfg, signer = _signer_and_config()
        vaults_client = (oci.key_management.KmsVaultClient(cfg, signer=signer)
                         if signer else oci.key_management.KmsVaultClient(cfg))
        active = [v for v in (vaults_client.list_vaults(COMPARTMENT_ID).data or [])
                  if v.lifecycle_state == "ACTIVE"]
        return {
            "control": "SC.3.177",
            "status": "PASS" if active else "FAIL",
            "active_vault_count": len(active),
            "vault_ids": [v.id for v in active],
            "detail": f"{len(active)} active KMS vault(s) found.",
        }
    except Exception as e:
        return {"control": "SC.3.177", "status": "ERROR", "detail": str(e)}
```

**Section 6 - Security list ingress check (SC.1.175):**

```python
def check_security_lists() -> dict:
    # Detect sensitive ports open to 0.0.0.0/0. Maps to SC.1.175.
    SENSITIVE_PORTS = {22, 3389, 5432, 6443}
    client = make_client(oci.core.VirtualNetworkClient)
    try:
        violations = []
        for sl in (client.list_security_lists(COMPARTMENT_ID).data or []):
            for rule in (sl.ingress_security_rules or []):
                src = getattr(rule, "source", "") or ""
                tcp = getattr(rule, "tcp_options", None)
                if src in ("0.0.0.0/0", "::/0"):
                    if tcp is None:
                        violations.append({"security_list": sl.display_name,
                                           "issue": "All TCP ports open to 0.0.0.0/0"})
                    elif tcp.destination_port_range:
                        lo = tcp.destination_port_range.min or 0
                        hi = tcp.destination_port_range.max or 65535
                        for p in SENSITIVE_PORTS:
                            if lo <= p <= hi:
                                violations.append({"security_list": sl.display_name,
                                                   "port": p,
                                                   "issue": f"Port {p} open to 0.0.0.0/0"})
        return {
            "control": "SC.1.175",
            "status": "FAIL" if violations else "PASS",
            "violation_count": len(violations),
            "violations": violations,
            "detail": f"{len(violations)} network exposure finding(s).",
        }
    except Exception as e:
        return {"control": "SC.1.175", "status": "ERROR", "detail": str(e)}
```

**Section 7 - Main report assembly and upload:**

```python
def main():
    if not COMPARTMENT_ID:
        sys.exit("ERROR: Set OCI_COMPARTMENT_ID environment variable")
    if not NAMESPACE:
        sys.exit("ERROR: Set OCI_NAMESPACE environment variable")

    print("[*] Running compliance evidence collection...")
    checks = [
        check_iam_policies(),
        check_audit_config(),
        check_kms_vaults(),
        check_security_lists(),
    ]

    pass_count = sum(1 for c in checks if c.get("status") == "PASS")
    fail_count = sum(1 for c in checks if c.get("status") == "FAIL")
    err_count  = sum(1 for c in checks if c.get("status") == "ERROR")

    report = {
        "report_generated_at": datetime.now(timezone.utc).isoformat(),
        "framework": "CMMC 2.0 Level 2 / NIST 800-171",
        "compartment_id": COMPARTMENT_ID,
        "summary": {
            "total_checks": len(checks),
            "pass": pass_count,
            "fail": fail_count,
            "error": err_count,
            "overall_status": "COMPLIANT" if fail_count == 0 and err_count == 0 else "NON-COMPLIANT",
        },
        "control_findings": checks,
        "controls_catalog": CONTROLS,
    }

    local_path = "/tmp/cmmc_evidence_report.json"
    with open(local_path, "w") as fh:
        json.dump(report, fh, indent=2)
    print(f"[+] Report written to {local_path}")

    import io as _io
    client = make_client(oci.object_storage.ObjectStorageClient)
    key = f"compliance/cmmc_evidence_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}.json"
    client.put_object(NAMESPACE, BUCKET, key,
                      _io.BytesIO(json.dumps(report, indent=2).encode("utf-8")))
    print(f"[+] Uploaded: {BUCKET}/{key}")
    print(f"\n{'='*55}")
    print(f"  Overall: {report['summary']['overall_status']}")
    print(f"  PASS: {pass_count}  FAIL: {fail_count}  ERROR: {err_count}")
    print(f"{'='*55}")
    sys.exit(1 if fail_count > 0 else 0)

if __name__ == "__main__":
    main()
```

**Run and verify:**

```bash
export OCI_COMPARTMENT_ID=$(oci iam compartment list --query 'data[0].id' --raw-output)
export OCI_NAMESPACE=$(oci os ns get --query 'data' --raw-output)
python3 ~/scripts/compliance_collector.py
cat /tmp/cmmc_evidence_report.json | python3 -m json.tool | head -40
```

---

### Step 25.8 - Add Compliance Evidence as Jenkins Pipeline Stage

**Location:** Bastion VM - `~/fedcompliance-app/Jenkinsfile`

Open the Jenkinsfile and add Stage 10 after the existing Stage 9 (ArgoCD sync trigger):

```groovy
        stage('10 - Compliance Evidence') {
            steps {
                sshagent(['bastion-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no opc@${BASTION_IP} '
                            export OCI_COMPARTMENT_ID=\$(oci iam compartment list \\
                              --query "data[0].id" --raw-output)
                            export OCI_NAMESPACE=\$(oci os ns get --query "data" --raw-output)
                            export LOG_BUCKET=app_logs
                            python3 ~/scripts/compliance_collector.py
                        '
                        scp opc@${BASTION_IP}:/tmp/cmmc_evidence_report.json ./
                    """
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'cmmc_evidence_report.json', fingerprint: true
                }
                failure {
                    echo 'Compliance check found FAIL or ERROR findings - review cmmc_evidence_report.json'
                }
            }
        }
```

> **What this does:** Every pipeline run now ends with a compliance snapshot. The JSON report is archived as a Jenkins build artifact alongside the Trivy CVE report and SBOM. An auditor can pull any build and see exactly what the security posture was at deploy time.

**Commit and push:**

```bash
cd ~/fedcompliance-app
git add Jenkinsfile
git commit -m "ci: add Stage 10 compliance evidence collection"
git push origin main
```

Trigger a build in Jenkins and confirm the `cmmc_evidence_report.json` artifact appears in the build's Archive section.

---

### Step 25.9 - Verification Checklist

```bash
# 1. OCI Function deployed
fn list functions log-processor-app

# 2. Log processor produced a summary object
oci os object list --bucket-name app_logs --prefix summaries/ --output table

# 3. Security detector produced a digest
oci os object list --bucket-name app_logs --prefix digests/ --output table

# 4. Compliance report uploaded to Object Storage
oci os object list --bucket-name app_logs --prefix compliance/ --output table

# 5. Jenkins Stage 10 artifact present
# Jenkins UI -> Build -> Artifacts -> cmmc_evidence_report.json
```

---

### Step 25.10 - Interview Insight: Classical ML vs LLM

> **Interview Insight - "Why not just use an LLM for log analysis?"**
>
> A strong answer covers four dimensions:
>
> **1. Latency and cost.** IsolationForest scores 10,000 log records in under a second on a single CPU core with no network call. An LLM API call takes 1-5 seconds and costs money per token. In a CI/CD pipeline gate that runs on every commit, that difference matters.
>
> **2. Determinism and auditability.** IsolationForest with `random_state=42` produces the same score for the same input every time. An LLM is non-deterministic and its reasoning is not inspectable. In a FedRAMP or CMMC audit you need to explain exactly why a specific log window was flagged - a numerical anomaly score from a documented algorithm satisfies that requirement; "the LLM said it looked suspicious" does not.
>
> **3. Data residency.** Sending log data containing IP addresses and access patterns to a third-party LLM API may violate CUI handling requirements. IsolationForest runs entirely on your infrastructure.
>
> **4. The right tool for the task.** Anomaly detection on structured numerical features is a textbook ML problem. LLMs excel at unstructured reasoning - e.g., "given this security digest, draft an incident report." The correct architecture uses both: classical ML to score, LLM (if available and accredited) to narrate.

---

### Step 25.11 - Interview Insight: What is Compliance-as-Code?

> **Interview Insight - "What is compliance-as-code and have you implemented it?"**
>
> "Compliance-as-code is the practice of expressing security control requirements as executable checks rather than static documents, so that compliance evidence is generated automatically and continuously instead of manually and periodically.
>
> In this project I wrote `compliance_collector.py` - a Python script that queries the OCI APIs directly: it inspects IAM policy statements for overly-broad grants, checks audit log retention against the 365-day requirement, verifies KMS vault existence for encryption-at-rest evidence, and scans security list rules for sensitive port exposure. Each check maps to a named NIST 800-171 control. The output is a structured JSON report that serves as an audit artifact.
>
> The key operational benefit is that this script runs as Stage 10 of the Jenkins pipeline on every merge to main. Every deployment produces a fresh evidence snapshot automatically - rather than requiring someone to manually collect screenshots before an audit. The JSON report is archived in Jenkins alongside the Trivy CVE scan and SBOM, giving you a complete per-build security evidence package."

---

### Step 25.12 - Phase 25 Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `fn deploy` fails with image push denied | OCIR auth token expired or fn context region mismatch | Re-run `docker login <region>.ocir.io` and confirm `fn list context` shows correct registry |
| `fn invoke` returns 502 or function timeout | OCI Function cannot reach Object Storage (resource principal not granted) | Add dynamic group rule: `resource.type = 'fnfunc'`; add policy: `allow dynamic-group fn-group to manage objects in compartment <name>` |
| IsolationForest gives all scores near 0 | Fewer than 5 summary records (cold start) | Generate more data by invoking the function multiple times; the code skips scoring for fewer than 5 records |
| False positive rate too high | `contamination` value too high | Lower `IF_CONTAMINATION` env var (try `0.01`); contamination is the expected fraction of outliers |
| `compliance_collector.py` raises NotAuthenticated | Running outside OCI with no `~/.oci/config` | Run `oci setup config` or set `OCI_CLI_AUTH=instance_principal` on the bastion |
| OCI pagination: only first 100 objects returned | `list_objects` default limit is 100 | Add pagination loop: check `resp.data.next_start_with` and repeat call until `None` |
| Jenkins Stage 10 marks build UNSTABLE not FAIL | `compliance_collector.py` exits 0 even on FAIL findings | Confirm `sys.exit(1 if fail_count > 0 else 0)` is present in the script |

---

### Step 25 Command Reference

| Command | Purpose |
|---|---|
| `fn list context` | Show fn CLI OCI context |
| `fn deploy --app log-processor-app` | Build and push function image, update function config |
| `fn invoke log-processor-app log-processor` | Manually trigger the function |
| `oci os object list --bucket-name app_logs --prefix summaries/` | List generated log summaries |
| `python3 ~/scripts/security_detector.py` | Run IsolationForest anomaly detection |
| `python3 ~/scripts/compliance_collector.py` | Run CMMC compliance evidence collection |
| `oci os object list --bucket-name app_logs --prefix compliance/` | List uploaded compliance reports |
| `cat /tmp/cmmc_evidence_report.json \| python3 -m json.tool` | Pretty-print local compliance report |

---

### Phase 25 Complete

**What you built:**
- An OCI Function (`log-processor`) written from scratch in Python 3.11 that ingests raw application logs from Object Storage, aggregates them into summary metrics, and writes structured JSON summaries back to the same bucket
- A scikit-learn IsolationForest anomaly detector (`security_detector.py`) that scores numerical log features and flags unusual windows, augmented by a deterministic rule engine for known-bad patterns (high error rate, brute-force indicators, privilege escalation signals)
- A compliance-as-code evidence collector (`compliance_collector.py`) that queries four OCI API surfaces - IAM, Audit, KMS, and VCN - and maps findings to named NIST 800-171 / CMMC 2.0 controls, outputting a per-run JSON report
- Jenkins Stage 10 that runs the compliance collector on every pipeline execution and archives the JSON report as a build artifact alongside the CVE scan and SBOM

**Why this matters for the interview:**
- You can explain classical ML anomaly detection (IsolationForest) and articulate exactly why it is preferable to an LLM for structured log scoring in a federal environment: determinism, auditability, data residency, cost
- You can define compliance-as-code with a concrete implementation: API-driven checks, named control mappings, machine-readable evidence artifacts, integrated into CI/CD
- You understand the OCI Functions resource principal model and can explain why it is preferable to embedding API keys in function code
- Your pipeline now produces a complete per-build evidence package: CVE report + SBOM + compliance evidence - the artifact set an auditor would ask for in a FedRAMP or CMMC assessment

---

## PHASE 25B: BREAK-FIX EXERCISES — KUBERNETES, PIPELINE & SECURITY (1-1.5 hrs)

> **Why break-fix exercises?** In Phase 1, you broke the firewall, file permissions, and the systemd service on purpose — then diagnosed and fixed them. Those exercises built the troubleshooting muscle memory that interviewers test. Phase 3 introduces more complex systems (Kubernetes, CI/CD pipelines, Helm, ArgoCD) that fail in more complex ways. These exercises simulate the real failures you'll encounter in production federal environments.
>
> 📍 **Where work happens:** Bastion Terminal (k3s, Jenkins), App Node Terminal, Local Terminal.
>
> 🛠️ **Approach:** Each exercise follows the same pattern: (1) break something deliberately, (2) observe the symptoms, (3) diagnose using the tools you've learned, (4) fix it, (5) verify the fix.

---

### Exercise 1: Pod in CrashLoopBackOff
📍 **Bastion Terminal**

> **🧠 ELI5 — CrashLoopBackOff:** Kubernetes tries to run your pod. It crashes. Kubernetes restarts it. It crashes again. Kubernetes waits longer, restarts it. Crashes. The wait time doubles each time (exponential backoff) — 10s, 20s, 40s, up to 5 minutes. This is the most common pod failure state, and knowing how to diagnose it quickly is essential.

**Break it:**

```bash
# Corrupt the FedCompliance startup command
kubectl -n fedcompliance set env deployment/fedcompliance SQLITE_PATH=/nonexistent/path/db.sqlite
# This forces a restart with a bad path — the app will crash trying to create the DB
```

**Observe the symptoms:**

```bash
# Watch the pod cycle through CrashLoopBackOff
kubectl -n fedcompliance get pods -w
# Expected: STATUS changes from Running → Error → CrashLoopBackOff
# Ctrl+C after you see CrashLoopBackOff

# Check pod events
kubectl -n fedcompliance describe pod -l app=fedcompliance | tail -20
# Look for: "Back-off restarting failed container"
```

**Diagnose:**

```bash
# Read the container logs — this is always the first step
kubectl -n fedcompliance logs -l app=fedcompliance --previous
# The --previous flag shows logs from the CRASHED container (not the new one trying to start)
# Expected: Python traceback showing the bad SQLITE_PATH
```

<sub><em>

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `kubectl get pods -w` | `-w` = watch (live updates) | Shows pod status in real time. You'll see the status cycle through Error → CrashLoopBackOff |
| `kubectl describe pod -l app=X` | `-l` = label selector | Shows events, conditions, and container state. The Events section at the bottom tells you what Kubernetes tried to do |
| `kubectl logs --previous` | `--previous` = previous container instance | When a container crashes and restarts, `kubectl logs` shows the NEW container's logs (which may be empty). `--previous` shows the CRASHED container's logs — where the error actually is |

</em></sub>

**Fix it:**

```bash
# Restore the correct path
kubectl -n fedcompliance set env deployment/fedcompliance SQLITE_PATH=/app/fedcompliance.db
# Kubernetes rolls out a new pod with the correct env var

# Verify
kubectl -n fedcompliance get pods -w
# Expected: New pod reaches Running status, stays there
curl -s http://localhost:30080/health | python3 -m json.tool
```

> **💼 Interview Insight — CrashLoopBackOff:** "When I see CrashLoopBackOff, my first command is always `kubectl logs --previous` — the crashed container's logs tell you exactly what went wrong. Common causes: missing environment variables, bad config paths, database connection failures, or insufficient memory (OOMKilled). The `describe pod` events section tells you if it's a Kubernetes-level issue (image pull failure, resource limits) vs an application-level issue (crash on startup)."

---

### Exercise 2: Pipeline Security Gate Blocks Deployment
📍 **Browser (Jenkins UI)** + **Bastion Terminal**

> **🧠 ELI5 — Why Gates Fail:** Your Jenkins pipeline has a Trivy security scan that blocks deployment if CRITICAL CVEs are found. In production, this is how you prevent shipping known vulnerabilities. In this exercise, you deliberately introduce a vulnerable base image and watch the gate catch it.

**Break it:**

```bash
# Edit the Dockerfile to use an old, vulnerable base image
cd ~/fedcompliance-app
# Save the original
cp Dockerfile Dockerfile.backup

# Switch to an older image with known CVEs
sed -i 's|FROM oraclelinux:9-slim|FROM python:3.9-slim-buster|' Dockerfile
# python:3.9-slim-buster has known HIGH/CRITICAL CVEs in system libraries

# Commit and push to trigger the pipeline
git add Dockerfile
git commit -m "test: use older base image (break-fix exercise)"
git push
```

**Observe:**

```bash
# Watch the Jenkins pipeline in the browser
# Navigate to: http://<BASTION_IP>:8080 → fedcompliance pipeline → latest build
# Expected: Stage 3 (Trivy Scan) turns RED — build fails before reaching deployment

# Check the Trivy output in Jenkins console log
# Click the failed build → "Console Output"
# Look for: "CRITICAL" and "HIGH" vulnerability counts
```

**Fix it:**

```bash
# Restore the secure base image
cp Dockerfile.backup Dockerfile
git add Dockerfile
git commit -m "fix: restore oraclelinux:9-slim base image"
git push
# Pipeline re-runs with clean scan — deployment proceeds
```

> **💼 Interview Insight — Security Gates:** "In our pipeline, Trivy runs as a blocking gate — not just a report. If it finds CRITICAL or HIGH CVEs in the container image, the build fails before the image is ever pushed to the registry. The insecure image never reaches production. This is shift-left security — catching vulnerabilities at build time, not in production."

---

### Exercise 3: Helm Rollback After Bad Config
📍 **Bastion Terminal**

> **🧠 ELI5 — Why Helm Rollback Exists:** You push a config change that breaks the app. In the old world (raw `kubectl apply`), you'd have to remember what the previous config looked like, find the old YAML, and re-apply it. Helm keeps a history of every release — you just say "go back to revision 3" and it restores everything.

**Break it:**

```bash
# Deploy a bad config change via Helm
helm -n fedcompliance upgrade fedcompliance-app ./helm/fedcompliance \
  --set replicas=2 \
  --set image.tag=nonexistent-tag-12345
# This sets a tag that doesn't exist in OCIR — pods will fail with ImagePullBackOff
```

**Observe:**

```bash
# Check pod status
kubectl -n fedcompliance get pods
# Expected: New pods stuck in ImagePullBackOff, old pods terminating

# Check Helm release history
helm -n fedcompliance history fedcompliance-app
# Shows: current release = FAILED, previous = DEPLOYED
```

**Diagnose:**

```bash
# Check why the pod can't start
kubectl -n fedcompliance describe pod -l app=fedcompliance | grep -A5 "Events"
# Expected: "Failed to pull image" with the nonexistent tag
```

**Fix it:**

```bash
# Roll back to the last working release
helm -n fedcompliance rollback fedcompliance-app
# Helm restores the previous revision's configuration

# Verify
kubectl -n fedcompliance get pods
# Expected: Pods running with the correct image tag
curl -s http://localhost:30080/health | python3 -m json.tool

# Check history — rollback creates a new revision pointing to the old config
helm -n fedcompliance history fedcompliance-app
```

<sub><em>

| Command | What It Does |
|---------|-------------|
| `helm upgrade --set image.tag=X` | Updates the release with a new value. If the value is bad, pods fail |
| `helm history` | Shows every revision — number, status (DEPLOYED/FAILED/SUPERSEDED), timestamp |
| `helm rollback <release>` | Restores the previous working revision. Creates a NEW revision that points to the old config (Helm never deletes history) |

</em></sub>

> **💼 Interview Insight — Rollback Strategy:** "Helm release history is our safety net. Every `helm upgrade` creates a numbered revision. If the new revision fails, `helm rollback` restores the previous working state in seconds. We keep at least 10 revisions (`--history-max 10`). In a federal change management process, each revision maps to an approved change request — the history is your audit trail."

---

### Exercise 4: ArgoCD Out-of-Sync Detection
📍 **Bastion Terminal**

> **🧠 ELI5 — What "Out of Sync" Means:** ArgoCD watches your git repo and compares it to what's running in the cluster. If someone changes the cluster directly (bypassing git), ArgoCD flags it as "OutOfSync" — the cluster doesn't match the source of truth. This is how GitOps enforces that ALL changes go through git.

**Break it:**

```bash
# Make a direct change to the cluster, bypassing git
kubectl -n fedcompliance scale deployment/fedcompliance --replicas=5
# This creates a "drift" — the cluster has 5 replicas but git says 2
```

**Observe:**

```bash
# Check ArgoCD status
argocd app get fedcompliance-app
# Expected: Status = OutOfSync, Health = Healthy
# The app still works (5 replicas), but ArgoCD knows it doesn't match git

# In ArgoCD UI (browser): the app card shows yellow "OutOfSync" badge
```

**Fix it (two options):**

```bash
# Option A: Let ArgoCD fix it (restore git state)
argocd app sync fedcompliance-app
# ArgoCD re-applies the git config — replicas go back to 2

# Option B: If the change was intentional, update git
# Edit values.yaml → replicas: 5 → git push
# ArgoCD syncs and status returns to "Synced"
```

> **💼 Interview Insight — GitOps Drift Detection:** "ArgoCD gives us continuous drift detection. If someone runs `kubectl scale` directly — whether it's a well-meaning engineer or a compromised account — ArgoCD flags it within seconds. In our setup, ArgoCD auto-syncs to restore the git state, so manual changes are automatically reverted. This enforces the principle that git is the single source of truth for cluster state."

---

### Break-Fix Exercises Complete ✅

| Exercise | What Broke | Skill Tested | Interview Topic |
|----------|-----------|-------------|-----------------|
| 1. CrashLoopBackOff | Bad environment variable | Pod debugging with `kubectl logs --previous` | "How do you diagnose a crashing pod?" |
| 2. Pipeline gate | Vulnerable base image | Security gate enforcement | "How do you prevent vulnerable images in production?" |
| 3. Helm rollback | Bad image tag | Release management and rollback | "How do you roll back a bad deployment?" |
| 4. ArgoCD drift | Direct kubectl change | GitOps drift detection | "What happens when someone changes the cluster manually?" |

---

## PHASE 26: END-TO-END VALIDATION & TEARDOWN (4-6 hrs)

**Day 5 - What you are doing:** You are not building new infrastructure. You are proving the entire system works as designed, hardening the developer workflow with pre-commit secrets scanning, documenting what you built, and then destroying everything cleanly in the correct order.

> **Why this phase matters:** Being able to articulate what you tore down, in what order, and why the order matters is as impressive in a federal cloud interview as building it. Ordered teardown demonstrates you understand dependency graphs. Demonstrating full E2E flow shows you understand how all the pieces connect.

---

### Phase 26 Architecture - Full E2E Flow

```
Developer workstation
  |  git commit  (pre-commit: detect-secrets runs here)
  |  git push to GitHub
  |
  v
Jenkins (bastion :8080)
  Stage 1:  Checkout
  Stage 2:  Lint / Unit Tests
  Stage 3:  Docker Build
  Stage 4:  Trivy CVE Scan       -> blocks on CRITICAL/HIGH
  Stage 5:  Syft SBOM            -> artifact: .spdx.json
  Stage 6:  Manual Approval Gate -> human approval required
  Stage 7:  Push to OCIR
  Stage 8:  Helm upgrade --install (k3s)
  Stage 9:  ArgoCD sync trigger
  Stage 10: Compliance Evidence  -> artifact: cmmc_evidence_report.json
  |
  v
k3s cluster (bastion VM, port 30080)
  |-- fedcompliance namespace
        |-- Deployment (2 pods, resource limits, health probes)
        |-- Service (NodePort 30080)
  |
  v
ArgoCD (k3s, NodePort)
  |-- Application: fedcompliance-app
        |-- Watching git repo -> auto-sync on push
  |
  v
Object Storage (app_logs bucket)
  |-- logs/        (raw app logs)
  |-- summaries/   (log-processor function output)
  |-- digests/     (IsolationForest security digest)
  |-- compliance/  (cmmc_evidence_report.json per run)
```

---

### Step 26.1 - ELI5: Pre-Commit Hooks and detect-secrets

> **ELI5 - Pre-Commit Hooks**
>
> Imagine your IDE is a postal clerk. Before you mail a letter (commit code), the clerk has a checklist. If the letter contains a bank account number, the clerk refuses to mail it and hands it back to you. That checklist is a pre-commit hook - a script that runs automatically every time you type `git commit`, before the commit is actually recorded.
>
> Git has eight hook points: pre-commit, commit-msg, pre-push, etc. The `pre-commit` framework (the Python tool, not just the git hook concept) makes it easy to manage multiple hooks via a single `.pre-commit-config.yaml` file that lives in the repo and applies to every developer automatically when they run `pre-commit install`.
>
> **ELI5 - detect-secrets**
>
> `detect-secrets` is a tool from Yelp that scans files for patterns that look like secrets: AWS access keys, private keys, high-entropy strings, API tokens, passwords in assignment statements. It uses a combination of regex patterns and Shannon entropy analysis.
>
> **How it works in practice:**
>
> 1. You run `detect-secrets scan > .secrets.baseline` once to snapshot any intentional "false positives" already in the repo (e.g., test fixtures that resemble keys).
> 2. The pre-commit hook runs `detect-secrets audit` on every commit. It compares what it finds against the baseline. Anything new that is not in the baseline fails the commit.
> 3. If a finding is a genuine false positive, you run `detect-secrets audit .secrets.baseline` interactively to mark it as not-a-secret. That updated baseline is committed to the repo, and the hook passes.
>
> **Why this matters for federal work:** NIST 800-53 IA-5(7) and CMMC IA.3.083 both require that authenticators (which includes API keys and passwords) not be embedded in source code. detect-secrets is a scalable, automated enforcement mechanism for that control.

---

### Step 26.2 - Install and Configure Pre-Commit with detect-secrets

**Location:** Developer workstation (or bastion VM) - `~/fedcompliance-app/`

```bash
# Install both tools
# Linux/macOS/WSL2:
python3 -m pip install pre-commit detect-secrets --user
# Windows: use "python" instead of "python3" if python3 is not in your PATH

# Verify
pre-commit --version
detect-secrets --version
```

**Create `.pre-commit-config.yaml` by hand:**

```bash
cat > ~/fedcompliance-app/.pre-commit-config.yaml << 'EOF'
# .pre-commit-config.yaml
# Runs on every git commit in this repo.
# Managed by the pre-commit framework: https://pre-commit.com

repos:
  # General hygiene hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key

  # Secrets detection
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package.lock.json
EOF
```

**Generate the initial secrets baseline:**

```bash
cd ~/fedcompliance-app

# Scan the entire repo and create the baseline file
detect-secrets scan \
  --exclude-files '\.secrets\.baseline' \
  --exclude-files 'package-lock\.json' \
  > .secrets.baseline

# Review what was found (should be empty or only known items)
cat .secrets.baseline | python3 -m json.tool | head -40

# Install the pre-commit hooks into the local git repo
pre-commit install

# Verify hook is installed
ls -la .git/hooks/pre-commit
```

**Commit the configuration files:**

```bash
git add .pre-commit-config.yaml .secrets.baseline
git commit -m "chore: add pre-commit hooks with detect-secrets baseline"
git push origin main
```

**Test that the hook works:**

```bash
# Deliberately introduce a fake secret
echo 'AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"' \
  > ~/fedcompliance-app/test_secret.py
cd ~/fedcompliance-app && git add test_secret.py

# This commit should be BLOCKED
git commit -m "test: this should be blocked"
# Expected output: [ERROR] Secrets were detected in your commit. Aborting.

# Clean up
rm ~/fedcompliance-app/test_secret.py
git restore --staged test_secret.py 2>/dev/null || git reset HEAD test_secret.py
```

---

### Step 26.3 - Run the Full End-to-End Validation

**Location:** Bastion VM + Jenkins UI

This step walks through a complete push-to-deploy cycle and verifies every stage.

```bash
cd ~/fedcompliance-app
```

Open `app/main.py` and update the health endpoint to return a version field:

```python
@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.3.0",
        "phase": "Phase-3-complete",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
    }
```

```bash
# Commit and push - pre-commit hooks run here
git add phases/phase-3-fedcompliance-gitops-security/app/main.py
git commit -m "feat: add version and phase fields to health endpoint"
git push origin main
```

**Follow the pipeline in Jenkins UI (port 8080). Watch each stage:**

| Stage | What to verify |
|---|---|
| 1 - Checkout | Correct branch and commit SHA shown |
| 2 - Lint / Tests | All tests pass, 0 failures |
| 3 - Docker Build | Image tagged with Git SHA |
| 4 - Trivy Scan | 0 CRITICAL, 0 HIGH CVEs (or known baseline) |
| 5 - SBOM | `.spdx.json` artifact appears in build |
| 6 - Approval | Click Proceed in Jenkins |
| 7 - Push OCIR | Image appears in OCIR with new SHA tag |
| 8 - Helm Deploy | `helm upgrade --install` exits 0 |
| 9 - ArgoCD Sync | ArgoCD shows Synced and Healthy |
| 10 - Compliance | `cmmc_evidence_report.json` artifact appears |

**Verify deployment after pipeline completes:**

```bash
# Confirm pods are running the new image
kubectl get pods -n fedcompliance -o wide
kubectl describe pod -n fedcompliance | grep Image:

# Confirm the health endpoint returns updated response
curl http://localhost:30080/health
# Expected: {"status":"ok","version":"1.3.0","phase":"Phase-3-complete",...}

# Confirm ArgoCD sees the app as healthy
kubectl get application fedcompliance-app -n argocd \
  -o jsonpath='{.status.sync.status}'
# Expected: Synced

# Confirm compliance report on Object Storage
oci os object list --bucket-name app_logs --prefix compliance/ --output table
```

---

### Step 26.4 - Interview Insight: Preventing Secrets in Commits

> **Interview Insight - "How do you prevent secrets from being committed to source control?"**
>
> A strong answer covers defense in depth - multiple layers, not just one:
>
> **Layer 1 - Pre-commit hooks (developer workstation, shift-left).** `detect-secrets` runs before every commit and blocks anything matching secret patterns or high-entropy strings against the baseline. This catches secrets at the earliest possible moment, before they enter git history at all. The `.pre-commit-config.yaml` and `.secrets.baseline` are committed to the repo so every developer on the team gets the same protection automatically when they run `pre-commit install`.
>
> **Layer 2 - CI/CD pipeline scan.** Even if a developer bypasses pre-commit with `--no-verify`, the pipeline can run a second detect-secrets scan as a pipeline stage. This acts as a safety net - no secret-containing commit can reach the main branch undetected.
>
> **Layer 3 - Secret management architecture.** The root solution is not scanning for secrets - it is ensuring secrets never need to be in code in the first place. In this project: database passwords and API keys live in Jenkins Credentials Store (encrypted at rest, referenced by ID in Jenkinsfile); OCI auth is handled by instance principals and resource principals (no key file at all); application runtime secrets are injected as Kubernetes Secrets (base64-encoded, stored in etcd, not in git).
>
> **Layer 4 - Git history scanning.** Tools like `trufflehog` and `git-secrets` can scan the entire git history retroactively. If a secret was committed before pre-commit was installed, scheduled history scans catch it.
>
> The key interview point: pre-commit hooks are the shift-left enforcement mechanism. They run in under a second, provide immediate feedback to the developer, and are the correct place to catch secrets before they ever touch a server.

---

### Step 26.5 - Document the Pipeline Architecture

**Location:** Bastion VM - `~/fedcompliance-app/docs/pipeline-architecture.md`

```bash
mkdir -p ~/fedcompliance-app/docs
cat > ~/fedcompliance-app/docs/pipeline-architecture.md << 'EOF'
# FedCompliance App - Pipeline Architecture

## Overview

10-stage Jenkins pipeline implementing a DevSecOps workflow for a
federal-aligned Python API deployed to k3s via Helm, with GitOps
reconciliation via ArgoCD.

## Pipeline Stages

| Stage | Name | Type | Fail Behavior |
|---|---|---|---|
| 1 | Checkout | Automation | Fails build |
| 2 | Lint / Unit Tests | Automation | Fails build |
| 3 | Docker Build | Automation | Fails build |
| 4 | Trivy CVE Scan | Security Gate | Fails build on CRITICAL/HIGH |
| 5 | Syft SBOM | Evidence | Archives artifact, non-blocking |
| 6 | Manual Approval | Human Gate | 2-hr timeout, aborts build |
| 7 | Push to OCIR | Automation | Fails build |
| 8 | Helm Deploy | Automation | Fails build |
| 9 | ArgoCD Sync | GitOps | Fails build |
| 10 | Compliance Evidence | Evidence | Fails build on FAIL findings |

## Security Controls Demonstrated

| Control | NIST 800-53 | Implementation |
|---|---|---|
| Software supply chain | SA-12 | Trivy scan before push; Syft SBOM archived |
| Change management | CM-3 | Manual approval gate with ticket field |
| Least privilege | AC-6 | Jenkins credentials store; instance principals |
| Audit logging | AU-2 | All stages logged; artifacts archived per build |
| Encryption at rest | SC-28 | KMS vault verified by compliance collector |
| Network controls | SC-7 | Security list ingress rules verified |

## Artifact Package (per build)

- trivy-report.json - CVE scan results
- fedcompliance-sbom-N.spdx.json - SPDX format SBOM
- terraform/tfplan - Infrastructure change plan
- cmmc_evidence_report.json - CMMC control mapping snapshot

## Infrastructure

- Bastion VM: Oracle Linux 9, 1 OCPU, 6 GB RAM (VM.Standard.E4.Flex)
- k3s cluster: single-node, running on bastion VM
- OCIR: OCI Container Registry (private repository)
- Object Storage: app_logs bucket, Standard tier
- OCI Functions: log-processor-app application, Python 3.11 runtime
EOF
```

```bash
git add docs/pipeline-architecture.md
git commit -m "docs: add pipeline architecture documentation"
git push origin main
```

---

### Step 26.6 - Write the Teardown Script by Hand

**Location:** Bastion VM - `~/teardown.sh`

Write this script yourself section by section. Understand each section before moving to the next.

**Section 1 - Header and safety check:**

```bash
#!/usr/bin/env bash
# teardown.sh - Ordered destruction of the OCI Federal Lab (Phase 3).
# Order matters: application layer first, infrastructure last.
# Run with: bash ~/teardown.sh
set -euo pipefail

echo "=============================================="
echo "  OCI Federal Lab - Ordered Teardown"
echo "  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=============================================="
read -rp "Type DESTROY to confirm full teardown: " CONFIRM
if [[ "${CONFIRM}" != "DESTROY" ]]; then
    echo "Aborted."
    exit 1
fi
```

**Section 2 - Remove ArgoCD Application (stops GitOps reconciliation):**

```bash
echo ""
echo "[1/6] Removing ArgoCD Application..."
kubectl delete application fedcompliance-app -n argocd --ignore-not-found=true
echo "      ArgoCD application deleted."
```

**Section 3 - Uninstall Helm release:**

```bash
echo ""
echo "[2/6] Uninstalling Helm release..."
helm uninstall fedcompliance -n fedcompliance --ignore-not-found 2>/dev/null || true
kubectl delete namespace fedcompliance --ignore-not-found=true
echo "      Helm release and namespace removed."
```

**Section 4 - Remove ArgoCD from k3s:**

```bash
echo ""
echo "[3/6] Removing ArgoCD from k3s..."
kubectl delete -n argocd -f \
    https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml \
    --ignore-not-found=true 2>/dev/null || true
kubectl delete namespace argocd --ignore-not-found=true
echo "      ArgoCD removed."
```

**Section 5 - Uninstall k3s:**

```bash
echo ""
echo "[4/6] Uninstalling k3s..."
if command -v k3s-uninstall.sh &>/dev/null; then
    k3s-uninstall.sh
else
    echo "      k3s-uninstall.sh not found - skipping."
fi
echo "      k3s removed."
```

**Section 6 - Stop Jenkins:**

```bash
echo ""
echo "[5/6] Stopping Jenkins..."
sudo systemctl stop jenkins || true
sudo systemctl disable jenkins || true
echo "      Jenkins stopped and disabled."
```

**Section 7 - Terraform destroy:**

```bash
echo ""
echo "[6/6] Running Terraform destroy..."
cd ~/fedcompliance-app/terraform

terraform workspace show
terraform plan -destroy -out=destroy.tfplan
read -rp "Review the destroy plan above. Type YES to proceed: " TF_CONFIRM
if [[ "${TF_CONFIRM}" != "YES" ]]; then
    echo "Terraform destroy aborted. Infrastructure is still running."
    exit 1
fi
terraform apply destroy.tfplan
echo "      Terraform destroy complete."
```

**Section 8 - Final summary:**

```bash
echo ""
echo "=============================================="
echo "  Teardown complete - $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "  Resources destroyed (in order):"
echo "    1. ArgoCD Application manifest"
echo "    2. Helm release + fedcompliance namespace"
echo "    3. ArgoCD installation + argocd namespace"
echo "    4. k3s cluster"
echo "    5. Jenkins service"
echo "    6. OCI infrastructure (Terraform)"
echo "=============================================="
```

**Make the script executable:**

```bash
chmod +x ~/teardown.sh
```

> **Why this order?** Application resources (ArgoCD application, Helm release) must be removed before the Kubernetes cluster. The cluster must be removed before the VM (Terraform) because the VM hosts k3s - destroying the VM first would leave k3s in an inconsistent state. Jenkins is stopped before Terraform because it runs on the bastion VM that Terraform will destroy. This is a dependency graph, not an arbitrary sequence.

---

### Step 26.7 - Execute the Teardown

```bash
bash ~/teardown.sh
```

Follow the prompts. After each section completes, verify in the OCI Console:

```bash
# After Helm uninstall
kubectl get all -n fedcompliance   # should return "No resources found"

# After k3s uninstall
systemctl status k3s   # should return "Unit k3s.service could not be found"

# After Terraform destroy - confirm no running instances
oci compute instance list \
  --compartment-id $OCI_COMPARTMENT_ID \
  --lifecycle-state RUNNING \
  --output table

# Confirm no VCNs remaining
oci network vcn list \
  --compartment-id $OCI_COMPARTMENT_ID \
  --output table
```

---

### Step 26.8 - Phase 26 Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `detect-secrets` blocks a legitimate config value | False positive on high-entropy string (e.g., a UUID or base64 config value) | Run `detect-secrets audit .secrets.baseline`, mark the finding as false positive (`n`), commit the updated baseline |
| Pre-commit hook not running | `pre-commit install` was not run in this clone | Run `pre-commit install` in the repo root; verify `.git/hooks/pre-commit` exists |
| Pipeline race condition: ArgoCD syncs before Helm stage completes | ArgoCD polling interval fires during Helm upgrade | Set ArgoCD sync policy to manual during pipeline runs, or add `argocd app wait --sync` in Stage 9 before the compliance stage |
| `helm uninstall` fails with release not found | Release was never deployed or already removed | Add `--ignore-not-found` flag (already in the script); this is non-fatal |
| `k3s-uninstall.sh` not found | k3s was installed to a non-standard path | Locate with `which k3s` and run `$(dirname $(which k3s))/k3s-uninstall.sh` |
| Terraform destroy fails on VCN with dependent resources | Security lists, subnets, or gateways were created outside Terraform | Manually delete the dependent resources in OCI Console, then re-run `terraform destroy` |
| Terraform destroy fails on compute instance still running | Instance is in STOPPING state | Wait 2-3 minutes for TERMINATED state, then re-run |
| Object Storage bucket not destroyed | Bucket contains objects; Terraform cannot delete non-empty bucket | Run `oci os object bulk-delete --bucket-name app_logs --force`, then re-run Terraform |

---

### Step 26.9 - Phase 26 Verification Checklist

```bash
# All k3s namespaces gone
kubectl get namespaces 2>&1 || echo "k3s not running - expected"

# No running OCI compute instances
oci compute instance list \
  --compartment-id $OCI_COMPARTMENT_ID \
  --lifecycle-state RUNNING \
  --output table

# No VCNs remaining
oci network vcn list \
  --compartment-id $OCI_COMPARTMENT_ID \
  --output table

# Object Storage bucket status (data preserved for reference)
oci os bucket get --bucket-name app_logs --output table

# Jenkins not running
systemctl is-active jenkins || echo "Jenkins stopped - expected"

echo "Teardown completed: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
```

---

## PHASE 3 COMPLETE

### Everything Built Across All 5 Days

---

**DAY 1 - Phase 22: Environment & Secure Foundations**

- OCI tenancy configured: compartment, VCN, public subnet, private subnet, internet gateway, NAT gateway, route tables, security lists - all written as Terraform HCL by hand
- Bastion VM: Oracle Linux 9, VM.Standard.E4.Flex, provisioned via Terraform, SSH key pair created locally
- `cloud-init` bootstrap script: installs Docker, k3s, fn CLI, OCI CLI, Jenkins, Python 3, pip packages
- OCI CLI configured with API key authentication; Terraform OCI provider configured
- k3s single-node cluster running on bastion VM; `kubectl` functional
- Object Storage bucket `app_logs` created via Terraform with versioning enabled
- OCIR private repository created; Docker login configured with OCI auth token
- Jenkins installed and running on port 8080; initial admin setup complete
- fn CLI context configured pointing at OCI Functions endpoint

---

**DAY 2 - Phase 23: The Pipeline + Raw K8s Deploy**

- FedCompliance Python API: FastAPI application with `/health`, `/compliance`, `/audit` endpoints; Dockerfile written by hand
- 9-stage Jenkins pipeline written as `Jenkinsfile` (pipeline-as-code):
  - Stage 1: Checkout
  - Stage 2: Lint / Unit Tests
  - Stage 3: Docker Build (tagged with Git commit SHA)
  - Stage 4: Trivy CVE scan (blocks on CRITICAL/HIGH)
  - Stage 5: Syft SBOM generation (SPDX JSON format, archived as artifact)
  - Stage 6: Manual approval gate (2-hour timeout, change ticket field)
  - Stage 7: Push to OCIR
  - Stage 8: Raw `kubectl apply` deploy (Namespace + ConfigMap + Deployment + Service)
  - Stage 9: Smoke test
- Raw Kubernetes manifests written by hand: Namespace, ConfigMap, Deployment (2 replicas, resource limits, liveness/readiness probes), Service (NodePort 30080)
- Jenkins credentials store: OCI auth token, kubeconfig, SSH key, OCI CLI config - all referenced by ID
- Trivy and Syft installed on bastion VM

---

**DAY 3 - Phase 24: Helm + ArgoCD (GitOps)**

- Helm chart written from scratch: `Chart.yaml`, `values.yaml`, `templates/deployment.yaml`, `templates/service.yaml`, `templates/configmap.yaml`, `templates/ingress.yaml`
- `values.yaml`: image.repository, image.tag, replicaCount, resources, env vars - all parameterized
- Helm release deployed: `helm upgrade --install fedcompliance ./helm/fedcompliance -n fedcompliance --set image.tag=$(git rev-parse --short HEAD)`
- Jenkins Stage 8 replaced: `sed -i IMAGE_TAG` pattern removed, replaced with `helm upgrade --install --set image.tag`
- ArgoCD installed on k3s via official manifest
- ArgoCD `Application` manifest written by hand: watches git repo, targets `helm/fedcompliance` path, auto-sync enabled
- ArgoCD Stage 9 in pipeline: triggers sync and waits for healthy status
- Git SHA image tag strategy: every running pod is traceable to its exact source commit

---

**DAY 4 - Phase 25: AI-Augmented Operations & Compliance**

- OCI Function `log-processor` written from scratch in Python 3.11:
  - Reads raw log files from Object Storage (`logs/` prefix)
  - Parses structured log lines into dicts
  - Aggregates: error rate, latency percentiles, unique IPs, status code counts
  - Writes summary JSON back to Object Storage (`summaries/` prefix)
  - Uses resource principal signer (no credentials in code)
- `security_detector.py` written from scratch:
  - Downloads all summary JSONs from Object Storage
  - Extracts 5 numerical features per summary
  - Trains scikit-learn IsolationForest (`n_estimators=200`, `random_state=42`)
  - Scores each window; flags anomalies above threshold
  - Rule engine: HIGH_ERROR_RATE, POTENTIAL_BRUTE_FORCE, PRIVILEGE_ESC_INDICATOR
  - Writes `security_digest_latest.json` to Object Storage
- `compliance_collector.py` written from scratch:
  - IAM policy check -> AC.1.001 / AC.1.002 (overly-broad statement detection)
  - Audit log retention check -> AU.2.041 (>= 365 days required)
  - KMS vault check -> SC.3.177 (at least one active vault)
  - Security list ingress check -> SC.1.175 (no sensitive ports open to 0.0.0.0/0)
  - Outputs structured JSON report with CMMC 2.0 control mappings
  - Uploads report to Object Storage (`compliance/` prefix)
- Jenkins Stage 10: runs compliance collector, archives JSON report as build artifact

---

**DAY 5 - Phase 26: End-to-End Validation & Teardown**

- Pre-commit framework installed with `detect-secrets`: `.pre-commit-config.yaml` written by hand, secrets baseline generated, hook installed and tested
- Full E2E validation: code push -> all 10 pipeline stages -> Helm deploy -> ArgoCD sync -> compliance report - verified end-to-end
- Pipeline architecture documented: `docs/pipeline-architecture.md` with stage table, control mapping table, artifact package list
- Teardown script (`teardown.sh`) written from scratch with ordered destruction: ArgoCD App -> Helm release -> ArgoCD installation -> k3s -> Jenkins -> Terraform
- All OCI infrastructure destroyed via `terraform destroy` with plan review step

---

### Portfolio Screenshot

Take one screenshot now and save it to `docs/screenshots/` in your repo:

**Jenkins pipeline with all green stages:** Open the Jenkins Blue Ocean UI (or classic pipeline view) showing all stages passed: Terraform validate, Trivy scan, SBOM generation, Ansible lint, build + push, Helm deploy. Name it `phase-3-jenkins-pipeline.png`.

> **Why this screenshot?** A green Jenkins pipeline is universally recognized by engineering managers — they immediately understand the scope. It shows security scanning (Trivy + SBOM for EO 14028), infrastructure validation (Terraform), and automated deployment in one frame.

---

**Complete Artifact Package (per Jenkins build):**

| Artifact | Tool | Federal Relevance |
|---|---|---|
| `trivy-report.json` | Trivy | CVE evidence, EO 14028 |
| `fedcompliance-sbom-N.spdx.json` | Syft (SPDX) | Software supply chain, EO 14028 |
| `terraform/tfplan` | Terraform | Infrastructure change control, CM-3 |
| `cmmc_evidence_report.json` | compliance_collector.py | CMMC 2.0 / NIST 800-171 control evidence |
| `digests/security_digest_latest.json` | security_detector.py | Runtime anomaly detection record |

---

**Technologies Used Across Phase 3:**

Oracle Linux 9 - Terraform (OCI provider) - Docker - k3s - Kubernetes (raw manifests) - Helm - ArgoCD - Jenkins (Jenkinsfile) - Trivy - Syft (SPDX) - OCI Functions (Python 3.11, fn CLI) - OCI Object Storage - OCI Container Registry (OCIR) - OCI IAM - OCI KMS - OCI Audit - scikit-learn (IsolationForest) - NumPy - Python OCI SDK - FastAPI - pre-commit - detect-secrets - Bash

---

*Phase 3 implementation guide complete. All phases: 22 - 23 - 24 - 25 - 26*

---

## APPENDICES: OCI Managed Services Exploration

> These appendices explore OCI's managed service equivalents for the tools you built by hand in Phases 1-3. The interview story: "I built it from scratch to understand the primitives. Here's what the managed service replaces and what stays the same."
>
> **See also:** ADR-007 in `docs/ARCHITECTURE-DECISIONS.md` for the rationale behind this approach.

---

### Appendix A: OCI Resource Manager — Managed Terraform

> **🧠 ELI5 — Resource Manager:** Throughout this project, you've been running `terraform apply` from your laptop. OCI Resource Manager does the same thing, but Oracle runs it for you — in a managed environment with automatic state storage, audit logging, and git integration. Your `.tf` files don't change at all. It's like going from compiling code on your laptop to using a CI/CD build server: the code is the same, the execution environment is managed.

**What it replaces:**
- Running `terraform init/plan/apply` from your local machine
- Managing `terraform.tfstate` manually (Resource Manager stores state automatically)
- The "inception problem" from ADR-006 — Layer 0 is eliminated because Oracle manages the execution environment

**What stays the same:**
- Your Terraform modules (`modules/network/`, `modules/compute/`, `modules/database/`)
- Your variable definitions (`variables.tf`, `terraform.tfvars`)
- HCL syntax, resource definitions, outputs — all identical

**Lab Exercise: Create a Resource Manager Stack**

📍 **OCI Console** → **Developer Services** → **Resource Manager** → **Stacks**

1. Click **Create Stack**
2. Choose **Source Code Control** → select your GitHub repo (or upload a zip of your `terraform/environments/lab/` directory)
3. **Working Directory:** Point to `terraform/environments/lab/` (where your `main.tf` lives)
4. **Terraform Version:** Select 1.5+ (matches what you've been using locally)
5. **Variables:** The console auto-detects variables from your `variables.tf` — fill in the same values from your `terraform.tfvars`
6. Click **Create**

**Run a Plan Job:**

1. From your Stack page, click **Plan**
2. Review the plan output — it should show the same resources as `terraform plan` on your laptop
3. Compare: same resource count, same changes, same outputs

**Run an Apply Job (optional — only if you want Resource Manager to take over state):**

1. Click **Apply** → select the plan you just ran
2. Resource Manager executes `terraform apply` in Oracle's managed environment
3. State is stored automatically — no more `.tfstate` file on your laptop

> ⚠️ **If you apply via Resource Manager, your local Terraform state will be out of sync.** You'd need to either always use Resource Manager going forward, or import the state back locally. For this lab, running Plan only is the safest demonstration.

**Cost:** Resource Manager itself is free. The infrastructure it provisions costs the same as running Terraform locally.

**Interview talking point:** "I use OCI Resource Manager for managed Terraform execution. My HCL modules are identical — I developed them locally with `terraform plan/apply`, then uploaded them to Resource Manager for managed execution with automatic state storage and audit logging. This eliminates the Layer 0 inception problem: Oracle manages the Terraform execution environment."

---

### Appendix B: OKE — Oracle Kubernetes Engine Comparison

> **🧠 ELI5 — OKE vs k3s:** In Phase 2, you installed k3s on VMs — you managed the Kubernetes control plane yourself (the API server, etcd, scheduler). OKE is Oracle's managed Kubernetes: they handle the control plane, you just add worker nodes. It's like the difference between running your own email server vs. using Gmail: the email protocol (SMTP) is the same, but someone else handles the infrastructure.

**What OKE handles (that you did manually with k3s):**
| Component | k3s (you manage) | OKE (Oracle manages) |
|-----------|-------------------|----------------------|
| API Server | Running on your VM | Managed, HA, auto-patched |
| etcd (cluster state) | SQLite/embedded on VM | Managed, backed up automatically |
| Control plane upgrades | Manual `curl -sfL ...` | One-click version upgrade |
| TLS certificates | Auto-generated, manually renewed | Managed, auto-rotated |
| Networking (CNI) | Flannel (k3s default) | OCI VCN-Native Pod Networking |
| Load balancing | NodePort or manual | OCI Load Balancer (integrated) |

**What stays identical:**
- `kubectl` commands — same API, same syntax
- Helm charts — your `helm install` commands work unchanged
- ArgoCD — watches the same git repo, syncs the same manifests
- RBAC policies — same `Role`, `ClusterRole`, `RoleBinding` YAML
- Your application manifests — same Deployments, Services, ConfigMaps

**Architecture comparison:**

```
k3s (Phase 2):                        OKE:
┌──────────────────────┐               ┌──────────────────────┐
│ bastion VM           │               │ OKE Managed          │
│ ├── k3s server       │               │ Control Plane        │
│ │   ├── API server   │               │ (Oracle manages)     │
│ │   ├── etcd (SQLite)│               │ ├── API server (HA)  │
│ │   └── scheduler    │               │ ├── etcd (managed)   │
│ └── k3s agent        │               │ └── scheduler        │
├──────────────────────┤               ├──────────────────────┤
│ app-server VM        │               │ Node Pool            │
│ └── k3s agent        │               │ ├── A1.Flex node 1   │
│     └── pods         │               │ │   └── pods         │
│         ├── app      │               │ └── A1.Flex node 2   │
│         └── argocd   │               │     └── pods         │
└──────────────────────┘               └──────────────────────┘
  You manage everything                  You manage nodes + apps
                                         Oracle manages control plane
```

**Cost analysis:**
- **k3s:** $0 — runs on your existing Always Free VMs
- **OKE control plane:** Free (Oracle made OKE control plane free in 2024)
- **OKE worker nodes:** Same cost as regular compute instances (A1 Flex nodes use your Always Free allocation)
- **OCI Load Balancer:** ~$10/month if you add one (optional)

> **Note:** OKE control plane is now free, but you need a paid tenancy (trial credits work). Always Free-only accounts may not be able to create OKE clusters.

**Optional lab exercise (if trial credits available):**

```bash
# Create a minimal OKE cluster with 1 A1 Flex node
# Use the OCI Console: Developer Services → Kubernetes Clusters (OKE) → Create Cluster
# Select "Quick Create" → Kubernetes version 1.28+ → Node pool: 1 node, VM.Standard.A1.Flex
# This takes ~10 minutes to provision

# Once ready, download the kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id $OKE_CLUSTER_OCID \
  --file ~/.kube/oke-config \
  --region us-ashburn-1

# Set the kubeconfig
export KUBECONFIG=~/.kube/oke-config

# Verify — same kubectl commands as k3s
kubectl get nodes
kubectl get namespaces

# Deploy your existing Helm chart — it works unchanged
helm install fedtracker ./helm/fedtracker/

# ⚠️ TEARDOWN when done to save credits
# OCI Console → OKE → your cluster → Delete
```

**Interview talking point:** "I used k3s in my lab to understand Kubernetes internals — control plane components, etcd state, CNI networking. In production, I'd use OKE so Oracle manages the control plane, patching, and HA. My Helm charts, ArgoCD configs, and kubectl workflows transfer directly — the Kubernetes API is identical. The only difference is who manages the control plane."

---

### Appendix C: OCIR Enhancements — Image Scanning and Signing

> **🧠 ELI5 — Defense in depth for containers:** In Phase 3, you run Trivy in the build pipeline to scan images before pushing to OCIR. That's pipeline-time scanning. OCIR also offers registry-time scanning — it scans images after they're pushed and continuously checks for new CVEs. In production, you want both: Trivy catches issues before code merges, OCIR scanning catches issues discovered after the image was built.

**Enable image scanning on your OCIR repository:**

📍 **OCI Console** → **Developer Services** → **Container Registry**

1. Find your existing OCIR repository (e.g., `fedtracker`)
2. Click the repository name → **Settings**
3. Under **Scanning**, toggle **Enable image scanning**
4. **Scan on push:** Enable — every new image push triggers a scan automatically

**View scan results:**

1. Click any image tag in your OCIR repository
2. Click **Scan Results** tab
3. Review: CVE ID, severity (Critical/High/Medium/Low), affected package, fixed version

**Compare with Trivy (already in your pipeline):**

| Aspect | Trivy (Pipeline) | OCIR Scanning (Registry) |
|--------|-------------------|--------------------------|
| When it runs | During CI/CD build | After push + continuous |
| What it catches | Issues known at build time | New CVEs discovered post-push |
| Integration | Jenkins stage, exit code | OCI Console, API, Events |
| Cost | Free (open source) | Free for up to 5 images/month |
| Coverage | OS packages + app dependencies | OS packages only |

**Image signing with OCI Vault (conceptual):**

Your Phase 3 lab already has OCI Vault configured (Day 1, Step 22.9). Container image signing uses Vault's KMS keys to cryptographically sign images, proving they came from your pipeline and haven't been tampered with. This maps to EO 14028 (Executive Order on Improving the Nation's Cybersecurity) supply chain requirements.

```bash
# Conceptual flow (requires cosign CLI):
# 1. Generate a signing key in OCI Vault
# 2. After Trivy scan passes, sign the image:
#    cosign sign --key oci://vault-key-ocid $OCIR_IMAGE_URL
# 3. At deploy time, verify the signature:
#    cosign verify --key oci://vault-key-ocid $OCIR_IMAGE_URL
# 4. Kubernetes admission controller rejects unsigned images
```

> **Interview talking point:** "I implement defense-in-depth for container security: Trivy scans during CI/CD for known CVEs at build time, OCIR scanning continuously monitors for newly discovered vulnerabilities post-deployment, and I use Cosign with OCI Vault KMS keys for image signing to verify supply chain integrity per EO 14028."

---

### Appendix D: OCI DevOps — Managed CI/CD Comparison

> **🧠 ELI5 — OCI DevOps vs Jenkins:** Jenkins is the Swiss Army knife of CI/CD — infinitely flexible, runs anywhere, but you manage the server, plugins, and Java runtime. OCI DevOps is Oracle's managed CI/CD service: you define build pipelines and deployment pipelines, Oracle runs them. It's integrated with OCIR, OKE, and OCI Functions out of the box. The trade-off: less flexibility, zero server management.

**Why Jenkins was chosen for this lab:**
- The target job description (federal cloud engineer) specifies **CloudBees/Jenkins** experience
- Jenkins teaches pipeline-as-code concepts (Jenkinsfile) that transfer to any CI/CD system
- Self-managing Jenkins demonstrates Linux admin skills (Java, systemd, plugin management)

**What OCI DevOps replaces:**

| Component | Jenkins (your lab) | OCI DevOps (managed) |
|-----------|-------------------|----------------------|
| Build server | VM you provision and maintain | Oracle-managed build runners |
| Plugin management | You install, update, debug | Built-in integrations, no plugins |
| Pipeline definition | Jenkinsfile (Groovy DSL) | Build spec YAML |
| Artifact storage | Local workspace + OCIR push | Integrated with OCIR |
| Deployment | Pipeline calls kubectl/helm | Deployment pipeline with approval gates |
| Secrets | Jenkins Credential Store | OCI Vault (native integration) |
| Cost | VM cost (Always Free A1 Flex) | Free tier: 5000 build minutes/month |

**What stays the same:**
- Pipeline stages: validate → scan → build → test → deploy
- Container image workflow: build → tag → push to OCIR → deploy to K8s
- Security scanning: Trivy/Syft still run as build steps
- GitOps: ArgoCD can still watch your repo (complementary, not replaced)

**Architecture comparison:**

```
Jenkins (your lab):                    OCI DevOps:
┌──────────────────────┐               ┌──────────────────────┐
│ bastion VM           │               │ OCI DevOps Project   │
│ ├── Jenkins server   │               │ (Oracle manages)     │
│ │   ├── Java runtime │               │                      │
│ │   ├── Plugins      │               │ Build Pipeline:      │
│ │   └── Credentials  │               │ ├── build_spec.yaml  │
│ │                    │               │ ├── Build runner     │
│ └── Jenkinsfile:     │               │ ├── OCIR push        │
│     ├── Build        │               │ └── Trivy scan       │
│     ├── Trivy scan   │               │                      │
│     ├── SBOM         │               │ Deploy Pipeline:     │
│     ├── OCIR push    │               │ ├── Approval gate    │
│     └── Deploy       │               │ ├── kubectl/helm     │
└──────────────────────┘               │ └── Rollback         │
  You manage the server                └──────────────────────┘
  and all plugins                        Zero server management
```

**Interview talking point:** "In my lab, I use Jenkins because the role requires CloudBees experience. I understand Jenkins deeply — Jenkinsfile pipeline-as-code, credential management, plugin architecture, and running Jenkins as a systemd service on Oracle Linux. For comparison, OCI DevOps eliminates server management entirely while providing native integration with OCIR, OKE, and OCI Vault. The pipeline concepts (build → scan → deploy with approval gates) are identical — only the execution platform differs."

---

> **Summary: The OCI Managed Services Spectrum**
>
> | What You Built | Managed Equivalent | Cost | Lab Coverage |
> |----------------|-------------------|------|-------------|
> | `terraform apply` from laptop | OCI Resource Manager | Free | Appendix A (hands-on) |
> | k3s on VMs | OKE (Oracle Kubernetes Engine) | Free control plane + node cost | Appendix B (comparison + optional lab) |
> | Trivy pipeline scanning | OCIR Image Scanning | Free (5 images/month) | Appendix C (hands-on) |
> | Jenkins on VM | OCI DevOps | Free (5000 min/month) | Appendix D (comparison) |
> | `dnf update` manual patching | OCI OS Management Hub | Free on paid tenancy | Linux Admin Deep Dive Step 9 (hands-on) |
>
> **The progression:** Phase 1 teaches you to do it by hand. Phase 2 automates with open-source tools. Phase 3 adds enterprise patterns. These appendices show what the cloud provider handles when you're ready to let go of the knobs.

---

### Appendix E: OCI Load Balancer — 3-Tier Architecture (Terraform)

> **🧠 ELI5 — Why a Load Balancer?** Your k3s NodePort works for a lab, but in production you'd never expose a NodePort directly to the internet. A load balancer sits in the public subnet, accepts traffic on port 443 (HTTPS), and distributes it across your k3s nodes in the private subnet. If one node dies, the LB stops sending traffic to it — users never notice.
>
> This completes the **3-tier architecture** every hiring manager expects to see:
>
> ```
> Tier 1 (Presentation):  OCI Load Balancer (public subnet, HTTPS)
>                              │
> Tier 2 (Application):   k3s pods across 2 nodes (private subnet)
>                              │
> Tier 3 (Data):          Oracle Autonomous DB (OCI-managed)
> ```
>
> In Phase 2, you set up the load balancer manually via the OCI Console to understand the concepts. Here in Phase 3, you manage it as Terraform code — the production pattern.

**Cost:** OCI provides 1 Always Free flexible load balancer (10 Mbps bandwidth). Additional LBs or higher bandwidth require paid tenancy.

**Terraform resource (`modules/network/load_balancer.tf`):**

```hcl
# load_balancer.tf — OCI Flexible Load Balancer for k3s cluster
# 3-tier architecture: LB (public) → k3s nodes (private) → ADB (managed)

resource "oci_load_balancer_load_balancer" "k3s_lb" {
  compartment_id = var.compartment_id
  display_name   = "fedcompliance-lb"
  shape          = "flexible"

  shape_details {
    minimum_bandwidth_in_mbps = 10    # Always Free minimum
    maximum_bandwidth_in_mbps = 10    # Always Free maximum
  }

  subnet_ids = [oci_core_subnet.public.id]

  freeform_tags = {
    "project"   = "oci-federal-lab"
    "phase"     = "phase-3"
    "component" = "load-balancer"
  }
}

# Backend set — the group of k3s nodes that receive traffic
resource "oci_load_balancer_backend_set" "k3s_backends" {
  load_balancer_id = oci_load_balancer_load_balancer.k3s_lb.id
  name             = "k3s-backend-set"
  policy           = "ROUND_ROBIN"

  health_checker {
    protocol          = "HTTP"
    port              = 30080                    # NodePort for FedCompliance
    url_path          = "/health"
    return_code       = 200
    interval_ms       = 10000                    # Check every 10 seconds
    timeout_in_millis = 3000
    retries           = 3
  }
}

# Backend 1 — k3s node 1
resource "oci_load_balancer_backend" "node_1" {
  load_balancer_id = oci_load_balancer_load_balancer.k3s_lb.id
  backendset_name  = oci_load_balancer_backend_set.k3s_backends.name
  ip_address       = module.compute.node_1_private_ip
  port             = 30080
}

# Backend 2 — k3s node 2
resource "oci_load_balancer_backend" "node_2" {
  load_balancer_id = oci_load_balancer_load_balancer.k3s_lb.id
  backendset_name  = oci_load_balancer_backend_set.k3s_backends.name
  ip_address       = module.compute.node_2_private_ip
  port             = 30080
}

# Listener — accepts HTTPS traffic on port 443
resource "oci_load_balancer_listener" "https" {
  load_balancer_id         = oci_load_balancer_load_balancer.k3s_lb.id
  default_backend_set_name = oci_load_balancer_backend_set.k3s_backends.name
  name                     = "https-listener"
  port                     = 443
  protocol                 = "HTTP"    # Use "HTTP" for lab; production would use SSL with a certificate

  # In production, add:
  # ssl_configuration {
  #   certificate_ids          = [oci_certificates_management_certificate.app.id]
  #   verify_peer_certificate  = false
  # }
}

output "load_balancer_ip" {
  description = "Public IP of the load balancer"
  value       = oci_load_balancer_load_balancer.k3s_lb.ip_address_details[0].ip_address
}
```

<sub><em>

| Resource | What It Does |
|----------|-------------|
| `oci_load_balancer_load_balancer` | Creates the LB itself in the public subnet. `flexible` shape lets you set bandwidth (10 Mbps for free tier) |
| `oci_load_balancer_backend_set` | Defines the group of servers + health check. `ROUND_ROBIN` distributes requests evenly. The health checker hits `/health` every 10 seconds — if a node fails 3 checks, it's removed from rotation |
| `oci_load_balancer_backend` | Registers each k3s node as a target. Traffic goes to the NodePort (30080) on each node's private IP |
| `oci_load_balancer_listener` | The public-facing entry point. Port 443 accepts incoming requests and forwards to the backend set |

</em></sub>

**Full 3-tier request path (production architecture):**

```
Client (browser/curl)
    │  HTTPS request
    ▼
┌─────────────────────────┐
│ OCI Load Balancer       │  Tier 1: Public subnet
│ (10 Mbps, round-robin)  │  - HTTPS termination
│ Health check: /health   │  - Distributes across healthy nodes
└────────────┬────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌──────────┐   ┌──────────┐
│ k3s      │   │ k3s      │  Tier 2: Private subnet
│ node-1   │   │ node-2   │  - FedCompliance pods
│ :30080   │   │ :30080   │  - Helm-managed, ArgoCD-synced
└────┬─────┘   └────┬─────┘
     │               │
     └───────┬───────┘
             ▼
┌─────────────────────────┐
│ Oracle Autonomous DB    │  Tier 3: OCI-managed
│ (compliance data)       │  - Automatic backups
│                         │  - Encryption at rest
└─────────────────────────┘
```

> **💼 Interview Insight — 3-Tier Architecture:** "My lab uses a standard 3-tier architecture. The OCI Load Balancer in the public subnet handles HTTPS termination and distributes traffic across k3s nodes using round-robin with health checks. The application tier runs in a private subnet — pods are Helm-managed and ArgoCD-synced. The database tier is Oracle Autonomous DB, fully managed with automatic backups. All three tiers are Terraform-coded. If a node fails the health check, the LB removes it from rotation within 30 seconds — users see zero downtime."

> **💼 Interview Insight — Load Balancer vs API Gateway vs Ingress Controller:**
>
> | Component | Layer | Purpose | When to Use |
> |-----------|-------|---------|-------------|
> | **OCI Load Balancer** | L4/L7 | Traffic distribution, health checks, SSL termination | Always — it's the front door to your infrastructure |
> | **OCI API Gateway** | L7 | Rate limiting, auth, routing, request transformation | When you need API-specific policies per route |
> | **K8s Ingress Controller** | L7 | In-cluster HTTP routing (path-based, host-based) | When you have multiple services inside the cluster |
>
> "In a production setup, you'd chain them: Load Balancer → API Gateway → Ingress Controller → Pods. Each layer handles different concerns. In our lab, the LB distributes traffic and the API Gateway handles rate limiting. For a single-service deployment, you could skip the Ingress Controller and route directly to the NodePort."

---

### Appendix F: API Types — REST vs GraphQL vs gRPC vs Webhooks

> This project deliberately focuses on **REST** as the primary API pattern — it's the foundation of every cloud service, and the pattern you'll use in 90% of federal work. But interviewers will ask about the alternatives. This appendix gives you the mental model to discuss all four patterns confidently.

> **💼 Interview Insight — API Types Comparison:**
>
> | Aspect | REST | GraphQL | gRPC | Webhooks |
> |--------|------|---------|------|----------|
> | **Protocol** | HTTP/1.1 or HTTP/2 | HTTP/1.1 (typically POST) | HTTP/2 (always) | HTTP/1.1 (POST callback) |
> | **Data format** | JSON (typically) | JSON (always) | Protocol Buffers (binary) | JSON (typically) |
> | **Schema** | OpenAPI/Swagger (optional) | SDL schema (required) | .proto files (required) | No standard schema |
> | **Strengths** | Simple, cacheable, universal | Client picks exact fields needed | Fast, strongly typed, streaming | Real-time event notification |
> | **Weaknesses** | Over-fetching, multiple round trips | Complex caching, N+1 query problem | Not browser-friendly, tooling overhead | Delivery not guaranteed |
> | **Best for** | CRUD APIs, public APIs, microservices | Complex nested data, mobile apps | Internal microservice communication | Event-driven architectures |
> | **Federal use** | Standard for all external APIs | Growing in data-heavy agencies | DoD service mesh (Istio/Envoy) | Cloud events, CI/CD triggers |

> **Where each appears in this project:**
>
> | Pattern | Where You Built It | Phase |
> |---------|-------------------|-------|
> | **REST** | FedTracker (CRUD), FedAnalytics (ingest/metrics), FedCompliance (scan/report/auth) | 1, 2, 3 |
> | **Webhooks** | FedAnalytics POST /webhook — receives OCI Events with HMAC signature validation | 2 |
> | **gRPC** | Not implemented — discussed here. gRPC is the protocol used internally by Kubernetes (kubectl → API server), Envoy proxies, and service mesh sidecars. You interact with it indirectly every time you run `kubectl` | — |
> | **GraphQL** | Not implemented — discussed here. GraphQL would be a natural fit for the compliance data model (deeply nested controls → findings → evidence), but REST is sufficient for the lab scope | — |

> **🧠 ELI5 — When to Use What:**
>
> - **REST:** "I need a standard API that any client can call." → Default choice. Use it unless you have a specific reason not to.
> - **GraphQL:** "My clients need different subsets of deeply nested data, and I don't want 15 different REST endpoints." → Mobile apps querying compliance hierarchies, dashboard APIs that aggregate multiple data sources.
> - **gRPC:** "I need fast, strongly-typed communication between internal services with streaming support." → Microservice-to-microservice calls, real-time data feeds, anything latency-sensitive. Not for browser clients (requires gRPC-Web proxy).
> - **Webhooks:** "I need to know when something happens in another system without polling." → Cloud events (file uploaded, resource created), CI/CD triggers, audit notifications.

> **💼 Interview Insight — The Right Answer:** "We use REST for all external-facing APIs because it's universally supported and cacheable. For internal microservice communication in high-throughput scenarios, I'd consider gRPC — it's what Kubernetes uses internally, and Istio service mesh routes gRPC natively. For event-driven workflows like our OCI Events → webhook integration, webhooks are the right pattern. GraphQL is powerful for complex data queries but adds schema management overhead — I'd use it for data-heavy dashboards, not simple CRUD. The key is matching the protocol to the use case, not picking one for everything."

> **Why we focused on REST:** The original project design chose REST as the primary pattern because: (1) every cloud CLI and SDK is a REST client under the hood, (2) it's the most likely pattern in the job description, (3) mastering REST deeply (proper status codes, Pydantic validation, HATEOAS concepts, OpenAPI docs) is more valuable than shallow exposure to four patterns. The webhooks in Phase 2 and API Gateway routing demonstrate event-driven and managed API patterns without forcing a protocol change.
