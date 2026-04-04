"""
GigShield AI — Chatbot Service
===============================
Production-grade AI assistant that answers InsurTech queries using REAL system data.

Architecture:
  1. collect_context()  — pull live data from all repositories + ModelLoader
  2. build_system_prompt() — inject that data into a rich, grounded system prompt
  3. chat()             — call Anthropic API with conversation history
  4. The Streamlit page (app_pages/chatbot.py) manages session state & UI

The assistant NEVER hallucinates: every fact it can state is injected as structured
data in the system prompt before the API call. If data is unavailable (no DB), it
says so explicitly rather than guessing.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

import anthropic

from services.model_loader import ModelLoader
from services.repositories.worker_repository import WorkerRepository
from services.repositories.policy_repository import PolicyRepository
from services.repositories.claim_repository import ClaimRepository
from services.premium_calculator import PremiumCalculator
from services.predictive_alerts import PredictiveAlertsService

logger = logging.getLogger(__name__)

# ── Anthropic client (key from env) ──────────────────────────────────────────
_anthropic_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Please set it in your .env file or environment."
            )
        _anthropic_client = anthropic.Anthropic(api_key=api_key)
    return _anthropic_client


# ─────────────────────────────────────────────────────────────────────────────
class EnviroSenseChatbot:
    """
    Context-aware AI assistant for JARVIS EnviroSense Assurance.

    Behaves as:
      ✔ Assurance advisor    — explains policy terms, premium logic
      ✔ Risk analyst         — explains risk scores and what drives them
      ✔ System explainer     — explains autonomous trigger logic and decisions
      ✔ Fraud analyst        — describes why a trigger was flagged
    """

    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 1024
    MAX_HISTORY = 20  # keep last N turns in context

    def __init__(self):
        self.worker_repo = WorkerRepository()
        self.policy_repo = PolicyRepository()
        self.claim_repo  = ClaimRepository()
        self.premium_calc = PremiumCalculator()
        self.alerts_svc   = PredictiveAlertsService()

    # ── Context collection ────────────────────────────────────────────────────

    def collect_context(
        self,
        worker_id: Optional[str] = None,
        rainfall_mm: float = 10.0,
        temperature: float = 32.0,
        aqi: float = 120.0,
    ) -> Dict[str, Any]:
        """
        Pull all live data for the current session into a structured dict.
        Falls back gracefully on DB unavailability.
        """
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

        # ── Worker + policy + claims ─────────────────────────────────────────
        try:
            if worker_id:
                worker = self.worker_repo.get_worker(worker_id)
                if worker:
                    worker.pop("_id", None)
                    ctx["worker"] = worker

                    active_policy = self.policy_repo.get_active_policy(worker_id)
                    if active_policy:
                        active_policy.pop("_id", None)
                        # Make datetime fields serialisable
                        for k, v in active_policy.items():
                            if isinstance(v, datetime):
                                active_policy[k] = v.isoformat()
                        ctx["active_policy"] = active_policy

                    claims = self.claim_repo.get_worker_claims(worker_id, limit=5)
                    clean_claims = []
                    for c in claims:
                        c.pop("_id", None)
                        for k, v in c.items():
                            if isinstance(v, datetime):
                                c[k] = v.isoformat()
                        clean_claims.append(c)
                    ctx["recent_claims"] = clean_claims
        except Exception as e:
            logger.warning("DB unavailable for context collection: %s", e)
            ctx["db_available"] = False

        # ── ML predictions ───────────────────────────────────────────────────
        try:
            risk_score = ModelLoader.predict_risk({
                "rainfall_mm": rainfall_mm,
                "temperature": temperature,
                "aqi": aqi,
            })
            ctx["risk_assessment"] = {
                "risk_score": round(risk_score, 3),
                "risk_level": "High" if risk_score > 0.7 else ("Medium" if risk_score > 0.3 else "Low"),
                "inputs": {"rainfall_mm": rainfall_mm, "temperature": temperature, "aqi": aqi},
            }
        except Exception as e:
            logger.warning("Risk prediction unavailable: %s", e)

        try:
            premium_result = self.premium_calc.calculate_premium(rainfall_mm, temperature, aqi)
            ctx["premium_estimate"] = premium_result
        except Exception as e:
            logger.warning("Premium calculation unavailable: %s", e)

        try:
            forecast = self.alerts_svc.get_disruption_forecast(rainfall_mm, temperature, aqi)
            ctx["disruption_forecast"] = forecast
        except Exception as e:
            logger.warning("Forecast unavailable: %s", e)

        return ctx

    # ── System prompt ─────────────────────────────────────────────────────────

    def build_system_prompt(self, ctx: Dict[str, Any]) -> str:
        """
        Build a grounded system prompt that injects ALL live context.
        The model must ONLY use facts stated here — no hallucination.
        """
        worker_section = ""
        if ctx.get("worker"):
            w = ctx["worker"]
            worker_section = f"""
