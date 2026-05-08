# Fix #43 — Phase 17 Retrofit: Rewire OCI Functions Around the Real FedTracker Flow

**Status:** Planning only — not executed. Phase 1 is currently scope-frozen (see commit `a75fe02`, 2026-05-08), so the apply step requires explicit unfreeze approval before editing the implementation guide or app code.

**Source spec:**
- `RETROFIT-TODO.md` item #7
- Master design `../../Project ideas/2026-03-18-interview-lab-project-design.md`, lines 303–319

**One-line goal:** Replace the current Phase 17 *hypothetical* Object Storage trigger with a real end-to-end pipeline:
**FedTracker `POST /audit/export` → `audit-evidence` bucket → OCI Events → audit-processor Function → Ollama narrative synthesis → `audit-evidence-processed` bucket.** And retarget the health-check Function to hit a new `/health/deep` endpoint that exercises all dependencies, not just the DB.

---

## Problems with the current Phase 17

1. **The trigger source is fictional.** Step 17.4's function expects events from `audit-evidence`, but FedTracker writes nothing there. `POST /audit/export` exists at [main.py:304](../../phases/phase-1-fedtracker-migration/app/main.py#L304-L331) — but it streams CSV back to the caller, not to Object Storage. Nothing ever fires the Function in real operation.
2. **No reason for the Function to exist.** The function's only job is "extract event metadata, build a summary, return JSON." That's a `print` statement, not a serverless workload.
3. **Health-check Function is shallow.** Step 17.5 hits `/health` — which is just a SQLite SELECT 1. Says nothing about whether Object Storage is reachable, whether Ollama is up, or whether the disk is full. Misses the value of a deep probe.
4. **No production lesson.** Today's chapter teaches `fn deploy`. After the rewire, it teaches event-driven architecture, dynamic-group authn, cross-subnet networking, and graceful degradation.

---

## Code changes — `phases/phase-1-fedtracker-migration/app/main.py`

### Change 1: rewrite `POST /audit/export` ([main.py:304-331](../../phases/phase-1-fedtracker-migration/app/main.py#L304-L331))

Old behavior: build CSV in memory → return as `StreamingResponse`.

New behavior: build CSV in memory → upload to OCI Object Storage `audit-evidence` bucket → return JSON pointer.

```python
@app.post("/audit/export")
def export_audit_csv():
    """
    Export the audit log as CSV to Object Storage.
    Triggers downstream OCI Function via Events for narrative synthesis.
    Returns: JSON pointer to the uploaded object.
    """
    conn = get_db()
    rows = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC").fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "timestamp", "action", "resource_type",
                     "resource_id", "details", "source_ip"])
    for row in rows:
        writer.writerow([row[k] for k in
            ("id","timestamp","action","resource_type","resource_id","details","source_ip")])
    csv_bytes = output.getvalue().encode("utf-8")

    # Upload to OCI Object Storage using Instance Principal auth
    import oci
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    namespace = client.get_namespace().data
    bucket = os.environ.get("AUDIT_EVIDENCE_BUCKET", "audit-evidence")
    object_name = f"audit-export-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.csv"

    client.put_object(namespace_name=namespace,
                      bucket_name=bucket,
                      object_name=object_name,
                      put_object_body=csv_bytes,
                      content_type="text/csv")

    log_audit("EXPORT", "audit_log",
              details=f"Exported {len(rows)} entries → {bucket}/{object_name}")

    return {
        "bucket": bucket,
        "object": object_name,
        "namespace": namespace,
        "rows": len(rows),
        "size_bytes": len(csv_bytes)
    }
```

`requirements.txt` changes:
- Add `oci>=2.0.0`

### Change 2: add `GET /health/deep`

