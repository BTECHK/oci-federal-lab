#!/bin/bash
# WSL2 Setup Script — installs Terraform and OCI CLI
# Run from WSL2: bash /mnt/c/Users/<your-windows-username>/OneDrive/Desktop/github/oci-federal-lab/tools/setup-wsl2.sh

set -e

echo "========================================="
echo " WSL2 Lab Setup — Terraform + OCI CLI"
echo "========================================="

# --- 1. Terraform ---
echo ""
echo "[1/2] Installing Terraform..."
wget -qO- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg 2>/dev/null
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list > /dev/null
sudo apt-get update -qq
sudo apt-get install -y terraform
echo "Terraform: $(terraform --version | head -1)"

# --- 2. OCI CLI ---
echo ""
echo "[2/2] Installing OCI CLI..."
pip install --quiet oci-cli 2>/dev/null || pip3 install --quiet oci-cli 2>/dev/null
echo "OCI CLI: $(oci --version)"

# --- Verify everything ---
echo ""
echo "========================================="
echo " Verification"
echo "========================================="
echo "Terraform:  $(command -v terraform && echo OK || echo MISSING)"
echo "Ansible:    $(command -v ansible && echo OK || echo MISSING)"
echo "Git:        $(command -v git && echo OK || echo MISSING)"
echo "SSH:        $(command -v ssh && echo OK || echo MISSING)"
echo "Python3:    $(command -v python3 && echo OK || echo MISSING)"
echo "Docker:     $(command -v docker && echo OK || echo 'MISSING — enable WSL2 integration in Docker Desktop settings')"
echo "OCI CLI:    $(command -v oci && echo OK || echo MISSING)"
echo ""
echo "Done. Run everything from:"
echo "  cd /mnt/c/Users/<your-windows-username>/OneDrive/Desktop/github/oci-federal-lab"
