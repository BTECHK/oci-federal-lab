#!/usr/bin/env python3
"""
OCI Federal Lab — Full Cost Projection Calculator
===================================================
Estimates total project cost across all 3 phases assuming:
  - PAYG (Pay-As-You-Go) pricing, NO commitments
  - NO Always Free tier
  - NO $300 trial credits
  - All resources billed at Oracle list rates (2025-2026)

Usage:
    python cost_estimator.py
    python cost_estimator.py --months-per-phase 2
    python cost_estimator.py --include-optional
"""

import argparse
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# OCI PAYG Unit Prices (USD, 2025-2026 list rates)
# Sources:
#   - https://www.oracle.com/cloud/price-list/
#   - https://www.oracle.com/cloud/compute/pricing/
#   - https://www.oracle.com/autonomous-database/pricing/
#   - https://www.oracle.com/cloud/storage/block-volumes/pricing/
#   - https://www.oracle.com/cloud/storage/object-storage/pricing/
# ============================================================

PRICES = {
    # Compute - VM.Standard.A1.Flex (ARM)
    "a1_flex_ocpu_per_hr":       0.0200,   # per OCPU per hour
    "a1_flex_mem_per_gb_hr":     0.0030,   # per GB RAM per hour

    # Compute - VM.Standard.E2.1.Micro (AMD) - if needed
    "e2_micro_per_hr":           0.0125,   # ~$0.0125/hr estimated (1/8 OCPU)

    # Autonomous Database (ATP) - legacy OCPU billing
    "atp_ocpu_per_hr":           0.3360,   # per OCPU per hour
    "atp_storage_per_tb_mo":   255.00,     # per TB per month

    # Block Volume (balanced performance, 10 VPU)
    "block_vol_per_gb_mo":       0.0255,   # base storage per GB/month
    "block_vol_perf_per_gb_mo":  0.0170,   # balanced performance per GB/month
    # total balanced = 0.0425/GB/month

    # Object Storage
    "obj_storage_per_gb_mo":     0.0255,   # standard tier per GB/month
    "obj_put_per_10k":           0.0040,   # PUT/POST/LIST per 10K requests
    "obj_get_per_10k":           0.0003,   # GET/HEAD per 10K requests

    # Networking (OCI advantage: most networking is FREE)
    "nat_gateway_per_hr":        0.00,     # FREE on OCI
    "internet_gw_per_hr":        0.00,     # FREE on OCI
    "service_gw_per_hr":         0.00,     # FREE on OCI
    "vcn_per_hr":                0.00,     # FREE on OCI

    # Load Balancer (flexible)
    "lb_base_per_hr":            0.0143,   # base fee per hour
    "lb_bandwidth_per_mbps_hr":  0.0081,   # per Mbps per hour

    # OCI Functions
    "fn_per_invocation":         0.0000002,  # $0.20 per million
    "fn_per_gb_second":          0.00001417, # per GB-second of execution

    # API Gateway
    "apigw_per_million_calls":   3.00,     # per million API calls

    # Container Registry (OCIR) - uses object storage pricing
    "ocir_per_gb_mo":            0.0255,   # per GB/month

    # Vault / KMS
    "vault_software_key_mo":     0.00,     # software-protected keys are FREE
    "vault_hsm_key_mo":          0.53,     # HSM keys beyond 20 versions

    # Logging
    "logging_per_gb_mo":         0.05,     # per GB/month (first 10GB free normally)

    # Monitoring
    "monitoring_ingestion":      0.00,     # effectively free for lab scale

    # Data Transfer
    "data_transfer_out_per_gb":  0.00,     # first 10 TB/month is FREE on OCI
    "data_transfer_in_per_gb":   0.00,     # always FREE
}

HOURS_PER_MONTH = 730  # standard billing month


# ============================================================
# Resource Definitions
# ============================================================

