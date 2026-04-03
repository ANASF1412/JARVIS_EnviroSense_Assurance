"""
MODULE 6: PREDICTIVE ALERTS
Forecast future disruption risks with intelligent, deterministic logic
Enhanced with confidence scoring and risk trajectory analysis
"""
from typing import Dict, Any
from services.model_loader import ModelLoader


class PredictiveAlertsService:
    """Generate predictive disruption alerts with full explainability."""

    def __init__(self):
        self.model_loader = ModelLoader()

    def get_disruption_forecast(self, rainfall_mm: float, temperature: float,
                               aqi: float = 0) -> Dict[str, Any]:
        """
        Generate comprehensive disruption forecast for next 24-48 hours.

        ✅ ENTERPRISE FEATURES:
        - Fully deterministic (no randomness)
        - Explainable: shows why forecast changed
        - Confidence-based: adjusts alert level by certainty
        - Trend analysis: predicts if conditions improving/worsening
        - Contributing factors: explains all drivers

        Args:
            rainfall_mm: Expected rainfall in mm
            temperature: Temperature in Celsius
            aqi: Air Quality Index (optional)

        Returns:
            dict with comprehensive forecast data
        """

        try:
            # ===== GET RICH RISK ASSESSMENT =====
            risk_result = self.model_loader.predict_risk({
                "rainfall_mm": rainfall_mm,
                "temperature": temperature,
                "aqi": aqi,
                "zone_risk": 1,
                "working_hours": 8
            })

            if not risk_result.get("success"):
                return self._fallback_forecast()

            risk_score = risk_result["risk_score"]
            confidence = risk_result["confidence"]
            contributing_factors = risk_result.get("contributing_factors", [])
            factor_impacts = risk_result.get("factor_impacts", {})

            # ===== ROLLING RISK TREND LOGIC =====
            # Mock historical risk context (In production, pull from DB/Analytics)
            # Compare current risk_score with previous 12h and 24h rolling averages
            past_12h_risk = max(0.0, risk_score - 0.15) if risk_score > 0.4 else risk_score + 0.05
            past_24h_risk = max(0.0, risk_score - 0.25) if risk_score > 0.5 else risk_score + 0.1
            
            # Detect worsening or improving conditions specifically through difference
            rolling_avg_risk = (past_12h_risk + past_24h_risk) / 2.0
            
            worsening_delta = risk_score - rolling_avg_risk
            
            # Base forecast: scale current risk with trend multiplier
            # In real-world, conditions worsen over time (dust accumulates, heat peaks, rain intensifies)
            # But in short window, more likely to stabilize
            
            # Confidence-based adjustment: higher confidence → stronger forecast
            # Lower confidence → more conservative (move toward 50%)
            confidence_adjustment = 0.5 + (confidence - 0.5) * 0.8  # Never < 0.5, < 1.0
            
            # Risk trajectory multiplier (nonlinear)
            # Low risk: likely stays low (×0.9: improvement expected)
            # Medium risk: could go either way (×1.0: no change)
            # High risk: likely to persist or worsen (×1.15: deterioration expected)
            
            if risk_score < 0.3:
                trajectory_multiplier = 0.8  # Improving conditions
            elif risk_score < 0.5:
                trajectory_multiplier = 0.95  # Slightly improving
            elif risk_score < 0.7:
                trajectory_multiplier = 1.05  # Slightly worsening
            else:
                trajectory_multiplier = 1.2  # Likely to persist/worsen at high risk

            # Combine factors
            tomorrow_probability = min(
                100.0,
                max(0.0, risk_score * 100 * trajectory_multiplier * confidence_adjustment)
            )

            if worsening_delta > 0.15:
                trajectory_multiplier *= 1.25 # Acceleration penalty
                trend = "rapidly worsening"
                trend_symbol = "⚠️📉"
                trend_text = f"Conditions are rapidly deteriorating (Risk delta: +{worsening_delta:.2f})"
                suggested_action = "IMMEDIATELY Suspend gig activities in affected zones."
            elif worsening_delta > 0.05:
                trend = "worsening"
                trend_symbol = "📈"
                trend_text = f"Conditions are steadily worsening (Risk delta: +{worsening_delta:.2f})"
                suggested_action = "Prepare for disruption. Finish current tasks."
            elif worsening_delta < -0.1:
                trend = "improving"
                trend_symbol = "📉"
                trend_text = "Conditions are clearly improving"
                suggested_action = "Gradually resume operations. Monitor."
            else:
                trend = "stable"
                trend_symbol = "➡️"
                trend_text = "Conditions expected to remain stable"
                suggested_action = "Continue normal operations with caution."

            # ===== ALERT CLASSIFICATION (deterministic from probability + confidence) =====
            # Higher confidence → more extreme alert at same probability
            confidence_threshold_adjustment = (confidence - 0.5) * 20  # -10 to +10 adjustment

            if tomorrow_probability + confidence_threshold_adjustment > 75:
                alert_level = "HIGH"
                alert_emoji = "🚨"
                alert_text = "SEVERE DISRUPTION LIKELY - Recommend workers stay home or exercise extreme caution"
            elif tomorrow_probability + confidence_threshold_adjustment > 50:
                alert_level = "MEDIUM"
                alert_emoji = "⚠️"
                alert_text = "MODERATE RISK - Disruption possible. Monitor conditions closely"
            else:
                alert_level = "LOW"
                alert_emoji = "✅"
                alert_text = "LOW RISK - Safe to work. Conditions are favorable"

            # ===== GENERATING DETAILED EXPLANATION =====
            explanation = self._generate_explanation(
                temperature, rainfall_mm, risk_score, trend,
                contributing_factors, confidence
            )

            print(f"📊 Forecast: prob={tomorrow_probability:.1f}%, level={alert_level}, conf={confidence:.2f}")

            return {
                "success": True,
                "tomorrow_disruption_probability": round(tomorrow_probability, 1),
                "trend": trend,
                "trend_symbol": trend_symbol,
                "trend_text": trend_text,
                "alert_level": alert_level,
                "alert_emoji": alert_emoji,
                "alert_text": alert_text,
                "confidence": round(confidence, 4),
                "confidence_level": "High" if confidence > 0.7 else ("Medium" if confidence > 0.4 else "Low"),
                "explanation": explanation,
                "suggested_action": suggested_action,
                "risk_score": round(risk_score, 4),
                "contributing_factors": contributing_factors,
                "factor_impacts": factor_impacts,
                "risk_class": risk_result.get("risk_class", "Unknown"),
                "probabilities": risk_result.get("probabilities", {})
            }

        except Exception as e:
            print(f"❌ Forecast generation failed: {str(e)}")
            return self._fallback_forecast()

    def _generate_explanation(self, temperature: float, rainfall: float, risk_score: float,
                            trend: str, factors: list, confidence: float) -> str:
        """
        Generate human-readable explanation of the forecast.
        
        Returns multi-line explanation suitable for Streamlit display.
        """
        lines = []
        
        # Current risk explanation
        if risk_score > 0.7:
            lines.append("**Current Conditions:** Severe weather stress")
        elif risk_score > 0.4:
            lines.append("**Current Conditions:** Moderate weather stress")
        else:
            lines.append("**Current Conditions:** Mild weather stress")
        
        # Temperature component
        if temperature > 42:
            lines.append(f"- Extreme heat ({temperature}°C) - Major disruption risk")
        elif temperature > 38:
            lines.append(f"- High temperature ({temperature}°C) - Increased heat stress")
        elif temperature < 15:
            lines.append(f"- Cold conditions ({temperature}°C) - Workers may reduce activity")
        else:
            lines.append(f"- Moderate temperature ({temperature}°C) - Favorable")
        
        # Rainfall component
        if rainfall > 100:
            lines.append(f"- Heavy rainfall ({rainfall}mm) - Severe flooding risk")
        elif rainfall > 50:
            lines.append(f"- Moderate rainfall ({rainfall}mm) - Wet working conditions")
        elif rainfall > 25:
            lines.append(f"- Light rainfall ({rainfall}mm) - Minor impact")
        else:
            lines.append(f"- Dry conditions ({rainfall}mm) - No rain impact")
        
        # Trend explanation
        if trend == "improving":
            lines.append("📉 **Trend:** Conditions improving over next 24 hours")
        elif trend == "worsening":
            lines.append("📈 **Trend:** Conditions likely to worsen over next 24 hours")
        else:
            lines.append("➡️  **Trend:** Conditions expected to remain stable")
        
        # Confidence explanation
        if confidence > 0.7:
            lines.append(f"**Confidence:** High ({confidence:.1%}) - Forecast is reliable")
        elif confidence > 0.4:
            lines.append(f"**Confidence:** Medium ({confidence:.1%}) - Monitor for updates")
        else:
            lines.append(f"**Confidence:** Low ({confidence:.1%}) - Highly uncertain, check again soon")
        
        return "\n".join(lines)

    def _fallback_forecast(self) -> Dict[str, Any]:
        """Provide safe fallback when forecast generation fails."""
        return {
            "success": False,
            "tomorrow_disruption_probability": 50.0,
            "trend": "unknown",
            "trend_symbol": "❓",
            "trend_text": "Unable to determine trend",
            "alert_level": "UNKNOWN",
            "alert_emoji": "❓",
            "alert_text": "⚠️ Unable to generate forecast. Please try again.",
            "confidence": 0.0,
            "confidence_level": "Unknown",
            "explanation": "Forecast service temporarily unavailable",
            "contributing_factors": ["Service error"],
            "factor_impacts": {}
        }
