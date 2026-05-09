# ADR-013: Instance Principal Auth for fedplatform-cli

**Status:** Accepted  
**Date:** 2026-05-08  
**Deciders:** Portfolio architect

---

## Context

`fedplatform-cli` needs to call OCI APIs (Object Storage, etc.) when operators run it on OCI VM instances. Authentication options:

1. **API key in `~/.oci/config`** — operator generates a key pair, uploads the public key to OCI Console, stores the private key in `~/.oci/config` on the VM.
2. **Instance Principal** — the VM itself has an IAM identity via a Dynamic Group. The OCI SDK automatically obtains short-lived tokens from the instance metadata endpoint; no file storage required.
3. **Resource Principal** — similar to Instance Principal but for OCI Functions and containers, not VMs.

---

## Decision

Use **Instance Principal** when running on an OCI VM; fall back to `~/.oci/config` for local development (developer's laptop).

Detection: attempt `InstancePrincipalsSecurityTokenSigner()`; catch the metadata-endpoint failure and fall back to config-file auth.

---

## Rationale

| Criterion | API Key (~/.oci/config) | Instance Principal |
|---|---|---|
| Credential storage on VM | Private key file on disk — rotation toil | No credentials on disk — tokens auto-rotated by OCI |
| EO 14028 / CMMC compliance | Long-lived credentials violate least-privilege requirements | Short-lived, automatically rotated — aligns with zero-trust |
| Key rotation | Manual — easily forgotten | Automatic — OCI handles it |
| Local development | Works natively | Requires ~/.oci/config fallback |
| IAM blast radius on breach | Compromised key = full API access until revoked | Compromised token expires in minutes |

The EO 14028 and CMMC rationale is decisive for federal tooling. Storing long-lived API keys on VMs is explicitly called out as a risk in federal security frameworks.

---

## Consequences

- The VM must be in a Dynamic Group with an IAM policy granting it the needed permissions (e.g., `manage objects in audit-evidence`).
- Local development still requires `~/.oci/config` (the same setup used for Terraform and the OCI CLI throughout the lab).
- The fallback detection adds one network round-trip on startup when running locally — acceptable.

---

## Implementation pattern (Python OCI SDK)

```python
import oci

def get_signer():
    """Return OCI signer: Instance Principal on VM, config file locally."""
    try:
        return oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    except Exception:
        config = oci.config.from_file()
        return oci.signer.Signer(
            tenancy=config["tenancy"],
            user=config["user"],
            fingerprint=config["fingerprint"],
            private_key_file_location=config["key_file"],
        )
```

---

## Learning Check

1. What is an OCI Instance Principal and how does it differ from an API key stored in `~/.oci/config`?
2. Why is storing API keys in environment variables on a production VM still a security risk under EO 14028?
3. How does the OCI Python SDK detect whether to use Instance Principal — what endpoint does it call?
4. Write the IAM policy statement that grants the `fedtracker-instances` Dynamic Group permission to write objects to the `audit-evidence` bucket.
5. What happens to fedplatform-cli's OCI calls if the VM is stopped and restarted — is re-authentication required?
