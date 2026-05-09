"""
failover commands — Phase 2 RTO measurement helper.
"""
import click


# ── Section 1: failover-check command ─────────────────────────────────
# WHAT: Measure FedTracker /health/deep recovery time after a simulated failure
# LEARNING: time.monotonic for elapsed measurement, exponential backoff polling
# LOOK UP: time.monotonic, requests + retry pattern, click.echo + colors
#
# Write your implementation below. Check answers/ only after attempting.

@click.command(name="failover-check")
@click.option("--rto", type=int, default=15, help="RTO target in minutes (default: 15)")
def failover_check(rto: int):
    """Stub — implement in answers/commands/failover.py."""
    click.echo(f"failover-check (RTO={rto}m): not yet implemented (see answers/)")
