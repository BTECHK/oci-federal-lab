# Database Layer — User-Written + Scaffolded Tooling

**Convention:** User writes DDL, procedures, migrations, and design rationale. Agents/Claude scaffold the tooling (Faker seed scripts, migration runner config, integration glue code).

This is intentional — SQL is your strength; the lab keeps it sharp instead of auto-provisioning it away.

## What goes where

| Folder | Owner | Contents |
|---|---|---|
| `schemas/` | **USER WRITES** | DDL — `01-tables.sql`, `02-indexes.sql`, `03-views.sql`, `04-constraints.sql` (PL/SQL dialect for Oracle ADB) |
| `procedures/` | **USER WRITES** | Stored procedures + functions (PL/SQL) |
| `migrations/` | **USER WRITES** | Migration files (Flyway/Liquibase style) — `V001__initial_schema.sql`, etc. |
| `seed/` | Claude scaffolds, user customizes | `generate.py` Faker-based data generator |
| `explain-output/` | **USER CAPTURES** | EXPLAIN ANALYZE output before/after index addition, with annotations |
| `design-doc.md` | **USER WRITES** | Schema rationale: normalization, indexes, partitioning, locking model |

## Order to write (recommended)

1. `design-doc.md` — write the rationale first; it forces you to think about access patterns before DDL
2. `schemas/01-tables.sql` — table DDL based on the access patterns
3. `schemas/02-indexes.sql` — indexes derived from query patterns
4. `schemas/03-views.sql` — views for common access patterns
5. `schemas/04-constraints.sql` — FKs, CHECK constraints, unique constraints
6. `procedures/` — PL/SQL for batch operations or complex logic
7. `migrations/V001__initial_schema.sql` — your initial DDL as a single migration file (Flyway/Liquibase format)
8. Run `seed/generate.py` to populate (Claude provides this)
9. Capture EXPLAIN ANALYZE output as you tune queries

## ADR

Write `adrs/ADR-XXX-db-design-decisions.md` — your schema rationale as an architectural decision record with 5 quiz questions + Key Takeaways. This is the file you'd put in front of an L6 interviewer to explain your design choices.

## Why this split

If Claude/agent generates the DDL, you don't learn it. You wrote SQL for years; this lab honors that. The tooling around it (Faker seed generators, migration runners) is the part that's tedious but not high-learning, so we scaffold that.
