"""
MODULE 9: AUTOMATION ENGINE
Continuous/On-demand automation of claim processing across all policies
"""
from typing import Dict, Any, List
from datetime import datetime

from services.repositories.policy_repository import PolicyRepository
from services.repositories.worker_repository import WorkerRepository
from services.claims.claim_orchestrator import ClaimOrchestrator


class AutomationEngine:
    """Automated claim processing  for active policies."""

    def __init__(self):
        """Initialize automation engine."""
        self.policy_repo = PolicyRepository()
        self.worker_repo = WorkerRepository()
        self.claim_orchestrator = ClaimOrchestrator()

    def trigger_claims_for_event(self, rainfall_mm: float, temperature: float,
                                aqi: float, alert_texts: List[str] = None) -> Dict[str, Any]:
        """
        Trigger automatic claims for all active policies when event is detected.

        Process:
        1. Get all active policies
        2. For each policy:
           - Call claim orchestrator
           - Process full claim lifecycle
           - Track results
        3. Return summary of all processed claims

        Args:
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            aqi: Air Quality Index
            alert_texts: Optional alert texts

        Returns:
            Automation results with processed claims
        """
        try:
            # Get all active policies
            active_policies = self.policy_repo.find_many({
                "active_status": True,
                "start_date": {"$lte": datetime.now()},
                "end_date": {"$gte": datetime.now()}
            })

            if not active_policies:
                return {
                    "success": True,
                    "message": "No active policies to process",
                    "policies_processed": 0,
                    "claims_created": 0,
                    "payouts_processed": 0,
                    "results": []
                }

            results = []
            claims_created = 0
            payouts_processed = 0

            # Process each active policy
            for policy in active_policies:
                try:
                    claim_result = self.claim_orchestrator.process_claim_for_policy(
                        policy_id=policy["policy_id"],
                        rainfall_mm=rainfall_mm,
                        temperature=temperature,
                        aqi=aqi,
                        disruption_hours=4,
                        gps_movement=2.0,
                        alert_texts=alert_texts
                    )

                    if claim_result["success"]:
                        claims_created += 1
                        if claim_result.get("payout_id"):
                            payouts_processed += 1

                    results.append({
                        "policy_id": policy["policy_id"],
                        "worker_id": policy["worker_id"],
                        "claim_created": claim_result.get("success", False),
                        "claim_id": claim_result.get("claim_id"),
                        "claim_status": claim_result.get("claim_status"),
                        "message": claim_result.get("message"),
                    })

                except Exception as e:
                    results.append({
                        "policy_id": policy["policy_id"],
                        "worker_id": policy["worker_id"],
                        "claim_created": False,
                        "error": str(e),
                    })

            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "policies_processed": len(active_policies),
                "claims_created": claims_created,
                "payouts_processed": payouts_processed,
                "message": f"✅ Automated {claims_created} claims from {len(active_policies)} active policies",
                "results": results,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Automation failed: {str(e)}",
                "policies_processed": 0,
                "claims_created": 0,
                "payouts_processed": 0,
            }

    def process_single_policy(self, policy_id: str, rainfall_mm: float,
                             temperature: float, aqi: float,
                             disruption_hours: float = 4,
                             gps_movement: float = 2.0,
                             alert_texts: List[str] = None) -> Dict[str, Any]:
        """
        Process claim for a specific policy.

        Args:
            policy_id: Policy ID
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            aqi: Air Quality Index
            disruption_hours: Hours of disruption
            gps_movement: GPS movement score
            alert_texts: Optional alert texts

        Returns:
            Claim processing result
        """
        return self.claim_orchestrator.process_claim_for_policy(
            policy_id=policy_id,
            rainfall_mm=rainfall_mm,
            temperature=temperature,
            aqi=aqi,
            disruption_hours=disruption_hours,
            gps_movement=gps_movement,
            alert_texts=alert_texts
        )

    def get_automation_status(self) -> Dict[str, Any]:
        """
        Get automation engine status.

        Returns:
            Status information
        """
        try:
            active_policy_count = self.policy_repo.get_active_policies_count()

            return {
                "success": True,
                "status": "operational",
                "active_policies": active_policy_count,
                "auto_trigger_enabled": True,
                "message": f"Automation engine ready with {active_policy_count} active policies"
            }

        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "error": str(e)
            }
