#!/usr/bin/env python3
"""
MemeGPT — Database Migration Management CLI
Specification: 06_Database/Migrations.md
"""

import argparse
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.migration_service import (
    get_migration_workflow_guide,
    classify_schema_change,
    generate_safe_column_migration,
    get_rollback_decision_matrix,
    get_migration_checklist,
    get_common_migration_errors,
    verify_migration_health,
)


def main():
    parser = argparse.ArgumentParser(description="MemeGPT Database Migration CLI")
    parser.add_argument("--status", action="store_true", help="Verify migration directory structure & health")
    parser.add_argument("--guide", action="store_true", help="Show migration workflow guide")
    parser.add_argument("--classify", type=str, help="Classify a schema change type (e.g. add_not_null_column)")
    parser.add_argument("--safe-column", nargs=3, metavar=("TABLE", "COLUMN", "TYPE"), help="Generate 3-step safe migration SQL")
    parser.add_argument("--rollback-matrix", action="store_true", help="Show rollback decision matrix")
    parser.add_argument("--checklist", action="store_true", help="Show pre-flight migration checklist")
    parser.add_argument("--errors", action="store_true", help="Show common migration errors and fixes")

    args = parser.parse_args()

    if args.status:
        health = verify_migration_health()
        print("\n=== Prisma Migration Health & Status ===")
        print(json.dumps(health, indent=2))
        return

    if args.guide:
        guide = get_migration_workflow_guide()
        print("\n=== Migration Workflow Guide ===")
        print(json.dumps(guide, indent=2))
        return

    if args.classify:
        classification = classify_schema_change(args.classify)
        print(f"\n=== Schema Change Classification: {args.classify} ===")
        print(json.dumps(classification, indent=2))
        return

    if args.safe_column:
        tbl, col, ctype = args.safe_column
        gen = generate_safe_column_migration(tbl, col, ctype, default_val=0.0)
        print(f"\n=== Safe Column Migration Plan: {tbl}.{col} ===")
        print(f"Full SQL:\n{gen['full_sql']}")
        print(f"\nRollback SQL:\n{gen['rollback_sql']}")
        return

    if args.rollback_matrix:
        matrix = get_rollback_decision_matrix()
        print("\n=== Rollback Decision Matrix ===")
        print(json.dumps(matrix, indent=2))
        return

    if args.checklist:
        checklist = get_migration_checklist()
        print("\n=== Pre-Flight Migration Checklist ===")
        for i, item in enumerate(checklist, 1):
            print(f" [ ] {i}. {item}")
        return

    if args.errors:
        errs = get_common_migration_errors()
        print("\n=== Common Migration Errors & Fixes ===")
        print(json.dumps(errs, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