@dataclass
class VMInstance:
    name: str
    ocpus: int
    memory_gb: int
    boot_volume_gb: int = 50
    active_weeks: float = 4.0  # how many weeks of the month it runs
    notes: str = ""

    @property
    def active_hours(self) -> float:
        return (self.active_weeks / 4.0) * HOURS_PER_MONTH

    @property
    def compute_cost_mo(self) -> float:
        ocpu_cost = self.ocpus * PRICES["a1_flex_ocpu_per_hr"] * self.active_hours
        mem_cost = self.memory_gb * PRICES["a1_flex_mem_per_gb_hr"] * self.active_hours
        return ocpu_cost + mem_cost

    @property
    def boot_vol_cost_mo(self) -> float:
        rate = PRICES["block_vol_per_gb_mo"] + PRICES["block_vol_perf_per_gb_mo"]
        return self.boot_volume_gb * rate


@dataclass
class AutonomousDB:
    name: str
    ocpus: int = 1
    storage_gb: int = 20
    active_weeks: float = 4.0
    notes: str = ""

    @property
    def active_hours(self) -> float:
        return (self.active_weeks / 4.0) * HOURS_PER_MONTH

    @property
    def compute_cost_mo(self) -> float:
        return self.ocpus * PRICES["atp_ocpu_per_hr"] * self.active_hours

    @property
    def storage_cost_mo(self) -> float:
        tb = self.storage_gb / 1024.0
        return tb * PRICES["atp_storage_per_tb_mo"]

    @property
    def total_cost_mo(self) -> float:
        return self.compute_cost_mo + self.storage_cost_mo


@dataclass
class ObjectStorage:
    name: str
    size_gb: float
    monthly_puts: int = 10000    # PUT/POST/LIST requests
    monthly_gets: int = 50000    # GET/HEAD requests
    notes: str = ""

    @property
    def total_cost_mo(self) -> float:
        storage = self.size_gb * PRICES["obj_storage_per_gb_mo"]
        puts = (self.monthly_puts / 10000) * PRICES["obj_put_per_10k"]
        gets = (self.monthly_gets / 10000) * PRICES["obj_get_per_10k"]
        return storage + puts + gets


@dataclass
class Functions:
    name: str
    monthly_invocations: int
    avg_memory_mb: int = 256
    avg_duration_ms: int = 500
    notes: str = ""

    @property
    def total_cost_mo(self) -> float:
        invocation_cost = self.monthly_invocations * PRICES["fn_per_invocation"]
        gb_seconds = (self.monthly_invocations
                      * (self.avg_memory_mb / 1024.0)
                      * (self.avg_duration_ms / 1000.0))
        execution_cost = gb_seconds * PRICES["fn_per_gb_second"]
        return invocation_cost + execution_cost


@dataclass
class LoadBalancer:
    name: str
    bandwidth_mbps: int = 10
    active_weeks: float = 4.0
    notes: str = ""

    @property
    def active_hours(self) -> float:
        return (self.active_weeks / 4.0) * HOURS_PER_MONTH

    @property
    def total_cost_mo(self) -> float:
        base = PRICES["lb_base_per_hr"] * self.active_hours
        bw = self.bandwidth_mbps * PRICES["lb_bandwidth_per_mbps_hr"] * self.active_hours
        return base + bw


