# Schemas — USER WRITES

Write your PL/SQL DDL here. Files load in alphabetical order during migration:

- `01-tables.sql` — `CREATE TABLE` statements
- `02-indexes.sql` — `CREATE INDEX` statements
- `03-views.sql` — `CREATE OR REPLACE VIEW` statements
- `04-constraints.sql` — `ALTER TABLE ... ADD CONSTRAINT` (FKs, CHECKs, UNIQUEs)

See `../design-doc.md` for the rationale that drives these files.

**Conventions:**
- Schema-qualify all object names (`FEDPLATFORM.personnel`, not just `personnel`)
- Use `NOCOMPRESS` for narrow tables, consider compression for audit_log
- Keep DDL idempotent where possible (`CREATE TABLE IF NOT EXISTS` if your tooling supports it)
