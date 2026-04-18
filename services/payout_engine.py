"""
Unified Payout Engine — JARVIS EnviroSense Assurance
Infrastructure Layer: Liquidity protection, Solvency Caps, and Adaptive Learning.
"""
import time
import hashlib
import threading
import uuid
import os
import json
import random
from typing import Dict, Any, List
from datetime import datetime

class UnifiedPayoutEngine:
    """Atomic financial engine with built-in idempotency and solvency gating."""

    def __init__(self, claim_repo=None, payout_repo=None, activity_feed=None):
        self._lock = threading.Lock()
        self._processed_ids = set()
        self.pool_initial = 1000000.0
        self.pool_balance = 1000000.0
        self.max_exposure_per_claim = 0.05
        self.system_confidence_eci = 0.82
        self.avg_latency_ms = 312
        self.today_payout_total = 0.0
        self.last_10_payouts = []

    def calculate_adaptive_eci(self):
        if not self.last_10_payouts: return 0.82
        avg_fraud = sum(p[1] for p in self.last_10_payouts) / len(self.last_10_payouts)
        new_eci = max(0.6, min(0.95, 1.0 - (avg_fraud / 150.0)))
        self.system_confidence_eci = round(new_eci, 3)
        return self.system_confidence_eci

    def generate_system_proof(self):
        """REAL-TIME BACKEND TELEMETRY FOR UI."""
        with self._lock:
            exposure_pct = (self.today_payout_total / self.pool_initial) * 100
            eci = self.calculate_adaptive_eci()
            return {
                "idempotency": "ACTIVE / GUARDED",
                "liquidity": f"₹{self.pool_balance:,.0f}",
                "pool_balance_raw": self.pool_balance,
                "solvency": "OPTIMAL" if exposure_pct < 5 else "STRESSED",
                "status_msg": "⚠️ STRESS MODE ACTIVE (20% reduction)" if exposure_pct > 5.0 else "✅ POOL HEALTH OPTIMAL",
                "eci": eci,
                "latency": f"{self.avg_latency_ms}ms",
                "today_exposure": f"₹{self.today_payout_total:,.0f}",
                "exposure_pct": exposure_pct,
                "max_allowed": "5.0%",
                "memory_size": len(self.last_10_payouts),
                "avg_payout": round(sum(p[0] for p in self.last_10_payouts) / max(1, len(self.last_10_payouts)), 2)
            }

    def calculate_payout_math(self, claim: Dict[str, Any]):
        base = float(claim.get("estimated_loss", 480))
        trust_mult = 1.05 if float(claim.get("loyalty_score", 0.92)) > 0.8 else 1.0
        eci_factor = 1.0 if self.system_confidence_eci > 0.8 else 0.95
        liq_factor = 0.8 if (self.today_payout_total / self.pool_initial) * 100 > 5.0 else 1.0
        
        # Hyperlocal Zone Intelligence
        zone_risk = float(claim.get("zone_risk", 1.0))
        zone_mult = 1.1 if zone_risk > 0.8 else 1.0
            
        subtotal = base * trust_mult * eci_factor * liq_factor * zone_mult
        liq_limit = self.pool_balance * self.max_exposure_per_claim
        final = round(min(subtotal, liq_limit))
        
        math_dna = f"Base({int(base)}) \u00d7 Trust({trust_mult}) \u00d7 ECI({eci_factor}) \u00d7 Liq({liq_factor}) \u00d7 Zone({zone_mult})"
        stress_msg = "⚠️ Liquidity stress detected \u2192 intensity reduction applied" if liq_factor < 1.0 else ""
        return final, math_dna, stress_msg

    def process_payout(self, claim: Dict[str, Any], audit_trail: List = None, delay: bool = False) -> Dict[str, Any]:
        claim_id = claim.get("claim_id")
        with self._lock:
            if claim_id in self._processed_ids:
                return {"success": True, "message": "IDEMPOTENT_SKIP"}
            final_amt, math_dna, stress_msg = self.calculate_payout_math(claim)
            if final_amt > self.pool_balance or final_amt <= 0:
                return {"success": False, "reason": "SAFETY_LOCK_VOOL_INSOLVENT"}
            self._processed_ids.add(claim_id)

        t_start = time.time()
        time.sleep(0.4)
        txn_id = f"rzp_pay_{hashlib.sha256(claim_id.encode()).hexdigest()[:14]}"
        
        with self._lock:
            self.pool_balance -= final_amt
            self.today_payout_total += final_amt
            self.last_10_payouts.append((final_amt, float(claim.get("fraud_score", 0))))
            if len(self.last_10_payouts) > 10: self.last_10_payouts.pop(0)
            self.avg_latency_ms = int((self.avg_latency_ms * 0.8) + (int((time.time() - t_start) * 1000) * 0.2))
            
            claim.update({
                "status": "PAID" if not delay else "SETTLED_AFTER_REVIEW",
                "payout_ref": txn_id, "payout_math": math_dna, "payout_amount": final_amt,
                "decision_confidence": (100 - float(claim.get("fraud_score", 0))) * 0.7 + (float(claim.get("loyalty_score", 0.92)) * 30),
                "processing_time_ms": int((time.time() - t_start) * 1000), "stress_response": stress_msg
            })
            if audit_trail is not None:
                if stress_msg: audit_trail.append({"step": "liquidity_guard", "ts": datetime.now().isoformat(), "narration": f"\ud83d\udcb8 {stress_msg}"})
                audit_trail.append({"step": "payout_settlement", "ts": datetime.now().isoformat(), "narration": f"\u2705 Settled: {txn_id} | DNA: {math_dna}"})

        return {"success": True, "amount": final_amt, "ref": txn_id}

