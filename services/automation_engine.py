"""
Automation Engine — JARVIS EnviroSense Assurance
Zero-Touch Orchestrator: Sensor Pipeline -> Gating -> Integrity -> Payout
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import time
import random
import uuid

from services.repositories.policy_repository import PolicyRepository
from services.repositories.worker_repository import WorkerRepository
from services.repositories.claim_repository import ClaimRepository
from services.payout_engine import UnifiedPayoutEngine, InstantPayoutSimulator
from services.fraud_engine import FraudDetectionEngine
from services.claims.initiate_claim import ClaimInitiator
from services.environmental_api import EnvironmentalAPI

class AutomationEngine:
    def __init__(self):
        self.policy_repo = PolicyRepository()
        self.worker_repo = WorkerRepository()
        self.claim_repo = ClaimRepository()
        self.integrity_guard = FraudDetectionEngine()
        self.core_payout_engine = UnifiedPayoutEngine()
        self.payout_engine = InstantPayoutSimulator(self.core_payout_engine)
        self.claim_initiator = ClaimInitiator()

    def has_recent_claim_for_event(self, worker_id: str, event_type: str, zone_id: str = None) -> bool:
        """
        TEMPORAL IDEMPOTENCY: Query existing claims and block duplicates
        for the same worker and event type within the same calendar day.
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Get claims specifically for this worker
        worker_claims = self.claim_repo.get_worker_claims(worker_id, limit=50)
        
        for c in worker_claims:
            if c.get("event_type") == event_type:
                # Handle both datetime objects and ISO strings
                c_date = c.get("created_at")
                if isinstance(c_date, datetime):
                    c_date_str = c_date.strftime("%Y-%m-%d")
                elif isinstance(c_date, str):
                    c_date_str = c_date[:10]  # Get YYYY-MM-DD from ISO string
                else:
                    continue
                
                # Check zone match to be safe
                zone_match = True
                if zone_id and c.get("zone_id"):
                    zone_match = c.get("zone_id") == zone_id
                    
                if c_date_str == today_str and zone_match:
                    return True
                    
        return False

    def compute_zone_risk(self, zone_id: str) -> Dict[str, Any]:
        """ZONE RISK ENGINE: Computes dynamic risk index for a given zone."""
        claims = self.claim_repo.find_many({"zone_id": zone_id}, limit=100)
        
        # Get live environmental data for zone context
        env_data = EnvironmentalAPI.fetch_current_conditions()
        rainfall = env_data.get("rainfall_mm", 0)
        aqi = env_data.get("aqi", 0)
        
        if not claims:
            return {
                "index": 0.0, "level": "SAFE", "fraud_density": 0.0, "payout_volume": 0.0,
                "rainfall": rainfall, "aqi": aqi, "status_badge": "🟢 SAFE", "trend": "STABLE",
                "active_claims": 0, "payout_count": 0
            }
        
        fraud_count = sum(1 for c in claims if float(c.get("fraud_score", 0)) > 60.0 or c.get("status") in ("BLOCKED", "FLAGGED"))
        paid_claims = [c for c in claims if c.get("status") in ("PAID", "SUCCESS", "SETTLED_AFTER_REVIEW")]
        payout_vol = sum(float(c.get("payout_amount", c.get("amount", 0))) for c in paid_claims)
        
        density = fraud_count / len(claims)
        
        # Hyper-local intelligent formula incorporating weather and claim stats
        risk_index = (density * 100) + (payout_vol / 20000.0) + (rainfall / 10.0) + (aqi / 50.0)
        
        level = "WATCH" if risk_index > 20.0 else "SAFE"
        badge = "🟡 WATCH" if risk_index > 20.0 else "🟢 SAFE"
        if risk_index > 40.0:
            level = "CRITICAL"
            badge = "🔴 CRITICAL"
            
        trend = "ESCALATING" if len(claims) > 10 and risk_index > 25.0 else "STABLE"
            
        return {
            "index": round(risk_index, 2), 
            "level": level, 
            "fraud_density": round(density, 4), 
            "payout_volume": payout_vol,
            "payout_count": len(paid_claims),
            "active_claims": len(claims),
            "rainfall": rainfall,
            "aqi": aqi,
            "status_badge": badge,
            "trend": trend
        }

    def estimate_worker_loss(self, worker_id, zone_id, zone_risk_level=None):
        """Estimate payout based on worker profile + zone risk."""
        base_loss = 400.0
        try:
            worker = self.worker_repo.get_worker(worker_id)
            if worker:
                base_loss = worker.get("hourly_income", 40.0) * 8.0 
                if "avg_hourly_income" in worker: base_loss = worker["avg_hourly_income"] * 8.0
        except Exception:
            pass

        zone_multiplier = 1.0
        if zone_risk_level:
            level = zone_risk_level.upper()
            if level == "CRITICAL": zone_multiplier = 1.4
            elif level == "HIGH": zone_multiplier = 1.2
            elif level in ["WATCH", "MEDIUM"]: zone_multiplier = 1.1
        else:
            if zone_id and "HIGH" in zone_id.upper():
                zone_multiplier = 1.2

        return base_loss * zone_multiplier

    def get_recent_claims(self, worker_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Velocity Check: Get claims for a worker in the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        worker_claims = self.claim_repo.get_worker_claims(worker_id, limit=100)
        recent = []
        for c in worker_claims:
            c_date = c.get("created_at")
            if isinstance(c_date, str):
                try:
                    c_date = datetime.fromisoformat(c_date.replace("Z", "+00:00"))
                except Exception:
                    # fallback
                    c_date = datetime.now()
            if isinstance(c_date, datetime) and c_date >= cutoff:
                recent.append(c)
        return recent

    def pre_loop_fairness_gate(self, active_policies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        PRE-LOOP FAIRNESS GATE: Assessments pool exposure BEFORE execution.
        If total potential liability > 40% of pool, triggers SAFE_MODE to prevent insolvency.
        """
        total_liability = 0.0
        for policy in active_policies:
            w_id = policy["worker_id"]
            z_id = policy.get("delivery_zone", "South-Zone")
            z_level = self.compute_zone_risk(z_id)["level"]
            total_liability += self.estimate_worker_loss(w_id, z_id, z_level)
            
        current_pool_balance = float(self.core_payout_engine.pool_balance)
        max_allowed_payout = current_pool_balance * 0.40
        
        return {
            "mass_event_blocked": total_liability > max_allowed_payout,
            "total_liability": total_liability,
            "max_allowed": max_allowed_payout,
            "pool_balance": current_pool_balance
        }

    def simulate_mass_event(self, num_workers=50) -> Dict[str, Any]:
        """MASS SIMULATION ENGINE: Multi-threaded parallel risk stress testing."""
        start_time = time.time()
        blocked_count, payout_total = 0, 0.0
        all_claims = self.claim_repo.find_many({}, limit=100)
        for i in range(num_workers):
            uid = uuid.uuid4().hex[:6]
            claim = {
                "claim_id": f"CLM-STRESS-{uid}", "worker_id": f"WRK-{i}", "policy_id": f"POL-{i}",
                "estimated_loss": 480.0, "loyalty_score": random.uniform(0.7, 1.0),
                "gps": {"lat": 13.08, "lon": 80.27}, "reported_weather": {"rain_mm": 85.0}, "timestamp": datetime.now()
            }
            fraud = self.integrity_guard.analyze_claim(claim, {"gps_history": []}, {"sensor_weather": {"rain_mm": 85.0}}, all_claims)
            claim.update({"fraud_score": fraud["fraud_score"], "fraud_level": fraud["risk_level"]})
            if claim["fraud_score"] > 60:
                blocked_count += 1
                claim["status"] = "FLAGGED"
            else:
                p_res = self.payout_engine.core.process_payout(claim)
                if p_res.get("success"): payout_total += p_res.get("amount", 0)
            
            # Use appropriate persistence method
            if self.claim_repo.find_by_id(claim['claim_id'], id_field="claim_id"):
                self.claim_repo.update_claim(claim['claim_id'], **claim)
            else:
                self.claim_repo.create(claim)
        return {"total_processed": num_workers, "blocked_count": blocked_count, "payout_total": payout_total, "execution_time_ms": int((time.time() - start_time) * 1000)}

    def trigger_claims_for_event(self, rainfall_mm: float = 0, temperature: float = 0, aqi: float = 0) -> Dict[str, Any]:
        start_exec_time = time.time()
        if rainfall_mm == 0 and temperature == 0 and aqi == 0:
            env_data = EnvironmentalAPI.fetch_current_conditions("Chennai")
            if env_data.get("source") == "CRITICAL_SYSTEM_ERROR":
                 return {"success": False, "error": "SYSTEM_CRITICAL_FAILURE"}
            # PROCEED even if it is_real_data is False (it's using the local failsafe array)
            rainfall_mm, temperature, aqi = env_data["rainfall_mm"], env_data["temperature"], env_data["aqi"]
            alert_texts = env_data.get("alerts", [])
        else:
            alert_texts = []

        if rainfall_mm < 40 and temperature < 38 and aqi < 250 and not alert_texts:
            return {"success": True, "message": "Stable stats."}
        now = datetime.now()
        active_policies = self.policy_repo.find_many({
            "active_status": True,
            "start_date": {"$lte": now},
            "end_date": {"$gte": now}
        })
        all_claims = self.claim_repo.find_many({}, limit=100)
        payout_stats = {"blocked": 0, "safe": 0}

        target_event_type = "Autonomous Settlement"
        
        # --- PRE-LOOP LIABILITY CALCULATION (FAIRNESS GUARANTEE) ---
        fairness_results = self.pre_loop_fairness_gate(active_policies)
        mass_event_blocked = fairness_results["mass_event_blocked"]
        total_liability = fairness_results["total_liability"]
        
        anomaly_detected = False
        if rainfall_mm > 150 or aqi > 500:
            anomaly_detected = True
            
        global_log = ""
        if mass_event_blocked:
            global_log = "⚠️ Pool protection triggered — total liability exceeds 40%"
        elif anomaly_detected:
            global_log = "🚫 Circuit breaker — anomaly detected in environmental data"

        for policy in active_policies:
            worker_id = policy["worker_id"]
            zone_id = policy.get("delivery_zone", "South-Zone")
            
            # TEMPORAL IDEMPOTENCY RULE: Block duplicates
            if self.has_recent_claim_for_event(worker_id, target_event_type, zone_id=zone_id):
                payout_stats["blocked"] += 1
                today_str = datetime.now().strftime("%Y-%m-%d")
                print(f"Temporal Idempotency Blocked: worker {worker_id} already compensated for {target_event_type} on {today_str} in {zone_id}")
                continue

            audit_trail = [{"step": "trigger_fired", "ts": datetime.now().isoformat(), "narration": f"📡 **Sensor Guard:** Environmental threshold breach detected (R:{rainfall_mm}mm, T:{temperature}°C, A:{aqi})."}]
            init_res = self.claim_initiator.initiate_claim(policy_id=policy["policy_id"], worker_id=policy["worker_id"], event_type="Autonomous Settlement", trigger_conditions=f"Parametric Breach: R:{rainfall_mm}")
            if not init_res.get("success"): continue
            
            claim = self.claim_repo.get_claim(init_res["claim_id"])
            
            # --- ZONE RISK ENGINE ---
            zone_risk_state = self.compute_zone_risk(zone_id)
            zone_risk_high = zone_risk_state["level"] in ("WATCH", "CRITICAL")
            
            est_loss = self.estimate_worker_loss(worker_id, zone_id, zone_risk_state["level"])
            claim.update({"estimated_loss": est_loss, "city": policy.get("city", "Chennai"), "zone_id": zone_id, "loyalty_score": policy.get("loyalty_score", 0.92)})
            
            if zone_risk_high:
                audit_trail.append({"step": "zone_risk_high", "ts": datetime.now().isoformat(), "narration": f"⚠️ Zone Risk: {zone_risk_state['status_badge']} — stricter payout validation active"})

            # --- GLOBAL LIQUIDITY PROTECTION (KILL SWITCH) ---
            safe_mode_active = (
                mass_event_blocked
                or anomaly_detected
                or zone_risk_state["level"] == "CRITICAL"
            )
            # DO NOT spam log here. Only assign protection metadata.
            
            # --- STEP 3: VELOCITY + LIMITS ENFORCEMENT ---
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            recent_claims_7d = self.get_recent_claims(worker_id, days=7)
            
            today_claims = []
            daily_payout = 0.0
            for c in recent_claims_7d:
                c_d = c.get("created_at")
                c_d_str = c_d.strftime("%Y-%m-%d") if isinstance(c_d, datetime) else str(c_d)[:10]
                if c_d_str == today_str:
                    today_claims.append(c)
                    if c.get("status") == "PAID" or c.get("claim_status") == "Paid":
                        daily_payout += float(c.get("amount", c.get("payout_amount", c.get("approved_payout", 0.0))))
            
            claim_amount = claim["estimated_loss"]
            
            velocity_flag = False
            payout_abuse_flag = False
            daily_limit_flag = False
            fraud_reason_parts = []
            
            historical_7d = [c for c in recent_claims_7d if c.get("claim_id") != claim["claim_id"]]
            historical_today = [c for c in today_claims if c.get("claim_id") != claim["claim_id"]]
            
            if len(historical_7d) >= 3:
                velocity_flag = True
                fraud_reason_parts.append("Velocity Attack Detected: >3 claims in 7-day window")
                audit_trail.append({"step": "velocity_check", "ts": datetime.now().isoformat(), "narration": f"🚨 VELOCITY BLOCK: Worker {worker_id} exceeded 3 claims in 7 days"})
                
            if len(historical_today) >= 2:
                daily_limit_flag = True
                fraud_reason_parts.append("Daily Claim Limit Reached")
                audit_trail.append({"step": "daily_limit_check", "ts": datetime.now().isoformat(), "narration": f"🚨 DAILY LIMIT: Worker {worker_id} triggered >2 claims in one day"})
                
            if daily_payout + claim_amount > 2000.0:
                payout_abuse_flag = True
                fraud_reason_parts.append("Payout Threshold Exceeded (₹2000/day limit)")
                audit_trail.append({"step": "payout_throttle", "ts": datetime.now().isoformat(), "narration": f"🚨 PAYOUT THROTTLE: Worker {worker_id} attempted >₹2000 in 1 day"})
            
            # --- STEP 4: FRAUD ML SCORING (WITH RING DETECTION) ---
            audit_trail.append({"step": "integrity_scan", "ts": datetime.now().isoformat(), "narration": "🧠 **Integrity Guard:** Analyzing spatial signatures and behavioral patterns for fraud anomalies..."})
            fraud = self.integrity_guard.analyze_claim(claim, {"gps_history": []}, {"sensor_weather": {"rain_mm": rainfall_mm}}, all_claims)
            
            base_score = fraud["fraud_score"]
            final_score = base_score
            
            # REAL RING FRAUD BLOCKING
            ring_flag = False
            if fraud.get("signals", {}).get("ring_activity"):
                ring_flag = True
                final_score += 100
                fraud_reason_parts.append(f"Cluster attack blocked (Zone {zone_id})")
                audit_trail.append({"step": "ring_fraud_blocked", "ts": datetime.now().isoformat(), "narration": f"🚫 RING FRAUD DETECTED — Cluster attack blocked (Zone {zone_id})"})

            if velocity_flag:
                final_score += 30
            if payout_abuse_flag or daily_limit_flag:
                final_score += 25
            if zone_risk_high:
                final_score += 15 # Increase fraud sensitivity for High Risk Zones
                
            final_score = min(final_score, 100.0)
            
            claim.update({
                "fraud_score": final_score, 
                "fraud_level": "Critical" if final_score > 60 else fraud["risk_level"], 
                "fraud_explanation": " | ".join(fraud_reason_parts) if fraud_reason_parts else fraud["explanation"]
            })

            # --- STEP 5: FINAL DECISION THEN PAYOUT ---
            if safe_mode_active:
                claim["status"] = "REVIEW"
                
                if anomaly_detected:
                    claim["governance_status"] = "ANOMALY_BLOCK"
                elif mass_event_blocked:
                    claim["governance_status"] = "POOL_PROTECTION"
                else:
                    claim["governance_status"] = "SAFE_MODE"
                
                payout_stats["blocked"] += 1
            elif final_score > 60 or velocity_flag or ring_flag:
                claim["status"] = "BLOCKED" if (velocity_flag or ring_flag) else "FLAGGED"
                payout_stats["blocked"] += 1
                if ring_flag:
                    reason = "Ring Fraud Sync Detected"
                elif velocity_flag:
                    reason = "Velocity/Throttling Block"
                else:
                    reason = "Critical risk score detected"
                audit_trail.append({"step": "payout_blocked", "ts": datetime.now().isoformat(), "narration": f"❌ **Integrity Guard:** {reason}. Transaction suspended."})
            elif daily_limit_flag or payout_abuse_flag:
                claim["status"] = "REVIEW"
                payout_stats["blocked"] += 1
                audit_trail.append({"step": "payout_review", "ts": datetime.now().isoformat(), "narration": f"⚖️ **Integrity Guard:** Limit flag. Transaction sent for manual review."})
            else:
                audit_trail.append({"step": "behavior_engine", "ts": datetime.now().isoformat(), "narration": "📊 **Economic Core Intelligence:** Calculating adaptive trust factor and hyperlocal risk scaling..."})
                p_res = self.payout_engine.process_instant_payout(claim, policy, audit_trail=audit_trail, payout_abuse_flag=payout_abuse_flag)
                if p_res.get("success"): payout_stats["safe"] += 1

            claim["audit_trail"] = audit_trail
            claim["processing_time_ms"] = int((time.time() - start_exec_time) * 1000)
            self.claim_repo.update_claim(claim['claim_id'], **claim)

        # --- POST-LOOP GLOBAL LOG RECORDING ---
        if global_log:
            import logging
            logging.warning(global_log)
            # Extensible: Single persistent log trace can be added here if needed without repeating internally 

        return {"success": True, "execution_time_ms": int((time.time() - start_exec_time) * 1000), "payout_stats": payout_stats}
