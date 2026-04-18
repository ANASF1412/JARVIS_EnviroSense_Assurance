"""
GigShield AI — Chatbot Service (Gemini Edition)
===============================================
Production-grade AI assistant that answers InsurTech queries using REAL system data.
# HOTFIX RELOAD: Ensuring get_smart_suggestions is visible to Streamlit.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from services.model_loader import ModelLoader
from services.repositories.worker_repository import WorkerRepository
from services.repositories.policy_repository import PolicyRepository
from services.repositories.claim_repository import ClaimRepository
from services.premium_calculator import PremiumCalculator
from services.predictive_alerts import PredictiveAlertsService

logger = logging.getLogger(__name__)

# ── Gemini client ──────────────────────────────────────────────
_gemini_configured = False

def _configure_gemini():
    global _gemini_configured
    if _gemini_configured: return True
    
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        except:
            pass
            
    if not api_key:
        return False
        
    if genai:
        genai.configure(api_key=api_key)
        _gemini_configured = True
        return True
    return False

# ─────────────────────────────────────────────────────────────────────────────
class EnviroSenseChatbot:
    """
    Context-aware AI assistant for JARVIS EnviroSense Assurance.
    """
    MODEL = "gemini-1.5-flash"

    def __init__(self):
        self.worker_repo = WorkerRepository()
        self.policy_repo = PolicyRepository()
        self.claim_repo  = ClaimRepository()
        self.premium_calc = PremiumCalculator()
        self.alerts_svc   = PredictiveAlertsService()
        self.use_llm = _configure_gemini()

    def collect_context(
        self,
        worker_id: Optional[str] = None,
        rainfall_mm: float = 10.0,
        temperature: float = 32.0,
        aqi: float = 120.0,
    ) -> Dict[str, Any]:
        """Pull all live data for the current session into a structured dict."""
        ctx: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "worker": None,
            "active_policy": None,
            "recent_claims": [],
            "risk_assessment": None,
            "premium_estimate": None,
            "disruption_forecast": None,
            "db_available": True,
        }

        try:
            if worker_id:
                worker = self.worker_repo.get_worker(worker_id)
                if worker:
                    ctx["worker"] = {k:v for k,v in worker.items() if k != "_id"}
                    active_policy = self.policy_repo.get_active_policy(worker_id)
                    if active_policy:
                        ctx["active_policy"] = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in active_policy.items() if k != "_id"}

                    claims = self.claim_repo.get_worker_claims(worker_id, limit=5)
                    clean_claims = []
                    for c in claims:
                        clean_c = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in c.items() if k != "_id"}
                        clean_claims.append(clean_c)
                    ctx["recent_claims"] = clean_claims
            else:
                claims = self.claim_repo.find_many({}, limit=10)
                clean_claims = []
                for c in claims:
                    clean_c = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in c.items() if k != "_id"}
                    clean_claims.append(clean_c)
                ctx["recent_claims"] = clean_claims
        except Exception as e:
            logger.warning("DB unavailable for context collection: %s", e)
            ctx["db_available"] = False

        try:
            risk_result = ModelLoader.predict_risk({"rainfall_mm": rainfall_mm, "temperature": temperature, "aqi": aqi})
            if isinstance(risk_result, dict):
                risk_score = risk_result.get("risk_score", 0.0)
                risk_level = risk_result.get("risk_class", "Low")
            else:
                risk_score = risk_result
                risk_level = "High" if risk_score > 0.7 else ("Medium" if risk_score > 0.3 else "Low")
                
            ctx["risk_assessment"] = {
                "risk_score": round(risk_score, 3), "risk_level": risk_level,
                "inputs": {"rainfall_mm": rainfall_mm, "temperature": temperature, "aqi": aqi},
            }
        except: pass

        try:
            ctx["premium_estimate"] = self.premium_calc.calculate_premium(rainfall_mm, temperature, aqi)
        except: pass

        try:
            ctx["disruption_forecast"] = self.alerts_svc.get_disruption_forecast(rainfall_mm, temperature, aqi)
        except: pass

        return ctx

    def build_system_prompt(self, ctx: Dict[str, Any]) -> str:
        worker_section = ""
        if ctx.get("worker"):
            w = ctx["worker"]
            worker_section = f"Worker ID: {w.get('worker_id')}, City: {w.get('city')}, NCB Streak: {w.get('ncb_streak', 0)}\n"
        else:
            worker_section = "No worker selected (Admin Mode). Answering generally.\n"

        policy_section = ""
        if ctx.get("active_policy"):
            p = ctx["active_policy"]
            policy_section = f"Policy: {p.get('policy_id')}, Premium: ₹{p.get('weekly_premium', 0)}, Status: {'Active' if p.get('active_status') else 'Inactive'}\n"
        
        claims_section = ""
        if ctx.get("recent_claims"):
            for c in ctx["recent_claims"]:
                reason = c.get('decision_reason', 'ML Pattern Match')
                claims_section += f"- Claim {c.get('claim_id')}: Status={c.get('status', c.get('claim_status'))}, Confidence={c.get('decision_confidence', 'N/A')}%, Reason={reason}, Fraud={c.get('fraud_level')}\n"
        
        prompt = f"""You are JARVIS EnviroSense AI Assistant. Answer questions based on the live system data below. Be simple and explainable.
        
