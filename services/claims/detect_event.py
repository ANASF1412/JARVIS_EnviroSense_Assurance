"""
MODULE 5.1: EVENT DETECTION (Claim Init)
Detect event and prepare for claim creation
"""
from typing import Dict, Any, List
from services.event_detector import EventDetector


class ClaimEventDetector:
    """Detect events for claim initiation."""

    def __init__(self):
        """Initialize claim event detector."""
        self.event_detector = EventDetector()

    def detect_event_for_claim(self, rainfall_mm: float, temperature: float,
                              aqi: float, alert_texts: List[str] = None) -> Dict[str, Any]:
        """
        Detect event that triggers claim.

        Args:
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            aqi: Air Quality Index
            alert_texts: Optional alert texts

        Returns:
            Event detection result
        """
        result = self.event_detector.detect_event(
            rainfall_mm=rainfall_mm,
            temperature=temperature,
            aqi=aqi,
            alert_texts=alert_texts
        )

        return result
