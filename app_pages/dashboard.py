"""
PAGE: Dashboard
Main KPI dashboard and overview
"""
import streamlit as st
import pandas as pd
from services.dashboard_service import DashboardService
from services.event_detector import EventDetector
from services.premium_calculator import PremiumCalculator
from services.automation_engine import AutomationEngine
from services.repositories.worker_repository import WorkerRepository
from services.repositories.policy_repository import PolicyRepository
from ui.components import (
    render_kpi_cards, render_worker_header, render_policy_status,
    render_weather_conditions, render_event_triggers, render_risk_gauge,
    render_claims_table, render_payout_table, render_fraud_indicator
)


def show():
    """Render dashboard page."""
    st.title("📊 GigShield AI Dashboard")
    st.markdown("Real-time Parametric Income Protection Overview")

    # Initialize services
    dashboard_svc = DashboardService()
    event_detector = EventDetector()
    premium_calc = PremiumCalculator()
    automation_engine = AutomationEngine()
    worker_repo = WorkerRepository()
    policy_repo = PolicyRepository()

    # ===== SECTION 1: WORKER SELECTION =====
    st.subheader("👤 Select Worker")
    workers = worker_repo.get_all_workers()

    if not workers:
        st.warning("No workers registered. Please register a worker first.")
        return

    worker_ids = [w["worker_id"] + " - " + w["name"] for w in workers]
    selected = st.selectbox("Choose a worker to monitor", worker_ids)
    worker_id = selected.split(" - ")[0]

    worker = worker_repo.get_worker(worker_id)
    policy = policy_repo.get_active_policy(worker_id)

    # Render worker and policy headers
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Worker Profile**")
        render_worker_header(worker)
    with col2:
        st.markdown("**Active Policy**")
        if policy:
            render_policy_status(policy)
        else:
            st.warning("No active policy")

    st.divider()

    # ===== SECTION 2: LIVE WEATHER & RISK =====
    st.subheader("🌦️ Live Weather & Risk Assessment")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Environmental Conditions**")
        rainfall = st.slider("Rainfall (mm)", 0.0, 200.0, 25.0, step=5.0,
                            help="Adjust to simulate different rainfall amounts")
        temperature = st.slider("Temperature (°C)", 20.0, 50.0, 35.0, step=1.0)
        aqi = st.slider("Air Quality Index", 0, 500, 150, step=10)

        weather_data = {
            "rainfall_mm": rainfall,
            "temperature": temperature,
            "aqi": aqi,
        }

    with col2:
        st.markdown("**Current Risk Score**")
        try:
            premium_result = premium_calc.calculate_premium(rainfall, temperature, aqi)

            if premium_result["success"]:
                risk_score = premium_result["risk_score"] * 100  # Convert to 0-100
                render_risk_gauge(risk_score)
                st.markdown(f"**Premium Recommendation:** ₹{premium_result['weekly_premium']}/week")
                
                # ONE-LOOK UNDERSTANDING LAYER
                st.markdown(f"""
                <div style='background-color:#1e1e1e; padding:10px; border-radius:5px; text-align:center;'>
                <strong>💡 Quick Trace:</strong> Environment ➝ Risk ({risk_score:.0f}%) ➝ Premium (₹{premium_result['weekly_premium']})
                </div>
                """, unsafe_allow_html=True)
                
                # AI Explainability (HACKATHON REQUIREMENT)
                with st.expander("🧠 AI Reasoning & Explainability", expanded=True):
                    st.markdown(f"**Confidence Score:** {premium_result.get('confidence', 0) * 100:.1f}%")
                    st.markdown(f"**Reasoning:** {premium_result.get('ai_recommendation', 'N/A')}")
                    st.markdown("**Top 3 Risk Drivers:**")
                    factors = premium_result.get('contributing_factors', [])
                    for f in factors[:3]:
                        st.markdown(f"- {f}")
                    st.markdown("**Feature Influence:**")
                    impacts = premium_result.get('factor_impacts', {})
                    for feature, impact in impacts.items():
                        st.markdown(f"- {feature}: *{impact}*")
            else:
                st.error("Failed to calculate risk")
                
        except Exception as e:
            st.error("⚠️ AI temporarily unavailable. Running on baseline fallback.")
            st.markdown("**Premium Recommendation:** ₹100/week (Fallback)")

    st.divider()

    # ===== SECTION 3: EVENT DETECTION & CLAIMS =====
    st.subheader("🚨 Automatic Claims Processing")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Detect events
        event_result = event_detector.detect_event(rainfall, temperature, aqi)

        if event_result["event_detected"]:
            render_event_triggers(event_result["trigger_conditions"])

            # Zero-Touch Automation (No Manual Intervention)
            st.info("⚡ Zero-Touch Pipeline Activated: Automatically processing claims...")
            with st.spinner("Processing claims..."):
                automation_result = automation_engine.trigger_claims_for_event(
                    rainfall, temperature, aqi
                )

                if automation_result["success"]:
                    st.success(automation_result["message"])
                    st.write(f"**Policies Processed:** {automation_result['policies_processed']}")
                    st.write(f"**Claims Created:** {automation_result['claims_created']}")
                    st.write(f"**Payouts Processed:** {automation_result['payouts_processed']}")

                    # One Look Claim Journey Summary
                    st.success(f"**🎯 Action Track:** Environment Signal ➝ Risk Evaluated ➝ Premium Adjusted ➝ {automation_result['claims_created']} Claim(s) Auto-Triggered ✔")
                    
                    # Show results
                    if automation_result["results"]:
                        st.markdown("**📋 Claim Processing Trace:**")
                        for r in automation_result["results"][:10]:
                            msg = r.get("message", "").replace("\n", "\n\n")
                            if r["claim_created"]:
                                st.info(f"**Policy {r['policy_id'][:8]}** ➝ {msg}")
                            else:
                                st.warning(f"**Policy {r['policy_id'][:8]}** ➝ Ignored (No impact/Flagged)")
                else:
                    st.error(f"Automation failed: {automation_result['error']}")
        else:
            st.info("✅ No disruption events detected. Conditions are safe.")

    with col2:
        st.markdown("**Forecast**")
        forecast = {
            "Tomorrow": f"{min(100, int((premium_result['risk_score'] * 100) + 10))}%"
        }
        st.metric("Disruption Probability", forecast["Tomorrow"])

    st.divider()

    # ===== SECTION 4: DASHBOARD DATA =====
    st.subheader("📊 System Overview")

    dashboard_data = dashboard_svc.get_dashboard_data()

    if dashboard_data["success"]:
        # KPI cards
        col1, col2, col3, col4, col5 = st.columns(5)

        kpis = dashboard_data["kpis"]

        with col1:
            st.metric("Total Workers", kpis["total_workers"])
        with col2:
            st.metric("Active Policies", kpis["active_policies"])
        with col3:
            st.metric("Claims Today", kpis["claims_today"])
        with col4:
            st.metric("Success Rate", f"{kpis['success_rate_percent']}%")
        with col5:
            st.metric("Total Payouts", f"₹{int(kpis['total_payout_amount'])}")

        st.divider()

        # Recent Activities
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Recent Claims**")
            render_claims_table(dashboard_data["recent_data"]["recent_claims"])

        with col2:
            st.markdown("**Recent Payouts**")
            render_payout_table(dashboard_data["recent_data"]["recent_payouts"])

        if dashboard_data["recent_data"]["flagged_claims_count"] > 0:
            st.warning(
                f"⚠️ {dashboard_data['recent_data']['flagged_claims_count']} claims flagged for review"
            )

    st.divider()

    # Footer
    st.markdown("""
    ---
    **GigShield AI** | Powered by Streamlit & MongoDB | Real-time Parametric Insurance
    """)
