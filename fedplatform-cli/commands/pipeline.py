"""
pipeline commands — Phase 3 Jenkins build status surfacing.
"""
import click


# ── Section 1: pipeline-status command ────────────────────────────────
# WHAT: Scrape FedAgent /metrics for fedplatform_pipeline_last_build_status
# LEARNING: text-format Prometheus parsing, tabular output with severity colors
# LOOK UP: requests.get, click.style for color, parsing label sets
#
# Write your implementation below. Check answers/ only after attempting.

@click.command(name="pipeline-status")
def pipeline_status():
    """Stub — implement in answers/commands/pipeline.py."""
    click.echo("pipeline-status: not implemented (see answers/)")
