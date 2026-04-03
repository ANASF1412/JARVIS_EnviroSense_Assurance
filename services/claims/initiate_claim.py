"""
MODULE 5.2: CLAIM INITIATION
Create and initiate new insurance claim
"""
from typing import Dict, Any, List
from datetime import datetime
from services.repositories.claim_repository import ClaimRepository
from config.settings import CLAIM_STATUS_INITIAL


class ClaimInitiator:
    """Initiate new insurance claims."""

    def __init__(self):
        """Initialize claim initiator."""
        self.claim_repo = ClaimRepository()

    def initiate_claim(self, policy_id: str, worker_id: str, event_type: str,
                      trigger_conditions: List[str]) -> Dict[str, Any]:
        """
        Initiate a new claim in "Initiated" status.

        Process:
        1. Create claim_id
        2. Set status = "Initiated"
        3. Link to policy and worker
        4. Store in database

        Args:
            policy_id: Policy ID
            worker_id: Worker ID
            event_type: Type of event
            trigger_conditions: List of triggered conditions

        Returns:
            Initiated claim response
        """
        try:
            # Create claim
            claim = self.claim_repo.create_claim(
                policy_id=policy_id,
                worker_id=worker_id,
                event_type=event_type,
                trigger_conditions=trigger_conditions
            )

            return {
                "success": True,
                "claim_id": claim["claim_id"],
                "message": f"✅ Claim {claim['claim_id']} initiated",
                "claim": claim,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Claim initiation failed: {str(e)}",
                "claim_id": None,
            }

    def get_claim(self, claim_id: str) -> Dict[str, Any] | None:
        """Get claim details."""
        return self.claim_repo.get_claim(claim_id)
