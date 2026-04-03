"""
MODULE 5.7: PAYOUT PROCESSING
Process instant payouts for approved claims
"""
from typing import Dict, Any
from services.repositories.claim_repository import ClaimRepository
from services.repositories.payout_repository import PayoutRepository
from services.repositories.worker_repository import WorkerRepository
from config.settings import (
    CLAIM_STATUS_APPROVED,
    CLAIM_STATUS_PAID,
    PAYOUT_STATUS_COMPLETED,
)


class PayoutProcessor:
    """Process instant payouts for approved claims."""

    def __init__(self):
        """Initialize payout processor."""
        self.claim_repo = ClaimRepository()
        self.payout_repo = PayoutRepository()
        self.worker_repo = WorkerRepository()

    def process_payout(self, claim_id: str, approved_payout: float) -> Dict[str, Any]:
        """
        Process instant payout for approved claim.

        Process:
        1. Verify claim is approved
        2. Generate UPI transaction ID
        3. Create payout record
        4. Update claim status to "Paid"
        5. Update worker payout statistics

        Args:
            claim_id: Claim ID
            approved_payout: Approved payout amount

        Returns:
            Payout processing result
        """
        try:
            # Get claim details
            claim = self.claim_repo.get_claim(claim_id)
            if not claim:
                return {
                    "success": False,
                    "error": "Claim not found",
                    "payout_id": None,
                }

            # Verify claim is approved
            if claim["claim_status"] != CLAIM_STATUS_APPROVED:
                return {
                    "success": False,
                    "error": f"Claim status is {claim['claim_status']}, not {CLAIM_STATUS_APPROVED}",
                    "payout_id": None,
                }

            # Create payout record
            payout = self.payout_repo.create_payout(
                claim_id=claim_id,
                worker_id=claim["worker_id"],
                amount=approved_payout
            )

            payout_id = payout["payout_id"]

            # Generate UPI transaction ID
            upi_txn_id = self.payout_repo.generate_upi_txn_id()

            # Complete the payout (mark as completed)
            self.payout_repo.complete_payout(payout_id, upi_txn_id)

            # Update claim status to "Paid"
            self.claim_repo.update_claim_status(claim_id, CLAIM_STATUS_PAID)

            # Update worker payout statistics
            self.worker_repo.update_payouts(
                claim["worker_id"],
                approved_payout
            )

            return {
                "success": True,
                "payout_id": payout_id,
                "claim_id": claim_id,
                "worker_id": claim["worker_id"],
                "amount": approved_payout,
                "upi_txn_id": upi_txn_id,
                "status": PAYOUT_STATUS_COMPLETED,
                "message": f"✅ Payout processed! ₹{approved_payout} credited via {upi_txn_id}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Payout processing failed: {str(e)}",
                "payout_id": None,
            }

    def get_payout_status(self, payout_id: str) -> Dict[str, Any]:
        """Get payout status."""
        payout = self.payout_repo.get_payout(payout_id)
        if not payout:
            return {"error": "Payout not found"}
        return payout
