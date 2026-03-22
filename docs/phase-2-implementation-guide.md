# AFS Cloud Engineer Interview Lab — Phase 2 Implementation Guide
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
│  │  (Oracle Linux 8, 1 OCPU)   │                      │
│  └──────────────┬──────────────┘                      │
│                 │ SSH tunnel                           │
│  ┌──────────────▼──────────────┐                      │
│  │ Private Subnet (10.0.2.0/24)│                      │
│  │  App Server VM              │                      │
│  │  (Oracle Linux 8, 1 OCPU)   │                      │
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
| 📍 **Local Terminal** | Your machine's terminal | bash / PowerShell / Git Bash on your laptop |
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
  description = "Oracle Linux 8 ARM image OCID"
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
    "Project"     = "fedanalytics-lab"
    "Environment" = "lab"
    "Phase"       = "2"
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
    "Project"     = "fedanalytics-lab"
    "Environment" = "lab"
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
    "Project"     = "fedanalytics-lab"
    "Environment" = "lab"
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
  cpu_core_count           = 1
  data_storage_size_in_tbs = 1
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
image_ocid          = "ocid1.image.oc1..YOUR_OL8_ARM_IMAGE"

db_admin_password  = "YourStr0ngP@ssw0rd!"
db_wallet_password = "W@lletP@ss123!"
EOF
```

> **Important:** Fill in the actual values from your OCI account. You can find most of these in `~/.oci/config` and the OCI Console. The `image_ocid` is the Oracle Linux 8 ARM image for your region — find it under **Compute** → **Custom Images** or the [OCI image list](https://docs.oracle.com/en-us/iaas/images/).

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

### Step 21.1 — Create Ansible Inventory
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
    "start_time": datetime.now(timezone.utc).isoformat() + "Z"
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
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
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
    METRICS["last_ingest_time"] = datetime.now(timezone.utc).isoformat() + "Z"

    log_audit("INGEST", "ingest_data", resource_id=batch_id,
              details=f"Batch {batch_id}: {accepted} accepted, {rejected} rejected from {request.source}")
    log_app("INFO", "ingest", f"Batch {batch_id} processed: {accepted} accepted, {rejected} rejected")

    return IngestResponse(
        status="complete",
        records_accepted=accepted,
        records_rejected=rejected,
        batch_id=batch_id,
        timestamp=datetime.now(timezone.utc).isoformat() + "Z"
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
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
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
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
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
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
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
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
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
        executable: pip3
        state: present

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
> Oracle Linux 8 ships with SELinux in enforcing mode. If your service fails to start, check SELinux first:
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
📍 **Local Terminal**

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

git add terraform/ ansible/ app/ .gitignore
git commit -m "Phase 2 Day 1: Terraform infra + Ansible deploy + FedAnalytics app

- Terraform: VCN, subnets, bastion, app-server, Autonomous DB
- Ansible: hardening playbook + FedAnalytics deployment playbook
- FedAnalytics: FastAPI app with 6 endpoints (ingest, webhook, logs, metrics, health, ingest/status)
- Webhook endpoint with HMAC-SHA256 signature validation (Phase 2 API Pillar)
- systemd service management"
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
- Ansible hardening playbook: SSH lockdown, firewall, users, auto-updates (Oracle Linux 8)
- Ansible deployment playbook: FedAnalytics FastAPI app with systemd service management
- FedAnalytics API: 6 endpoints (ingest, webhook, logs, metrics, health, ingest/status)
- Webhook endpoint with HMAC-SHA256 signature validation (Phase 2 API Pillar)
- OCI Generative AI integration for compliance report generation

**What's running:**
- Bastion host (SSH gateway)
- Application server with FedAnalytics API (systemd-managed)
- Autonomous Database with analytics schema
- All accessible via SSH through bastion

**Next phase:** Phase 3 builds advanced infrastructure — Vault secrets management, Helm charts, ArgoCD GitOps, compliance-as-code, and E2E validation.

---

## PHASE 2 COMPLETE

**Phase 2 covered Phases 20-21 (Days 1-2):** Infrastructure deployment with Terraform + Ansible, FedAnalytics FastAPI application with webhook integration, OCI Generative AI compliance reports, and full operational deployment on OCI.

**Skills practiced:** Terraform (OCI provider reps), Ansible (hardening + deployment), FastAPI (second build with webhook/HMAC patterns), OCI Autonomous Database, OCI Generative AI Service, systemd service management, webhook signature validation.

**Total Phase 2 artifacts:** Terraform configs, Ansible playbooks, FedAnalytics FastAPI app, systemd service files, database schema.

---