class PayoutComplianceLayer:
    @staticmethod
    def run_compliance_check(claim: Dict[str, Any], policy: Dict[str, Any], payout_abuse_flag: bool = False) -> Dict[str, Any]:
        """Runs compliance checks before authorizing payout."""
        reasons = []
        decision = "APPROVE"
        confidence = "HIGH"
        
        # A. Policy Validity Check
        if not policy.get("active_status", True):
            return {"compliant": False, "decision": "REJECT", "reasons": ["Policy is expired or inactive"], "confidence": "HIGH"}
            
        # B. Payout Limit Check
        if payout_abuse_flag:
            reasons.append("Payout caps exceeded")
            decision = "REVIEW"
            
        # C. Fraud Safety Check
        fraud_score = float(claim.get("fraud_score", 0))
        if fraud_score >= 70:
            return {"compliant": False, "decision": "REJECT", "reasons": ["Critical Fraud Score (>= 70)"], "confidence": "HIGH"}
        elif 40 <= fraud_score < 70:
            decision = "REVIEW"
            reasons.append("Medium Risk Fraud Score")
            
        # D. Data Authenticity Check
        trigger_conditions = claim.get("trigger_conditions", "")
        # Real-world approximation for fallback text
        if "Fallback" in trigger_conditions or not claim.get("is_real_data", True):
            confidence = "LOW"
            claim["compliance_tag"] = "LOW_CONFIDENCE_AUTOMATION"
            if decision == "REVIEW" or len(reasons) > 0:
                decision = "REVIEW"
            
        return {
            "compliant": decision == "APPROVE",
            "decision": decision,
            "reasons": reasons,
            "confidence": confidence
        }

