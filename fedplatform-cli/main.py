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

@click.group()
def cli():
    """FedPlatform operator CLI."""
    pass


if __name__ == "__main__":
    cli()
