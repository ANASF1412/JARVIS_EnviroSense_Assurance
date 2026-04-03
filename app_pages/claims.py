"""
PAGE: Claims
Claims history and management
"""
import streamlit as st
import pandas as pd
from services.repositories.claim_repository import ClaimRepository
from services.repositories.worker_repository import WorkerRepository
from ui.components import render_claims_table


def show():
    """Render claims page."""
    st.title("📝 Claims Management")
    st.markdown("View and manage insurance claims")

    claim_repo = ClaimRepository()
    worker_repo = WorkerRepository()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["All Claims", "By Worker", "By Status"])

    with tab1:
        st.subheader("📊 All Claims")
        limit = st.slider("Show last N claims", 10, 100, 50)
        all_claims = claim_repo.find_many({}, limit=limit, sort_field="created_at", sort_order=-1)
        render_claims_table(all_claims)

    with tab2:
        st.subheader("👤 Claims by Worker")
        workers = worker_repo.get_all_workers()
        if workers:
            worker_ids = [w["worker_id"] + " - " + w["name"] for w in workers]
            selected = st.selectbox("Select worker", worker_ids)
            worker_id = selected.split(" - ")[0]
            worker_claims = claim_repo.find_many(
                {"worker_id": worker_id},
                limit=50,
                sort_field="created_at",
                sort_order=-1
            )
            render_claims_table(worker_claims)
        else:
            st.info("No workers found")

    with tab3:
        st.subheader("📋 Claims by Status")
        status = st.selectbox("Select status", ["Paid", "Approved", "Under Review", "Rejected", "Flagged"])
        status_claims = claim_repo.find_many(
            {"claim_status": status},
            limit=50,
            sort_field="created_at",
            sort_order=-1
        )
        render_claims_table(status_claims)

    st.divider()
    st.markdown("---\n**GigShield AI** | Claims Management")
