# DevOps Architecture Reference

Visual reference for how the lab tools map to production patterns. Useful for interview prep, blog posts, and understanding where everything runs.

Last updated: 2026-03-31

---

## Your Lab Setup

```
+------------------------------------------------------------------+
|  YOUR LAPTOP (Layer 0)                                           |
|  Windows Desktop                                                 |
|                                                                  |
|  +---------------+  +---------------+  +----------------------+  |
|  | VS Code       |  | Terraform     |  | Git Bash             |  |
|  | (write code)  |  | (builds       |  | (SSH, SCP, git push) |  |
|  |               |  |  infra)       |  |                      |  |
|  +-------+-------+  +-------+-------+  +-----------+----------+  |
|          |                  |                       |             |
|  +-------+------------------+-----------------------+----------+  |
|  | ~/.oci/oci_api_key.pem    (Terraform credentials)           |  |
|  | ~/.ssh/oci-federal-lab/   (SSH keys)                        |  |
|  | ~/Desktop/github/oci-federal-lab/  (your repo)              |  |
|  +-------------------------------------------------------------+  |
+----------+------------------+-----------------+-----------------+
           | API calls        | SSH             | git push
           | (creates infra)  | (configures VMs)|
           v                  v                 v
+------------------+  +------------------+  +-------------+
|  OCI Cloud       |  |  OCI VMs         |  |  GitHub     |
|  (Layer 1)       |  |  (Layer 2)       |  |             |
|                  |  |                  |  |  stores your|
|  VCN, subnets,   |  |  bastion         |  |  code       |
|  gateways, DB    |  |  app-server      |  |             |
|  -- built by TF  |  |  -- configured   |  |             |
|                  |  |    by you (SSH)  |  |             |
+------------------+  +------------------+  +-------------+
```

---

## Production / Enterprise Team

```
+----------------------------------------------------------------------+
|  DEVELOPER LAPTOP                                                    |
|                                                                      |
|  +-----------+  +-----------+                                        |
|  | VS Code   |  | Git       |   <-- Developers ONLY write code here |
|  |           |  |           |       No Terraform, no SSH to prod     |
|  +-----+-----+  +-----+-----+                                       |
|        +-------+-------+                                             |
+-----------------+----------------------------------------------------+
                  | git push
                  v
+----------------------------------------------------------------------+
|  GITHUB / GITLAB                                                     |
|                                                                      |
|  Pull Request created                                                |
|       |                                                              |
|       v                                                              |
|  Team reviews code (Terraform, app code, Ansible)                    |
|       |                                                              |
|       v                                                              |
|  PR merged to main                                                   |
+-----------------+----------------------------------------------------+
                  | triggers
                  v
+----------------------------------------------------------------------+
|  CI/CD PIPELINE  (Layer 0 -- set up once, manually or bootstrapped)  |
|  Jenkins / GitHub Actions / GitLab CI                                |
|                                                                      |
|  +----------------------------------------------------------------+  |
|  | Stage 1: TERRAFORM                                             |  |
|  |  terraform plan  -> shows what will change                     |  |
|  |  (human approves)                                              |  |
|  |  terraform apply -> creates/updates cloud infrastructure       |  |
|  |                                                                |  |
|  |  Uses: service account credentials (from Vault/secrets mgr)   |  |
|  |  State: stored in remote object storage (S3, OCI bucket)      |  |
|  +----------------------------------------------------------------+  |
|  | Stage 2: ANSIBLE                                               |  |
|  |  Connects via SSH to new/updated VMs                           |  |
|  |  Installs packages, configures OS, deploys app                 |  |
|  +----------------------------------------------------------------+  |
|  | Stage 3: DOCKER BUILD + PUSH                                   |  |
|  |  Builds container image from app code                          |  |
|  |  Pushes to container registry (OCIR, ECR, Docker Hub)          |  |
|  +----------------------------------------------------------------+  |
|  | Stage 4: DEPLOY                                                |  |
|  |  Kubernetes: kubectl apply / helm upgrade / ArgoCD sync        |  |
|  |  Non-K8s: Ansible pulls new container, restarts service        |  |
|  +----------------------------------------------------------------+  |
|  | Stage 5: TEST                                                  |  |
|  |  Smoke tests, integration tests, health checks                 |  |
|  |  If tests fail -> rollback                                     |  |
|  +----------------------------------------------------------------+  |
+-----------------+----------------------------------------------------+
                  | API calls, SSH, kubectl
                  v
+----------------------------------------------------------------------+
|  CLOUD  (OCI / AWS / Azure / GCP)                                    |
|                                                                      |
|  +- Layer 1: Infrastructure (Terraform manages) -----------------+   |
|  |  VCN/VPC, subnets, gateways, security lists                  |   |
|  |  IAM policies, compartments                                   |   |
|  |  Databases (Autonomous DB, RDS)                               |   |
|  |  Container registry (OCIR, ECR)                               |   |
|  |  Load balancers, DNS                                          |   |
|  +---------------------------------------------------------------+   |
|                                                                      |
|  +- Layer 2: Application (Ansible/K8s/CI/CD manages) ------------+   |
|  |                                                                |   |
|  |  Option A: VMs (your lab)         Option B: Kubernetes         |   |
|  |  +-----------+ +-----------+      +---------------------+     |   |
|  |  | bastion   | |app-server |      | k8s cluster         |     |   |
|  |  |           | |           |      |  +-----+ +-----+   |     |   |
|  |  | SSH jump  | | Podman/   |      |  | pod | | pod |   |     |   |
|  |  | host      | | systemd   |      |  |     | |     |   |     |   |
|  |  |           | | runs app  |      |  +-----+ +-----+   |     |   |
|  |  +-----------+ +-----------+      |  managed by Helm/   |     |   |
|  |                                   |  ArgoCD             |     |   |
|  |                                   +---------------------+     |   |
|  +---------------------------------------------------------------+   |
+----------------------------------------------------------------------+
```

