"""
MODULE 8: DASHBOARD DATA AGGREGATION
Aggregate data for dashboard display
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from services.repositories.worker_repository import WorkerRepository
from services.repositories.policy_repository import PolicyRepository
from services.repositories.claim_repository import ClaimRepository
from services.repositories.payout_repository import PayoutRepository
from services.repositories.zone_repository import ZoneRepository


class DashboardService:
    """Aggregate and prepare data for dashboard display."""

    def __init__(self):
        """Initialize dashboard service."""
        self.worker_repo = WorkerRepository()
        self.policy_repo = PolicyRepository()
        self.claim_repo = ClaimRepository()
        self.payout_repo = PayoutRepository()
        self.zone_repo = ZoneRepository()

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get complete dashboard data.

        Returns:
            Dictionary with all KPIs and recent data
        """
        try:
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)

            # Get KPIs
            total_workers = self.worker_repo.count({})
            active_policies = self.policy_repo.get_active_policies_count()

            # Claims today
            claims_today = self.claim_repo.count({
                "created_at": {"$gte": today}
            })

            # Claims this week
            claims_week = self.claim_repo.count({
                "created_at": {"$gte": week_ago}
            })

            # Payouts statistics
            payout_stats = self.payout_repo.get_payout_stats()
            total_payout_amount = self.payout_repo.get_total_payout_amount()

            # Calculate success rate
            total_claims_week = self.claim_repo.count({
                "created_at": {"$gte": week_ago}
            })
            paid_claims = self.claim_repo.count({
                "claim_status": "Paid",
                "created_at": {"$gte": week_ago}
            })
            success_rate = (paid_claims / total_claims_week * 100) if total_claims_week > 0 else 0

            # Recent claims
            recent_claims = self.claim_repo.find_many({}, limit=10, sort_field="created_at", sort_order=-1)

            # Recent payouts
            recent_payouts = self.payout_repo.find_many({}, limit=10, sort_field="timestamp", sort_order=-1)

            # Flagged claims (alerts)
            flagged_claims = self.claim_repo.get_flagged_claims()

            return {
                "success": True,
                "timestamp": now.isoformat(),
                "kpis": {
                    "total_workers": total_workers,
                    "active_policies": active_policies,
                    "claims_today": claims_today,
                    "claims_this_week": claims_week,
                    "total_payouts": payout_stats.get("total_payouts", 0),
                    "total_payout_amount": total_payout_amount,
                    "success_rate_percent": round(success_rate, 1),
                },
                "recent_data": {
                    "recent_claims": [self._format_claim(c) for c in recent_claims],
                    "recent_payouts": [self._format_payout(p) for p in recent_payouts],
                    "flagged_claims_count": len(flagged_claims),
                    "high_risk_alerts": len(flagged_claims),
                },
                "zones": self.zone_repo.get_zone_stats(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Dashboard data query failed: {str(e)}"
            }

    def get_worker_dashboard(self, worker_id: str) -> Dict[str, Any]:
        """
        Get worker-specific dashboard data.

        Args:
            worker_id: Worker ID

        Returns:
            Worker-specific dashboard data
        """
        try:
            worker = self.worker_repo.get_worker(worker_id)
            if not worker:
                return {"success": False, "error": "Worker not found"}

            # Get worker's current policy
            active_policy = self.policy_repo.get_active_policy(worker_id)

            # Get worker's claims
            worker_claims = self.claim_repo.find_many(
                {"worker_id": worker_id},
                limit=20,
                sort_field="created_at",
                sort_order=-1
            )

            # Get worker's payouts
            worker_payouts = self.payout_repo.find_many(
                {"worker_id": worker_id},
                limit=20,
                sort_field="timestamp",
                sort_order=-1
            )

            # Calculate worker stats
            claim_stats = self.claim_repo.get_claim_stats(worker_id)
            payout_stats = self.payout_repo.get_payout_stats(worker_id=worker_id)

            return {
                "success": True,
                "worker": {
                    "worker_id": worker["worker_id"],
                    "name": worker["name"],
                    "zone": worker["delivery_zone"],
                    "city": worker["city"],
                    "hourly_income": worker["avg_hourly_income"],
                    "rating": worker.get("rating", 4.5),
                },
                "active_policy": {
                    "policy_id": active_policy["policy_id"] if active_policy else None,
                    "weekly_premium": active_policy["weekly_premium"] if active_policy else None,
                    "coverage_limit": active_policy["coverage_limit"] if active_policy else None,
                    "active": active_policy is not None,
                },
                "statistics": {
                    "total_claims": claim_stats.get("total_claims", 0),
                    "paid_claims": claim_stats.get("approved_count", 0),
                    "flagged_claims": claim_stats.get("flagged_count", 0),
                    "total_loss": claim_stats.get("total_loss", 0.0),
                    "total_payouts": payout_stats.get("total_amount", 0.0),
                },
                "recent_claims": [self._format_claim(c) for c in worker_claims],
                "recent_payouts": [self._format_payout(p) for p in worker_payouts],
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Worker dashboard failed: {str(e)}"
            }

    def _format_claim(self, claim: Dict) -> Dict:
        """Format claim for display."""
        return {
            "claim_id": claim["claim_id"],
            "status": claim["claim_status"],
            "event_type": claim.get("event_type"),
            "loss": claim.get("estimated_loss", 0),
            "created_at": claim["created_at"].isoformat() if hasattr(claim["created_at"],
 'isoformat') else str(claim["created_at"]),
        }

    def _format_payout(self, payout: Dict) -> Dict:
        """Format payout for display."""
        return {
            "payout_id": payout["payout_id"],
            "claim_id": payout["claim_id"],
            "amount": payout["amount"],
            "status": payout["status"],
            "timestamp": payout["timestamp"].isoformat() if hasattr(payout["timestamp"], 'isoformat') else str(
                payout["timestamp"]),
        }
