"""
Reusable UI Components for GigShield AI
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
from config.settings import COLORS
from ui.theme import badge, success_box, warning_box, error_box, info_box


def render_kpi_cards(metrics: Dict[str, Any]) -> None:
    """
    Render KPI cards in a grid.

    Args:
        metrics: Dictionary of metric_name: value
    """
    cols = st.columns(len(metrics))

    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            st.metric(label=label, value=value)


def render_worker_header(worker: Dict[str, Any]) -> None:
    """
    Render worker profile header.

    Args:
        worker: Worker profile dictionary
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Worker ID", worker.get("worker_id", "N/A"))
    with col2:
        st.metric("Zone", worker.get("delivery_zone", "N/A"))
    with col3:
        st.metric("Hourly Income", f"₹{worker.get('avg_hourly_income', 0)}")
    with col4:
        st.metric("Rating", f"⭐ {worker.get('rating', 0)}")


def render_policy_status(policy: Dict[str, Any]) -> None:
    """
    Render policy status display.

    Args:
        policy: Policy dictionary
    """
    if not policy:
        st.warning("No active policy found")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Policy ID", policy["policy_id"][:10] + "...")
    with col2:
        st.metric("Premium", f"₹{policy['weekly_premium']}/week")
    with col3:
        st.metric("Coverage", f"₹{policy['coverage_limit']}")
    with col4:
        days_left = (policy["end_date"] - datetime.now()).days
        st.metric("Days Left", days_left)


def render_claim_status_timeline(claim: Dict[str, Any]) -> None:
    """
    Render claim status timeline.

    Args:
        claim: Claim dictionary
    """
    status_flow = ["Initiated", "Validated", "Under Review", "Approved", "Paid"]
    current_status = claim.get("claim_status", "Initiated")

    st.subheader("Claim Status Timeline")

    cols = st.columns(len(status_flow))
    for col, status in zip(cols, status_flow):
        with col:
            is_complete = status_flow.index(status) <= status_flow.index(current_status) if current_status in status_flow else False
            symbol = "✅" if is_complete else "⭕"
            color = "green" if is_complete else "gray"

            st.markdown(f"""
            <div style="text-align: center;">
                <div style="font-size: 1.5rem; color: {'#10b981' if is_complete else '#9ca3af'};">{symbol}</div>
                <div style="font-size: 0.8rem; color: {'#1f2937' if is_complete else '#6b7280'};">{status}</div>
            </div>
            """, unsafe_allow_html=True)


def render_fraud_indicator(fraud_score: float, fraud_status: str) -> None:
    """
    Render fraud risk indicator.

    Args:
        fraud_score: Fraud score (0-100)
        fraud_status: Fraud status (Cleared, Suspicious, Flagged)
    """
    col1, col2 = st.columns([2, 1])

    with col1:
        # Fraud score gauge
        st.metric("Fraud Risk Score", f"{fraud_score}/100")

    with col2:
        if fraud_status == "Cleared":
            badge("✅ Cleared", "success")
        elif fraud_status == "Suspicious":
            badge("⚠️ Suspicious", "warning")
        else:
            badge("❌ Flagged", "error")


def render_claims_table(claims: List[Dict[str, Any]]) -> None:
    """
    Render claims as formatted table.

    Args:
        claims: List of claim dictionaries
    """
    if not claims:
        st.info("No claims found")
        return

    df = pd.DataFrame([
        {
            "Claim ID": c["claim_id"][:8],
            "Status": c["claim_status"],
            "Event": c.get("event_type", "N/A"),
            "Loss": f"₹{c.get('estimated_loss', 0)}",
            "Payout": f"₹{c.get('approved_payout', 0)}",
            "Date": c["created_at"].strftime("%Y-%m-%d") if hasattr(c["created_at"], 'strftime') else str(c["created_at"])[:10],
        }
        for c in claims
    ])

    st.dataframe(df, use_container_width=True, hide_index=True)


def render_payout_table(payouts: List[Dict[str, Any]]) -> None:
    """
    Render payouts as formatted table.

    Args:
        payouts: List of payout dictionaries
    """
    if not payouts:
        st.info("No payouts found")
        return

    df = pd.DataFrame([
        {
            "Payout ID": p["payout_id"][:8],
            "Claim ID": p["claim_id"][:8],
            "Amount": f"₹{p['amount']}",
            "Status": p["status"],
            "TXN ID": p.get("upi_txn_id", "Pending")[:12] if p.get("upi_txn_id") else "Pending",
            "Date": p["timestamp"].strftime("%Y-%m-%d %H:%M") if hasattr(p["timestamp"], 'strftime') else str(p["timestamp"])[:16],
        }
        for p in payouts
    ])

    st.dataframe(df, use_container_width=True, hide_index=True)


def render_weather_conditions(weather: Dict[str, Any]) -> None:
    """
    Render current weather conditions.

    Args:
        weather: Weather data dictionary
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🌧️ Rainfall", f"{weather.get('rainfall_mm', 0)} mm")
    with col2:
        st.metric("🌡️ Temperature", f"{weather.get('temperature', 0)}°C")
    with col3:
        st.metric("💨 AQI", f"{weather.get('aqi', 0)}")


def render_event_triggers(triggers: List[str]) -> None:
    """
    Render triggered event conditions.

    Args:
        triggers: List of trigger descriptions
    """
    if not triggers:
        st.success("✅ No disruption events detected")
        return

    st.error("🚨 **Disruption Event Detected!**")
    for trigger in triggers:
        st.write(f"- {trigger}")


def render_risk_gauge(risk_score: float) -> None:
    """
    Render risk score gauge visualization.

    Args:
        risk_score: Risk score (0-100)
    """
    # Simple gauge-like display
    if risk_score < 30:
        color = "green"
        level = "🟢 LOW"
    elif risk_score < 70:
        color = "orange"
        level = "🟡 MEDIUM"
    else:
        color = "red"
        level = "🔴 HIGH"

    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <div style="font-size: 3rem; color: {color};">{level}</div>
        <div style="font-size: 2rem; font-weight: bold; color: {color};">{risk_score:.1f}</div>
        <div style="font-size: 0.9rem; color: #6b7280;">Disruption Risk Score</div>
    </div>
    """, unsafe_allow_html=True)


def render_form_section(title: str) -> None:
    """Render a form section header."""
    st.subheader(f"📝 {title}")


def render_result_message(result: Dict[str, Any]) -> None:
    """
    Render result message from service call.

    Args:
        result: Result dictionary with success and message
    """
    if result.get("success"):
        success_box("Success", result.get("message", "Operation successful"))
    else:
        error_box("Error", result.get("error", "Operation failed"))


def render_collapse_section(title: str, content_func) -> None:
    """
    Render collapsible section.

    Args:
        title: Section title
        content_func: Function to render content
    """
    with st.expander(title):
        content_func()