Insert after the existing `/health` handler (after [main.py:203](../../phases/phase-1-fedtracker-migration/app/main.py#L203)):

```python
@app.get("/health/deep")
def health_deep():
    """
    Deep health probe — exercises every external dependency.
    Returns 200 only if ALL components are healthy.
    Used by the OCI Function health-checker as the canonical liveness signal.
    """
    import shutil, requests
    components = {}

    # DB
    try:
        get_db().execute("SELECT 1")
        components["database"] = {"ok": True}
    except Exception as e:
        components["database"] = {"ok": False, "error": str(e)}

    # Object Storage (HEAD bucket)
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        c = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
        ns = c.get_namespace().data
        c.head_bucket(namespace_name=ns,
                      bucket_name=os.environ.get("AUDIT_EVIDENCE_BUCKET", "audit-evidence"))
        components["object_storage"] = {"ok": True, "namespace": ns}
    except Exception as e:
        components["object_storage"] = {"ok": False, "error": str(e)}

    # Ollama
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        components["ollama"] = {"ok": r.ok, "models": [m["name"] for m in r.json().get("models", [])]}
    except Exception as e:
        components["ollama"] = {"ok": False, "error": str(e)}

    # Disk
    du = shutil.disk_usage("/")
    components["disk"] = {"ok": du.free > 1_000_000_000,
                          "free_gb": round(du.free / 1e9, 1)}

    all_ok = all(c.get("ok") for c in components.values())
    body = {"status": "healthy" if all_ok else "degraded", "components": components}
    return JSONResponse(status_code=200 if all_ok else 503, content=body)
```

(Requires importing `JSONResponse` from `fastapi.responses` and `oci` at module top. Both already in `requirements.txt` after Change 1.)

---

## Terraform changes — `phases/phase-1-fedtracker-migration/terraform/`

### New file: `object-storage.tf`

```hcl
resource "oci_objectstorage_bucket" "audit_evidence" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.ns.namespace
  name           = "audit-evidence"
  access_type    = "NoPublicAccess"
  versioning     = "Enabled"  # required so Events fires
  metadata = { source = "fedtracker", lifecycle = "30d" }
}

resource "oci_objectstorage_bucket" "audit_evidence_processed" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.ns.namespace
  name           = "audit-evidence-processed"
  access_type    = "NoPublicAccess"
}

data "oci_objectstorage_namespace" "ns" {
  compartment_id = var.tenancy_ocid
}
```

### New file: `iam-fedtracker-instance.tf`

```hcl
# Dynamic group: any compute instance in the fedtracker-lab compartment
resource "oci_identity_dynamic_group" "fedtracker_instances" {
  compartment_id = var.tenancy_ocid
  name           = "fedtracker-instances"
  description    = "FedTracker app servers — write audit CSVs to Object Storage"
  matching_rule  = "instance.compartment.id = '${var.compartment_ocid}'"
}

# Policy: allow that dynamic group to put objects into audit-evidence
resource "oci_identity_policy" "fedtracker_instance_policies" {
  compartment_id = var.tenancy_ocid
  name           = "fedtracker-instance-policies"
  description    = "FedTracker VM permissions for audit export pipeline"
  statements = [
    "Allow dynamic-group fedtracker-instances to manage objects in compartment id ${var.compartment_ocid} where target.bucket.name = 'audit-evidence'",
    "Allow dynamic-group fedtracker-instances to read buckets in compartment id ${var.compartment_ocid}",
  ]
}
```

### New file: `events-and-functions.tf`

```hcl
# Event rule: fire when an object is created in audit-evidence
resource "oci_events_rule" "audit_evidence_created" {
  compartment_id = var.compartment_ocid
  display_name   = "audit-evidence-object-created"
  is_enabled     = true
  condition      = jsonencode({
    eventType = ["com.oraclecloud.objectstorage.createobject"]
    data = {
      additionalDetails = { bucketName = ["audit-evidence"] }
    }
  })
  actions {
    actions {
      action_type = "FAAS"
      function_id = oci_functions_function.audit_processor.id
      is_enabled  = true
    }
  }
}

# Resource principal policy for the Function — manage processed bucket + read source bucket
resource "oci_identity_policy" "audit_processor_fn_policies" {
  compartment_id = var.tenancy_ocid
  name           = "audit-processor-fn-policies"
  statements = [
    "Allow any-user to use functions-family in compartment id ${var.compartment_ocid} where ALL { request.principal.type='servicecode', request.principal.servicename='objectstorage' }",
    "Allow resource id ${oci_functions_function.audit_processor.id} to read objects in compartment id ${var.compartment_ocid} where target.bucket.name = 'audit-evidence'",
    "Allow resource id ${oci_functions_function.audit_processor.id} to manage objects in compartment id ${var.compartment_ocid} where target.bucket.name = 'audit-evidence-processed'",
  ]
}
```

(The Function resource itself — `oci_functions_application` and `oci_functions_function` — is added per the existing Step 17.2 OCI Console flow OR can be Terraform'd; current Step 17.2 uses Console, so plan keeps that and adds the *imports* via `terraform import` — alternative is to convert 17.2 to Terraform. **Open question for user.**)

### Existing security-list change

The Function deploys to `p1-fedtracker-public-subnet` (per Step 17.2). The app-server lives in `p1-fedtracker-private-subnet`. To let the Function call the app's Ollama at `:11434` and `/health/deep` at `:8000`, add to `network.tf` (or wherever the app-server private security list is defined):

```hcl
ingress_security_rules {
  protocol  = "6"  # TCP
  source    = "<public subnet CIDR>"  # narrow to the public subnet, not 0.0.0.0/0
  description = "Allow OCI Functions to call FedTracker /health/deep and Ollama"
  tcp_options { destination_port_range { min = 8000  max = 8000 } }
}
ingress_security_rules {
  protocol  = "6"
  source    = "<public subnet CIDR>"
  description = "Allow OCI Functions to reach Ollama for narrative synthesis"
  tcp_options { destination_port_range { min = 11434 max = 11434 } }
}
```

---

## Function code changes — `phases/phase-1-fedtracker-migration/functions/audit-processor/func.py`

Replace the current "extract metadata, return JSON" stub with a real handler that reads the CSV, calls Ollama, and writes a paired narrative artifact.

```python
"""
Audit File Processor — OCI Function
Triggered: object create in audit-evidence bucket
Action: read CSV → ask Ollama for a narrative summary → write
        <basename>.narrative.md to audit-evidence-processed bucket
"""
import io, json, logging, os
from datetime import datetime, timezone
import oci
import requests
from fdk import response

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://10.0.2.201:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "tinyllama")
PROCESSED_BUCKET = os.environ.get("PROCESSED_BUCKET", "audit-evidence-processed")

def handler(ctx, data: io.BytesIO = None):
    body = json.loads(data.getvalue())
    bucket = body["data"]["additionalDetails"]["bucketName"]
    namespace = body["data"]["additionalDetails"]["namespace"]
    obj_name = body["data"]["resourceName"]

    # Resource principal auth
    signer = oci.auth.signers.get_resource_principals_signer()
    os_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)

    # Read the CSV
    csv_bytes = os_client.get_object(namespace, bucket, obj_name).data.content
    csv_text = csv_bytes.decode("utf-8")
    line_count = csv_text.count("\n")
    head = "\n".join(csv_text.splitlines()[:20])  # first 20 lines into LLM context

    # Ask Ollama for a narrative
    prompt = (f"You are a federal compliance auditor. The following is the head of an audit log "
              f"CSV with {line_count} total rows. Summarize the top 3 actions, flag anomalies, "
              f"and recommend follow-up.\n\n{head}")
    try:
        r = requests.post(OLLAMA_URL,
                          json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
                          timeout=120)
        narrative = r.json().get("response", "[ollama empty]")
    except Exception as e:
        narrative = f"[ollama unreachable: {e}]"  # graceful degradation

    out = (f"# Audit Narrative — {obj_name}\n\n"
           f"- Source: `{bucket}/{obj_name}`\n"
           f"- Rows: {line_count}\n"
           f"- Generated: {datetime.now(timezone.utc).isoformat()}Z\n"
           f"- Model: {OLLAMA_MODEL}\n\n"
           f"---\n\n{narrative}\n")

    # Write the paired narrative artifact
    out_name = obj_name.rsplit(".", 1)[0] + ".narrative.md"
    os_client.put_object(namespace, PROCESSED_BUCKET, out_name,
                         out.encode("utf-8"))

    return response.Response(ctx,
        response_data=json.dumps({"source": obj_name, "narrative": out_name,
                                  "rows": line_count}),
        headers={"Content-Type": "application/json"})
```

`requirements.txt` changes:
- Add `requests>=2.31`
- (Already had `oci`, `fdk`.)

`func.yaml` changes:
- `timeout: 300` (was 120) — Ollama on tinyllama can take 30–60 s
- `memory: 512` (was 256) — `oci` SDK + `requests` adds RSS

---

## Function code changes — `phases/phase-1-fedtracker-migration/functions/health-checker/func.py`

Two changes: target URL and verdict logic.

- **URL:** `http://app-server:8000/health` → `http://10.0.2.201:8000/health/deep` (or wire via function config var so it's not hardcoded).
- **Verdict logic:** parse the new multi-component body; surface which component failed; treat 503 as `DEGRADED` (still alive, partial dependency loss) and connect-error as `UNREACHABLE`.

```python
result = {
    "function": "health-checker",
    "checked_at": datetime.now(timezone.utc).isoformat() + "Z",
    "target": app_url,
    "status_code": status_code,
    "verdict": "HEALTHY" if status_code == 200 else "DEGRADED",
    "components": body.get("components", {}),
    "failures": [name for name, c in body.get("components", {}).items()
                 if not c.get("ok")]
}
```

---

## Guide changes — `phases/phase-1-fedtracker-migration/docs/implementation-guide.md`

| Existing location | Change |
|---|---|
| Phase 17 intro (line 7443) | Reframe from "two functions" to "one end-to-end pipeline (export → bucket → Function → narrative) plus one deep-health probe." |
| **NEW Step 17.0 — Provision the Pipeline Backbone** (insert ~line 7470) | Walk the user through `terraform apply` for the new buckets, dynamic group, policies, event rule, and security-list rules. Verify with `oci os bucket get --name audit-evidence`. |
| Step 17.4 (lines 7516–7641) | Rewrite per the new `audit-processor/func.py` above. New `requirements.txt` and `func.yaml` snippets. New "Why this works" callout: dynamic-group on the VM authorizes the upload; resource-principal on the Function authorizes the read+write+downstream-Ollama. |
| Step 17.5 (lines 7643–7740) | Rewrite per the new `health-checker/func.py` above. Update target URL discussion. Add a sub-callout: "the deep-health endpoint is the canonical liveness signal — a function that calls a function that calls a deep probe is the federal-grade health check pattern." |
| **NEW Step 17.7 — End-to-End Test** (after 17.6) | New section, see verify block below. |
| Phase 17 Troubleshooting table (line 7772) | Add 5 new rows: (a) "Function 401 from Object Storage" → resource principal policy missing or wrong dynamic group rule; (b) "Function timeout calling Ollama" → security-list ingress on 11434 missing or Ollama bound to 127.0.0.1; (c) "Event rule never fires" → bucket versioning must be enabled; (d) "POST /audit/export returns 500 with NotAuthenticated" → instance principal token expired or dynamic-group policy missing; (e) "/health/deep returns 503 with object_storage failure" → expected on first run if Terraform hasn't applied yet. |
| Day 5 / Phase 17 recap | Add: "I built an event-driven Object Storage → Function → Ollama pipeline using Instance Principal on the producer, Resource Principal on the consumer, and a deep-health probe to validate the dependency graph." |

---

## Step 17.7 — End-to-End Test (verify block to copy in)

```bash
# 1. From the app-server, trigger the export
ssh p1-app-server
curl -X POST http://localhost:8000/audit/export
# Expected:
# {"bucket":"audit-evidence","object":"audit-export-20260508T...Z.csv","rows":N,...}

# 2. Confirm the Function fired (Logging Search)
oci logging-search search-logs --search-query \
  "search \"<compartment-OCID>/<log-group-OCID>/<log-OCID>\" | source.service=\"functions\" | message=\"audit-processor\"" \
  --time-start "$(date -u -d '5 minutes ago' '+%Y-%m-%dT%H:%M:%SZ')" \
  --time-end   "$(date -u                        '+%Y-%m-%dT%H:%M:%SZ')"

# 3. Confirm the paired narrative artifact landed
oci os object list --bucket-name audit-evidence-processed --output table
oci os object get  --bucket-name audit-evidence-processed \
                   --name audit-export-<ts>.narrative.md --file -

# 4. Health probe — exercise all dependencies
echo '{}' | fn invoke fedtracker-functions health-checker
# Expected: {"verdict":"HEALTHY","components":{...all ok...},"failures":[]}

# 5. Deliberate failure — stop Ollama, re-probe, see DEGRADED
sudo systemctl stop ollama
echo '{}' | fn invoke fedtracker-functions health-checker
# Expected: {"verdict":"DEGRADED","failures":["ollama"],...}
sudo systemctl start ollama
```

---

## Interview framing block (copy into Step 17 recap)

> **💼 Interview Insight — Event-Driven Architecture in OCI:** "I wired a real event-driven pipeline instead of a contrived one. FedTracker's `POST /audit/export` writes a CSV to Object Storage using Instance Principal auth — the VM has a dynamic-group identity, no static credentials. The bucket emits a `createobject` event, OCI Events routes it to the audit-processor Function, and the Function — running under Resource Principal — reads the CSV, calls Ollama on the private subnet for a narrative synthesis, and writes the paired markdown back to a processed bucket. The lesson is that the same federation that lets your VM talk to Object Storage without keys lets your Function talk to your VM without keys: dynamic groups for compute, resource principals for serverless, and policies that scope on `target.bucket.name` so each identity has the minimum surface. The `/health/deep` probe makes the dependency graph observable — when ZeroOps is broken, you see exactly which dependency dropped, not a generic 'unhealthy.'"

---

## Acceptance criteria

- [ ] `POST /audit/export` writes CSV to `audit-evidence` bucket and returns JSON pointer (no more `StreamingResponse`).
- [ ] `GET /health/deep` returns 200 when all components healthy, 503 with per-component detail otherwise.
- [ ] `terraform apply` creates: 2 buckets, 1 dynamic group, 2 policies, 1 event rule, 2 security-list rules.
- [ ] `audit-processor` reads from `audit-evidence`, calls Ollama, writes to `audit-evidence-processed`.
- [ ] `health-checker` targets `/health/deep` and surfaces per-component failures.
- [ ] End-to-end: `curl POST /audit/export` produces a `.narrative.md` in `audit-evidence-processed` within 60 s.
- [ ] Deliberate failure (stop Ollama) flips `health-checker` from `HEALTHY` → `DEGRADED` with `failures: ["ollama"]`.
- [ ] All 5 new troubleshooting rows are present in the Phase 17 table.

---

## Open questions before apply

1. **Phase 1 scope freeze** — same as Plan #42. This is a substantial multi-file change inside a frozen phase. Apply in Phase 1, defer to a Phase 2/3 callback ("Phase 1 had a stub Function; here's the real event-driven pipeline"), or split (the FastAPI changes live in Phase 1 because main.py is there, but the Function rewrite lives in Phase 2 where event-driven architecture is taught more deeply)?
2. **Plan B for cross-subnet Ollama** — calling Ollama *from* a Function *to* a private VM is a real cross-subnet design; it works but it's fragile (Ollama must bind `0.0.0.0`, security-list must permit 11434, function VCN attachment must be configured). Cleaner alternative: Function uploads CSV to processed bucket *without* narrative, and a small consumer on the VM polls the bucket and adds the narrative locally. Worth considering — adds a second component but removes the cross-subnet network dependency. Confirm preferred path.
3. **Step 17.2 Console-vs-Terraform** — current Step 17.2 creates the Functions Application via OCI Console. The retrofit can keep that and just `terraform import` the resulting OCID, OR convert to full Terraform. Convert is cleaner pedagogically but adds 30 minutes to the step. Confirm preference.
4. **Model choice for narrative synthesis** — same question as Plan #42. tinyllama narrative quality is poor. Bumping to qwen2.5:1.5b or llama3.2:1b improves it materially. OK with the additional ~1 GB pull?
