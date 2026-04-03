"""
Worker Repository - CRUD operations for worker profiles
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from services.repositories.base_repository import BaseRepository
import uuid


class WorkerRepository(BaseRepository):
    """Repository for worker profile management."""

    def __init__(self):
        """Initialize worker repository."""
        super().__init__("workers")

    def generate_worker_id(self) -> str:
        """
        Generate unique worker ID.

        Returns:
            Unique worker_id in format W{XXX}
        """
        # Get count and generate ID
        count = self.collection.count_documents({})
        return f"W{count + 1:03d}"

    def create_worker(self, name: str, city: str, delivery_zone: str,
                     avg_hourly_income: float) -> Dict[str, Any]:
        """
        Create new worker profile.

        Args:
            name: Worker name
            city: City
            delivery_zone: Delivery zone
            avg_hourly_income: Average hourly income

        Returns:
            Created worker document
        """
        worker_id = self.generate_worker_id()

        worker = {
            "worker_id": worker_id,
            "name": name,
            "city": city,
            "delivery_zone": delivery_zone,
            "avg_hourly_income": avg_hourly_income,
            "kyc_status": "Verified",
            "rating": 4.5,
            "total_deliveries": 0,
            "total_earnings": 0.0,
            "total_payouts": 0.0,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        self.create(worker)
        return worker

    def get_worker(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get worker profile by ID.

        Args:
            worker_id: Worker ID

        Returns:
            Worker document or None
        """
        return self.find_one({"worker_id": worker_id})

    def get_workers_by_zone(self, delivery_zone: str) -> List[Dict[str, Any]]:
        """
        Get all workers in a delivery zone.

        Args:
            delivery_zone: Delivery zone

        Returns:
            List of worker documents
        """
        return self.find_many({"delivery_zone": delivery_zone})

    def get_workers_by_city(self, city: str) -> List[Dict[str, Any]]:
        """
        Get all workers in a city.

        Args:
            city: City name

        Returns:
            List of worker documents
        """
        return self.find_many({"city": city})

    def get_all_workers(self, limit: int = 0) -> List[Dict[str, Any]]:
        """
        Get all workers.

        Args:
            limit: Maximum number of workers to return

        Returns:
            List of worker documents
        """
        return self.find_many({}, limit=limit)

    def update_worker(self, worker_id: str, **kwargs) -> bool:
        """
        Update worker profile.

        Args:
            worker_id: Worker ID
            **kwargs: Fields to update

        Returns:
            True if successful
        """
        kwargs["updated_at"] = datetime.now()
        return self.update_by_id(worker_id, kwargs, id_field="worker_id")

    def update_earnings(self, worker_id: str, earnings_amount: float) -> bool:
        """
        Update worker total earnings and delivery count.

        Args:
            worker_id: Worker ID
            earnings_amount: Amount earned

        Returns:
            True if successful
        """
        return self.collection.update_one(
            {"worker_id": worker_id},
            {
                "$inc": {
                    "total_earnings": earnings_amount,
                    "total_deliveries": 1
                },
                "$set": {"updated_at": datetime.now()}
            }
        ).modified_count > 0

    def update_payouts(self, worker_id: str, payout_amount: float) -> bool:
        """
        Update worker total payouts.

        Args:
            worker_id: Worker ID
            payout_amount: Payout amount

        Returns:
            True if successful
        """
        return self.collection.update_one(
            {"worker_id": worker_id},
            {
                "$inc": {"total_payouts": payout_amount},
                "$set": {"updated_at": datetime.now()}
            }
        ).modified_count > 0

    def update_rating(self, worker_id: str, rating: float) -> bool:
        """
        Update worker rating.

        Args:
            worker_id: Worker ID
            rating: New rating (0-5)

        Returns:
            True if successful
        """
        return self.update_worker(worker_id, rating=min(5.0, max(0.0, rating)))

    def get_worker_stats(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get worker statistics.

        Args:
            worker_id: Worker ID

        Returns:
            Worker stats dictionary
        """
        worker = self.get_worker(worker_id)
        if not worker:
            return None

        return {
            "worker_id": worker["worker_id"],
            "name": worker["name"],
            "total_deliveries": worker.get("total_deliveries", 0),
            "total_earnings": worker.get("total_earnings", 0.0),
            "total_payouts": worker.get("total_payouts", 0.0),
            "rating": worker.get("rating", 0.0),
            "city": worker["city"],
            "zone": worker["delivery_zone"],
        }

    def delete_worker(self, worker_id: str) -> bool:
        """
        Delete worker profile.

        Args:
            worker_id: Worker ID

        Returns:
            True if successful
        """
        return self.delete({"worker_id": worker_id})

    def worker_exists(self, worker_id: str) -> bool:
        """
        Check if worker exists.

        Args:
            worker_id: Worker ID

        Returns:
            True if worker exists
        """
        return self.exists({"worker_id": worker_id})
