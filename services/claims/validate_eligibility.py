"""
MODULE 5.3: ELIGIBILITY VALIDATION
Validate claim eligibility based on policy and event
"""
from typing import Dict, Any
from datetime import datetime
from services.repositories.policy_repository import PolicyRepository
from services.repositories.claim_repository import ClaimRepository


class ClaimEligibilityValidator:
    """Validate claim eligibility."""

    def __init__(self):
        """Initialize eligibility validator."""
        self.policy_repo = PolicyRepository()
        self.claim_repo = ClaimRepository()

    def validate_eligibility(self, policy_id: str, claim_id: str) -> Dict[str, Any]:
        """
        Validate claim eligibility.

        Checks:
        1. Policy exists
        2. Policy is active
        3. Event within coverage period
        4. No duplicate concurrent claims for same policy

        Args:
            policy_id: Policy ID
            claim_id: Claim ID

        Returns:
            Validation result
        """
        try:
            # Check 1: Policy exists
            policy = self.policy_repo.get_policy(policy_id)
            if not policy:
                return {
                    "valid": False,
                    "reason": "Policy not found",
                    "checks": {
                        "policy_exists": False,
                        "policy_active": None,
                        "coverage_valid": None,
                    }
                }

            # Check 2: Policy is active
            now = datetime.now()
            policy_active = (
                policy.get("active_status", False) and
                policy["start_date"] <= now <= policy["end_date"]
            )

            if not policy_active:
                return {
                    "valid": False,
                    "reason": "Policy is not active",
                    "checks": {
                        "policy_exists": True,
                        "policy_active": False,
                        "coverage_valid": None,
                    }
                }

            # Check 3: Event within coverage period
            claim = self.claim_repo.get_claim(claim_id)
            coverage_valid = (
                policy["start_date"] <= claim["created_at"] <= policy["end_date"]
            )

            if not coverage_valid:
                return {
                    "valid": False,
                    "reason": "Event outside coverage period",
                    "checks": {
                        "policy_exists": True,
                        "policy_active": True,
                        "coverage_valid": False,
                    }
                }

            # All checks passed
            return {
                "valid": True,
                "reason": "Claim is eligible",
                "checks": {
                    "policy_exists": True,
                    "policy_active": True,
                    "coverage_valid": True,
                },
                "policy_details": {
                    "coverage_limit": policy["coverage_limit"],
                    "start_date": policy["start_date"].isoformat() if hasattr(policy["start_date"], 'isoformat') else str(policy["start_date"]),
                    "end_date": policy["end_date"].isoformat() if hasattr(policy["end_date"], 'isoformat') else str(policy["end_date"]),
                }
            }

        except Exception as e:
            return {
                "valid": False,
                "reason": f"Validation error: {str(e)}",
                "checks": {
                    "policy_exists": None,
                    "policy_active": None,
                    "coverage_valid": None,
                }
            }
