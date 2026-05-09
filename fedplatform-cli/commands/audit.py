"""export-audit command."""
import click


# ── Section 1: --since option parsing ───────────────────────────────
# WHAT: Accept --since Nd (e.g., "7d") and convert to a start date for the API
# LEARNING: Click option type conversion, datetime arithmetic
# LOOK UP: click.option, datetime.timedelta, strftime
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Trigger export and display pointer ────────────────────
# WHAT: Call client.trigger_audit_export(), print the returned Object Storage JSON
# LEARNING: Displaying structured data from an API response
# LOOK UP: click.echo, json.dumps with indent
#
# Write your implementation below. Check answers/ only after attempting.

@click.command("export-audit")
@click.option("--since", default="7d", help="Export entries from the last N days (e.g., 7d)")
def export_audit(since):
    pass
