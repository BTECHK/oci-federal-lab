# Migrations — USER WRITES

Flyway-style migration files. Naming: `V<number>__<description>.sql`.

**Suggested initial migrations:**
- `V001__initial_schema.sql` — combines schemas/01-tables.sql through 04-constraints.sql into a single migration
- `V002__add_app_logs_table.sql` — for P2 ingest pipeline
- `V003__add_compliance_controls_table.sql` — for P3

**Why Flyway over Liquibase here:**
- Pure SQL files (no XML changelog) — easier to review in PR
- Convention-based ordering (Vnnn prefix) is unambiguous
- Native Oracle support, plays well with ADB wallet auth

**Migration runner config:** see `../../tools/` for the runner script (Claude-scaffolded).

**Discipline:**
- Migrations are append-only. Never edit a migration that has been applied to any environment.
- New schema changes go in new V<n>__ files, not by editing V001.
- Use V001 for the initial state; iterate forward.
