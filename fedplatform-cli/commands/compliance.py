"""compliance-check command."""
import click


# ── Section 1: --framework option ───────────────────────────────────
# WHAT: Accept --framework with choices fedramp|nist; default fedramp
# LEARNING: Click option with type=click.Choice for validated enum-like args
# LOOK UP: click.Choice, click.option type parameter
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Fetch and display compliance score ────────────────────
# WHAT: Call client.get_compliance_score(framework), display score with pass/fail
# LEARNING: Threshold-based CLI output, click.style for color output
# LOOK UP: click.style, click.echo, ANSI colors in Click
#
# Write your implementation below. Check answers/ only after attempting.

@click.command("compliance-check")
@click.option("--framework", type=click.Choice(["fedramp", "nist"]), default="fedramp")
def compliance_check(framework):
    pass


# ── Section 3 (P3): scan-trigger command ─────────────────────────────
# WHAT: POST /compliance/scan with --framework option
# LEARNING: HTTP POST from CLI, exit codes that reflect remote outcomes
# LOOK UP: requests.post, click.option, sys.exit(1) on remote error
#
# Write your implementation below. Check answers/ only after attempting.

@click.command(name="scan-trigger")
@click.option("--framework", default="cmmc-l2")
def scan_trigger(framework: str):
    """Stub — implement in answers/commands/compliance.py."""
    click.echo(f"scan-trigger (framework={framework}): not implemented (see answers/)")


# ── Section 4 (P3): policy-report command ────────────────────────────
# WHAT: GET /compliance/report and render as JSON or Markdown
# LEARNING: choosing output formats from CLI flags, sys.stdout for piping
# LOOK UP: click.option with type=click.Choice, json.dumps indent
#
# Write your implementation below. Check answers/ only after attempting.

@click.command(name="policy-report")
@click.option("--output", type=click.Choice(["json", "md"]), default="md")
def policy_report(output: str):
    """Stub — implement in answers/commands/compliance.py."""
    click.echo(f"policy-report (output={output}): not implemented (see answers/)")
