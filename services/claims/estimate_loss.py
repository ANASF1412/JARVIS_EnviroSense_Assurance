"""
MODULE 5.5: LOSS ESTIMATION
Estimate income loss using ML model
"""
from typing import Dict, Any
from services.model_loader import ModelLoader


class LossEstimator:
    """Estimate income loss from disruption."""

    def __init__(self):
        """Initialize loss estimator."""
        self.model_loader = ModelLoader()

    def estimate_loss(self, disruption_hours: float,
                     hourly_income: float, weather_data: dict = None) -> Dict[str, Any]:
        """
        Estimate worker income loss from disruption with confidence scoring.

        ✅ ENTERPRISE FEATURE:
        - Accepts optional weather context for more accurate estimates
        - Returns confidence score
        - Shows model adjustment details
        - Always returns fallback value if model fails

        Args:
            disruption_hours: Number of hours of disruption
            hourly_income: Worker's average hourly income 
            weather_data: Optional dict with {"temperature": float, "rainfall_mm": float}

        Returns:
            Loss estimation result with confidence and details
        """
        try:
            # Validate inputs
            if disruption_hours <= 0 or hourly_income <= 0:
                return {
                    "success": False,
                    "error": "Invalid input values",
                    "estimated_loss": 0.0,
                    "confidence": 0.0
                }

            # Estimate loss using enhanced model that accepts weather data
            loss_result = self.model_loader.predict_income_loss(
                disruption_hours,
                hourly_income,
                weather_data  # Pass optional weather context
            )

            # Extract values
            estimated_loss = loss_result.get("loss", 0.0)
            confidence = loss_result.get("confidence", 0.5)
            baseline_loss = loss_result.get("baseline_loss", 0.0)
            multiplier = loss_result.get("model_adjustment_multiplier", 1.0)
            uses_weather = loss_result.get("uses_actual_weather", False)
            weather_context = loss_result.get("weather_context", {})

            # Validate the result
            if estimated_loss < 0:
                estimated_loss = baseline_loss

            return {
                "success": True,
                "estimated_loss": estimated_loss,
                "disruption_hours": disruption_hours,
                "hourly_income": hourly_income,
                "confidence": round(confidence, 4),
                "breakdown": {
                    "base_calculation": baseline_loss,
                    "model_adjusted": estimated_loss,
                    "adjustment_factor": round(multiplier, 4),
                },
                "uses_actual_weather": uses_weather,
                "weather_context": weather_context,
                "message": f"💰 Estimated loss: ₹{estimated_loss:.2f} ({disruption_hours}h × ₹{hourly_income}/h)",
                "confidence_level": "High" if confidence > 0.7 else ("Medium" if confidence > 0.4 else "Low")
            }

        except Exception as e:
            print(f"❌ Loss estimation error: {str(e)}")
            # Fallback to simple calculation
            baseline_loss = round(disruption_hours * hourly_income, 2)
            return {
                "success": True,  # Still successful with fallback
                "estimated_loss": baseline_loss,
                "disruption_hours": disruption_hours,
                "hourly_income": hourly_income,
                "confidence": 0.2,  # Very low confidence (using fallback)
                "breakdown": {
                    "base_calculation": baseline_loss,
                    "model_adjusted": baseline_loss,
                    "adjustment_factor": 1.0,
                },
                "uses_actual_weather": False,
                "weather_context": {},
                "message": f"💰 Estimated loss: ₹{baseline_loss:.2f} ({disruption_hours}h × ₹{hourly_income}/h)",
                "confidence_level": "Low",
                "warning": "Using baseline calculation - model unavailable"
            }
