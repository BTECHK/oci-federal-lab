# Evidence Artifacts — FedPlatform

This directory captures the **evidence of execution** for the FedPlatform portfolio project. Every implementation guide step has an EVIDENCE CHECKPOINT specifying what to capture here.

## Why this exists

Implementation guides say "I followed steps." Evidence says "I produced output." When hiring managers review a portfolio, **evidence proves the work happened** — not just that it was planned.

## Folder map

| Folder | What lives here |
|---|---|
| `admin/p{1,2,3}/` | Output of admin days per phase: hardened config files, captured command outputs, labeled screenshots, reflection notes |
| `db/` | Database design + schemas + procedures + migrations (user-written), plus EXPLAIN ANALYZE captures and Faker seed scripts (agent-scaffolded) |
| `runbooks/` | Ops procedures (Symptom → Diagnostics → Remediation → Verification → Escalation), scaffolded with section comments; user fills commands during admin day execution |
| `dr-drills/` | DR scenario reports with pre/post SLI snapshots, failure injection commands, recovery measurements, postmortems |
| `network/` | nmap scans, tcpdump captures, iptables snapshots (with annotations) |
| `reports/` | SLO breakdowns, postmortem summaries, ad-hoc analysis outputs |
| `screenshots/` | Labeled cloud console captures (general, not phase-specific) |
| `key-takeaways/` | Per-phase compressed interview prep (`p1-takeaways.md`, `p2-takeaways.md`, `p3-takeaways.md`) |

## Discipline

- Commit evidence as you produce it. Don't batch-commit at end of phase.
- Use the EVIDENCE CHECKPOINT format in implementation guides to know what to capture.
- Annotate captures with context: when, why, what you observed. A raw tcpdump pcap without notes is half-evidence.
- `key-takeaways/` is interview prep, not project documentation. Format: "if asked about X, here are 5 bullets to lead with."

## Excluded

- `answers/` reference implementations live in component folders (e.g., `fedtracker-app/answers/`), not here. They're gitignored.
- Personal working notes live in `phases/phase-N-*/docs/implementation-guide.md` (gitignored). The tracked public guide is `phases/phase-N-*/docs/PHASE-GUIDE.md`.
