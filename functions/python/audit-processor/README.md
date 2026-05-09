# audit-processor

OCI Function (Python). Triggered when a CSV is uploaded to the `audit-evidence/` bucket.
Reads the CSV, extracts action summary + top source IPs, writes a JSON artifact to `audit-evidence-processed/`.

Trigger: OCI Events — Object Storage createobject on audit-evidence/
Auth: Resource Principal (no API key required)

## Patterns exercised
1. fdk (Oracle Function Development Kit) handler signature
2. OCI Object Storage client with resource principal auth
3. CSV parsing with csv.DictReader
4. Structured JSON artifact output

## P1 learning: Compare with functions/go/health-checker-go/ to see Python vs Go serverless patterns
