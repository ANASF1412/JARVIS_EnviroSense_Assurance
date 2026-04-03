"""
Payout Repository - CRUD operations for payout transactions
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from services.repositories.base_repository import BaseRepository
from config.settings import PAYOUT_STATUS_PENDING, PAYOUT_STATUS_COMPLETED
import uuid
import time


class PayoutRepository(BaseRepository):
    """Repository for payout transaction management."""

    def __init__(self):
        """Initialize payout repository."""
        super().__init__("payouts")

    def generate_payout_id(self) -> str:
        """
        Generate unique payout ID.

        Returns:
            Unique payout_id in format PO{XXXXX}
        """
        return f"PO{str(uuid.uuid4())[:8]}"

    def generate_upi_txn_id(self) -> str:
        """
        Generate UPI transaction ID.

        Returns:
            UPI transaction ID
        """
        return f"UPI{int(time.time())}{str(uuid.uuid4())[:6]}"

    def create_payout(self, claim_id: str, worker_id: str,
                     amount: float) -> Dict[str, Any]:
        """
        Create payout transaction.

        Args:
            claim_id: Claim ID
            worker_id: Worker ID
            amount: Payout amount

        Returns:
            Created payout document
        """
        payout_id = self.generate_payout_id()
        now = datetime.now()

        payout = {
            "payout_id": payout_id,
            "claim_id": claim_id,
            "worker_id": worker_id,
            "amount": amount,
            "status": PAYOUT_STATUS_PENDING,
            "upi_txn_id": None,
            "timestamp": now,
            "completed_at": None,
        }

        self.create(payout)
        return payout

    def get_payout(self, payout_id: str) -> Optional[Dict[str, Any]]:
        """
        Get payout by ID.

        Args:
            payout_id: Payout ID

        Returns:
            Payout document or None
        """
        return self.find_one({"payout_id": payout_id})

    def get_payout_by_claim(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Get payout for a claim.

        Args:
            claim_id: Claim ID

        Returns:
            Payout document or None
        """
        return self.find_one({"claim_id": claim_id})

    def get_worker_payouts(self, worker_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all payouts for a worker.

        Args:
            worker_id: Worker ID
            limit: Maximum number of payouts

        Returns:
            List of payout documents
        """
        return self.find_many(
            {"worker_id": worker_id},
            limit=limit,
            sort_field="timestamp",
            sort_order=-1
        )

    def get_payouts_by_status(self, status: str, limit: int = 0) -> List[Dict[str, Any]]:
        """
        Get payouts with specific status.

        Args:
            status: Payout status
            limit: Maximum number of payouts

        Returns:
            List of payouts
        """
        return self.find_many(
            {"status": status},
            limit=limit,
            sort_field="timestamp",
            sort_order=-1
        )

    def get_pending_payouts(self) -> List[Dict[str, Any]]:
        """
        Get all pending payouts.

        Returns:
            List of pending payouts
        """
        return self.get_payouts_by_status(PAYOUT_STATUS_PENDING)

    def get_completed_payouts(self) -> List[Dict[str, Any]]:
        """
        Get all completed payouts.

        Returns:
            List of completed payouts
        """
        return self.get_payouts_by_status(PAYOUT_STATUS_COMPLETED)

    def complete_payout(self, payout_id: str, upi_txn_id: str) -> bool:
        """
        Mark payout as completed.

        Args:
            payout_id: Payout ID
            upi_txn_id: UPI transaction ID

        Returns:
            True if successful
        """
        return self.collection.update_one(
            {"payout_id": payout_id},
            {
                "$set": {
                    "status": PAYOUT_STATUS_COMPLETED,
                    "upi_txn_id": upi_txn_id,
                    "completed_at": datetime.now()
                }
            }
        ).modified_count > 0

    def get_payouts_by_date_range(self, start_date: datetime, end_date: datetime,
                                 limit: int = 0) -> List[Dict[str, Any]]:
        """
        Get payouts within date range.

        Args:
            start_date: Start date
            end_date: End date
            limit: Maximum number of payouts

        Returns:
            List of payouts
        """
        return self.find_many(
            {
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            },
            limit=limit,
            sort_field="timestamp",
            sort_order=-1
        )

    def delete_payout(self, payout_id: str) -> bool:
        """
        Delete payout.

        Args:
            payout_id: Payout ID

        Returns:
            True if successful
        """
        return self.delete({"payout_id": payout_id})

    def get_payout_stats(self, worker_id: str = None,
                        status: str = None) -> Dict[str, Any]:
        """
        Get payout statistics.

        Args:
            worker_id: Optional worker ID filter
            status: Optional status filter

        Returns:
            Statistics dictionary
        """
        query = {}
        if worker_id:
            query["worker_id"] = worker_id
        if status:
            query["status"] = status

        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "total_payouts": {"$sum": 1},
                    "total_amount": {"$sum": "$amount"},
                    "avg_amount": {"$avg": "$amount"},
                }
            }
        ]

        result = self.aggregate(pipeline)
        if result:
            return result[0]

        return {
            "total_payouts": 0,
            "total_amount": 0.0,
            "avg_amount": 0.0,
        }

    def get_total_payout_amount(self, worker_id: str = None) -> float:
        """
        Get total payout amount (completed payouts only).

        Args:
            worker_id: Optional worker ID filter

        Returns:
            Total amount paid out
        """
        query = {"status": PAYOUT_STATUS_COMPLETED}
        if worker_id:
            query["worker_id"] = worker_id

        result = self.collection.aggregate([
            {"$match": query},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])

        result_list = list(result)
        return result_list[0]["total"] if result_list else 0.0
