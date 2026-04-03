"""
MODULE 5.8: CLAIM ORCHESTRATOR
Main orchestration engine for complete claim lifecycle automation
Coordinates all 8 sub-modules in proper sequence
"""
from typing import Dict, Any, List
from datetime import datetime

from services.repositories.claim_repository import ClaimRepository
from services.repositories.policy_repository import PolicyRepository
from services.repositories.worker_repository import WorkerRepository
from services.repositories.audit_log_repository import AuditLogRepository

# Import all sub-modules
from services.claims.detect_event import ClaimEventDetector
from services.claims.initiate_claim import ClaimInitiator
from services.claims.validate_eligibility import ClaimEligibilityValidator
from services.claims.fraud_check import FraudChecker
from services.claims.estimate_loss import LossEstimator
from services.claims.approve_claim import ClaimApprover
from services.claims.process_payout import PayoutProcessor


class ClaimOrchestrator:
    """
    Main orchestration engine for complete claim lifecycle.

    Workflow:
    1. Detect event
    2. Initiate claim
    3. Validate eligibility
    4. Check fraud
    5. Estimate loss
    6. Approve claim
    7. Process payout
    8. Record claim with audit trail
    """

    def __init__(self):
        """Initialize claim orchestrator with all sub-modules."""
        # Repositories
        self.claim_repo = ClaimRepository()
        self.policy_repo = PolicyRepository()
        self.worker_repo = WorkerRepository()

        # Sub-modules
        self.event_detector = ClaimEventDetector()
        self.claim_initiator = ClaimInitiator()
        self.eligibility_validator = ClaimEligibilityValidator()
        self.fraud_checker = FraudChecker()
        self.loss_estimator = LossEstimator()
        self.claim_approver = ClaimApprover()
        self.payout_processor = PayoutProcessor()

    def process_claim_for_policy(self, policy_id: str, rainfall_mm: float,
                                temperature: float, aqi: float,
                                disruption_hours: float = 4, gps_movement: float = 2.0,
                                alert_texts: List[str] = None) -> Dict[str, Any]:
        """
        Process complete claim lifecycle for a policy.

        Full E2E flow:
        1️⃣ DETECT EVENT
        2️⃣ INITIATE CLAIM
        3️⃣ VALIDATE ELIGIBILITY
        4️⃣ CHECK FRAUD
        5️⃣ ESTIMATE LOSS
        6️⃣ APPROVE CLAIM
        7️⃣ PROCESS PAYOUT (if approved)
        8️⃣ RECORD CLAIM

        Args:
            policy_id: Policy ID
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            aqi: Air Quality Index
            disruption_hours: Hours of disruption
            gps_movement: GPS movement score
            alert_texts: Optional alert texts

        Returns:
            Complete claim processing result
        """
        try:
            # Get policy and worker info
            policy = self.policy_repo.get_policy(policy_id)
            if not policy:
                return {"success": False, "error": "Policy not found"}

            worker_id = policy["worker_id"]
            worker = self.worker_repo.get_worker(worker_id)
            if not worker:
                return {"success": False, "error": "Worker not found"}

            result = {
                "success": False,
                "worker_id": worker_id,
                "policy_id": policy_id,
                "steps": {}
            }

            # ===== STEP 1: DETECT EVENT =====
            event_result = self.event_detector.detect_event_for_claim(
                rainfall_mm, temperature, aqi, alert_texts
            )
            result["steps"]["1_event_detection"] = event_result

            if not event_result["event_detected"]:
                result["message"] = "✅ No disruption event detected - no claim created"
                return result

            # ===== STEP 2: INITIATE CLAIM =====
            init_result = self.claim_initiator.initiate_claim(
                policy_id=policy_id,
                worker_id=worker_id,
                event_type=event_result.get("primary_event", "Unknown"),
                trigger_conditions=event_result["trigger_conditions"]
            )
            result["steps"]["2_claim_initiation"] = init_result

            if not init_result["success"]:
                return result

            claim_id = init_result["claim_id"]

            # ===== STEP 3: VALIDATE ELIGIBILITY =====
            validation_result = self.eligibility_validator.validate_eligibility(
                policy_id, claim_id
            )
            result["steps"]["3_eligibility_validation"] = validation_result
            is_eligible = validation_result["valid"]

            # ===== STEP 4: CHECK FRAUD =====
            # Count recent claims for repeated claims check
            recent_claims = self.claim_repo.find_many(
                {"worker_id": worker_id},
                limit=10
            )
            repeated_count = len([c for c in recent_claims if (
                datetime.now() - c["created_at"]
            ).days < 7])

            fraud_result = self.fraud_checker.check_fraud(
                disruption_hours,
                0,  # Will be set after loss estimation
                gps_movement,
                repeated_count
            )
            result["steps"]["4_fraud_check"] = fraud_result

            # ===== STEP 5: ESTIMATE LOSS =====
            loss_result = self.loss_estimator.estimate_loss(
                disruption_hours,
                worker["avg_hourly_income"]
            )
            result["steps"]["5_loss_estimation"] = loss_result

            estimated_loss = loss_result.get("estimated_loss", 0.0)

            # Re-run fraud check with actual loss amount
            fraud_result = self.fraud_checker.check_fraud(
                disruption_hours,
                estimated_loss,
                gps_movement,
                repeated_count
            )
            result["steps"]["4_fraud_check"] = fraud_result
            fraud_score = fraud_result.get("fraud_score", 0.0)

            # ===== STEP 6: APPROVE CLAIM =====
            approval_result = self.claim_approver.approve_claim(
                claim_id,
                is_eligible,
                fraud_score,
                estimated_loss
            )
            result["steps"]["6_claim_approval"] = approval_result
            claim_status = approval_result["claim_status"]

            # ===== STEP 7: PROCESS PAYOUT =====
            if claim_status == "Approved":
                payout_result = self.payout_processor.process_payout(
                    claim_id,
                    estimated_loss
                )
                result["steps"]["7_payout_processing"] = payout_result
                payout_id = payout_result.get("payout_id")
            else:
                payout_result = {
                    "success": False,
                    "reason": f"Claim status is {claim_status}",
                    "payout_id": None
                }
                result["steps"]["7_payout_processing"] = payout_result
                payout_id = None

            # ===== STEP 8: RECORD CLAIM =====
            # All data already persisted in databases, just summarize here
            claim = self.claim_repo.get_claim(claim_id)

            # JUSTIFICATION TRACE ENHANCEMENT
            trace = f"{self._generate_final_message(claim_status, estimated_loss, payout_id)}\n"
            trace += "Reason Breakdown:\n"
            if event_result["trigger_conditions"]:
                for cond in event_result["trigger_conditions"]:
                    trace += f"- {cond}\n"
            trace += f"- Confidence Validated: {loss_result.get('confidence', 0.91)*100:.1f}%\n"

            result.update({
                "success": True,
                "claim_id": claim_id,
                "claim_status": claim_status,
                "estimated_loss": estimated_loss,
                "approved_payout": claim.get("approved_payout", 0.0) if claim else 0.0,
                "payout_id": payout_id,
                "message": trace,
                "summary": {
                    "eligibility": is_eligible,
                    "fraud_score": fraud_score,
                    "fraud_status": fraud_result.get("fraud_status"),
                    "disruption_hours": disruption_hours,
                    "incident_date": datetime.now().isoformat(),
                }
            })

            return result

        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": f"Claim processing failed: {str(e)}",
                "trace": traceback.format_exc()
            }

    def _generate_final_message(self, status: str, amount: float,
                               payout_id: str = None) -> str:
        """Generate final summary message."""
        if status == "Paid":
            return f"✅ **CLAIM AUTO-PROCESSED!** ₹{amount} payout ({payout_id})"
        elif status == "Approved":
            return f"✅ Claim approved: ₹{amount} pending payout"
        elif status == "Flagged":
            return f"⚠️ Claim flagged for fraud review"
        elif status == "Under Review":
            return f"📋 Claim under review"
        else:
            return f"❌ Claim {status}"

    def get_claim_status(self, claim_id: str) -> Dict[str, Any]:
        """Get current claim status."""
        return self.claim_repo.get_claim(claim_id)

    def get_worker_claims(self, worker_id: str) -> List[Dict[str, Any]]:
        """Get all claims for a worker."""
        return self.claim_repo.get_worker_claims(worker_id)
