# EXPLAIN ANALYZE Captures — USER CAPTURES

When you add an index, partition, or change a query plan, capture EXPLAIN ANALYZE output here BEFORE and AFTER the change.

**Naming pattern:**
- `<query-name>-pre-<change>.txt` — captured before
- `<query-name>-post-<change>.txt` — captured after
- `<query-name>-annotation.md` — your annotation on the deltas

**Example:**
- `personnel-by-name-pre-index.txt` — full table scan baseline
- `personnel-by-name-post-index.txt` — index range scan after adding IDX_personnel_name
- `personnel-by-name-annotation.md` — "Reduced from 12s/450MB to 4ms/4KB; index added because the GET /personnel?name= endpoint was driving 80% of the slow query log"

**Oracle-specific:**
- Use `SET AUTOTRACE ON EXPLAIN` or `DBMS_XPLAN.DISPLAY_CURSOR` for runtime stats
- Capture the actual cardinality vs estimate — that's where optimizer mistakes hide

**Why this matters for interviews:**
Most engineers can say "I added an index." Senior engineers can show the before/after plan and explain *why* the optimizer made a different choice. This folder is your evidence of that depth.
