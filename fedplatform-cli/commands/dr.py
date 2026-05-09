"""
dr commands — Phase 2 disaster-recovery status checks.
"""
import click


# ── Section 1: dr-status command ──────────────────────────────────────
# WHAT: Show k3s node readiness + ADB backup age in a single tabular view
# LEARNING: Click commands, calling FedAgent /metrics, parsing Prometheus text format
# LOOK UP: tabulate.tabulate, requests.get to FEDAGENT_URL/metrics
#
# Write your implementation below. Check answers/ only after attempting.

@click.command(name="dr-status")
def dr_status():
    """Stub — implement in answers/commands/dr.py."""
    click.echo("dr-status: not yet implemented (see answers/)")
