"""
MemeGPT — Backup & Disaster Recovery CLI Manager
Specification: 06_Database/Backup_Recovery.md
"""

import argparse
import json
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.backup_service import (
    create_database_backup,
    restore_database_backup,
    create_qdrant_snapshot,
    verify_disaster_recovery_health,
)
from app.services.recovery_service import (
    get_recovery_scenarios_catalog,
    get_recovery_checklist,
    execute_recovery_dry_run,
)


def main():
    parser = argparse.ArgumentParser(description="MemeGPT Backup & Recovery Manager")
    parser.add_argument("--backup", action="store_true", help="Create a database backup")
    parser.add_argument("--restore", type=str, help="Restore database from specified backup file")
    parser.add_argument("--snapshot-qdrant", action="store_true", help="Create a Qdrant collection snapshot")
    parser.add_argument("--verify-dr", action="store_true", help="Verify Disaster Recovery readiness and RTO/RPO SLAs")
    parser.add_argument("--recover-scenario", type=int, choices=[1, 2, 3, 4], help="Execute recovery procedure dry-run for scenario 1-4")
    parser.add_argument("--checklist", action="store_true", help="Show recovery verification checklist")
    args = parser.parse_args()

    if args.backup:
        print("Creating database backup...")
        res = create_database_backup()
        print(json.dumps(res, indent=2))

    elif args.restore:
        print(f"Restoring database from {args.restore}...")
        res = restore_database_backup(args.restore)
        print(json.dumps(res, indent=2))

    elif args.snapshot_qdrant:
        print("Creating Qdrant snapshot...")
        res = create_qdrant_snapshot()
        print(json.dumps(res, indent=2))

    elif args.verify_dr:
        print("Verifying Disaster Recovery health...")
        res = verify_disaster_recovery_health()
        print(json.dumps(res, indent=2))

    elif args.recover_scenario:
        print(f"\n=== Executing Disaster Recovery Dry-Run: Scenario {args.recover_scenario} ===")
        res = execute_recovery_dry_run(args.recover_scenario)
        print(json.dumps(res, indent=2))

    elif args.checklist:
        checklist = get_recovery_checklist()
        print("\n=== Disaster Recovery Validation Checklist ===")
        for i, item in enumerate(checklist, 1):
            print(f" [ ] {i}. {item}")

    else:
        # Default behavior: run backup and verify
        res = create_database_backup()
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