@dataclass
class Phase:
    name: str
    description: str
    months: float
    vms: list = field(default_factory=list)
    databases: list = field(default_factory=list)
    object_storage: list = field(default_factory=list)
    functions: list = field(default_factory=list)
    load_balancers: list = field(default_factory=list)
    extra_block_volume_gb: int = 0
    ocir_storage_gb: float = 0
    vault_software_keys: int = 0
    apigw_monthly_calls: int = 0
    logging_gb: float = 0

    def compute_cost(self) -> dict:
        """Calculate all costs for this phase, returns itemized dict."""
        costs = {}

        # --- Compute ---
        vm_total = 0
        vm_details = []
        for vm in self.vms:
            c = vm.compute_cost_mo
            vm_total += c
            vm_details.append((vm.name, vm.ocpus, vm.memory_gb, c))
        costs["compute"] = {"total": vm_total, "details": vm_details}

        # --- Database ---
        db_total = 0
        db_details = []
        for db in self.databases:
            c = db.total_cost_mo
            db_total += c
            db_details.append((db.name, db.ocpus, db.storage_gb, c))
        costs["database"] = {"total": db_total, "details": db_details}

        # --- Block Storage (boot volumes + extra) ---
        boot_total = sum(vm.boot_vol_cost_mo for vm in self.vms)
        extra_block = self.extra_block_volume_gb * (
            PRICES["block_vol_per_gb_mo"] + PRICES["block_vol_perf_per_gb_mo"]
        )
        costs["block_storage"] = {
            "total": boot_total + extra_block,
            "boot_volumes": boot_total,
            "extra_block": extra_block,
        }

        # --- Object Storage ---
        obj_total = sum(o.total_cost_mo for o in self.object_storage)
        costs["object_storage"] = {"total": obj_total}

        # --- Functions ---
        fn_total = sum(f.total_cost_mo for f in self.functions)
        costs["functions"] = {"total": fn_total}

        # --- Load Balancer ---
        lb_total = sum(lb.total_cost_mo for lb in self.load_balancers)
        costs["load_balancer"] = {"total": lb_total}

        # --- OCIR ---
        ocir_cost = self.ocir_storage_gb * PRICES["ocir_per_gb_mo"]
        costs["ocir"] = {"total": ocir_cost}

        # --- Vault ---
        vault_cost = self.vault_software_keys * PRICES["vault_software_key_mo"]
        costs["vault"] = {"total": vault_cost}

        # --- API Gateway ---
        apigw_cost = (self.apigw_monthly_calls / 1_000_000) * PRICES["apigw_per_million_calls"]
        costs["api_gateway"] = {"total": apigw_cost}

        # --- Logging ---
        log_cost = self.logging_gb * PRICES["logging_per_gb_mo"]
        costs["logging"] = {"total": log_cost}

        # --- Networking (FREE on OCI) ---
        costs["networking"] = {"total": 0.00, "note": "VCN, NAT GW, IGW, SVC GW all free"}

        # --- Data Transfer (first 10TB free) ---
        costs["data_transfer"] = {"total": 0.00, "note": "< 10TB/month = free"}

        # --- Monthly & Phase Totals ---
        monthly = sum(v["total"] for v in costs.values() if isinstance(v, dict) and "total" in v)
        costs["monthly_total"] = monthly
        costs["phase_total"] = monthly * self.months

        return costs


# ============================================================
# Phase Definitions (from implementation guides)
# ============================================================

