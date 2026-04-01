#!/bin/bash
# =============================================================
# app-server-setup.sh — Prepare a fresh OCI compute instance for FedTracker
# Replicates the Day 1 legacy-server setup on the new app-server.
#
# Run on:  app-server (SSH via bastion)
# Run as:  opc (default OCI user with sudo)
# Usage:   bash app-server-setup.sh
#
# Idempotent — safe to re-run if interrupted.
# =============================================================
set -euo pipefail

echo "=== 1/6 Creating clouduser ==="
if id clouduser &>/dev/null; then
    echo "  clouduser already exists — skipping"
else
    sudo useradd -m clouduser
    sudo usermod -aG wheel clouduser
    sudo chage -M 90 -m 7 -W 14 clouduser
    echo "  Created clouduser with wheel group + password aging"
fi

echo "=== 2/6 Setting up clouduser sudo ==="
if [ -f /etc/sudoers.d/clouduser ]; then
    echo "  sudoers drop-in already exists — skipping"
else
    echo 'clouduser ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/clouduser > /dev/null
    sudo chmod 440 /etc/sudoers.d/clouduser
    sudo visudo -c
    echo "  NOPASSWD:ALL configured (lab only — tighten with Ansible on Day 3)"
fi

echo "=== 3/6 Creating service account ==="
if id svc-fedtracker &>/dev/null; then
    echo "  svc-fedtracker already exists — skipping"
else
    sudo useradd -r -s /sbin/nologin -M svc-fedtracker
    echo "  Created svc-fedtracker (no login, no home)"
fi

echo "=== 4/6 Installing Python 3.11 ==="
if command -v python3.11 &>/dev/null; then
    echo "  python3.11 already installed — $(python3.11 --version)"
else
    sudo dnf install -y python3.11 python3.11-pip python3.11-devel
    echo "  Installed $(python3.11 --version)"
fi

echo "=== 5/6 Installing Python packages ==="
sudo python3.11 -m pip install fastapi uvicorn pydantic oracledb
echo "  Installed fastapi, uvicorn, pydantic, oracledb"

echo "=== 6/6 Setting up directories ==="
sudo mkdir -p /opt/fedtracker
sudo chown clouduser:clouduser /opt/fedtracker
sudo mkdir -p /opt/oracle/wallet
sudo chown clouduser:clouduser /opt/oracle/wallet
echo "  /opt/fedtracker (owned by clouduser)"
echo "  /opt/oracle/wallet (owned by clouduser, for ADB wallet)"

echo ""
echo "=== Setup complete ==="
echo "Verify:"
echo "  id clouduser"
echo "  python3.11 --version"
echo "  python3.11 -c \"import fastapi, uvicorn, pydantic, oracledb; print('All packages OK')\""
echo "  ls -la /opt/fedtracker"
