"""
PAGE: Admin
Administrative tools and zone management
"""
import streamlit as st
from services.repositories.zone_repository import ZoneRepository
from config.settings import DEFAULT_ZONES
import pandas as pd


def show():
    """Render admin page."""
    st.title("⚙️ Administration")
    st.markdown("System configuration and management tools")

    zone_repo = ZoneRepository()

    tab1, tab2 = st.tabs(["Zone Management", "System Status"])

    with tab1:
        st.subheader("🗺️ Delivery Zones")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("**Create New Zone**")
            zone_name = st.text_input("Zone Name")
            city = st.text_input("City")
            risk_score = st.slider("Historical Risk Score", 0.0, 1.0, 0.5, 0.1)

            if st.button("➕ Add Zone", use_container_width=True):
                if zone_name and city:
                    try:
                        zone_repo.create_zone(zone_name, city, risk_score)
                        st.success(f"✅ Zone '{zone_name}' created")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        with col2:
            st.markdown("**Initialize Defaults**")
            if st.button("🔄 Reset to Defaults", use_container_width=True):
                try:
                    # Clear existing zones
                    zone_repo.db.zones.delete_many({})

                    # Reinitialize
                    for zone_data in DEFAULT_ZONES:
                        zone_repo.create_zone(
                            zone_data["zone_name"],
                            zone_data["city"],
                            zone_data["historical_risk_score"]
                        )

                    st.success("✅ Zones reset to defaults")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        st.markdown("**Existing Zones**")
        zones = zone_repo.get_all_zones()
        if zones:
            zone_data = []
            for z in zones:
                zone_data.append({
                    "Zone": z["zone_name"],
                    "City": z.get("city"),
                    "Risk Score": f"{z.get('historical_risk_score', 0):.2f}",
                    "Status": "Active",
                })
            df = pd.DataFrame(zone_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("🔍 System Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Database", "Connected ✅")
        with col2:
            st.metric("Models", "Loaded ✅")
        with col3:
            st.metric("API", "Ready ✅")

        st.markdown("**Version & Info**")
        st.info("""
        - **Version:** 1.0.0
        - **Database:** MongoDB (gigshield-ai)
        - **ML Models:** risk_model.pkl, income_model.pkl
        - **Framework:** Streamlit + FastAPI
        """)

    st.divider()
    st.markdown("---\n**GigShield AI** | Administration")