def define_phases(months_per_phase: float = 1.0, include_optional: bool = False) -> list:
    """Define all 3 phases with their resources."""

    # ---- PHASE 1: Legacy-to-Cloud Migration ----
    phase1 = Phase(
        name="Phase 1",
        description="Legacy-to-Cloud Migration",
        months=months_per_phase,
        vms=[
            VMInstance("legacy-server", ocpus=2, memory_gb=8,
                       active_weeks=1.0,
                       notes="Day 1 only, then destroyed"),
            VMInstance("bastion", ocpus=1, memory_gb=6,
                       active_weeks=3.0,
                       notes="SSH jump box + Jenkins, runs Day 2 onward"),
            VMInstance("app-server", ocpus=1, memory_gb=6,
                       active_weeks=3.0,
                       notes="FedTracker FastAPI, runs Day 2 onward"),
        ],
        databases=[
            AutonomousDB("fedtracker-db", ocpus=1, storage_gb=20,
                         active_weeks=3.0,
                         notes="ATP, replaces SQLite on Day 2"),
        ],
        object_storage=[
            ObjectStorage("fedtracker-backups", size_gb=5,
                          monthly_puts=5000, monthly_gets=20000,
                          notes="DB exports, config snapshots"),
        ],
        functions=[
            Functions("audit-processor", monthly_invocations=5000,
                      avg_memory_mb=256, avg_duration_ms=500,
                      notes="Object storage event trigger"),
            Functions("health-check-automation", monthly_invocations=8640,
                      avg_memory_mb=128, avg_duration_ms=200,
                      notes="Scheduled every 5 min = 8640/month"),
        ],
        logging_gb=2.0,
    )

    # ---- PHASE 2: Disaster Recovery & k3s Cluster ----
    phase2 = Phase(
        name="Phase 2",
        description="Disaster Recovery Drill & Backup Architecture",
        months=months_per_phase,
        vms=[
            VMInstance("bastion", ocpus=1, memory_gb=6,
                       notes="SSH jump box, persistent"),
            VMInstance("k3s-node-1 (server)", ocpus=2, memory_gb=12,
                       active_weeks=3.0,
                       notes="k3s control plane, starts Day 3"),
            VMInstance("k3s-node-2 (agent)", ocpus=2, memory_gb=12,
                       active_weeks=3.0,
                       notes="k3s worker node, starts Day 3"),
            # app-server runs Days 1-2 before k3s replaces it
            VMInstance("app-server (temp)", ocpus=1, memory_gb=6,
                       active_weeks=1.0,
                       notes="FedAnalytics, replaced by k3s Day 3"),
        ],
        databases=[
            AutonomousDB("fedanalytics-db", ocpus=1, storage_gb=20,
                         notes="FedAnalytics schema"),
        ],
        object_storage=[
            ObjectStorage("fedanalytics-backups", size_gb=15,
                          monthly_puts=10000, monthly_gets=30000,
                          notes="Immutable backups, WORM retention"),
        ],
        extra_block_volume_gb=50,  # additional block volume for backup testing
        logging_gb=3.0,
    )

    # ---- PHASE 3: CI/CD & AI-Augmented Operations ----
    phase3 = Phase(
        name="Phase 3",
        description="CI/CD Pipeline Modernization & AI-Augmented Operations",
        months=months_per_phase,
        vms=[
            VMInstance("bastion/jenkins", ocpus=1, memory_gb=6,
                       notes="Jenkins CI/CD server"),
            VMInstance("k3s-node-1 (server)", ocpus=1, memory_gb=6,
                       notes="k3s control plane"),
            VMInstance("k3s-node-2 (agent)", ocpus=1, memory_gb=6,
                       notes="k3s worker node"),
        ],
        databases=[
            AutonomousDB("fedcompliance-db", ocpus=1, storage_gb=20,
                         notes="FedCompliance schema"),
        ],
        object_storage=[
            ObjectStorage("fedcompliance-backups", size_gb=20,
                          monthly_puts=15000, monthly_gets=50000,
                          notes="SBOMs, compliance evidence, DB exports"),
        ],
        functions=[
            Functions("log-processor", monthly_invocations=10000,
                      avg_memory_mb=256, avg_duration_ms=500),
            Functions("compliance-collector", monthly_invocations=720,
                      avg_memory_mb=512, avg_duration_ms=2000,
                      notes="Daily scheduled scan"),
        ],
        ocir_storage_gb=5.0,
        vault_software_keys=5,
        apigw_monthly_calls=100_000 if include_optional else 0,
        logging_gb=5.0,
    )

    # Optional: Load balancer if user decides to add one
    if include_optional:
        phase3.load_balancers.append(
            LoadBalancer("fedcompliance-lb", bandwidth_mbps=10,
                         notes="Optional flexible LB for API")
        )

    return [phase1, phase2, phase3]


# ============================================================
# Report Generation
# ============================================================

def print_separator(char="=", width=72):
    print(char * width)


