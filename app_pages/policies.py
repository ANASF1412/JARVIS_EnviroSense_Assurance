"""
PAGE: Policies
Insurance policy management
"""
import streamlit as st
import pandas as pd
from services.repositories.worker_repository import WorkerRepository
from services.repositories.policy_repository import PolicyRepository
from services.policy_service import PolicyService


def show():
    """Render policies page."""
    st.title("📋 Insurance Policies")
    st.markdown("Manage weekly insurance policies for workers")

    worker_repo = WorkerRepository()
    policy_repo = PolicyRepository()
    policy_svc = PolicyService()

    workers = worker_repo.get_all_workers()

    if not workers:
        st.warning("No workers registered")
        return

    # ===== SECTION 1: SELECT WORKER =====
    st.subheader("👤 Select Worker")
    worker_ids = [w["worker_id"] + " - " + w["name"] for w in workers]
    selected = st.selectbox("Choose worker", worker_ids)
    worker_id = selected.split(" - ")[0]

    worker = worker_repo.get_worker(worker_id)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Worker", worker["name"])
    with col2:
        st.metric("Zone", worker["delivery_zone"])
    with col3:
        st.metric("Hourly Income", f"₹{worker['avg_hourly_income']}")

    st.divider()

    # ===== SECTION 2: ACTIVE POLICY =====
    st.subheader("📌 Active Policy")
    active_policy = policy_repo.get_active_policy(worker_id)

    if active_policy:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Policy ID", active_policy["policy_id"][:12])
        with col2:
            st.metric("Premium", f"₹{active_policy['weekly_premium']}")
        with col3:
            st.metric("Coverage", f"₹{active_policy['coverage_limit']}")
        with col4:
            days_left = (active_policy["end_date"] - pd.Timestamp.now()).days
            st.metric("Days Left", days_left)

        if st.button("🔄 Renew Policy", use_container_width=True):
            renew_result = policy_svc.renew_policy(active_policy["policy_id"])
            if renew_result["success"]:
                st.success(f"✅ {renew_result['message']}")
            else:
                st.error(f"❌ {renew_result['error']}")
    else:
        st.info("No active policy. Creating new policy...")
        if st.button("➕ Create New Policy", use_container_width=True):
            result = policy_svc.create_policy_for_worker(
                worker_id,
                35.0,  # Default premium
                7  # 7 days
            )
            if result["success"]:
                st.success(f"✅ Policy {result['policy_id']} created")
                st.json(result["policy"])

    st.divider()

    # ===== SECTION 3: POLICY HISTORY =====
    st.subheader("📜 Policy History")
    all_policies = policy_repo.get_worker_policies(worker_id)

    if all_policies:
        policy_data = []
        for p in all_policies:
            policy_data.append({
                "Policy ID": p["policy_id"][:12],
                "Premium": f"₹{p['weekly_premium']}",
                "Coverage": f"₹{p['coverage_limit']}",
                "Status": "Active" if p["active_status"] else "Inactive",
                "Start": p["start_date"].strftime("%Y-%m-%d") if hasattr(p["start_date"], 'strftime') else str(p["start_date"])[:10],
                "End": p["end_date"].strftime("%Y-%m-%d") if hasattr(p["end_date"], 'strftime') else str(p["end_date"])[:10],
            })

        df = pd.DataFrame(policy_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No policies found")

    st.divider()
    st.markdown("---\n**GigShield AI** | Policy Management")
