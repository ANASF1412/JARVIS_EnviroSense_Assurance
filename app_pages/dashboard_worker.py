"""
Worker Partner HUD — JARVIS EnviroSense Assurance
Transparency Layer: Economic Explainability and Personal Protection Metrics.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from ui.theme import style_metric_card, badge, success_box, info_box, error_box, warning_box

def show():
    if "user" not in st.session_state or "data" not in st.session_state:
        st.error("Session identity lost. Please re-authenticate.")
        return

    user = st.session_state.user
    data = st.session_state.data
    
    st.markdown(f"## 👋 Welcome back, {user['name']}")
    st.caption(f"Protecting your income in **{user['city']}** | **{user['zone']}**")

    is_live = False
    try:
        from services.supabase_service import get_supabase_client
        if get_supabase_client(): is_live = True
    except: pass
    
    if is_live:
        st.markdown("<div style='text-align: right; margin-top: -40px; margin-bottom: 20px;'><span style='background: #111827; padding: 5px 12px; border-radius: 20px; font-size: 0.8em; color: #a7f3d0; border: 1px solid #059669;'>🟢 LIVE MODE — Cloud Connected</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: right; margin-top: -40px; margin-bottom: 20px;'><span style='background: #111827; padding: 5px 12px; border-radius: 20px; font-size: 0.8em; color: #fde68a; border: 1px solid #d97706;'>🟡 FALLBACK MODE — Synced Cache Active</span></div>", unsafe_allow_html=True)

    # 💠 PERSONAL KPI HUB
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    with stat_col1:
        style_metric_card("Total Aid Received", f"₹{data.get('statistics', {}).get('total_payouts', 0):,}", help_text="Total sum disbursed to you across all events.")
    with stat_col2:
        style_metric_card("Trust Score", f"{user.get('rating', 4.5)}", delta="+5% Trust Bonus Active")
    with stat_col3:
        style_metric_card("Active Policies", "Monsoon + AQI", help_text="Multi-hazard coverage enabled.")

    st.markdown("---")

    # 💠 BEHAVIORAL INCENTIVES & NCB PROFILE
    st.markdown("### 🏆 No Claim Bonus (NCB) Rewards")
    ncb_streak = user.get("ncb_streak", 0)
    ncb_discount_rate = user.get("ncb_discount_rate", 0.0)
    
    from services.ncb_service import NCBService
    ncb_tier_label = NCBService.get_tier_label(ncb_streak)
    next_rate = NCBService.get_discount_rate(ncb_streak + 1)
    
    # Optional savings projection
    base_premium_demo = 45.0
    discounted_amount = base_premium_demo * ncb_discount_rate
    
    ncb_1, ncb_2 = st.columns([1, 1.5])
    with ncb_1:
        color_val = "var(--success)" if ncb_streak > 0 else "var(--text-primary)"
        style_metric_card("Safe Worker Streak", f"{ncb_streak} Weeks", text_color=color_val, delta=f"Status: {ncb_tier_label}")
        
    with ncb_2:
        if ncb_streak > 0:
            success_box(f"NCB Active — {int(ncb_discount_rate * 100)}% Discount", f"You saved ₹{int(discounted_amount)} this week. 1 more claim-free week unlocks {int(next_rate * 100)}% discount. Minimum premium floor protection is active to preserve coverage fairness.")
        else:
            info_box("NCB Standby", f"Complete your current weekly coverage cycle with zero claims to unlock a {int(next_rate * 100)}% premium discount for your next renewal.")

    st.markdown("---")

    # 💠 COVERAGE & ECONOMIC CONTEXT
    c_col1, c_col2 = st.columns([1.5, 1])

    with c_col1:
        st.markdown("### 🛡️ Coverage Lifecycle & Payments")
        
        from datetime import datetime, timedelta
        policy = data.get("active_policy")
        latest = data.get("latest_policy")
        
        status_label = "EXPIRED"
        if policy and policy.get("active"):
            end_d = datetime.fromisoformat(policy["end_date"])
            now_d = datetime.now()
            hours_left = (end_d - now_d).total_seconds() / 3600
            
            if hours_left < 24:
                status_label = "EXPIRING SOON"
            else:
                status_label = "ACTIVE"
        
        with st.container(border=True):
            if status_label in ["ACTIVE", "EXPIRING SOON"]:
                st.markdown(f"**Coverage Status:** <span class='badge badge-{'warning' if status_label == 'EXPIRING SOON' else 'success'}'>{status_label}</span>", unsafe_allow_html=True)
                st.markdown(f"**Policy Node:** `{policy['policy_id']}`")
                st.write(f"**Active Window:** {policy['start_date'][:16].replace('T', ' ')} \u2192 **{policy['end_date'][:16].replace('T', ' ')}**")
                st.write(f"**Weekly Premium:** ₹{policy.get('weekly_premium', 45):,} (Paid via {policy.get('payment_ref', 'Wallet')})")
                
                st.markdown("**Protected Against:** 🌧️ Heavy Rain | 🌫️ AQI Spikes | 🌡️ Heatwave")
                
                if status_label == "EXPIRING SOON":
                    warning_box("Renewal Required", "Your weekly protection expires soon. Renew now to stay covered and protect your streak.")
                    if st.button("🔄 Renew Coverage for 7 Days (₹45)", type="primary", use_container_width=True):
                        # Trigger Renewal
                        from services.policy_service import PolicyService
                        ps = PolicyService()
                        res = ps.renew_policy(policy["policy_id"], duration_days=7)
                        if res["success"]:
                            st.success(res["message"])
                            st.rerun()
                else:
                    success_box("System Online", "Monitoring live signals. You are protected.")
            else:
                st.markdown(f"**Coverage Status:** <span class='badge badge-error'>EXPIRED</span>", unsafe_allow_html=True)
                if latest:
                    st.write(f"**Last Active:** Ended {latest['end_date'][:16].replace('T', ' ')}")
                
                error_box("Protection Offline", "Coverage expired or inactive. Pay your weekly premium to reactivate protection immediately.")
                
                if st.button("💳 Pay & Activate 7-Day Coverage (₹45)", type="primary", use_container_width=True):
                    # Trigger Mock Razorpay & Policy Creation
                    from services.policy_service import PolicyService
                    import uuid
                    import time
                    ps = PolicyService()
                    with st.spinner("Processing secure mock payment..."):
                        time.sleep(0.4) # Simulate network
                        try:
                            # Safely fetch premium config instead of hardcoding
                            from services.premium_calculator import PremiumCalculator
                            calc = PremiumCalculator()
                            res_calc = calc.calculate_premium(0, 30, 50, user.get('city', 'Chennai'), worker_id=user['worker_id'])
                            prem = res_calc['weekly_premium']
                            payment_id = f"rzp_test_{uuid.uuid4().hex[:8].upper()}"
                            
                            res = ps.policy_repo.create_policy(
                                worker_id=user['worker_id'],
                                weekly_premium=prem,
                                coverage_limit=user.get('hourly_income', 100) * 40,
                                duration_days=7,
                                payment_ref=payment_id
                            )
                            st.toast(f"✅ Payment {payment_id} Successful!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Payment simulation failed: {e}")

    with c_col2:
        st.markdown("### 💡 Premium Explainability")
        with st.container(border=True):
            st.write("**Why your premium is ₹45/week:**")
            
            from config.city_tiers import get_city_tier_context
            city_ctx = get_city_tier_context(user.get('city', 'Chennai'))
            
            if 'automation_engine' not in st.session_state:
                from services.automation_engine import AutomationEngine
                st.session_state.automation_engine = AutomationEngine()
                
            zr = st.session_state.automation_engine.compute_zone_risk(user.get('zone', 'South-Zone'))
            
            st.markdown(f"✔ **City Tier Rating ({city_ctx['tier']})** → Premium adjusted for **{user.get('city')}** macroeconomy (Pressure modifier: {city_ctx['base_premium_modifier']}x)")
            st.markdown(f"✔ **Hyper-Local Zone Risk ({zr['level']})** → Your zone (**{user.get('zone')}**) shows {zr['status_badge']} risk behavior.")
            st.markdown(f"✔ **Trust Score ({user.get('rating', 4.5)})** → loyalty discount applied.")
            
            st.info("Your smart policy adapts automatically to dynamic local conditions.")

    st.markdown("---")

    # 💠 SETTLEMENT HISTORY
    st.markdown("### 💰 Recent Automatic Settlements")
    
    import json
    import os
    recent_payouts = []
    if os.path.exists("data/payout_audit_db.json"):
        try:
            with open("data/payout_audit_db.json", "r") as f:
                all_p = json.load(f)
                wid = user.get("id", user.get("worker_id", user.get("name"))) # fallback to name if no id for demo
                if wid:
                    recent_payouts = [x for x in all_p if x.get("worker_id") == wid or x.get("worker_id") == "W001"] # demo fallback
                else:
                    recent_payouts = all_p
                recent_payouts.reverse()
        except Exception:
            pass
            
    if not recent_payouts:
        recent_payouts = data.get("recent_payouts", [])
    
    if recent_payouts:
        for p in recent_payouts[:5]:
            p_time = p.get('created_at', p.get('timestamp', ''))[:10]
            with st.expander(f"₹{p['amount']} Distributed — {p_time}", expanded=False):
                st.write(f"**Reference:** `{p['payout_id']}`")
                st.write(f"**Network Status:** {p['status']} ✨")
                if 'method' in p:
                    st.write(f"**Payout Method:** `{p['method']}`")
                    st.write(f"**Compliance Confidence:** `{p.get('compliance_confidence', 'HIGH')}`")
                
                # Show math DNA for transparency
                math = p.get("math", "Base \u00d7 Trust \u00d7 Regional Risk \u00d7 Economy Factor")
                st.code(math, language="text")
                st.caption("⚡ Settlement was pushed automatically after rainfall threshold exceeded 85mm.")
    else:
        info_box("No Active Payouts", "The environment is stable. No disruptions detected in your zone.")

    # 💠 MAP VISUALIZATION & LIVE ZONE CONDITIONS
    st.markdown("### 🗺️ Live Regional Monitoring")
    from services.environmental_api import EnvironmentalAPI
    api_snap = EnvironmentalAPI.get_live_environment_snapshot(user.get('city', 'Chennai'))
    
    with st.container(border=True):
        st.write(f"**Live Environmental Data Source:** `{api_snap['source']}`")
        if not api_snap['is_real_data'] if 'is_real_data' in api_snap else "FALLBACK" in api_snap['source']:
            st.warning("⚠️ Using safe fallback data because live environmental APIs are currently unreachable.")
        st.write(f"**Rainfall:** {api_snap['values']['rain']} | **Temperature:** {api_snap['values']['temp']} | **AQI:** {api_snap['values']['aqi']}")
        
        try:
            r_val = float(str(api_snap['values']['rain']).replace('mm', '').strip())
        except:
            r_val = 0.0
            
        if r_val > 50:
            st.error(f"🚨 Heavy rainfall ({r_val}mm) detected in your zone. Coverage triggers are actively evaluating.")
        elif r_val > 10:
            st.warning(f"🌧️ Moderate rainfall ({r_val}mm) detected in your zone. Coverage is ready.")
        else:
            st.success("🌤️ Weather is normal in your zone. Coverage is active for instant response if conditions change.")
        
    # Render proper Folium Map
    from services.map_service import render_worker_map
    render_worker_map(13.0827, 80.2707, user.get('city', 'Chennai'), source_status=api_snap['source'])

    # 🤖 AI CHATBOT ASSISTANT
    st.markdown("### 🤖 JARVIS Assistant")
    with st.expander("💬 Ask JARVIS Support (Claims, Cover, Premium)", expanded=False):
        from services.chatbot_service import EnviroSenseChatbot
        if "bot_history_worker" not in st.session_state:
            st.session_state.bot_history_worker = []
            
        bot = EnviroSenseChatbot()
        ctx = bot.collect_context(worker_id=user["worker_id"], rainfall_mm=r_val)
        
        for msg in st.session_state.bot_history_worker:
            role = "user" if msg["role"] == "user" else "assistant"
            with st.chat_message(role, avatar="🧑‍💻" if role=="user" else "🤖"):
                st.write(msg["content"])
                
        # Smart suggestions
        suggs = bot.get_smart_suggestions(ctx)
        
        if len(st.session_state.bot_history_worker) == 0:
            st.info("💡 **Try asking JARVIS:**")
            cols = st.columns(min(len(suggs), 4))
            for i, s in enumerate(suggs[:4]):
                with cols[i]:
                    st.caption(s)

        user_input = st.chat_input("Ask JARVIS anything about your coverage...")
        if user_input:
            st.session_state.bot_history_worker.append({"role": "user", "content": user_input})
            st.rerun()

        # Handle un-answered user messages
        if len(st.session_state.bot_history_worker) > 0 and st.session_state.bot_history_worker[-1]["role"] == "user":
            user_msg = st.session_state.bot_history_worker[-1]["content"]
            with st.spinner("JARVIS is thinking..."):
                resp = bot.chat(user_msg, st.session_state.bot_history_worker[:-1], ctx)
                st.session_state.bot_history_worker.append({"role": "assistant", "content": resp})
            st.rerun()

    st.markdown("<br><br><div class='footer'>🛡️ JARVIS EnviroSense — Financial Orchestration Engine | Worker Partner Interface</div>", unsafe_allow_html=True)
