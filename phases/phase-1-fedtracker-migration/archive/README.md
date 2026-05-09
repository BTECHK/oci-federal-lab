# Archive — Pre-4-Quadrant Originals

**Archived:** 2026-05-08  
**Reason:** Repo restructured to 4-quadrant model (Python app + Go app + Python serverless + Go serverless + Python CLI per phase).

## What's here

| Directory | Original location | Status |
|---|---|---|
| `app-original/` | `phases/phase-1-fedtracker-migration/app/` | Migrated to `fedtracker-app/answers/` (split into multi-file structure) |
| `docker-original/` | `phases/phase-1-fedtracker-migration/docker/main.py` | Reference only — docker/Dockerfile still in place |
| `functions-original/audit-processor/` | `phases/phase-1-fedtracker-migration/functions/audit-processor/` | Promoted to `functions/python/audit-processor/answers/func.py` |
| `functions-original/health-checker/` | `phases/phase-1-fedtracker-migration/functions/health-checker/` | Replaced by Go rewrite at `functions/go/health-checker-go/` |

## Canonical locations (post-restructure)

- Python app: `fedtracker-app/` (scaffold) + `fedtracker-app/answers/` (full impl)
- Python serverless: `functions/python/audit-processor/`
- Go serverless: `functions/go/health-checker-go/`
- Go app: `fedagent/`
- Python CLI: `fedplatform-cli/`
