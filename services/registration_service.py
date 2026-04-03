"""
MODULE 1: REGISTRATION SERVICE
Worker onboarding and registration
"""
from datetime import datetime
from typing import Dict, Any, Optional
from services.repositories.worker_repository import WorkerRepository
from services.repositories.policy_repository import PolicyRepository
from config.settings import COVERAGE_MULTIPLIER, PREMIUM_MID_RISK


class RegistrationService:
    """Handle worker registration and onboarding."""

    def __init__(self):
        """Initialize registration service."""
        self.worker_repo = WorkerRepository()
        self.policy_repo = PolicyRepository()

    def register_worker(self, name: str, city: str, delivery_zone: str,
                       avg_hourly_income: float) -> Dict[str, Any]:
        """
        Register a new worker.

        Process:
        1. Create worker profile in database
        2. Auto-create initial insurance policy
        3. Return confirmation with worker_id and policy_id

        Args:
            name: Worker name
            city: City
            delivery_zone: Delivery zone
            avg_hourly_income: Average hourly income

        Returns:
            Response dictionary with success status, worker profile, and policy
        """
        try:
            # Validate inputs
            if not name or not city or not delivery_zone:
                return {
                    "success": False,
                    "error": "Missing required fields",
                    "worker_id": None,
                    "policy_id": None,
                }

            if avg_hourly_income <= 0:
                return {
                    "success": False,
                    "error": "Hourly income must be greater than 0",
                    "worker_id": None,
                    "policy_id": None,
                }

            # Step 1: Create worker profile
            worker = self.worker_repo.create_worker(
                name=name,
                city=city,
                delivery_zone=delivery_zone,
                avg_hourly_income=avg_hourly_income
            )

            worker_id = worker["worker_id"]

            # Step 2: Auto-create insurance policy
            coverage_limit = avg_hourly_income * COVERAGE_MULTIPLIER
            weekly_premium = PREMIUM_MID_RISK  # Default premium

            policy = self.policy_repo.create_policy(
                worker_id=worker_id,
                weekly_premium=weekly_premium,
                coverage_limit=coverage_limit,
                duration_days=7
            )

            policy_id = policy["policy_id"]

            return {
                "success": True,
                "worker_id": worker_id,
                "policy_id": policy_id,
                "message": f"✅ Registration successful! Welcome {name}. Policy {policy_id} is now active.",
                "worker": {
                    "worker_id": worker_id,
                    "name": name,
                    "city": city,
                    "zone": delivery_zone,
                    "hourly_income": avg_hourly_income,
                },
                "policy": {
                    "policy_id": policy_id,
                    "weekly_premium": weekly_premium,
                    "coverage_limit": coverage_limit,
                    "active": True,
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Registration failed: {str(e)}",
                "worker_id": None,
                "policy_id": None,
            }

    def get_worker_profile(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get worker profile.

        Args:
            worker_id: Worker ID

        Returns:
            Worker profile or None
        """
        return self.worker_repo.get_worker(worker_id)

    def get_all_workers(self) -> list:
        """
        Get all registered workers.

        Returns:
            List of worker profiles
        """
        return self.worker_repo.get_all_workers()

    def worker_exists(self, worker_id: str) -> bool:
        """
        Check if worker exists.

        Args:
            worker_id: Worker ID

        Returns:
            True if worker exists
        """
        return self.worker_repo.worker_exists(worker_id)
