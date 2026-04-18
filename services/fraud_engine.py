"""
fraud_engine.py
---------------
Advanced Fraud Detection Engine for JARVIS EnviroSense Assurance.
"""
from __future__ import annotations
import math
from datetime import datetime, timedelta, timezone
from typing import Any

GPS_DISPLACEMENT_HIGH_RISK_KM: float = 3.0
WEATHER_DELTA_THRESHOLD_MM: float = 15.0
VELOCITY_SUSPICIOUS_COUNT: int = 3
VELOCITY_HIGH_RISK_COUNT: int = 5
RING_TIME_WINDOW_MINUTES: int = 15
RING_RADIUS_KM: float = 0.5
RING_MIN_CLUSTER_SIZE: int = 5

SCORE_GPS_SPOOF: int = 35
SCORE_WEATHER_MISMATCH: int = 25
SCORE_VELOCITY_SUSPICIOUS: int = 10
SCORE_VELOCITY_HIGH_RISK: int = 20
SCORE_RING_ACTIVITY: int = 30

THRESHOLD_SAFE: int = 30
THRESHOLD_REVIEW: int = 60

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def _centroid(coords: list[tuple[float, float]]) -> tuple[float, float]:
    if not coords: return (0.0, 0.0)
    return (sum(c[0] for c in coords) / len(coords), sum(c[1] for c in coords) / len(coords))

def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)): return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    raise TypeError(f"Cannot parse datetime from type {type(value)}")

class FraudDetectionEngine:
    def analyze_claim(self, claim: dict, worker_history: dict, zone_data: dict, all_claims: list[dict] | None = None) -> dict:
        all_claims = all_claims or []
        gps_result = self.detect_gps_spoof(claim, worker_history)
        weather_result = self.detect_weather_mismatch(claim, zone_data)
        velocity_result = self.detect_claim_velocity(worker_history)
        ring_result = self.detect_ring_activity(all_claims, reference_claim=claim)

        signals = {"gps_spoof": gps_result["flagged"], "weather_mismatch": weather_result["flagged"], 
                   "high_velocity": velocity_result["flagged"], "ring_activity": ring_result["flagged"]}
        metrics = {"gps_distance_km": round(gps_result["distance_km"], 2), "weather_delta": round(weather_result["delta_mm"], 2),
                   "claims_last_24h": velocity_result["count"], "cluster_size": ring_result["cluster_size"]}

        score = self.compute_fraud_score(signals, velocity_result["count"])
        return {
            "claim_id": claim.get("claim_id", "unknown"), "worker_id": claim.get("worker_id", "unknown"),
            "fraud_score": score, "risk_level": self.get_fraud_decision(score),
            "signals": signals, "metrics": metrics, "explanation": self.generate_explanation(signals, metrics)
        }

    def compute_fraud_score(self, signals: dict, velocity_count: int = 0) -> int:
        total = 0
        if signals.get("gps_spoof"): total += SCORE_GPS_SPOOF
        if signals.get("weather_mismatch"): total += SCORE_WEATHER_MISMATCH
        if signals.get("high_velocity"):
            total += SCORE_VELOCITY_HIGH_RISK if velocity_count > VELOCITY_HIGH_RISK_COUNT else SCORE_VELOCITY_SUSPICIOUS
        if signals.get("ring_activity"): total += SCORE_RING_ACTIVITY
        return min(total, 100)

    def detect_gps_spoof(self, claim: dict, worker_history: dict) -> dict:
        gps = claim.get("gps", {})
        coords = [(float(p["lat"]), float(p["lon"])) for p in worker_history.get("gps_history", []) if "lat" in p and "lon" in p]
        if not coords: return {"flagged": False, "distance_km": 0.0}
        lat, lon = _centroid(coords)
        dist = _haversine_km(float(gps.get("lat", 0)), float(gps.get("lon", 0)), lat, lon)
        return {"flagged": dist > GPS_DISPLACEMENT_HIGH_RISK_KM, "distance_km": dist}

    def detect_weather_mismatch(self, claim: dict, zone_data: dict) -> dict:
        claimed = float(claim.get("reported_weather", {}).get("rain_mm", 0.0))
        actual = float(zone_data.get("sensor_weather", {}).get("rain_mm", 0.0))
        delta = abs(claimed - actual)
        return {"flagged": delta > WEATHER_DELTA_THRESHOLD_MM, "delta_mm": delta}

    def detect_claim_velocity(self, worker_history: dict) -> dict:
        now = datetime.now(tz=timezone.utc)
        count = sum(1 for c in worker_history.get("claims", []) if _parse_dt(c.get("timestamp", now)) >= (now - timedelta(hours=24)))
        return {"flagged": count > VELOCITY_SUSPICIOUS_COUNT, "count": count}

    def detect_ring_activity(self, all_claims: list[dict], reference_claim: dict | None = None) -> dict:
        if not all_claims: return {"flagged": False, "cluster_size": 0}
        ref_zone = (reference_claim or {}).get("zone_id")
        ref_id = (reference_claim or {}).get("claim_id")
        candidates = [c for c in all_claims if c.get("zone_id") == ref_zone] if ref_zone else all_claims
        
        # Use localized current time as default
        now_utc = datetime.now(tz=timezone.utc)
        
        max_c = []
        for p in candidates:
            # Fallback for timestamp field names
            p_ts_raw = p.get("timestamp") or p.get("created_at") or now_utc
            p_ts = _parse_dt(p_ts_raw)
            p_lat = float(p.get("gps", {}).get("lat") or p.get("lat") or 0.0)
            p_lon = float(p.get("gps", {}).get("lon") or p.get("lon") or 0.0)
            
            cl = []
            for c in candidates:
                c_ts_raw = c.get("timestamp") or c.get("created_at") or now_utc
                c_ts = _parse_dt(c_ts_raw)
                c_lat = float(c.get("gps", {}).get("lat") or c.get("lat") or 0.0)
                c_lon = float(c.get("gps", {}).get("lon") or c.get("lon") or 0.0)
                
                time_match = (p_ts - timedelta(minutes=RING_TIME_WINDOW_MINUTES)) <= c_ts <= (p_ts + timedelta(minutes=RING_TIME_WINDOW_MINUTES))
                dist_match = _haversine_km(p_lat, p_lon, c_lat, c_lon) <= RING_RADIUS_KM
                
                if time_match and dist_match:
                    cl.append(c.get("claim_id") or str(id(c)))
            
            if len(cl) > len(max_c): max_c = cl
            
        if ref_id and ref_id not in max_c: return {"flagged": False, "cluster_size": len(max_c)}
        return {"flagged": len(max_c) >= RING_MIN_CLUSTER_SIZE, "cluster_size": len(max_c)}

    def generate_explanation(self, signals: dict, metrics: dict) -> list[str]:
        exps = []
        if signals.get("gps_spoof"): exps.append(f"GPS displacement of {metrics.get('gps_distance_km')} km exceeds threshold.")
        if signals.get("weather_mismatch"): exps.append(f"Reported rainfall deviates {metrics.get('weather_delta')} mm from sensor data.")
        if signals.get("high_velocity"): exps.append(f"{metrics.get('claims_last_24h')} claims filed in 24h.")
        if signals.get("ring_activity"): exps.append(f"Cluster of {metrics.get('cluster_size')} claims detected.")
        return exps or ["No fraud signals detected."]

    def get_fraud_decision(self, score: int) -> str:
        if score <= THRESHOLD_SAFE: return "SAFE"
        if score <= THRESHOLD_REVIEW: return "REVIEW"
        return "FRAUD"
