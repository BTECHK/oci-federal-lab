"""list-personnel command."""
import click
from tabulate import tabulate


# ── Section 1: Click command definition ─────────────────────────────
# WHAT: Define @click.command() with --clearance option for filtering
# LEARNING: Click decorators — @click.option, type=str, help string, default=None
# LOOK UP: click.command, click.option, click decorators
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Fetch and display personnel ───────────────────────────
# WHAT: Call client.get_personnel(), format as table with tabulate, print
# LEARNING: tabulate library, choosing table format (simple, grid, pipe)
# LOOK UP: tabulate(data, headers=..., tablefmt=...)
#
# Write your implementation below. Check answers/ only after attempting.

@click.command("list-personnel")
@click.option("--clearance", default=None, help="Filter by clearance level")
def list_personnel(clearance):
    pass
