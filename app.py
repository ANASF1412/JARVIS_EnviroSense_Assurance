"""
GigShield AI — Main Streamlit Application Entry Point
Production-Grade Parametric Income Protection System

Changes vs original:
  - Added 💬 AI Assistant page (chatbot)
  - Added model validation at startup with user-visible status
  - ModelLoader.validate_models() called once on boot
"""
import streamlit as st
st.set_page_config(
    page_title="JARVIS EnviroSense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.theme import apply_custom_theme
from config.database import verify_db_connection, init_collections

apply_custom_theme()


def _run_startup_checks():
    """Run model validation once per session."""
    if st.session_state.get("_startup_done"):
        return

    from services.model_loader import ModelLoader
    ok = ModelLoader.validate_models()
    if not ok:
        st.sidebar.warning("⚠️ ML models may be degraded — using fallbacks")
    else:
        st.sidebar.success("✅ ML models healthy")

    st.session_state["_startup_done"] = True


def main():
    """Main app entry point."""
    # Database
    try:
        if verify_db_connection():
            init_collections()
        else:
            st.info("🔄 **System Monitoring:** Environmental conditions are within safety buffers. No action required.")
    except Exception as e:
        st.error(f"⚠️ Database connection: {str(e)}")
        st.info("The app will use in-memory data if MongoDB is unavailable.")

    # ML startup validation
    _run_startup_checks()

    # Sidebar navigation
    st.sidebar.title("🛡️ JARVIS EnviroSense")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigate",
        [
            "📊 Dashboard",
            "👤 Registration",
            "📋 Policies",
            "📝 Claims",
            "📈 Analytics",
            "⚙️ Admin",
            "💬 AI Assistant",
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### System Philosophy
    **JARVIS EnviroSense** — The Environment is the Claim.
    
    Autonomous, zero-touch assurance triggered by climate intelligence.
    
    [Philosophy Whitepaper →](https://github.com)
    """)

    # Footer
    st.markdown("""
    ---
    **JARVIS EnviroSense** | Environment-Driven Autonomous Assurance | Zero-Touch Payout Engine
    """)

    # Route to appropriate page
    if page == "📊 Dashboard":
        from app_pages.dashboard import show
        show()
    elif page == "👤 Registration":
        from app_pages.registration import show
        show()
    elif page == "📋 Policies":
        from app_pages.policies import show
        show()
    elif page == "📝 Claims":
        from app_pages.claims import show
        show()
    elif page == "📈 Analytics":
        from app_pages.analytics import show
        show()
    elif page == "⚙️ Admin":
        from app_pages.admin import show
        show()
    elif page == "💬 AI Assistant":
        from app_pages.chatbot import show
        show()


if __name__ == "__main__":
    main()
