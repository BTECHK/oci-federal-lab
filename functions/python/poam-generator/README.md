# poam-generator (v3, P3 — stretch)

Drafts a **POA&M** (Plan of Action & Milestones) item from a HIGH-severity finding
and its classified control, using the **local Ollama** (air-gapped — no external API).

- **Trigger:** OCI Events on a HIGH finding, or a scheduled sweep.
- **Input:** a finding + the control_id(s) assigned by the evidence-collector
  classifier (ADR-022).
- **Output:** a POA&M **draft** (weakness, source, control, remediation, milestones,
  scheduled completion, resources) written to `compliance-artifacts/poam-drafts/`
  and optionally inserted into `poam_items` as `status='draft'`.

Drafts are **not final** — they require human review/sign-off before becoming an
open POA&M. The `poam_items` table DDL is yours to write (DB track).

See `adrs/ADR-022-llm-evidence-classification-poam.md`. Scaffold + `answers/` only.
