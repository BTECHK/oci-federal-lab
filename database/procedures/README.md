# Stored Procedures — USER WRITES

Write your PL/SQL procedures + functions here. Suggested file pattern:

- `sp_<action>_<resource>.sql` for procedures
- `fn_<purpose>.sql` for functions
- `pkg_<module>.sql` for packages

**Why procedures here vs in application code:**
- Heavy data transformation closer to the data (avoid round-trips)
- Atomicity guarantees that span multiple tables
- Auditable, version-controlled in git rather than rolled into Liquibase chains

**Examples to consider writing:**
- `sp_archive_audit_log` — moves audit_log rows older than N days to archive_audit_log
- `fn_calculate_personnel_clearance_age` — returns days since clearance issued
- `pkg_compliance_ops` — package wrapping common compliance-related ops