LIVE CONTEXT:
{worker_section}
{policy_section}
CLAIMS:
{claims_section}
RISK: {ctx.get('risk_assessment')}
PREMIUM ESTIMATE: {ctx.get('premium_estimate')}
"""
        return prompt

    def get_smart_suggestions(self, ctx: Dict[str, Any]) -> List[str]:
        """Generate context-aware suggestions for the user."""
        suggs = ["Am I covered today?", "How do I earn higher NCB?", "Why is my premium ₹45?"]
        if ctx.get("recent_claims"):
            suggs.append("Explain my last claim status")
        if ctx.get("risk_assessment") and ctx["risk_assessment"].get("risk_score", 0) > 0.5:
            suggs.append("Why is the risk score high today?")
        return suggs

    def _rule_based_fallback(self, query: str, ctx: Dict[str, Any]) -> str:
        q = query.lower()
        if "reject" in q or "claim" in q or "confidence" in q:
            if ctx.get("recent_claims"):
                claims = ctx["recent_claims"]
                for c in claims:
                    if "confidence" in q:
                        return f"Your latest claim {c.get('claim_id')} has a decision confidence of {c.get('decision_confidence', 'N/A')}%. Reason: {c.get('decision_reason', 'Analyzed by System Intelligence')}."
                    if c.get("status") in ["BLOCKED", "FLAGGED", "REVIEW", "REJECTED"]:
                        return f"Claim {c.get('claim_id')} was routed to {c.get('status')} due to: {c.get('fraud_explanation', 'High Risk Activity/Limits')}. (Confidence: {c.get('decision_confidence', 'N/A')}%)"
                return f"Your recent claims appear to be processed. Last claim {claims[0].get('claim_id')} has {claims[0].get('decision_confidence')}% confidence."
            return "You have no recent claims on file."
        elif "risk" in q or "today" in q:
            r = ctx.get("risk_assessment", {})
            return f"Your current zone risk level is {r.get('risk_level', 'Unknown')} with a score of {r.get('risk_score', '0')}."
        elif "cover" in q or "active" in q:
            p = ctx.get("active_policy")
            if p and p.get("active_status"):
                return f"Yes! You are currently covered. Your policy {p.get('policy_id')} is active until {p.get('end_date')}."
            return "You do not have active coverage at this moment."
        elif "premium" in q or "cost" in q:
            p = ctx.get("active_policy")
            pe = ctx.get("premium_estimate", {})
            if p:
                return f"Your current premium is ₹{p.get('weekly_premium')}. This is dynamically tailored based on your Zone Risk ({pe.get('risk_level', 'Local')})."
            return f"Estimated premium is ₹{pe.get('weekly_premium', '45')}. This fluctuates based on hyper-local weather risks."
        elif "safe mode" in q or "pool" in q:
            return "Safe Mode triggers if Total Claim Liability exceeds 40% of the pool's balance, or if an extreme anomaly (>150mm rain or >500 AQI) is detected to prevent glitches draining the pool."
        else:
            return "I am operating in Fallback Sandbox Mode and can only answer questions regarding Claims, Risks, Coverage, Premium, or Pool status based on Live Data."

    def chat(self, user_message: str, history: List[Dict[str, str]], ctx: Dict[str, Any]) -> str:
        if not self.use_llm or not genai:
            return self._rule_based_fallback(user_message, ctx)

        try:
            model = genai.GenerativeModel(self.MODEL, system_instruction=self.build_system_prompt(ctx))
            formatted_history = []
            for h in history:
                role = "user" if h["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [h["content"]]})
                
            chat_session = model.start_chat(history=formatted_history)
            response = chat_session.send_message(user_message)
            return response.text
        except Exception as e:
            logger.error("Gemini Error: %s", e)
            return self._rule_based_fallback(user_message, ctx)
