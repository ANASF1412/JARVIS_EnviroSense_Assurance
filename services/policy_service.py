"""
MODULE 2: POLICY MANAGEMENT
Create and manage weekly insurance policies
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from services.repositories.policy_repository import PolicyRepository
from services.repositories.worker_repository import WorkerRepository


class PolicyService:
    """Handle insurance policy management."""

    def __init__(self):
        """Initialize policy service."""
        self.policy_repo = PolicyRepository()
        self.worker_repo = WorkerRepository()

    def create_policy_for_worker(self, worker_id: str, weekly_premium: float,
                                 duration_days: int = 7) -> Dict[str, Any]:
        """
        Create a new policy for a worker.

        Process:
        1. Fetch worker profile
        2. Calculate coverage_limit = income × max_hours_per_week
        3. Create policy (7 days)
        4. Link policy to worker

        Args:
            worker_id: Worker ID
            weekly_premium: Weekly premium amount
            duration_days: Policy duration in days

        Returns:
            Policy creation response
        """
        try:
            # Validate worker exists
            worker = self.worker_repo.get_worker(worker_id)
            if not worker:
                return {
                    "success": False,
                    "error": f"Worker {worker_id} not found",
                    "policy_id": None,
                }

            # Calculate coverage limit
            coverage_limit = worker["avg_hourly_income"] * 40

            # Create policy
            policy = self.policy_repo.create_policy(
                worker_id=worker_id,
                weekly_premium=weekly_premium,
                coverage_limit=coverage_limit,
                duration_days=duration_days
            )

            return {
                "success": True,
                "policy_id": policy["policy_id"],
                "message": f"✅ Policy created successfully",
                "policy": {
                    "policy_id": policy["policy_id"],
                    "worker_id": worker_id,
                    "weekly_premium": weekly_premium,
                    "coverage_limit": coverage_limit,
                    "start_date": policy["start_date"].isoformat(),
                    "end_date": policy["end_date"].isoformat(),
                    "active": True,
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Policy creation failed: {str(e)}",
                "policy_id": None,
            }

    def get_active_policy(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get currently active policy for a worker.

        Args:
            worker_id: Worker ID

        Returns:
            Active policy or None
        """
        return self.policy_repo.get_active_policy(worker_id)

    def get_worker_policies(self, worker_id: str) -> List[Dict[str, Any]]:
        """
        Get all policies for a worker.

        Args:
            worker_id: Worker ID

        Returns:
            List of policies
        """
        return self.policy_repo.get_worker_policies(worker_id)

    def renew_policy(self, policy_id: str, duration_days: int = 7) -> Dict[str, Any]:
        """
        Renew an existing policy.

        Args:
            policy_id: Policy ID
            duration_days: Days to extend

        Returns:
            Renewal response
        """
        try:
            success = self.policy_repo.renew_policy(policy_id, duration_days)

            if success:
                policy = self.policy_repo.get_policy(policy_id)
                return {
                    "success": True,
                    "message": f"✅ Policy renewed until {policy['end_date']}",
                    "policy_id": policy_id,
                    "new_end_date": policy["end_date"].isoformat(),
                }
            else:
                return {
                    "success": False,
                    "error": "Policy not found",
                    "policy_id": None,
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Renewal failed: {str(e)}",
                "policy_id": policy_id,
            }

    def deactivate_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Deactivate a policy.

        Args:
            policy_id: Policy ID

        Returns:
            Deactivation response
        """
        try:
            success = self.policy_repo.deactivate_policy(policy_id)

            if success:
                return {
                    "success": True,
                    "message": f"✅ Policy {policy_id} deactivated",
                    "policy_id": policy_id,
                }
            else:
                return {
                    "success": False,
                    "error": "Policy not found",
                    "policy_id": policy_id,
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Deactivation failed: {str(e)}",
                "policy_id": policy_id,
            }

    def is_policy_active(self, policy_id: str) -> bool:
        """
        Check if policy is active and valid.

        Args:
            policy_id: Policy ID

        Returns:
            True if policy is valid and active
        """
        return self.policy_repo.policy_is_valid(policy_id)

    def get_policy_stats(self) -> Dict[str, Any]:
        """
        Get policy statistics.

        Returns:
            Statistics dictionary
        """
        total_active = self.policy_repo.get_active_policies_count()
        expiring_soon = len(self.policy_repo.get_policies_expiring_soon(hours=24))

        return {
            "total_active_policies": total_active,
            "policies_expiring_today": expiring_soon,
        }
