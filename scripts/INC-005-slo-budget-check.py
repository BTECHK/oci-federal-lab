#!/usr/bin/env python3
"""
─────────────────────────────────────────────────────────────────────────
INC-005 Prevention: SLO Error Budget Check
Incident: phases/phase-3-fedcompliance-gitops-security/INCIDENTS.md → INC-005
Postmortem: phases/phase-3-fedcompliance-gitops-security/postmortems/INC-005-*.md

Purpose: Calculate remaining error budget against the configured SLO.
         Exit 1 if remaining budget < threshold (default 20%).

Usage: ./scripts/INC-005-slo-budget-check.py [--threshold N]
  --threshold N: minimum remaining budget percentage (default 20)
─────────────────────────────────────────────────────────────────────────
"""
import argparse
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


PROM_URL = os.environ.get("PROM_URL", "http://localhost:9090")
SLO_TARGET = float(os.environ.get("SLO_TARGET", "99.5"))   # %
WINDOW = os.environ.get("PROM_WINDOW", "30d")


def query_prom(promql: str) -> float:
    """Run an instant Prometheus query, return the first numeric sample.
    Returns 0.0 if the query yields no data."""
    url = f"{PROM_URL}/api/v1/query?query={urllib.parse.quote(promql)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            import json
            body = json.load(resp)
    except (urllib.error.URLError, OSError) as exc:
        print(f"INC-005: ERROR — Prometheus unreachable: {exc}", file=sys.stderr)
        sys.exit(2)

    results = body.get("data", {}).get("result", [])
    if not results:
        return 0.0
    try:
        return float(results[0]["value"][1])
    except (KeyError, IndexError, ValueError):
        return 0.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=20.0,
                        help="Minimum remaining budget %% (default 20)")
    args = parser.parse_args()

    # Compute success rate over WINDOW. Adjust queries to your SLO definition.
    success_query = (
        f'1 - (sum(rate(http_requests_total{{status=~"5.."}}[{WINDOW}]))'
        f' / sum(rate(http_requests_total[{WINDOW}])))'
    )
    success_rate = query_prom(success_query) * 100  # to %

    allowed_error = 100.0 - SLO_TARGET
    actual_error = max(0.0, 100.0 - success_rate)
    if allowed_error <= 0:
        print("INC-005: ERROR — SLO_TARGET >= 100%; budget cannot exist", file=sys.stderr)
        return 2

    consumed_pct = (actual_error / allowed_error) * 100
    remaining_pct = max(0.0, 100.0 - consumed_pct)

    print(
        f"INC-005: success_rate={success_rate:.4f}%  slo={SLO_TARGET}%  "
        f"consumed_budget={consumed_pct:.1f}%  remaining_budget={remaining_pct:.1f}%"
    )

    if remaining_pct < args.threshold:
        print(
            f"INC-005: BURN — remaining budget {remaining_pct:.1f}% < threshold {args.threshold}%",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
