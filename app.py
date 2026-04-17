"""
JARVIS EnviroSense Assurance — Router (Phase 3 Final Polish)
"""
import streamlit as st
import time
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.dashboard_service import DashboardService
from services.automation_engine import AutomationEngine
from services.scheduler_service import MonitoringScheduler
from services.environmental_api import EnvironmentalAPI
from ui.theme import apply_custom_theme

# ── AUTO-MONITORING (PHASE 2) ────────────────────────────────────────────────
@st.cache_resource
def get_monitoring_scheduler():
    scheduler = MonitoringScheduler()
    scheduler.start()
    return scheduler

# Start the background monitoring scheduler (Singleton instance)
scheduler = get_monitoring_scheduler()

# Page Configuration
st.set_page_config(
    page_title="JARVIS EnviroSense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_theme()

@st.cache_resource
def get_global_engine():
    from services.automation_engine import AutomationEngine
    return AutomationEngine()

# ── SESSION STATE INITIALIZATION ──────────────────────────────────────────────
if "automation_engine" not in st.session_state:
    st.session_state.automation_engine = get_global_engine()
if "role" not in st.session_state:
    st.session_state.role = None
if "worker_id" not in st.session_state:
    st.session_state.worker_id = None
if "last_fetch" not in st.session_state:
    st.session_state.last_fetch = 0
if "data" not in st.session_state:
    st.session_state.data = {}

# ── TOPBAR LIVE INDICATOR ─────────────────────────────────────────────────────
def render_topbar():
    # ── SYSTEM TRUST BANNER (EXPLAINABILITY LAYER) ──
    try:
        env_data = EnvironmentalAPI.fetch_current_conditions("Chennai")
        src = env_data.get("source", "OpenWeather")
        is_live = env_data.get("is_real_data", True)
    except Exception:
        src, is_live = "Local Cache", False

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>🟢 System Status: ACTIVE &nbsp;|&nbsp; 🧠 ML Engine: CONNECTED &nbsp;|&nbsp; 💰 Liquidity Pool: ₹1,000,000</h4>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        c1.caption(f"⚡ Last Updated: {time.strftime('%H:%M:%S')}")
        if is_live:
            c2.markdown(f"<div style='text-align:center;'>🌍 Data Source: <b style='color:green;'>LIVE ({src})</b></div>", unsafe_allow_html=True)
        else:
            c2.warning("⚠️ Using cached data — API unavailable")
        c3.markdown("<div style='text-align: right;'><span style='color: gray;'>Data Sync: Encrypted SSL/TLS</span></div>", unsafe_allow_html=True)

# ── CENTRALIZED POLLING & FEEDBACK ───────────────────────────────────────────
if time.time() - st.session_state.get("last_fetch", 0) > 30:
    svc = DashboardService()
    st.session_state.data = svc.get_dashboard_data()
    st.session_state.last_fetch = time.time()
    st.toast("Intelligence data synchronized", icon="🔄")

# ── ROUTING LOGIC ─────────────────────────────────────────────────────────────
def main():
    render_topbar()
    
    if st.session_state.role is None:
        from app_pages.login import show
        show()
        return

    # ── WORKER DATA INITIALIZATION ───────────────────────────────────────────
    if st.session_state.role == "worker" and "user" not in st.session_state:
        svc = DashboardService()
        worker_data = svc.get_worker_dashboard(st.session_state.worker_id)
        if worker_data.get("success"):
            st.session_state.user = worker_data["worker"]
            st.session_state.data = worker_data
        else:
            st.error(f"Failed to load worker data: {worker_data.get('error')}")
            st.session_state.role = None
            st.rerun()

    # Sidebar Navigation
    st.sidebar.title("🛡️ JARVIS EnviroSense")
    
    st.sidebar.markdown("**🎨 Theme Settings**")
    theme_label = "☀️ Switch to Light Mode" if st.session_state.get("theme_mode", "dark") == "dark" else "🌙 Switch to Dark Mode"
    if st.sidebar.button(theme_label, use_container_width=True):
        st.session_state["theme_mode"] = "light" if st.session_state.get("theme_mode", "dark") == "dark" else "dark"
        st.rerun()
    st.sidebar.markdown("---")
    
    if st.session_state.role == "admin":
        st.sidebar.success("🔑 Admin Control Hub")
        nav_options = [
            "📊 Admin Overview",
            "📋 Autonomous Activations",
            "🛡️ Integrity Guard",
            "📈 Strategic Analytics",
            "🔮 Predictive Warning",
            "💬 AI Assistant",
            "⚙️ System Settings"
        ]
    else:
        st.sidebar.info(f"👷 Worker: {st.session_state.worker_id}")
        nav_options = [
            "🏠 My Dashboard",
            "🛡️ My Coverage",
            "💰 My Payouts",
            "🔮 Predictive Warning",
            "💬 AI Assistant"
        ]

    page = st.sidebar.radio("Navigation", nav_options)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.role = None
        st.session_state.worker_id = None
        st.session_state.pop("user", None)
        st.session_state.pop("data", None)
        st.rerun()

    # Routing
    if page == "📊 Admin Overview":
        from app_pages.dashboard_admin import show
        show()
    elif page == "📋 Autonomous Activations":
        from app_pages.claims import show
        show()
    elif page == "🛡️ Integrity Guard":
        from app_pages.fraud import show
        show()
    elif page == "📈 Strategic Analytics":
        from app_pages.analytics import show
        show()
    elif page in ["💬 AI Assistant"]:
        from app_pages.chatbot import show
        show()
    elif page == "🏠 My Dashboard":
        from app_pages.dashboard_worker import show
        show()
    elif page == "🛡️ My Coverage":
        from app_pages.policies import show
        show()
    elif page == "💰 My Payouts":
        from app_pages.claims import show
        show()
    elif page == "🔮 Predictive Warning":
        from app_pages.predictive_warning import show
        show()
    elif page == "⚙️ System Settings":
        from app_pages.admin import show
        show()

if __name__ == "__main__":
    main()
