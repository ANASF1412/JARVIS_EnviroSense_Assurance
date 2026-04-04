"""
PAGE: AI Assistant (Chatbot)
Context-aware insurance advisor powered by Claude via Anthropic API.
Integrates with all GigShield AI modules for real data-grounded answers.
"""

import streamlit as st
from services.chatbot_service import EnviroSenseChatbot
from services.repositories.worker_repository import WorkerRepository


def show():
    """Render the AI Assistant chatbot page."""
    st.title("💬 JARVIS EnviroSense Assistant")
    st.markdown("### **Intelligent Assurance Advisor**")
    st.caption("No claims. No requests. No waiting. Just automatic assurance.")

    # ── Initialise session state ──────────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_context" not in st.session_state:
        st.session_state.chat_context = None
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = EnviroSenseChatbot()

    chatbot: EnviroSenseChatbot = st.session_state.chatbot

    # ── Sidebar: context config ───────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        ---
        **JARVIS EnviroSense Assurance** | Zero-Touch Autonomous Protection
        """)

        # Worker selector
        try:
            worker_repo = WorkerRepository()
            workers = worker_repo.get_all_workers(limit=50)
            worker_options = ["(No worker — general queries)"] + [
                f"{w['worker_id']} — {w['name']}" for w in workers
            ]
        except Exception:
            workers = []
            worker_options = ["(Database unavailable)"]

        selected_worker_str = st.selectbox("Worker context", worker_options)
        worker_id = None
        if "—" in selected_worker_str:
            worker_id = selected_worker_str.split("—")[0].strip()

        st.markdown("**Current Weather Conditions**")
        rainfall_mm = st.slider("Rainfall (mm)", 0.0, 200.0, 10.0, 5.0)
        temperature  = st.slider("Temperature (°C)", 15.0, 50.0, 32.0, 0.5)
        aqi          = st.slider("AQI", 0.0, 500.0, 120.0, 10.0)

        if st.button("🔄 Refresh Context", use_container_width=True):
            st.session_state.chat_context = chatbot.collect_context(
                worker_id=worker_id,
                rainfall_mm=rainfall_mm,
                temperature=temperature,
                aqi=aqi,
            )
            st.success("Context updated!")

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    # ── Collect context on first load ─────────────────────────────────────────
    if st.session_state.chat_context is None:
        with st.spinner("Loading your data..."):
            st.session_state.chat_context = chatbot.collect_context(
                worker_id=worker_id,
                rainfall_mm=rainfall_mm,
                temperature=temperature,
                aqi=aqi,
            )

    ctx = st.session_state.chat_context

    # ── Context summary card ──────────────────────────────────────────────────
    with st.expander("📊 Live Context Loaded", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            if ctx.get("worker"):
                w = ctx["worker"]
                st.metric("Worker", w.get("name", "—"))
                st.caption(f"Zone: {w.get('delivery_zone','—')} | ₹{w.get('avg_hourly_income','—')}/hr")
            else:
                st.metric("Worker", "None selected")

        with col2:
            if ctx.get("risk_assessment"):
                r = ctx["risk_assessment"]
                st.metric("Risk Score", f"{r['risk_score']:.3f}", delta=r["risk_level"])
            else:
                st.metric("Risk Score", "—")

        with col3:
            if ctx.get("active_policy"):
                p = ctx["active_policy"]
                st.metric("Weekly Premium", f"₹{p.get('weekly_premium','—')}")
            else:
                st.metric("Policy", "No active policy")

        claims = ctx.get("recent_claims", [])
        if claims:
            st.caption(f"📋 {len(claims)} recent claim(s) loaded. Latest: "
                       f"{claims[0].get('claim_status','?')} — "
                       f"{claims[0].get('event_type','?')}")

        if not ctx.get("db_available"):
            st.warning("⚠️ Database unavailable — showing ML predictions only")

    # ── Smart suggestions ─────────────────────────────────────────────────────
    suggestions = chatbot.get_smart_suggestions(ctx)
    if not st.session_state.chat_history:
        st.markdown("**💡 Suggested questions:**")
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                    st.session_state._pending_message = suggestion

    # ── Chat history display ──────────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        for turn in st.session_state.chat_history:
            with st.chat_message(turn["role"]):
                st.markdown(turn["content"])

    # ── Handle pre-filled message from suggestion buttons ────────────────────
    pending = st.session_state.pop("_pending_message", None)

    # ── Chat input ────────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask about your policy, claims, risk score, premium...")

    message_to_send = pending or user_input

    if message_to_send:
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(message_to_send)

        # Append to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": message_to_send,
        })

        # Get response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chatbot.chat(
                        user_message=message_to_send,
                        history=st.session_state.chat_history[:-1],  # exclude current user msg
                        ctx=ctx,
                    )
                st.markdown(response)

        # Append assistant response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response,
        })

        st.rerun()

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.caption(
        "🛡️ JARVIS EnviroSense Assistant | Powered by Claude | "
        "Answers are based on live data from your account and real ML predictions. "
    )
