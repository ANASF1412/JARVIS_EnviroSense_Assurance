"""
Policy Repository - CRUD operations for insurance policies
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from services.repositories.base_repository import BaseRepository
import uuid


class PolicyRepository(BaseRepository):
    """Repository for policy management."""

    def __init__(self):
        """Initialize policy repository."""
        super().__init__("policies")

    def generate_policy_id(self) -> str:
        """
        Generate unique policy ID.

        Returns:
            Unique policy_id in format P{XXXXX}
        """
        # Short UUID-based ID
        return f"P{str(uuid.uuid4())[:8]}"

    def create_policy(self, worker_id: str, weekly_premium: float,
                     coverage_limit: float, duration_days: int = 7) -> Dict[str, Any]:
        """
        Create new insurance policy.

        Args:
            worker_id: Worker ID
            weekly_premium: Weekly premium amount
            coverage_limit: Maximum coverage amount
            duration_days: Policy duration in days

        Returns:
            Created policy document
        """
        policy_id = self.generate_policy_id()
        now = datetime.now()
        end_date = now + timedelta(days=duration_days)

        policy = {
            "policy_id": policy_id,
            "worker_id": worker_id,
            "weekly_premium": weekly_premium,
            "coverage_limit": coverage_limit,
            "start_date": now,
            "end_date": end_date,
            "active_status": True,
            "created_at": now,
            "updated_at": now,
        }

        self.create(policy)
        return policy

    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """
        Get policy by ID.

        Args:
            policy_id: Policy ID

        Returns:
            Policy document or None
        """
        return self.find_one({"policy_id": policy_id})

    def get_worker_policies(self, worker_id: str) -> List[Dict[str, Any]]:
        """
        Get all policies for a worker.

        Args:
            worker_id: Worker ID

        Returns:
            List of policy documents
        """
        return self.find_many(
            {"worker_id": worker_id},
            sort_field="created_at",
            sort_order=-1
        )

    def get_active_policy(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current active policy for a worker.

        Args:
            worker_id: Worker ID

        Returns:
            Active policy document or None
        """
        now = datetime.now()
        return self.find_one({
            "worker_id": worker_id,
            "active_status": True,
            "start_date": {"$lte": now},
            "end_date": {"$gte": now}
        })

    def get_policies_expiring_soon(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get policies expiring within specified hours.

        Args:
            hours: Hours until expiration

        Returns:
            List of expiring policies
        """
        now = datetime.now()
        expiry_threshold = now + timedelta(hours=hours)

        return self.find_many({
            "active_status": True,
            "end_date": {"$lte": expiry_threshold, "$gte": now}
        })

    def get_expired_policies(self) -> List[Dict[str, Any]]:
        """
        Get all expired policies.

        Returns:
            List of expired policies
        """
        now = datetime.now()
        return self.find_many({
            "end_date": {"$lt": now},
            "active_status": True
        })

    def update_policy(self, policy_id: str, **kwargs) -> bool:
        """
        Update policy.

        Args:
            policy_id: Policy ID
            **kwargs: Fields to update

        Returns:
            True if successful
        """
        kwargs["updated_at"] = datetime.now()
        return self.update_by_id(policy_id, kwargs, id_field="policy_id")

    def deactivate_policy(self, policy_id: str) -> bool:
        """
        Deactivate policy.

        Args:
            policy_id: Policy ID

        Returns:
            True if successful
        """
        return self.update_policy(policy_id, active_status=False)

    def renew_policy(self, policy_id: str, duration_days: int = 7) -> bool:
        """
        Renew policy for additional days.

        Args:
            policy_id: Policy ID
            duration_days: Days to extend

        Returns:
            True if successful
        """
        policy = self.get_policy(policy_id)
        if not policy:
            return False

        new_end_date = policy["end_date"] + timedelta(days=duration_days)
        return self.update_policy(policy_id, end_date=new_end_date)

    def disable_expired_policies(self) -> int:
        """
        Disable all expired policies.

        Returns:
            Number of policies disabled
        """
        expired = self.get_expired_policies()
        count = 0
        for policy in expired:
            if self.deactivate_policy(policy["policy_id"]):
                count += 1
        return count

    def policy_is_valid(self, policy_id: str) -> bool:
        """
        Check if policy is valid and active.

        Args:
            policy_id: Policy ID

        Returns:
            True if policy is valid and active
        """
        policy = self.get_policy(policy_id)
        if not policy:
            return False

        now = datetime.now()
        return (
            policy.get("active_status", False) and
            policy["start_date"] <= now <= policy["end_date"]
        )

    def delete_policy(self, policy_id: str) -> bool:
        """
        Delete policy.

        Args:
            policy_id: Policy ID

        Returns:
            True if successful
        """
        return self.delete({"policy_id": policy_id})

    def get_active_policies_count(self) -> int:
        """
        Get count of active policies.

        Returns:
            Number of active policies
        """
        now = datetime.now()
        return self.count({
            "active_status": True,
            "start_date": {"$lte": now},
            "end_date": {"$gte": now}
        })
