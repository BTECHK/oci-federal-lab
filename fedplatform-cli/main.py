"""
fedplatform-cli — FedPlatform operator CLI.
Wraps FedTracker API and FedAgent metrics for command-line access.
"""
import click


# ── Section 1: Click group setup ────────────────────────────────────
# WHAT: Create a Click group that acts as the top-level CLI entry point
# LEARNING: @click.group() — how CLI tools nest commands under a group
# LOOK UP: click.group, click.version_option
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Register commands ────────────────────────────────────
# WHAT: Add list-personnel, export-audit, compliance-check to the group
# LEARNING: cli.add_command() vs @cli.command decorator pattern
# LOOK UP: click.Group.add_command, importing from commands/
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3 (P2): Register dr-status and failover-check ───────────
# WHAT: Wire commands/dr.py and commands/failover.py into the cli group
# LEARNING: P2 adds DR-aware operator commands without rewriting P1 setup
# LOOK UP: import paths inside commands/ module
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 4 (P3): Register scan-trigger, policy-report, pipeline-status ─
# WHAT: Wire P3 supply-chain operator commands (compliance.py + pipeline.py)
# LEARNING: keep section comments grouped by phase so the CLI evolution is grep-able
# LOOK UP: cli.add_command, importing the new commands from commands/
#
# Write your implementation below. Check answers/ only after attempting.

@click.group()
def cli():
    """FedPlatform operator CLI."""
    pass


if __name__ == "__main__":
    cli()
