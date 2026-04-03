"""
Claim Repository - CRUD operations for insurance claims
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from services.repositories.base_repository import BaseRepository
from config.settings import CLAIM_STATUS_INITIAL
import uuid


class ClaimRepository(BaseRepository):
    """Repository for claim management."""

    def __init__(self):
        """Initialize claim repository."""
        super().__init__("claims")

    def generate_claim_id(self) -> str:
        """
        Generate unique claim ID.

        Returns:
            Unique claim_id in format CLM{XXXXX}
        """
        return f"CLM{str(uuid.uuid4())[:8]}"

    def create_claim(self, policy_id: str, worker_id: str, event_type: str,
                    trigger_conditions: List[str]) -> Dict[str, Any]:
        """
        Create new claim.

        Args:
            policy_id: Policy ID
            worker_id: Worker ID
            event_type: Type of disruption event
            trigger_conditions: List of triggered conditions

        Returns:
            Created claim document
        """
        claim_id = self.generate_claim_id()
        now = datetime.now()

        claim = {
            "claim_id": claim_id,
            "policy_id": policy_id,
            "worker_id": worker_id,
            "event_type": event_type,
            "trigger_conditions": trigger_conditions,
            "claim_status": CLAIM_STATUS_INITIAL,
            "fraud_score": 0.0,
            "fraud_status": "Cleared",
            "estimated_loss": 0.0,
            "approved_payout": 0.0,
            "created_at": now,
            "updated_at": now,
        }

        self.create(claim)
        return claim

    def get_claim(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Get claim by ID.

        Args:
            claim_id: Claim ID

        Returns:
            Claim document or None
        """
        return self.find_one({"claim_id": claim_id})

    def get_worker_claims(self, worker_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all claims for a worker.

        Args:
            worker_id: Worker ID
            limit: Maximum number of claims to return

        Returns:
            List of claim documents
        """
        return self.find_many(
            {"worker_id": worker_id},
            limit=limit,
            sort_field="created_at",
            sort_order=-1
        )

    def get_active_claims(self, worker_id: str) -> List[Dict[str, Any]]:
        """
        Get active (non-final) claims for a worker.

        Args:
            worker_id: Worker ID

        Returns:
            List of active claims
        """
        active_statuses = ["Initiated", "Validated", "Under Review", "Approved"]
        return self.find_many({
            "worker_id": worker_id,
            "claim_status": {"$in": active_statuses}
        })

    def get_claims_by_status(self, status: str, limit: int = 0) -> List[Dict[str, Any]]:
        """
        Get all claims with specific status.

        Args:
            status: Claim status
            limit: Maximum number of claims

        Returns:
            List of claims
        """
        return self.find_many(
            {"claim_status": status},
            limit=limit,
            sort_field="created_at",
            sort_order=-1
        )

    def get_flagged_claims(self) -> List[Dict[str, Any]]:
        """
        Get all flagged claims (potential fraud).

        Returns:
            List of flagged claims
        """
        return self.find_many(
            {"fraud_status": "Flagged"},
            sort_field="created_at",
            sort_order=-1
        )

    def update_claim(self, claim_id: str, **kwargs) -> bool:
        """
        Update claim.

        Args:
            claim_id: Claim ID
            **kwargs: Fields to update

        Returns:
            True if successful
        """
        kwargs["updated_at"] = datetime.now()
        return self.update_by_id(claim_id, kwargs, id_field="claim_id")

    def update_claim_status(self, claim_id: str, status: str) -> bool:
        """
        Update claim status.

        Args:
            claim_id: Claim ID
            status: New status

        Returns:
            True if successful
        """
        return self.update_claim(claim_id, claim_status=status)

    def update_fraud_assessment(self, claim_id: str, fraud_score: float,
                               fraud_status: str) -> bool:
        """
        Update fraud assessment.

        Args:
            claim_id: Claim ID
            fraud_score: Fraud score (0-100)
            fraud_status: Fraud status

        Returns:
            True if successful
        """
        return self.update_claim(
            claim_id,
            fraud_score=fraud_score,
            fraud_status=fraud_status
        )

    def update_loss_estimation(self, claim_id: str, estimated_loss: float) -> bool:
        """
        Update estimated loss.

        Args:
            claim_id: Claim ID
            estimated_loss: Estimated loss amount

        Returns:
            True if successful
        """
        return self.update_claim(claim_id, estimated_loss=estimated_loss)

    def update_payout(self, claim_id: str, approved_payout: float) -> bool:
        """
        Update approved payout amount.

        Args:
            claim_id: Claim ID
            approved_payout: Approved payout amount

        Returns:
            True if successful
        """
        return self.update_claim(claim_id, approved_payout=approved_payout)

    def get_claims_by_date_range(self, start_date: datetime, end_date: datetime,
                                limit: int = 0) -> List[Dict[str, Any]]:
        """
        Get claims created within date range.

        Args:
            start_date: Start date
            end_date: End date
            limit: Maximum number of claims

        Returns:
            List of claims
        """
        return self.find_many(
            {
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            },
            limit=limit,
            sort_field="created_at",
            sort_order=-1
        )

    def get_claims_for_policy(self, policy_id: str) -> List[Dict[str, Any]]:
        """
        Get all claims for a specific policy.

        Args:
            policy_id: Policy ID

        Returns:
            List of claims
        """
        return self.find_many(
            {"policy_id": policy_id},
            sort_field="created_at",
            sort_order=-1
        )

    def delete_claim(self, claim_id: str) -> bool:
        """
        Delete claim.

        Args:
            claim_id: Claim ID

        Returns:
            True if successful
        """
        return self.delete({"claim_id": claim_id})

    def get_claim_stats(self, worker_id: str = None) -> Dict[str, Any]:
        """
        Get claim statistics.

        Args:
            worker_id: Optional worker ID for specific worker stats

        Returns:
            Statistics dictionary
        """
        query = {} if worker_id is None else {"worker_id": worker_id}

        # Aggregate stats
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "total_claims": {"$sum": 1},
                    "approved_count": {
                        "$sum": {"$cond": [{"$eq": ["$claim_status", "Paid"]}, 1, 0]}
                    },
                    "flagged_count": {
                        "$sum": {"$cond": [{"$eq": ["$fraud_status", "Flagged"]}, 1, 0]}
                    },
                    "total_loss": {"$sum": "$estimated_loss"},
                    "total_payout": {"$sum": "$approved_payout"},
                }
            }
        ]

        result = self.aggregate(pipeline)
        if result:
            return result[0]

        return {
            "total_claims": 0,
            "approved_count": 0,
            "flagged_count": 0,
            "total_loss": 0.0,
            "total_payout": 0.0,
        }
