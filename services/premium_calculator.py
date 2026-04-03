"""
MODULE 3: DYNAMIC PREMIUM CALCULATION
Calculate weekly premium based on AI risk assessment
"""
from typing import Dict, Any
from services.model_loader import ModelLoader
from config.settings import (
    PREMIUM_LOW_RISK,
    PREMIUM_MID_RISK,
    PREMIUM_HIGH_RISK,
)


class PremiumCalculator:
    """Calculate insurance premiums based on risk assessment."""

    def __init__(self):
        """Initialize premium calculator."""
        self.model_loader = ModelLoader()

    def calculate_premium(self, rainfall_mm: float, temperature: float,
                         aqi: float) -> Dict[str, Any]:
        """
        Calculate recommended premium based on weather/environmental conditions.
        
        ✅ ENTERPRISE FEATURE: Now returns rich analysis including:
        - Risk score with confidence
        - Contributing factors
        - Detailed factor impacts
        - Qualified recommendation with certainty
        """
        try:
            weather_data = {
                "rainfall_mm": rainfall_mm,
                "temperature": temperature,
                "aqi": aqi,
                "zone_risk": 1,
                "working_hours": 8
            }

            # Get rich risk assessment (now returns dict with confidence, factors, etc.)
            risk_result = self.model_loader.predict_risk(weather_data)

            if not risk_result.get("success"):
                return {
                    "success": False,
                    "error": "Risk prediction failed",
                    "risk_score": 0.5,
                    "confidence": 0.0,
                    "risk_level": "Medium",
                    "weekly_premium": PREMIUM_MID_RISK,
                    "ai_recommendation": "Unable to calculate - using default premium"
                }

            risk_score = risk_result["risk_score"]
            confidence = risk_result.get("confidence", 0.5)
            risk_class = risk_result.get("risk_class", "Unknown")
            contributing_factors = risk_result.get("contributing_factors", [])

            # Enhanced Dynamic Premium rules:
            # Smooth premium adjustment based on probability risk score instead of step jumps.
            base_premium_spread = PREMIUM_HIGH_RISK - PREMIUM_LOW_RISK
            continuous_premium = PREMIUM_LOW_RISK + (base_premium_spread * risk_score)
            
            # Historical risk multiplier logic
            historical_risk_multiplier = 1.05  # Slight markup for baseline model
            
            # Additional environmental severity adjustments
            if rainfall_mm > 100 or temperature > 42:
                historical_risk_multiplier *= 1.15
            
            # Adjusted continuous logic
            premium = continuous_premium * historical_risk_multiplier

            # Keep risk levels for UI 
            if risk_score < 0.33:
                risk_level = "Low"
            elif risk_score < 0.66:
                risk_level = "Medium"
            else:
                risk_level = "High"

            # Adjust premium slightly based on confidence (more certain → can price more precisely)
            # But cap adjustment to avoid extreme variations
            confidence_adjustment = 1.0 + (confidence - 0.5) * 0.1  # -5% to +5% adjustment
            adjusted_premium = round(premium * confidence_adjustment, 0)
            
            # Store base calculated before adjustment
            premium = round(continuous_premium, 0)

            # Generate qualified recommendation with confidence caveat
            ai_recommendation = self._get_recommendation(risk_score, adjusted_premium, confidence)

            return {
                "success": True,
                "risk_score": round(risk_score, 4),
                "confidence": round(confidence, 4),
                "risk_level": risk_level,
                "risk_class": risk_class,
                "weekly_premium": adjusted_premium,
                "base_premium": premium,
                "confidence_adjustment": round(confidence_adjustment, 4),
                "ai_recommendation": ai_recommendation,
                "contributing_factors": contributing_factors,
                "factor_impacts": risk_result.get("factor_impacts", {}),
                "probabilities": risk_result.get("probabilities", {}),
                "breakdown": {
                    "rainfall_factor": self._rainfall_impact(rainfall_mm),
                    "temperature_factor": self._temperature_impact(temperature),
                    "aqi_factor": self._aqi_impact(aqi),
                }
            }

        except Exception as e:
            print(f"❌ Premium calculation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Premium calculation failed: {str(e)}",
                "risk_score": 0.5,
                "confidence": 0.0,
                "risk_level": "Medium",
                "weekly_premium": PREMIUM_MID_RISK,
                "ai_recommendation": "Unable to calculate - using default premium"
            }

    def _get_recommendation(self, risk_score: float, premium: float, confidence: float) -> str:
        """
        Generate qualified AI recommendation based on risk score and confidence.
        
        ✅ NEW: Now includes confidence qualifier to manage expectations
        """
        confidence_qualifier = ""
        if confidence < 0.3:
            confidence_qualifier = " (⚠️ Low confidence - highly uncertain)"
        elif confidence < 0.5:
            confidence_qualifier = " (Medium confidence)"
        elif confidence > 0.8:
            confidence_qualifier = " (✅ High confidence - reliable estimate)"

        if risk_score < 0.33:
            return f"✅ Low Risk - Recommended Premium: ₹{premium}/week. Weather conditions are stable.{confidence_qualifier}"
        elif risk_score < 0.66:
            return f"⚠️ Medium Risk - Recommended Premium: ₹{premium}/week. Moderate disruption possible.{confidence_qualifier}"
        else:
            return f"🚨 High Risk - Recommended Premium: ₹{premium}/week. Severe conditions expected. Claims likely soon.{confidence_qualifier}"

    def _rainfall_impact(self, rainfall_mm: float) -> Dict[str, Any]:
        """Calculate rainfall impact on risk."""
        if rainfall_mm < 10:
            return {"level": "Low", "mm": rainfall_mm}
        elif rainfall_mm < 50:
            return {"level": "Medium", "mm": rainfall_mm}
        else:
            return {"level": "High", "mm": rainfall_mm, "warning": "Heavy rainfall triggered"}

    def _temperature_impact(self, temperature: float) -> Dict[str, Any]:
        """Calculate temperature impact on risk."""
        if temperature < 35:
            return {"level": "Low", "celsius": temperature}
        elif temperature < 42:
            return {"level": "Medium", "celsius": temperature}
        else:
            return {"level": "High", "celsius": temperature, "warning": "Extreme heat triggered"}

    def _aqi_impact(self, aqi: float) -> Dict[str, Any]:
        """Calculate AQI impact on risk."""
        if aqi < 200:
            return {"level": "Low", "aqi": aqi}
        elif aqi < 300:
            return {"level": "Medium", "aqi": aqi}
        else:
            return {"level": "High", "aqi": aqi, "warning": "Severe pollution triggered"}

    def get_premium_tier_info(self) -> Dict[str, Any]:
        """
        Get information about premium tiers.
        """
        return {
            "low_risk": {
                "risk_range": "< 0.3",
                "premium": PREMIUM_LOW_RISK,
                "description": "Stable weather conditions, low disruption risk"
            },
            "medium_risk": {
                "risk_range": "0.3 - 0.7",
                "premium": PREMIUM_MID_RISK,
                "description": "Moderate weather impacts expected"
            },
            "high_risk": {
                "risk_range": "> 0.7",
                "premium": PREMIUM_HIGH_RISK,
                "description": "Severe weather or environmental disruptions likely"
            }
        }