class InstantPayoutSimulator:
    def __init__(self, core_engine: UnifiedPayoutEngine):
        self.core = core_engine
        self.db_path = "data/payout_audit_db.json"
        
        # Safe deferred import to prevent circular problems
        from services.repositories.worker_repository import WorkerRepository
        self.worker_repo = WorkerRepository()
        
        self._ensure_db()
        
        from services.repositories.base_repository import BaseRepository
        self.audit_repo = BaseRepository("payout_audit_logs")
        
    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump([], f)
                
    def log_payout(self, record: dict):
        try:
            self.audit_repo.create(record)
            
            # Keep legacy fallback structure for older demo elements
            try:
                with open(self.db_path, "r") as f:
                    db = json.load(f)
                db.append(record)
                with open(self.db_path, "w") as f:
                    json.dump(db, f, indent=4)
            except: pass
        except Exception as e:
            pass

    def process_instant_payout(self, claim: Dict[str, Any], policy: Dict[str, Any], audit_trail: List, payout_abuse_flag: bool = False) -> Dict[str, Any]:
        """Safe Instant Payout Simulation + Compliance Check"""
        comp_res = PayoutComplianceLayer.run_compliance_check(claim, policy, payout_abuse_flag)
        
        claim["compliance"] = comp_res
        
        if comp_res["decision"] == "REJECT":
            claim["status"] = "REJECTED"
            claim["governance_status"] = "NON-COMPLIANT"
            audit_trail.append({"step": "compliance_failed", "ts": datetime.now().isoformat(), "narration": f"🚫 COMPLIANCE REJECTED: {', '.join(comp_res['reasons'])}"})
            return {"success": False, "reason": "COMPLIANCE_REJECTED"}
            
        elif comp_res["decision"] == "REVIEW" or (comp_res["decision"] == "APPROVE" and comp_res["confidence"] == "LOW"):
            claim["status"] = "REVIEW"
            claim["governance_status"] = "UNDER REVIEW"
            audit_trail.append({"step": "compliance_review", "ts": datetime.now().isoformat(), "narration": f"⚖️ COMPLIANCE REVIEW: {', '.join(comp_res['reasons']) if comp_res['reasons'] else 'Low confidence data'}"})
            return {"success": False, "reason": "ROUTED_TO_REVIEW"}
            
        audit_trail.append({"step": "compliance_passed", "ts": datetime.now().isoformat(), "narration": f"✅ COMPLIANCE CHECK PASSED for worker {claim.get('worker_id')}"})
        
        try:
            time.sleep(random.uniform(0.3, 0.8))
            method = random.choice(["RAZORPAY_SANDBOX", "UPI_SIMULATION"])
            prefix = "rzp_test_" if method == "RAZORPAY_SANDBOX" else "upi_sim_"
            uid = uuid.uuid4().hex[:10].upper()
            simulation_id = f"{prefix}{uid}"
            
            # Process via core engine
            core_res = self.core.process_payout(claim, audit_trail, delay=False)
            if not core_res.get("success"):
                raise Exception(core_res.get("reason", "CORE_FAILED"))
                
            payout_amt = core_res.get("amount", float(claim.get("estimated_loss", 480)))
            
            audit_trail.append({"step": "instant_payout", "ts": datetime.now().isoformat(), "narration": f"💸 PAYOUT SUCCESS: ₹{payout_amt} via {method} Ref {simulation_id}"})
            
            record = {
                "worker_id": claim.get("worker_id"),
                "claim_id": claim.get("claim_id"),
                "amount": payout_amt,
                "payout_id": simulation_id,
                "method": method,
                "status": "SUCCESS",
                "created_at": datetime.now().isoformat(),
                "compliance_confidence": comp_res["confidence"]
            }
            self.log_payout(record)
            
            # --- NCB Core Rule Trigger: Reset streak to 0 upon real payout ---
            worker_id = claim.get("worker_id")
            if worker_id:
                self.worker_repo.reset_ncb_streak(worker_id)
                audit_trail.append({"step": "ncb_adjusted", "ts": datetime.now().isoformat(), "narration": "🛡️ NCB Streak reset to 0 due to executed claim."})
            
            claim["governance_tags"] = ["Policy Active", "Payout Limit Checked", "Fraud Screened", "Audit Logged"]
            claim["governance_status"] = "COMPLIANT"
            
            return {"success": True, "payout_id": simulation_id, "amount": payout_amt, "method": method}
            
        except Exception as e:
            method = "RAZORPAY_SANDBOX"
            audit_trail.append({"step": "instant_payout_failed", "ts": datetime.now().isoformat(), "narration": f"⚠️ PAYOUT FAILED: Gateway error ({str(e)})"})
            record = {
                "worker_id": claim.get("worker_id"),
                "claim_id": claim.get("claim_id"),
                "amount": float(claim.get("estimated_loss", 480)),
                "payout_id": f"FAIL_{uuid.uuid4().hex[:6].upper()}",
                "method": method,
                "status": "FAILED",
                "created_at": datetime.now().isoformat(),
                "compliance_confidence": comp_res["confidence"]
            }
            self.log_payout(record)
            claim["status"] = "PAYOUT_FAILED"
            claim["governance_tags"] = ["Policy Active", "Payout Limit Checked", "Fraud Screened", "Settlement Failed"]
            claim["governance_status"] = "UNDER REVIEW"
            return {"success": False, "reason": "GATEWAY_ERROR"}
