#!/bin/bash
# Destroy & Rebuild with Timing — captures real metrics for interview prep
# Run from repo root:
#   cd /mnt/c/Users/<your-windows-username>/OneDrive/Desktop/github/oci-federal-lab
#   bash tools/rebuild-and-time.sh

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TERRAFORM_DIR="$REPO_ROOT/phases/phase-1-fedtracker-migration/terraform"
INVENTORY="$REPO_ROOT/phases/phase-1-fedtracker-migration/ansible/inventory/inventory.ini"
METRICS_FILE="$REPO_ROOT/phases/phase-1-fedtracker-migration/docs/rebuild-metrics.txt"

cd "$REPO_ROOT"

echo "============================================"
echo " DESTROY & REBUILD — Timed Run"
echo " Started: $(date)"
echo "============================================"
echo ""

TOTAL_START=$SECONDS

# --- Phase 1: Destroy ---
echo "[1/5] Destroying infrastructure..."
PHASE_START=$SECONDS
terraform -chdir="$TERRAFORM_DIR" destroy -auto-approve
DESTROY_TIME=$(( SECONDS - PHASE_START ))
echo "      Destroy: ${DESTROY_TIME}s"

# --- Phase 2: Apply ---
echo ""
echo "[2/5] Rebuilding infrastructure..."
PHASE_START=$SECONDS
terraform -chdir="$TERRAFORM_DIR" apply -auto-approve
APPLY_TIME=$(( SECONDS - PHASE_START ))
echo "      Apply: ${APPLY_TIME}s"

# --- Phase 3: Update inventory ---
echo ""
echo "[3/5] Updating inventory and SSH config..."
bash "$REPO_ROOT/tools/update-inventory.sh"

# --- Wait for VMs to boot ---
echo ""
echo "[3.5] Waiting 60s for VMs to boot..."
sleep 60

# --- Phase 4: Harden ---
echo ""
echo "[4/5] Running hardening playbook..."
PHASE_START=$SECONDS
ansible-playbook -i "$INVENTORY" "$REPO_ROOT/phases/phase-1-fedtracker-migration/ansible/playbooks/harden.yml"
HARDEN_TIME=$(( SECONDS - PHASE_START ))
echo "      Harden: ${HARDEN_TIME}s"

# --- Phase 5: Deploy ---
echo ""
echo "[5/5] Running deploy playbook..."
PHASE_START=$SECONDS
ansible-playbook -i "$INVENTORY" "$REPO_ROOT/phases/phase-1-fedtracker-migration/ansible/playbooks/deploy_app.yml"
DEPLOY_TIME=$(( SECONDS - PHASE_START ))
echo "      Deploy: ${DEPLOY_TIME}s"

TOTAL_TIME=$(( SECONDS - TOTAL_START ))

# --- Health check ---
echo ""
echo "Verifying health..."
HEALTH=$(ssh -o StrictHostKeyChecking=no p1-app-server "curl -s http://localhost:8000/health" 2>/dev/null || echo "FAILED")
echo "  $HEALTH"

# --- Write metrics file ---
cat > "$METRICS_FILE" <<EOF
=== REBUILD METRICS ===
Date: $(date)

Terraform destroy:    $(( DESTROY_TIME / 60 ))m $(( DESTROY_TIME % 60 ))s
Terraform apply:      $(( APPLY_TIME / 60 ))m $(( APPLY_TIME % 60 ))s
VM boot wait:         1m 0s
Ansible hardening:    $(( HARDEN_TIME / 60 ))m $(( HARDEN_TIME % 60 ))s
Ansible deploy:       $(( DEPLOY_TIME / 60 ))m $(( DEPLOY_TIME % 60 ))s
---------------------------
Total wall clock:     $(( TOTAL_TIME / 60 ))m $(( TOTAL_TIME % 60 ))s

Health check: $HEALTH
===========================
EOF

echo ""
echo "============================================"
echo " REBUILD COMPLETE"
echo "============================================"
cat "$METRICS_FILE"
echo ""
echo "Metrics saved to: $METRICS_FILE"
