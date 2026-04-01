# Fix #41 — Terraform Step 11 Gaps: SSH Key, Image ID, Oracle Linux Version

## Problems Found

### 1. `ssh_public_key_path` references a key that doesn't exist

**Line 4752:** `ssh_public_key_path = "~/.ssh/fedtracker.pub"`

`fedtracker.pub` is never created anywhere in the guide. The guide creates these SSH keys:
- Step 2.1: `legacy-server.key` / `.pub` (for Day 1 VM, now destroyed)
- Step 8.3: `bastion.key` / `.pub` (for bastion VM)
- Step 8.5: `app-server.key` / `.pub` (for app server VM)

The user has no `fedtracker.pub`. This leaves them guessing which key to use.

**Fix:** Add guidance BEFORE the tfvars code block explaining:

```markdown
> **Which SSH key?** Terraform creates NEW VMs, so you need to tell it which public key to inject.
> You can reuse your existing bastion public key — it's already on your machine and works fine for a lab:
>
> ```bash
> # Find your bastion public key
> ls ~/.ssh/*bastion*.pub
> # Use that path for ssh_public_key_path below
> ```
>
> In production, you'd generate a dedicated key per environment. For this lab, reusing the bastion key avoids unnecessary key management.
```

Then change the tfvars example:

FROM:
```hcl
ssh_public_key_path    = "~/.ssh/fedtracker.pub"
```

TO:
```hcl
ssh_public_key_path    = "~/.ssh/<YOUR_BASTION_PUBLIC_KEY>.pub"
```

### 2. `oracle_linux_image_id` — no instructions to find it

**Line 4753:** `oracle_linux_image_id = "ocid1.image.oc1.iad.xxxxxxxxxxxxx"`

**Line 4756:** Says "Get the image OCID from the OCI Console: Compute → Images → Oracle Linux 8" — but the user is on Oracle Linux 9 (OL9), and the console nav path is incomplete.

**Fix:** Replace line 4756 with explicit instructions:

```markdown
> **How to find the Oracle Linux image OCID:**
>
> **Option A — OCI Console:**
> 1. Go to **Compute** → **Images**
> 2. Filter: Image source = "Platform images", Operating system = "Oracle Linux", OS version = "9"
> 3. Find the **aarch64** image (for A1 Flex shape) — click the image name
> 4. Copy the OCID from the image details page
>
> **Option B — OCI CLI** (Cloud Shell or local):
> ```bash
> oci compute image list \
>   --compartment-id <COMPARTMENT_OCID> \
>   --operating-system "Oracle Linux" \
>   --operating-system-version "9" \
>   --shape "VM.Standard.A1.Flex" \
>   --query "data[0].id" \
>   --raw-output
> ```
>
> ⚠️ Image OCIDs are **region-specific**. If you're in `us-ashburn-1`, the OCID starts with `ocid1.image.oc1.iad.`. A different region will have a different OCID.
```

### 3. `variables.tf` says "Oracle Linux 8" but user is on OL9

**Line 4705:** `description = "OCID of the Oracle Linux 8 image (region-specific)"`

The guide established in Step 8 that OL9 works fine (and OL8+A1 Flex may not be available). The variable description should say "Oracle Linux" without a version number, or "Oracle Linux 9".

**Fix:**

FROM:
```hcl
variable "oracle_linux_image_id" {
  description = "OCID of the Oracle Linux 8 image (region-specific)"
  type        = string
}
```

TO:
```hcl
variable "oracle_linux_image_id" {
  description = "OCID of the Oracle Linux image (region-specific, use OL9 for A1 Flex)"
  type        = string
}
```

Also update `terraform/variables.tf` in the repo (already clean, but check the description matches).

### 4. `private_key_path` may not exist on local machine

**Line 4749:** `private_key_path = "~/.oci/oci_api_key.pem"`

This is the OCI API signing key (not SSH). Step 6.1 created this key on the legacy-server VM, which has been destroyed. If the user didn't also set it up locally, Terraform can't authenticate.

This is **Fix #35** from the earlier sweep — the API key transfer gap. The tfvars file references a local file that may not exist. Step 11.5 should either:
- Reference the Step where the user sets up their local OCI CLI config, OR
- Add a check: "Verify `~/.oci/oci_api_key.pem` exists on your local machine. If not, generate a new API key: `oci setup keys` or create one in the OCI Console under Profile → API Keys."

## Files to Modify

- `docs/phase-1-implementation-guide.md`:
  - Line 4705: Update variable description from OL8 to OL9
  - Lines 4740-4756: Add SSH key guidance, image OCID lookup instructions, API key verification
  - Line 4752: Change placeholder from `fedtracker.pub` to `<YOUR_BASTION_PUBLIC_KEY>.pub`
- `terraform/variables.tf`: Update `oracle_linux_image_id` description (line ~112)

## Why This Matters

These are all "the user gets stuck at terraform plan/apply" gaps. Without the right image OCID, the plan fails. Without the right SSH key path, the plan fails. Without the API key locally, authentication fails. Three separate blockers in one step, all fixable with better instructions.