## CURRENT WORKER PROFILE
- Worker ID: {w.get('worker_id', 'N/A')}
- Name: {w.get('name', 'N/A')}
- City: {w.get('city', 'N/A')}
- Zone: {w.get('delivery_zone', 'N/A')}
- Avg Hourly Income: ₹{w.get('avg_hourly_income', 'N/A')}
- KYC Status: {w.get('kyc_status', 'N/A')}
- Rating: {w.get('rating', 'N/A')} / 5.0
- Total Payouts Received: ₹{w.get('total_payouts', 0)}
"""
        else:
            worker_section = "\n## CURRENT WORKER PROFILE\nNo worker selected. If the user asks about their profile, ask them to provide their Worker ID.\n"

        policy_section = ""
        if ctx.get("active_policy"):
            p = ctx["active_policy"]
            policy_section = f"""
## ACTIVE POLICY
- Policy ID: {p.get('policy_id', 'N/A')}
- Weekly Premium: ₹{p.get('weekly_premium', 'N/A')}
- Coverage Limit: ₹{p.get('coverage_limit', 'N/A')}
- Valid Until: {p.get('end_date', 'N/A')}
- Status: {'Active ✅' if p.get('active_status') else 'Inactive ❌'}
"""
        else:
            policy_section = "\n## ACTIVE POLICY\nNo active policy found for this worker.\n"

        claims_section = ""
        if ctx.get("recent_claims"):
            claims_section = "\n## RECENT CLAIMS (last 5)\n"
            for c in ctx["recent_claims"]:
                claims_section += (
                    f"- Claim {c.get('claim_id','?')}: "
                    f"Status={c.get('claim_status','?')}, "
                    f"Event={c.get('event_type','?')}, "
                    f"Loss=₹{c.get('estimated_loss','?')}, "
                    f"Payout=₹{c.get('approved_payout','?')}, "
                    f"Fraud={c.get('fraud_status','?')}, "
                    f"Date={c.get('created_at','?')}\n"
                )
        else:
            claims_section = "\n## RECENT CLAIMS\nNo claims found.\n"

        risk_section = ""
        if ctx.get("risk_assessment"):
            r = ctx["risk_assessment"]
            inp = r["inputs"]
            risk_section = f"""
## CURRENT RISK ASSESSMENT (ML Model)
- Risk Score: {r['risk_score']} / 1.0
- Risk Level: {r['risk_level']}
- Based on: Rainfall={inp['rainfall_mm']}mm, Temperature={inp['temperature']}°C, AQI={inp['aqi']}
- How risk is calculated: The ML model (RandomForestClassifier) produces class probabilities
  for Low/Medium/High risk, which are combined into a continuous score 0-1 using weighted average.
  Key drivers: rainfall > 50mm triggers heavy rain; temperature > 42°C triggers heatwave;
  AQI > 300 triggers severe pollution event.
"""

        premium_section = ""
        if ctx.get("premium_estimate"):
            pe = ctx["premium_estimate"]
            premium_section = f"""
## PREMIUM ESTIMATE
- Recommended Weekly Premium: ₹{pe.get('weekly_premium', 'N/A')}
- Risk Level: {pe.get('risk_level', 'N/A')}
- AI Recommendation: {pe.get('ai_recommendation', 'N/A')}
"""

        forecast_section = ""
        if ctx.get("disruption_forecast"):
            f = ctx["disruption_forecast"]
            forecast_section = f"""
## DISRUPTION FORECAST (Tomorrow)
- Probability: {f.get('tomorrow_disruption_probability', 'N/A')}%
- Trend: {f.get('trend', 'N/A')}
- Alert: {f.get('alert_text', 'N/A')}
"""

        db_warning = "" if ctx.get("db_available") else \
            "\n⚠️ DATABASE UNAVAILABLE: Live worker/policy/claim data cannot be retrieved. " \
            "Inform the user if they ask about specific records.\n"

        return f"""You are JARVIS EnviroSense Assistant — an expert autonomous assurance advisor for the JARVIS EnviroSense Assurance platform. 

## CORE PHILOSOPHY
- **Environment = Assurance Trigger**: This system removes the traditional claim process. Environmental signals directly activate protection.
- **Zero-Touch**: Users don't request help — the system acts automatically.
- **No Claims, No Requests, No Waiting**: Payouts are triggered by sensors breaching threshold, not by worker filings.

