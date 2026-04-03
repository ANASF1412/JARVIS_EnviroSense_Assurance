"""
PAGE: Analytics
Analytics and insights
"""
import streamlit as st
import pandas as pd
from services.dashboard_service import DashboardService
from services.repositories.claim_repository import ClaimRepository
from services.repositories.payout_repository import PayoutRepository
from services.repositories.zone_repository import ZoneRepository


def show():
    """Render analytics page."""
    st.title("📈 Analytics & Insights")
    st.markdown("Business intelligence and performance metrics")

    dashboard_svc = DashboardService()
    claim_repo = ClaimRepository()
    payout_repo = PayoutRepository()
    zone_repo = ZoneRepository()

    # Get dashboard data
    dashboard_data = dashboard_svc.get_dashboard_data()

    if not dashboard_data["success"]:
        st.error("Failed to load analytics data")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["KPIs", "Claims", "Payouts", "Zones"])

    with tab1:
        st.subheader("🎯 Key Performance Indicators")
        kpis = dashboard_data["kpis"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Workers", kpis["total_workers"])
            st.metric("Active Policies", kpis["active_policies"])
        with col2:
            st.metric("Claims Today", kpis["claims_today"])
            st.metric("Claims This Week", kpis["claims_this_week"])
        with col3:
            st.metric("Success Rate", f"{kpis['success_rate_percent']}%")
            st.metric("Total Payouts", f"₹{int(kpis['total_payout_amount'])}")

    with tab2:
        st.subheader("📊 Claim Statistics")
        stats = claim_repo.get_claim_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Claims", stats.get("total_claims", 0))
        with col2:
            st.metric("Approved", stats.get("approved_count", 0))
        with col3:
            st.metric("Flagged", stats.get("flagged_count", 0))
        with col4:
            st.metric("Total Loss", f"₹{int(stats.get('total_loss', 0))}")

    with tab3:
        st.subheader("💰 Payout Analysis")
        payout_stats = payout_repo.get_payout_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Payouts", payout_stats.get("total_payouts", 0))
        with col2:
            st.metric("Total Amount", f"₹{int(payout_stats.get('total_amount', 0))}")
        with col3:
            st.metric("Avg Amount", f"₹{int(payout_stats.get('avg_amount', 0))}")

    with tab4:
        st.subheader("🗺️ Zone Risk Analysis")
        zones = zone_repo.get_all_zones()
        if zones:
            zone_data = []
            for z in zones:
                risk_level = zone_repo.get_risk_level(z["zone_name"])
                zone_data.append({
                    "Zone": z["zone_name"],
                    "City": z.get("city"),
                    "Risk Score": f"{z.get('historical_risk_score', 0):.2f}",
                    "Risk Level": risk_level,
                })
            df = pd.DataFrame(zone_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("---\n**GigShield AI** | Analytics Dashboard")
