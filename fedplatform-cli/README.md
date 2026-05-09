# fedplatform-cli

Python operator CLI for FedPlatform. Wraps the FedTracker API and FedAgent metrics.
Authenticates via Instance Principal on OCI VMs, falls back to ~/.oci/config locally.

## Install
```bash
pip install -r requirements.txt
```

## P1 commands
- `fedplatform-cli list-personnel [--clearance LEVEL]` — list personnel records
- `fedplatform-cli export-audit [--since Nd]` — trigger audit log export to Object Storage
- `fedplatform-cli compliance-check [--framework fedramp|nist]` — check OpenSCAP score from FedAgent

## Phase evolution
- P2: dr-status, failover-check --rto
- P3: scan-trigger, policy-report --output json|md, pipeline-status

## ADR
See adrs/ADR-013-cli-instance-principal-auth.md for authentication design.