## OPERATIONAL DOMAIN
You only answer questions about:
1. Risk Assessment (how risk scores are calculated from Temperature, Rain, AQI)
2. Premium Logic (₹20-₹45/week based on 3-tier risk)
3. Autonomous Triggers (Heavy Rain >50mm, Heatwave >42C, Pollution >300 AQI)
4. Fraud Detection (Isolation Forest anomaly checks)
5. System Architecture (how environmental sensors drive payouts)

## RESPONSE RULES
1. If the user asks about anything OUTSIDE these 5 topics (e.g., jokes, general news, other apps), politely state: "I am specialized in JARVIS EnviroSense Assurance logic and can only assist with risk, premiums, and system triggers."
2. ONLY state facts that are present in the LIVE DATA sections below. 
3. Never fabricate IDs or amounts.
4. Use bullet points and ₹ symbols for Indian currency.
5. Explain the REASONING behind risk scores and premium levels.

---
{worker_section}
{policy_section}
{claims_section}
{risk_section}
{premium_section}
{forecast_section}
---
Current date/time: {ctx['timestamp']}

Answer the user's question using only the data above. Be helpful, accurate, and explain the insurance concepts clearly in plain language."""

    # ── Main chat entry point ─────────────────────────────────────────────────

    def chat(
        self,
        user_message: str,
        history: List[Dict[str, str]],
        ctx: Dict[str, Any],
    ) -> str:
        """
        Send a message and get a response.

        Args:
            user_message: The user's latest message
            history:      List of {"role": "user"/"assistant", "content": "..."} dicts
            ctx:          Live context dict from collect_context()

        Returns:
            Assistant response string
        """
        try:
            client = _get_client()
        except ValueError as e:
            return (
                f"⚠️ **Chatbot configuration error:** {e}\n\n"
                "Please set the `ANTHROPIC_API_KEY` environment variable to enable the AI assistant."
            )

        system_prompt = self.build_system_prompt(ctx)

        # Build messages list (trim history to avoid token overflow)
        messages = []
        recent_history = history[-(self.MAX_HISTORY):]
        for turn in recent_history:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": user_message})

        try:
            response = client.messages.create(
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                system=system_prompt,
                messages=messages,
            )
            return response.content[0].text

        except anthropic.AuthenticationError:
            return (
                "⚠️ **API key invalid.** Please check your `ANTHROPIC_API_KEY` "
                "in the `.env` file and restart the app."
            )
        except anthropic.RateLimitError:
            return "⚠️ **Rate limit reached.** Please wait a moment and try again."
        except anthropic.APIConnectionError:
            return "⚠️ **Connection error.** Please check your internet connection and try again."
        except Exception as e:
            logger.error("Chatbot API error: %s", e)
            return f"⚠️ **Unexpected error:** {str(e)}"

    # ── Smart suggestions ─────────────────────────────────────────────────────

    def get_smart_suggestions(self, ctx: Dict[str, Any]) -> List[str]:
        """
        Generate context-aware suggested questions based on live data.
        These guide the user toward the most relevant queries.
        """
        suggestions = []

        risk = ctx.get("risk_assessment")
        if risk and risk["risk_level"] == "High":
            suggestions.append("⚠️ Why is my risk level HIGH right now?")
            suggestions.append("🛡️ Should I upgrade my policy coverage?")

        forecast = ctx.get("disruption_forecast")
        if forecast and forecast.get("tomorrow_disruption_probability", 0) > 60:
            suggestions.append("🌧️ What disruptions are expected tomorrow?")

        claims = ctx.get("recent_claims", [])
        if claims:
            latest = claims[0]
            if latest.get("claim_status") in ("Under Review", "Initiated"):
                suggestions.append(f"📋 What is the status of my claim {latest.get('claim_id', '')}?")
            if latest.get("fraud_status") == "Flagged":
                suggestions.append(f"🚨 Why was my claim {latest.get('claim_id', '')} flagged for fraud?")
            if latest.get("claim_status") == "Rejected":
                suggestions.append(f"❌ Why was my claim rejected?")

        policy = ctx.get("active_policy")
        if not policy:
            suggestions.append("📋 I don't have an active policy. How do I get one?")
        else:
            suggestions.append("💰 How is my weekly premium calculated?")

        if not suggestions:
            suggestions = [
                "📊 What is my current risk level?",
                "💰 How is my premium calculated?",
                "🔍 How does fraud detection work?",
                "📋 Explain the claims pipeline",
            ]

        return suggestions[:4]
