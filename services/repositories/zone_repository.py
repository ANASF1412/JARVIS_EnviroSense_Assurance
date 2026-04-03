"""
Zone Repository - CRUD operations for delivery zones and risk data
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from services.repositories.base_repository import BaseRepository


class ZoneRepository(BaseRepository):
    """Repository for zone management."""

    def __init__(self):
        """Initialize zone repository."""
        super().__init__("zones")

    def create_zone(self, zone_name: str, city: str,
                   historical_risk_score: float) -> Dict[str, Any]:
        """
        Create new zone.

        Args:
            zone_name: Zone name
            city: City name
            historical_risk_score: Historical risk score (0-1)

        Returns:
            Created zone document
        """
        zone = {
            "zone_name": zone_name,
            "city": city,
            "historical_risk_score": max(0.0, min(1.0, historical_risk_score)),
            "last_updated": datetime.now(),
        }

        self.create(zone)
        return zone

    def get_zone(self, zone_name: str) -> Optional[Dict[str, Any]]:
        """
        Get zone by name.

        Args:
            zone_name: Zone name

        Returns:
            Zone document or None
        """
        return self.find_one({"zone_name": zone_name})

    def get_zones_by_city(self, city: str) -> List[Dict[str, Any]]:
        """
        Get all zones in a city.

        Args:
            city: City name

        Returns:
            List of zone documents
        """
        return self.find_many({"city": city})

    def get_all_zones(self) -> List[Dict[str, Any]]:
        """
        Get all zones.

        Returns:
            List of all zones
        """
        return self.find_all()

    def update_risk_score(self, zone_name: str, risk_score: float) -> bool:
        """
        Update zone risk score.

        Args:
            zone_name: Zone name
            risk_score: New risk score (0-1)

        Returns:
            True if successful
        """
        risk_score = max(0.0, min(1.0, risk_score))
        return self.update_by_id(
            zone_name,
            {
                "historical_risk_score": risk_score,
                "last_updated": datetime.now()
            },
            id_field="zone_name"
        )

    def get_risk_level(self, zone_name: str) -> Optional[str]:
        """
        Get risk level for a zone.

        Args:
            zone_name: Zone name

        Returns:
            Risk level ("Low", "Medium", "High") or None
        """
        zone = self.get_zone(zone_name)
        if not zone:
            return None

        score = zone.get("historical_risk_score", 0.5)
        if score < 0.33:
            return "Low"
        elif score < 0.67:
            return "Medium"
        else:
            return "High"

    def get_high_risk_zones(self) -> List[Dict[str, Any]]:
        """
        Get all high-risk zones.

        Returns:
            List of zones with risk > 0.66
        """
        return self.find_many({"historical_risk_score": {"$gt": 0.66}})

    def get_medium_risk_zones(self) -> List[Dict[str, Any]]:
        """
        Get all medium-risk zones.

        Returns:
            List of zones with risk 0.33-0.66
        """
        return self.find_many({
            "historical_risk_score": {"$gte": 0.33, "$lte": 0.66}
        })

    def get_low_risk_zones(self) -> List[Dict[str, Any]]:
        """
        Get all low-risk zones.

        Returns:
            List of zones with risk < 0.33
        """
        return self.find_many({"historical_risk_score": {"$lt": 0.33}})

    def delete_zone(self, zone_name: str) -> bool:
        """
        Delete zone.

        Args:
            zone_name: Zone name

        Returns:
            True if successful
        """
        return self.delete({"zone_name": zone_name})

    def zone_exists(self, zone_name: str) -> bool:
        """
        Check if zone exists.

        Args:
            zone_name: Zone name

        Returns:
            True if zone exists
        """
        return self.exists({"zone_name": zone_name})

    def get_zone_stats(self) -> Dict[str, Any]:
        """
        Get zone statistics.

        Returns:
            Statistics dictionary
        """
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_zones": {"$sum": 1},
                    "avg_risk": {"$avg": "$historical_risk_score"},
                    "max_risk": {"$max": "$historical_risk_score"},
                    "min_risk": {"$min": "$historical_risk_score"},
                }
            }
        ]

        result = self.aggregate(pipeline)
        if result:
            stats = result[0]
            stats.pop("_id", None)
            return stats

        return {
            "total_zones": 0,
            "avg_risk": 0.0,
            "max_risk": 0.0,
            "min_risk": 0.0,
        }

    def get_zones_by_risk_level(self, level: str) -> List[Dict[str, Any]]:
        """
        Get zones by risk level.

        Args:
            level: Risk level ("Low", "Medium", "High")

        Returns:
            List of zones
        """
        if level.lower() == "low":
            return self.get_low_risk_zones()
        elif level.lower() == "medium":
            return self.get_medium_risk_zones()
        elif level.lower() == "high":
            return self.get_high_risk_zones()
        else:
            return []
