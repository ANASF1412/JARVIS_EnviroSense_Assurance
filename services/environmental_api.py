"""
MODULE: ENVIRONMENTAL API
Pull environmental data using mock/public APIs (weather + AQI), checks for disruptions.
"""
import random
import datetime
from typing import Dict, Any, List

class EnvironmentalAPI:
    """Mock API layer for real-time environmental data pulling."""
    
    @staticmethod
    def fetch_current_conditions(location: str = "Bengaluru") -> Dict[str, Any]:
        """Fetch real-time weather and AQI data."""
        # Simulated api call
        return {
            "source": "MockWeatherAPI",
            "timestamp": datetime.datetime.now().isoformat(),
            "location": location,
            "temperature": random.uniform(25.0, 48.0),
            "rainfall_mm": random.uniform(0.0, 150.0),
            "aqi": random.uniform(50, 450),
            "alerts": EnvironmentalAPI._simulate_alerts()
        }

    @staticmethod
    def _simulate_alerts() -> List[str]:
        alerts = []
        if random.random() > 0.8:
            alerts.append("Severe weather warning: possible heavy rain")
        if random.random() > 0.9:
            alerts.append("Heatwave advisory in effect")
        return alerts

class DisruptionMonitor:
    """Scheduled or triggered checks for API data and disruption detection."""
    
    def __init__(self):
        from services.event_detector import EventDetector
        self.event_detector = EventDetector()
        self.api = EnvironmentalAPI()

    def run_check(self) -> Dict[str, Any]:
        """Run a single monitor check."""
        data = self.api.fetch_current_conditions()
        
        # Detect conditions
        detection_result = self.event_detector.detect_event(
            rainfall_mm=data["rainfall_mm"],
            temperature=data["temperature"],
            aqi=data["aqi"],
            alert_texts=data["alerts"]
        )
        
        return {
            "success": True,
            "environmental_data": data,
            "detection_result": detection_result,
            "disruption_detected": detection_result.get("event_detected", False)
        }
