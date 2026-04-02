#!/bin/bash
# =============================================================
# THROWAWAY SCRIPT — Delete after instance is created
# Creates A1.Flex instance with cloud-init bootstrap
# Run from: OCI Cloud Shell (has OCI CLI pre-configured)
# =============================================================

set -e

# --- CONFIGURATION (from your existing infrastructure) ---
COMPARTMENT_OCID="ocid1.compartment.oc1..YOUR_COMPARTMENT_OCID"
DISPLAY_NAME="legacy-server"
SHAPE="VM.Standard.A1.Flex"
OCPUS=2
MEMORY_GB=12

# SSH public key — paste yours between the quotes
# Get it from: cat ~/.ssh/oci-federal-lab/*.pub
SSH_PUBLIC_KEY="PASTE_YOUR_PUBLIC_KEY_HERE"

# --- AUTO-DETECT (Cloud Shell knows your tenancy) ---
echo "=== Detecting subnet and image OCIDs... ==="

# Find the public subnet in legacy-vcn
VCN_OCID=$(oci network vcn list \
  --compartment-id "$COMPARTMENT_OCID" \
  --display-name "legacy-vcn" \
  --query 'data[0].id' --raw-output 2>/dev/null)

if [ -z "$VCN_OCID" ]; then
  echo "ERROR: Could not find legacy-vcn in compartment. Check compartment OCID."
  exit 1
fi
echo "  VCN: $VCN_OCID"

SUBNET_OCID=$(oci network subnet list \
  --compartment-id "$COMPARTMENT_OCID" \
  --vcn-id "$VCN_OCID" \
  --display-name "public-subnet-legacy-vcn" \
  --query 'data[0].id' --raw-output 2>/dev/null)

if [ -z "$SUBNET_OCID" ]; then
  echo "ERROR: Could not find public-subnet-legacy-vcn."
  exit 1
fi
echo "  Subnet: $SUBNET_OCID"

# Find latest Oracle Linux 9 aarch64 image
IMAGE_OCID=$(oci compute image list \
  --compartment-id "$COMPARTMENT_OCID" \
  --operating-system "Oracle Linux" \
  --operating-system-version "9" \
  --shape "$SHAPE" \
  --sort-by TIMECREATED --sort-order DESC \
  --query 'data[0].id' --raw-output 2>/dev/null)

if [ -z "$IMAGE_OCID" ]; then
  echo "ERROR: Could not find Oracle Linux 9 ARM image."
  exit 1
fi
echo "  Image: $IMAGE_OCID"

# --- CLOUD-INIT USER DATA ---
CLOUD_INIT=$(cat <<'CLOUDINIT'
#!/bin/bash
# Bootstrap Steps 2.1-2.2 so user can start at Step 2.3

# Create clouduser with sudo
useradd -m clouduser
usermod -aG wheel clouduser
echo "clouduser ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/clouduser
chmod 440 /etc/sudoers.d/clouduser

# Password aging (NIST 800-53 IA-5)
chage -M 90 -m 7 -W 14 clouduser

# Create service account
useradd -r -s /sbin/nologin -M svc-fedtracker

# Install packages
dnf update -y
dnf install -y git wget curl vim
dnf install -y python3 python3-pip python3-devel

# Signal completion
touch /tmp/cloud-init-complete
echo "Cloud-init bootstrap complete at $(date)" >> /var/log/cloud-init-bootstrap.log
CLOUDINIT
)

# Base64 encode the cloud-init script
USERDATA_B64=$(echo "$CLOUD_INIT" | base64 -w 0)

# --- TRY ALL 3 AVAILABILITY DOMAINS ---
echo ""
echo "=== Attempting instance creation across all ADs... ==="

# Get list of ADs
ADS=$(oci iam availability-domain list \
  --compartment-id "$COMPARTMENT_OCID" \
  --query 'data[].name' --raw-output 2>/dev/null | tr -d '[]"' | tr ',' '\n' | sed 's/^ //')

for AD in $ADS; do
  AD=$(echo "$AD" | xargs)  # trim whitespace
  echo ""
  echo "--- Trying $AD ---"

  INSTANCE_ID=$(oci compute instance launch \
    --compartment-id "$COMPARTMENT_OCID" \
    --availability-domain "$AD" \
    --shape "$SHAPE" \
    --shape-config "{\"ocpus\": $OCPUS, \"memoryInGBs\": $MEMORY_GB}" \
    --display-name "$DISPLAY_NAME" \
    --image-id "$IMAGE_OCID" \
    --subnet-id "$SUBNET_OCID" \
    --assign-public-ip true \
    --ssh-authorized-keys "$SSH_PUBLIC_KEY" \
    --user-data "$USERDATA_B64" \
    --defined-tags '{"fedlab-cost": {"phase": "phase-1", "owner": "lab-operator", "component": "compute", "project": "fedtracker"}}' \
    --query 'data.id' --raw-output 2>/dev/null) || true

  if [ -n "$INSTANCE_ID" ] && [ "$INSTANCE_ID" != "null" ]; then
    echo "  SUCCESS! Instance launching: $INSTANCE_ID"
    echo ""
    echo "=== Waiting for instance to reach RUNNING state... ==="

    oci compute instance get \
      --instance-id "$INSTANCE_ID" \
      --wait-for-state RUNNING \
      --max-wait-seconds 300 2>/dev/null || true

    # Get the public IP
    VNIC_ATTACHMENTS=$(oci compute vnic-attachment list \
      --compartment-id "$COMPARTMENT_OCID" \
      --instance-id "$INSTANCE_ID" \
      --query 'data[0]."vnic-id"' --raw-output 2>/dev/null)

    PUBLIC_IP=$(oci network vnic get \
      --vnic-id "$VNIC_ATTACHMENTS" \
      --query 'data."public-ip"' --raw-output 2>/dev/null)

    echo ""
    echo "============================================="
    echo "  INSTANCE CREATED SUCCESSFULLY"
    echo "============================================="
    echo "  Name:      $DISPLAY_NAME"
    echo "  Shape:     $SHAPE ($OCPUS OCPU / ${MEMORY_GB}GB)"
    echo "  AD:        $AD"
    echo "  Public IP: $PUBLIC_IP"
    echo "  Instance:  $INSTANCE_ID"
    echo ""
    echo "  SSH command:"
    echo "    ssh opc@$PUBLIC_IP"
    echo ""
    echo "  Cloud-init is running in background."
    echo "  Wait 3-5 min, then verify:"
    echo "    ssh opc@$PUBLIC_IP 'cat /tmp/cloud-init-complete'"
    echo "    ssh opc@$PUBLIC_IP 'python3 --version'"
    echo "    ssh opc@$PUBLIC_IP 'id clouduser'"
    echo "============================================="
    exit 0
  else
    echo "  Failed in $AD (likely out of capacity). Trying next..."
  fi
done

echo ""
echo "============================================="
echo "  ALL ADs FAILED — out of capacity"
echo "============================================="
echo "  Try again in a few hours (off-peak: 2-6 AM EST)"
echo "  Or check: has your account upgrade completed?"
echo "    OCI Console → Billing → Account Type"
echo "============================================="
exit 1