def print_phase_report(phase: Phase) -> dict:
    """Print detailed cost breakdown for a phase."""
    costs = phase.compute_cost()

    print_separator()
    print(f"  {phase.name}: {phase.description}")
    print(f"  Duration: {phase.months} month(s)")
    print_separator()

    # Compute details
    print(f"\n  {'COMPUTE':40s} {'OCPUs':>6s} {'RAM GB':>7s} {'$/Month':>10s}")
    print(f"  {'-'*63}")
    for name, ocpus, mem, cost in costs["compute"]["details"]:
        print(f"  {name:40s} {ocpus:>6d} {mem:>7d} ${cost:>9.2f}")
    print(f"  {'Compute Subtotal':40s} {'':>6s} {'':>7s} ${costs['compute']['total']:>9.2f}")

    # Database details
    print(f"\n  {'DATABASE':40s} {'OCPUs':>6s} {'GB':>7s} {'$/Month':>10s}")
    print(f"  {'-'*63}")
    for name, ocpus, storage, cost in costs["database"]["details"]:
        print(f"  {name:40s} {ocpus:>6d} {storage:>7d} ${cost:>9.2f}")
    print(f"  {'Database Subtotal':40s} {'':>6s} {'':>7s} ${costs['database']['total']:>9.2f}")

    # Storage
    print(f"\n  {'STORAGE':40s} {'':>6s} {'':>7s} {'$/Month':>10s}")
    print(f"  {'-'*63}")
    print(f"  {'Boot Volumes (block storage)':40s} {'':>6s} {'':>7s} ${costs['block_storage']['boot_volumes']:>9.2f}")
    if costs["block_storage"]["extra_block"] > 0:
        print(f"  {'Extra Block Volumes':40s} {'':>6s} {'':>7s} ${costs['block_storage']['extra_block']:>9.2f}")
    print(f"  {'Object Storage':40s} {'':>6s} {'':>7s} ${costs['object_storage']['total']:>9.2f}")
    if costs["ocir"]["total"] > 0:
        print(f"  {'Container Registry (OCIR)':40s} {'':>6s} {'':>7s} ${costs['ocir']['total']:>9.2f}")
    storage_total = (costs["block_storage"]["total"]
                     + costs["object_storage"]["total"]
                     + costs["ocir"]["total"])
    print(f"  {'Storage Subtotal':40s} {'':>6s} {'':>7s} ${storage_total:>9.2f}")

    # Services
    print(f"\n  {'SERVICES':40s} {'':>6s} {'':>7s} {'$/Month':>10s}")
    print(f"  {'-'*63}")
    services_total = 0
    for svc_name, svc_key in [("Functions", "functions"),
                               ("Load Balancer", "load_balancer"),
                               ("API Gateway", "api_gateway"),
                               ("Vault/KMS", "vault"),
                               ("Logging", "logging"),
                               ("Networking", "networking"),
                               ("Data Transfer", "data_transfer")]:
        val = costs[svc_key]["total"]
        services_total += val
        if val > 0:
            print(f"  {svc_name:40s} {'':>6s} {'':>7s} ${val:>9.2f}")
        else:
            print(f"  {svc_name:40s} {'':>6s} {'':>7s}     $0.00")
    print(f"  {'Services Subtotal':40s} {'':>6s} {'':>7s} ${services_total:>9.2f}")

    # Totals
    print(f"\n  {'─'*63}")
    print(f"  {'MONTHLY TOTAL':40s} {'':>6s} {'':>7s} ${costs['monthly_total']:>9.2f}")
    if phase.months != 1.0:
        print(f"  {'PHASE TOTAL (' + str(phase.months) + ' months)':40s} {'':>6s} {'':>7s} ${costs['phase_total']:>9.2f}")
    print()

    return costs


