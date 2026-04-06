#!/bin/bash
# Updates Ansible inventory with current Terraform output IPs
# Run from repo root after terraform apply:
#   bash tools/update-inventory.sh

set -e

TERRAFORM_DIR="phases/phase-1-fedtracker-migration/terraform"
INVENTORY="phases/phase-1-fedtracker-migration/ansible/inventory/inventory.ini"

# Must run from repo root
if [ ! -d "$TERRAFORM_DIR" ]; then
  echo "ERROR: Run this from the repo root directory."
  echo "  cd /mnt/c/Users/<your-windows-username>/OneDrive/Desktop/github/oci-federal-lab"
  exit 1
fi

# Capture IPs from Terraform
echo "Reading Terraform outputs..."
BASTION_IP=$(terraform -chdir="$TERRAFORM_DIR" output -raw bastion_public_ip)
APP_IP=$(terraform -chdir="$TERRAFORM_DIR" output -raw app_server_private_ip)

echo "  Bastion:    $BASTION_IP"
echo "  App Server: $APP_IP"

# Update inventory — 3 sed commands
# 1. Bastion public IP
sed -i "s/bastion_server ansible_host=[^ ]*/bastion_server ansible_host=$BASTION_IP/" "$INVENTORY"

# 2. App server private IP
sed -i "s/app-server ansible_host=[^ ]*/app-server ansible_host=$APP_IP/" "$INVENTORY"

# 3. Bastion IP inside ProxyCommand
sed -i "s/opc@[0-9.]\+\"/opc@$BASTION_IP\"/" "$INVENTORY"

# Update WSL2 SSH config (creates if missing)
SSH_CONFIG="$HOME/.ssh/config"
echo "Updating SSH config at $SSH_CONFIG..."
mkdir -p "$HOME/.ssh"
cat > "$SSH_CONFIG" <<EOF
Host p1-bastion
    HostName $BASTION_IP
    User opc
    IdentityFile ~/.ssh/oci-federal-lab/<your-bastion-ssh-key>.key

Host p1-app-server
    HostName $APP_IP
    User opc
    IdentityFile ~/.ssh/oci-federal-lab/<your-appserver-ssh-key>.key
    ProxyJump p1-bastion
EOF
chmod 600 "$SSH_CONFIG"

# Verify
echo ""
echo "Updated inventory:"
cat "$INVENTORY"
echo ""
echo "Updated SSH config:"
cat "$SSH_CONFIG"
echo ""
echo "Done. Next steps:"
echo "  ssh p1-bastion 'echo SUCCESS'"
echo "  ssh p1-app-server 'echo SUCCESS'"
echo "  ansible-playbook -i $INVENTORY phases/phase-1-fedtracker-migration/ansible/playbooks/harden.yml"
echo "  ansible-playbook -i $INVENTORY phases/phase-1-fedtracker-migration/ansible/playbooks/deploy_app.yml"
