"""
MODULE 7: ZONE RISK DISPLAY
Show area-based risk assessments
"""
from typing import Dict, Any, List
from services.repositories.zone_repository import ZoneRepository


class ZoneRiskService:
    """Manage zone risk information."""

    def __init__(self):
        """Initialize zone risk service."""
        self.zone_repo = ZoneRepository()

    def get_zone_risk(self, zone_name: str) -> Dict[str, Any]:
        """
        Get risk assessment for a specific zone.

        Args:
            zone_name: Name of the zone

        Returns:
            Zone risk information
        """
        try:
            zone = self.zone_repo.get_zone(zone_name)
            if not zone:
                return {
                    "success": False,
                    "error": f"Zone '{zone_name}' not found"
                }

            risk_level = self.zone_repo.get_risk_level(zone_name)
            risk_score = zone.get("historical_risk_score", 0.5)

            return {
                "success": True,
                "zone_name": zone_name,
                "city": zone.get("city"),
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_description": self._get_risk_description(risk_level),
                "last_updated": zone.get("last_updated"),
                "alert_status": "🟢 Safe" if risk_level == "Low" else (
                    "🟡 Caution" if risk_level == "Medium" else "🔴 Warning"
                )
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Zone risk lookup failed: {str(e)}"
            }

    def get_all_zones_risk(self) -> Dict[str, Any]:
        """
        Get risk assessment for all zones.

        Returns:
            All zones with risk information
        """
        try:
            zones = self.zone_repo.get_all_zones()
            zone_risks = []

            for zone in zones:
                risk_level = self.zone_repo.get_risk_level(zone["zone_name"])
                zone_risks.append({
                    "zone_name": zone["zone_name"],
                    "city": zone.get("city"),
                    "risk_score": zone.get("historical_risk_score", 0.5),
                    "risk_level": risk_level,
                })

            stats = self.zone_repo.get_zone_stats()

            return {
                "success": True,
                "total_zones": len(zones),
                "zones": zone_risks,
                "statistics": stats,
                "high_risk_zones": [z["zone_name"] for z in zone_risks if z["risk_level"] == "High"],
                "medium_risk_zones": [z["zone_name"] for z in zone_risks if z["risk_level"] == "Medium"],
                "low_risk_zones": [z["zone_name"] for z in zone_risks if z["risk_level"] == "Low"],
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"All zones query failed: {str(e)}"
            }

    def get_high_risk_zones(self) -> List[Dict[str, Any]]:
        """Get all high-risk zones."""
        return self.zone_repo.get_high_risk_zones()

    def get_risk_level_distribution(self) -> Dict[str, int]:
        """Get count of zones by risk level."""
        zones = self.zone_repo.get_all_zones()
        distribution = {"Low": 0, "Medium": 0, "High": 0}

        for zone in zones:
            risk_level = self.zone_repo.get_risk_level(zone["zone_name"])
            distribution[risk_level] = distribution.get(risk_level, 0) + 1

        return distribution

    def _get_risk_description(self, risk_level: str) -> str:
        """Get description for risk level."""
        if risk_level == "Low":
            return "Safe for delivery operations. Weather conditions stable."
        elif risk_level == "Medium":
            return "Moderate risk. Monitor conditions. Claims likely."
        else:
            return "High risk. Severe disruptions expected. Many claims anticipated."