def print_grand_summary(all_costs: list, phases: list):
    """Print the grand total summary across all phases."""
    print_separator("=")
    print("  GRAND TOTAL — ALL PHASES")
    print_separator("=")

    grand_total = 0
    category_totals = {
        "Compute": 0, "Database": 0, "Storage": 0,
        "Services": 0, "Networking": 0,
    }

    print(f"\n  {'Phase':45s} {'Monthly':>10s} {'Duration':>10s} {'Phase Total':>12s}")
    print(f"  {'-'*77}")

    for phase, costs in zip(phases, all_costs):
        monthly = costs["monthly_total"]
        total = costs["phase_total"]
        grand_total += total
        print(f"  {phase.name + ': ' + phase.description:45s} ${monthly:>9.2f} {str(phase.months) + ' mo':>10s} ${total:>11.2f}")

        category_totals["Compute"] += costs["compute"]["total"] * phase.months
        category_totals["Database"] += costs["database"]["total"] * phase.months
        storage = (costs["block_storage"]["total"]
                   + costs["object_storage"]["total"]
                   + costs["ocir"]["total"]) * phase.months
        category_totals["Storage"] += storage
        services = (costs["functions"]["total"]
                    + costs["load_balancer"]["total"]
                    + costs["api_gateway"]["total"]
                    + costs["vault"]["total"]
                    + costs["logging"]["total"]) * phase.months
        category_totals["Services"] += services

    print(f"  {'-'*77}")
    print(f"  {'PROJECT GRAND TOTAL':45s} {'':>10s} {'':>10s} ${grand_total:>11.2f}")

    # Category breakdown
    print(f"\n  {'COST BY CATEGORY':45s} {'Total':>12s} {'% of Total':>12s}")
    print(f"  {'-'*69}")
    for cat, val in sorted(category_totals.items(), key=lambda x: -x[1]):
        pct = (val / grand_total * 100) if grand_total > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"  {cat:45s} ${val:>11.2f} {pct:>10.1f}%  {bar}")

    # Scenario comparison
    print(f"\n  {'─'*69}")
    print(f"  SCENARIO COMPARISON")
    print(f"  {'─'*69}")
    print(f"  {'No free tier, no credits (pure PAYG)':50s} ${grand_total:>11.2f}")
    credit_scenario = max(0, grand_total - 300)
    print(f"  {'$300 trial credit, no Always Free':50s} ${credit_scenario:>11.2f}")
    print(f"  {'Always Free tier (project as designed)':50s} ${'0.00':>10s}")
    print(f"  {'Always Free + $300 credit (your setup)':50s} ${'0.00':>10s}")

    # Per-day cost
    total_days = sum(p.months for p in phases) * 30
    daily = grand_total / total_days if total_days > 0 else 0
    print(f"\n  Average daily burn rate (no free tier):  ${daily:.2f}/day")
    print(f"  Days $300 credit would last:             {300/daily:.0f} days") if daily > 0 else None

    # Break-even analysis
    print(f"\n  {'─'*69}")
    print(f"  BREAK-EVEN ANALYSIS")
    print(f"  {'─'*69}")
    print(f"  The Autonomous Database alone costs:     ${category_totals['Database']:.2f}")
    print(f"  That's {category_totals['Database']/grand_total*100:.1f}% of your total bill.")
    print(f"  If you could use Always Free DB only:")
    no_db_total = grand_total - category_totals["Database"]
    print(f"    Remaining cost (compute+storage+svc):  ${no_db_total:.2f}")
    print(f"    $300 credit covers that?               {'YES ✓' if no_db_total <= 300 else 'NO ✗'}")


def main():
    parser = argparse.ArgumentParser(description="OCI Federal Lab Cost Estimator")
    parser.add_argument("--months-per-phase", type=float, default=1.0,
                        help="Duration of each phase in months (default: 1.0)")
    parser.add_argument("--include-optional", action="store_true",
                        help="Include optional resources (LB, API Gateway, etc.)")
    args = parser.parse_args()

    print("\n")
    print_separator("*")
    print("  OCI FEDERAL LAB — FULL COST PROJECTION")
    print(f"  Scenario: Pure PAYG, NO free tier, NO trial credits")
    print(f"  Duration: {args.months_per_phase} month(s) per phase, 3 phases")
    print(f"  Optional resources: {'INCLUDED' if args.include_optional else 'EXCLUDED'}")
    print_separator("*")

    phases = define_phases(
        months_per_phase=args.months_per_phase,
        include_optional=args.include_optional,
    )

    all_costs = []
    for phase in phases:
        costs = print_phase_report(phase)
        all_costs.append(costs)

    print_grand_summary(all_costs, phases)

    print(f"\n  {'─'*69}")
    print(f"  NOTE: OCI networking (VCN, NAT GW, IGW, Service GW) = $0.00")
    print(f"  NOTE: OCI outbound data transfer (first 10 TB/month) = $0.00")
    print(f"  NOTE: These are MAJOR cost advantages vs AWS/Azure")
    print(f"  {'─'*69}")
    print()


if __name__ == "__main__":
    main()
