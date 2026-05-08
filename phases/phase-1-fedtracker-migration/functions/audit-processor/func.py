"""
Audit File Processor — OCI Function

Triggered: object created in audit-evidence bucket
Action:    read CSV → extract metadata → write structured JSON to audit-evidence-processed
           Ollama narrative synthesis is handled by narrative-consumer.py on the app server.
"""
import csv, io, json, logging, os
from collections import Counter
from datetime import datetime, timezone
import oci
from fdk import response

PROCESSED_BUCKET = os.environ.get("PROCESSED_BUCKET", "audit-evidence-processed")
log = logging.getLogger(__name__)


def handler(ctx, data: io.BytesIO = None):
    body       = json.loads(data.getvalue())
    namespace  = body["data"]["additionalDetails"]["namespace"]
    bucket     = body["data"]["additionalDetails"]["bucketName"]
    obj_name   = body["data"]["resourceName"]

    signer    = oci.auth.signers.get_resource_principals_signer()
    os_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)

    csv_bytes = os_client.get_object(
        namespace_name=namespace, bucket_name=bucket, object_name=obj_name
    ).data.content
    csv_text = csv_bytes.decode("utf-8")

    reader = csv.DictReader(io.StringIO(csv_text))
    rows   = list(reader)

    action_summary = dict(
        Counter(r.get("action", "UNKNOWN") for r in rows)
    )
    top_ips = [
        ip for ip, _ in Counter(
            r.get("source_ip", "") for r in rows if r.get("source_ip")
        ).most_common(5)
    ]

    artifact = {
        "source_bucket":  bucket,
        "source_object":  obj_name,
        "rows":           len(rows),
        "generated_utc":  datetime.now(timezone.utc).isoformat(),
        "action_summary": action_summary,
        "top_ips":        top_ips,
        "status":         "pending_narrative",
    }

    out_name = obj_name.rsplit(".", 1)[0] + ".json"
    os_client.put_object(
        namespace_name=namespace,
        bucket_name=PROCESSED_BUCKET,
        object_name=out_name,
        put_object_body=json.dumps(artifact, indent=2).encode("utf-8"),
    )
    log.info("Artifact written: %s/%s", PROCESSED_BUCKET, out_name)

    return response.Response(
        ctx,
        response_data=json.dumps({
            "source": obj_name,
            "artifact": out_name,
            "rows": len(rows),
            "status": "pending_narrative",
        }),
        headers={"Content-Type": "application/json"},
    )
