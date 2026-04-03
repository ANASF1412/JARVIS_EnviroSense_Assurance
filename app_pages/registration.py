"""
PAGE: Registration
Worker onboarding and registration
"""
import streamlit as st
from services.registration_service import RegistrationService
from services.repositories.worker_repository import WorkerRepository
from ui.components import render_result_message, render_kpi_cards


def show():
    """Render registration page."""
    st.title("👤 Worker Registration")
    st.markdown("Onboard new gig workers to GigShield AI insurance protection")

    registration_svc = RegistrationService()
    worker_repo = WorkerRepository()

    # ===== SECTION 1: REGISTRATION FORM =====
    st.subheader("📝 Register New Worker")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Full Name", placeholder="Ramesh Kumar")
        city = st.text_input("City", placeholder="Delhi")

    with col2:
        delivery_zone = st.selectbox("Delivery Zone",
                                     ["North", "South", "East", "West", "Central"])
        avg_hourly_income = st.number_input("Average Hourly Income (₹)",
                                            min_value=50.0, max_value=1000.0, value=120.0)

    if st.button("✅ Register Worker", use_container_width=True):
        if not name or not city:
            st.error("Please fill in all fields")
        else:
            with st.spinner("Registering worker..."):
                result = registration_svc.register_worker(
                    name=name,
                    city=city,
                    delivery_zone=delivery_zone,
                    avg_hourly_income=avg_hourly_income
                )

                render_result_message(result)

                if result["success"]:
                    st.success(f"✅ Worker {result['worker_id']} registered successfully!")
                    st.json(result["worker"])

    st.divider()

    # ===== SECTION 2: REGISTERED WORKERS LIST =====
    st.subheader("👥 All Registered Workers")

    workers = worker_repo.get_all_workers()

    if workers:
        worker_data = []
        for w in workers:
            worker_data.append({
                "Worker ID": w["worker_id"],
                "Name": w["name"],
                "City": w["city"],
                "Zone": w["delivery_zone"],
                "Hourly Income": f"₹{w['avg_hourly_income']}",
                "Rating": f"⭐ {w.get('rating', 0)}",
                "Total Deliveries": w.get("total_deliveries", 0),
                "Total Earnings": f"₹{w.get('total_earnings', 0)}",
            })

        import pandas as pd
        df = pd.DataFrame(worker_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No workers registered yet")

    st.divider()

    # Footer
    st.markdown("""
    ---
    **GigShield AI** | Worker Registration Portal
    """)
