# Seed Data — Claude-scaffolded, user-customized

Faker-based Python script that populates tables with realistic synthetic data after migrations have run.

`generate.py` (scaffold below) generates data for:
- `personnel` (~50 rows)
- `audit_log` (~500 rows, mixed actions)
- `app_logs` (P2+; ~1000 rows, varied severity)
- `compliance_controls` (P3+; ~30 control mappings from CMMC catalog)

**How to run:**
```
pip install -r requirements.txt
export DATABASE_URL='oracle://user:pwd@host:port/service'
python generate.py --rows-personnel 50 --rows-audit 500
```

**Customizing:**
The scaffold defines `generate_personnel()`, `generate_audit()`, etc. as Python functions. Adjust the Faker providers, distributions, and row counts to match your test scenarios.

**Reference implementation in `seed/answers/`** (gitignored) — complete working Faker script. Check after attempting your own customization.