---

## The Three Layers

| Layer | What | Managed by | In your lab | In production |
|-------|------|-----------|-------------|---------------|
| **Layer 0** | Bootstrap foundation | Manual / one-time script | Your laptop | CI/CD server, service accounts, state storage |
| **Layer 1** | Cloud infrastructure | Terraform | VCN, subnets, gateways, ADB | Same, but via pipeline |
| **Layer 2** | App configuration | Ansible / K8s / CI/CD | Software, configs, app deploy | Same, but via pipeline |

**The inception rule:** Layer 0 is NEVER self-managed. Someone always sets it up by hand (or with a one-time bootstrap). This breaks the "who manages the manager?" loop.

---

## Lab vs Production Comparison

| Aspect | Your lab | Production |
|--------|---------|------------|
| Who runs Terraform | You, from your laptop | CI/CD pipeline, automated |
| Who runs Ansible | You, from your laptop | CI/CD pipeline, automated |
| Who approves changes | You (just hit enter) | Team reviews PR, then approves in pipeline |
| Where credentials live | `~/.oci/` on your laptop | Secrets manager (Vault, AWS Secrets Manager) |
| Where TF state lives | Local file (`terraform.tfstate`) | Remote storage (OCI bucket, S3) |
| Where app runs | VM with systemd | Kubernetes pods or VMs |
| Developer touches prod? | Yes (it's your lab) | Never -- pipeline does everything |

**Key insight:** The pipeline replaces your laptop. Everything else is the same architecture.

---

## Service Account Lifecycle (Production)

| Thing | How it's maintained |
|-------|-------------------|
| Service account | Created once in IAM, rarely changes |
| API keys | Rotated on a schedule (e.g., every 90 days), stored in secrets manager |
| CI/CD server | Managed by platform team, patched separately, or is a managed service (GitHub Actions = no server to manage) |
| Terraform state | Stored remotely in object storage, versioned automatically |

---

## Managed CI/CD Eliminates the Inception Problem

Many teams avoid the "who manages the manager?" problem entirely:

- **GitHub Actions** -- GitHub owns the runner, you don't manage any server
- **OCI Resource Manager** -- OCI runs Terraform for you as a service
- **Terraform Cloud** -- HashiCorp runs it for you

No "Terraform server" to manage. You push code, the platform handles execution.
