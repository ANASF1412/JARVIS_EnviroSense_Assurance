"""
MODULE 5.6: CLAIM APPROVAL
Approve or flag claim based on validation and fraud results
"""
from typing import Dict, Any
from services.repositories.claim_repository import ClaimRepository
from config.settings import (
    CLAIM_STATUS_APPROVED,
    CLAIM_STATUS_FLAGGED,
    FRAUD_SCORE_THRESHOLD,
)


class ClaimApprover:
    """Approve or flag claims based on validation results."""

    def __init__(self):
        """Initialize claim approver."""
        self.claim_repo = ClaimRepository()

    def approve_claim(self, claim_id: str, is_eligible: bool,
                     fraud_score: float, estimated_loss: float) -> Dict[str, Any]:
        """
        Approve or flag claim based on validation and fraud results.

        Logic:
        IF eligible AND fraud_score ≤ 70:
            → status = "Approved"
        ELSE:
            → status = "Under Review" or "Flagged"

        Args:
            claim_id: Claim ID
            is_eligible: Is claim eligible (from validation)
            fraud_score: Fraud score (0-100)
            estimated_loss: Estimated income loss

        Returns:
            Approval result
        """
        try:
            # Determine status based on validation and fraud check
            if not is_eligible:
                claim_status = "Rejected"
                approval_reason = "Not eligible based on policy validation"
            elif fraud_score >= FRAUD_SCORE_THRESHOLD:
                claim_status = CLAIM_STATUS_FLAGGED
                approval_reason = f"Fraud concerns (score: {fraud_score})"
            else:
                claim_status = CLAIM_STATUS_APPROVED
                approval_reason = "Approved - eligible and fraud check cleared"

            # Update claim status in database
            self.claim_repo.update_claim_status(claim_id, claim_status)
            self.claim_repo.update_payout(claim_id, estimated_loss if claim_status == CLAIM_STATUS_APPROVED else 0.0)

            return {
                "success": True,
                "claim_id": claim_id,
                "claim_status": claim_status,
                "approved_payout": estimated_loss if claim_status == CLAIM_STATUS_APPROVED else 0.0,
                "approval_reason": approval_reason,
                "can_payout": claim_status == CLAIM_STATUS_APPROVED,
                "message": f"📋 Claim {claim_status}: {approval_reason}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Approval failed: {str(e)}",
                "claim_id": claim_id,
                "claim_status": None,
            }
