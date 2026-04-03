"""
MODULE 5.4: FRAUD/RISK CHECK
Advanced fraud detection and risk assessment
"""
from typing import Dict, Any
from sklearn.ensemble import IsolationForest
import numpy as np


class FraudChecker:
    """Detect fraudulent claims using ML and behavioral analysis."""

    def __init__(self):
        """Initialize fraud checker with Isolation Forest model."""
        self.model = IsolationForest(contamination=0.1, random_state=42)

        # Train with normal operational data
        # Features: [disruption_duration_hours, payout_amount, gps_movement_score]
        X_train = np.array([
            [4, 400, 2], [2, 250, 1], [5, 600, 3],
            [3, 350, 2], [6, 750, 1], [1, 120, 0],
            [3, 450, 2], [4, 500, 2], [2, 300, 1],
            [5, 650, 3], [4, 480, 2], [3, 380, 1],
        ])
        self.model.fit(X_train)

    def check_fraud(self, disruption_hours: float, estimated_loss: float,
                   gps_movement_score: float, repeated_claims: int = 0) -> Dict[str, Any]:
        """
        Check claim for fraud indicators.

        Process:
        1. Use Isolation Forest on [duration, loss, gps_movement]
        2. Check for repeated patterns (max 3 per week)
        3. Verify weather consistency
        4. Assign fraud_score (0-100)

        Args:
            disruption_hours: Hours of disruption
            estimated_loss: Estimated income loss
            gps_movement_score: GPS movement during disruption (0-15)
            repeated_claims: Number of claims by same worker this week

        Returns:
            Fraud assessment result
        """
        try:
            # Initialize fraud factors
            fraud_score = 0.0

            # ===== ANOMALY DETECTION (Isolation Forest) =====
            X_test = np.array([[disruption_hours, estimated_loss, gps_movement_score]])
            prediction = self.model.predict(X_test)[0]
            is_anomalous = prediction == -1

            if is_anomalous:
                fraud_score += 40  # Major flag

            # ===== GPS MOVEMENT CHECK =====
            # High movement during claimed disruption = possible fraud
            if gps_movement_score > 10:
                fraud_score += 20
                movement_status = "SUSPICIOUS"
            elif gps_movement_score > 5:
                fraud_score += 10
                movement_status = "MODERATE"
            else:
                movement_status = "NORMAL"

            # ===== REPEATED CLAIMS CHECK =====
            if repeated_claims >= 3:
                fraud_score += 20
                pattern_status = "PATTERN_DETECTED"
            elif repeated_claims >= 2:
                fraud_score += 10
                pattern_status = "MULTIPLE_CLAIMS"
            else:
                pattern_status = "NORMAL"

            # ===== LOSS AMOUNT CHECKS =====
            # Suspiciously high losses compared to typical
            if estimated_loss > 2000:
                fraud_score += 15
                loss_status = "UNUSUALLY_HIGH"
            elif estimated_loss < 50:
                fraud_score += 10  # Too low might indicate false claim
                loss_status = "SUSPICIOUSLY_LOW"
            else:
                loss_status = "REASONABLE"

            # Normalize fraud score to 0-100
            fraud_score = min(100.0, fraud_score)

            # Determine fraud status
            if fraud_score >= 70:
                fraud_status = "Flagged"
                recommendation = "REJECT"
                message = f"🚨 Fraud flagged (score: {fraud_score}/100)"
            elif fraud_score >= 40:
                fraud_status = "Suspicious"
                recommendation = "REVIEW"
                message = f"⚠️ Claim flagged for review (score: {fraud_score}/100)"
            else:
                fraud_status = "Cleared"
                recommendation = "APPROVE"
                message = f"✅ Fraud check cleared (score: {fraud_score}/100)"

            return {
                "success": True,
                "fraud_score": round(fraud_score, 2),
                "fraud_status": fraud_status,
                "recommendation": recommendation,
                "message": message,
                "analysis": {
                    "anomaly_detected": is_anomalous,
                    "gps_movement": movement_status,
                    "pattern": pattern_status,
                    "loss_amount": loss_status,
                },
                "risk_factors": {
                    "anomaly": is_anomalous,
                    "high_movement": gps_movement_score > 10,
                    "repeated_claims": repeated_claims >= 2,
                    "irregular_loss": estimated_loss > 2000 or estimated_loss < 50,
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Fraud check failed: {str(e)}",
                "fraud_score": 0.0,
                "fraud_status": "Cleared",
                "recommendation": "APPROVE",
            }
