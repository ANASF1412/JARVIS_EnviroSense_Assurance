"""
Database Initialization Script
Initialize MongoDB with collections, indexes, and sample data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from config.database import get_database, init_collections
from config.settings import DEFAULT_ZONES
from services.repositories.zone_repository import ZoneRepository
from services.repositories.worker_repository import WorkerRepository
from services.repositories.policy_repository import PolicyRepository


def init_database():
    """Initialize the database with collections and indexes."""
    print("[*] Initializing GigShield AI Database...")

    try:
        # Create collections and indexes
        db = get_database()
        init_collections()
        print("[OK] Collections and indexes created")

        # Initialize zones
        print("[*] Initializing zones...")
        zone_repo = ZoneRepository()

        # Clear existing zones
        db.zones.delete_many({})

        for zone_data in DEFAULT_ZONES:
            zone_repo.create_zone(
                zone_name=zone_data["zone_name"],
                city=zone_data["city"],
                historical_risk_score=zone_data["historical_risk_score"]
            )

        print(f"[OK] {len(DEFAULT_ZONES)} zones initialized")

        # Create sample workers (optional)
        print("[*] Creating sample workers...")
        worker_repo = WorkerRepository()
        policy_repo = PolicyRepository()

        # Clear existing workers and policies
        db.workers.delete_many({})
        db.policies.delete_many({})

        sample_workers = [
            {"name": "Ramesh Kumar", "city": "Delhi", "zone": "North", "income": 120.0},
            {"name": "Priya Singh", "city": "Delhi", "zone": "South", "income": 130.0},
            {"name": "Raj Patel", "city": "Delhi", "zone": "East", "income": 115.0},
            {"name": "Anita Sharma", "city": "Delhi", "zone": "West", "income": 125.0},
            {"name": "Vikram Verma", "city": "Delhi", "zone": "Central", "income": 135.0},
        ]

        for worker_data in sample_workers:
            worker = worker_repo.create_worker(
                name=worker_data["name"],
                city=worker_data["city"],
                delivery_zone=worker_data["zone"],
                avg_hourly_income=worker_data["income"]
            )

            # Auto-create policy for each worker
            policy = policy_repo.create_policy(
                worker_id=worker["worker_id"],
                weekly_premium=30.0,
                coverage_limit=worker_data["income"] * 40,
                duration_days=7
            )

            print(f"  [+] {worker['name']} ({worker['worker_id']}) - Policy: {policy['policy_id']}")

        print(f"[OK] {len(sample_workers)} sample workers created with policies")

        print("\n" + "="*50)
        print("[OK] DATABASE INITIALIZATION COMPLETE")
        print("="*50)
        print("\n[INFO] Sample Workers (Use these for demo):")
        workers = worker_repo.get_all_workers()
        for w in workers:
            print(f"  - ID: {w['worker_id']}, Name: {w['name']}, Zone: {w['delivery_zone']}")

        print("\n[INFO] You can now:")
        print("  1. Run: streamlit run app.py")
        print("  2. Select a worker from the sidebar")
        print("  3. Adjust weather sliders to trigger events")
        print("  4. Watch claims auto-create and process!")

        return True

    except Exception as e:
        print(f"\n[ERROR] Initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_database()
    exit(0 if success else 1)
