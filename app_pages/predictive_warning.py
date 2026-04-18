import streamlit as st
from services.environmental_api import EnvironmentalAPI
from ui.theme import style_metric_card, badge, success_box, warning_box, error_box, info_box
from config.city_tiers import CITY_TIERS

def compute_warning_risk(rain, temp, aqi):
    # Rule-based calculation from 0 to 100
    risk = 0.0
    
    # Rainfall heavily contributes
    if rain > 100: risk += 60
    elif rain > 50: risk += 40
    elif rain > 20: risk += 20
    elif rain > 5:  risk += 10
    
    # AQI moderately contributes
    if aqi > 300: risk += 30
    elif aqi > 200: risk += 20
    elif aqi > 100: risk += 10
    
    # Heat moderately contributes
    if temp > 42: risk += 25
    elif temp > 38: risk += 15
    elif temp > 35: risk += 5
    
    risk = min(100.0, risk)
    
    if risk > 60:
        return risk, "HIGH", "danger"
    elif risk > 30:
        return risk, "MEDIUM", "warning"
    else:
        return risk, "LOW", "success"

def generate_prediction(rain, temp, aqi):
    if rain > 50:
        return "High rain disruption risk expected in next 3 hours."
    elif aqi > 200:
        return "AQI likely to worsen in the next 4 hours. Visibility & health risks elevated."
    elif temp > 38:
        return "Moderate heat stress expected to peak by afternoon."
    elif rain > 10:
        return "Scattered showers expected to intensify slightly. Minor delivery delays likely."
    else:
        return "Conditions expected to remain stable for the next 6 hours."

def generate_suggestions(risk_level, rain, temp, aqi):
    suggestions = []
    if risk_level == "HIGH":
        suggestions.append("⚠️ **Avoid High-Risk Zones:** Pause deliveries in flood-prone or extreme AQI sectors.")
        suggestions.append("⚠️ **Prepare for Downtime:** Significant order volume suppression expected.")
    elif risk_level == "MEDIUM":
        suggestions.append("⚠️ **Stay Vigilant:** Traffic delays expected. Equip appropriate gear.")
        if rain > 20: suggestions.append("☔ Monitor rainfall. Consider shifting operation hours.")
        if temp > 38: suggestions.append("💧 Maintain hydration. Take breaks between long routes.")
    else:
        suggestions.append("✅ **Conditions Clear:** Standard operating procedure.")
        suggestions.append("✅ Expect normal delivery volume and transit times.")
    return suggestions

def show():
    # Initialize demo state securely
    if 'demo_rain_boost' not in st.session_state:
        st.session_state.demo_rain_boost = 0.0
    if 'demo_aqi_boost' not in st.session_state:
        st.session_state.demo_aqi_boost = 0.0

    st.markdown("## 📡 Predictive Warning Intelligence System")
    st.write("Proactive environmental hazard tracking and worker impact forecasting.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        cities = list(CITY_TIERS.keys())
        selected_city = st.selectbox("🌍 Select Operation Branch", cities, index=cities.index("Chennai") if "Chennai" in cities else 0)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Simulate Heavy Rain / Disruption Event", use_container_width=True):
            st.session_state.demo_rain_boost = 85.0
            st.session_state.demo_aqi_boost = 150.0
            st.rerun()
            
        if st.session_state.demo_rain_boost > 0:
            if st.button("🔄 Reset Simulation", use_container_width=True):
                st.session_state.demo_rain_boost = 0.0
                st.session_state.demo_aqi_boost = 0.0
                st.rerun()

    st.markdown("---")
    
    # ── 1. LIVE DATA CARDS ──
    try:
        env_data = EnvironmentalAPI.fetch_current_conditions(selected_city)
        # Apply secure demo boost isolated dynamically
        rain_val = env_data["rainfall_mm"] + st.session_state.demo_rain_boost
        aqi_val = env_data["aqi"] + st.session_state.demo_aqi_boost
        temp_val = env_data["temperature"]
        is_live = env_data["is_real_data"]
        src = env_data["source"]
    except Exception as e:
        rain_val, aqi_val, temp_val, is_live, src = 0, 0, 0, False, "Error fallback"
        st.error("Sensor communication failure.")

    st.markdown("### 🌡️ Current Local Telemetry")
    t1, t2, t3, t4 = st.columns(4)
    with t1: style_metric_card("Temperature", f"{temp_val}°C")
    with t2: style_metric_card("Rainfall", f"{rain_val} mm")
    with t3: style_metric_card("AQI", f"{int(aqi_val)}")
    with t4: 
        weather_cond = "Clear" if rain_val == 0 else "Rain" if rain_val < 50 else "Heavy Rain"
        style_metric_card("Condition", weather_cond)
        
    st.caption(f"**Data Stream:** `{src}`")

    # ── 2. PREDICTIVE RISK ENGINE ──
    risk_score, risk_lvl, risk_color = compute_warning_risk(rain_val, temp_val, aqi_val)
    
    st.markdown("### 🔮 Proactive Intelligence Forecast")
    
    p1, p2 = st.columns([1, 1.5])
    with p1:
        color_val = "var(--danger)" if risk_lvl == "HIGH" else ("var(--warning)" if risk_lvl == "MEDIUM" else "var(--success)")
        style_metric_card("Short-Term Disruption Risk", f"{int(risk_score)} / 100", text_color=color_val, delta=f"STATUS: {risk_lvl}")
    
    with p2:
        prediction_text = generate_prediction(rain_val, temp_val, aqi_val)
        if risk_lvl == "HIGH":
            error_box("CRITICAL FORECAST", prediction_text)
        elif risk_lvl == "MEDIUM":
            warning_box("ELEVATED RISK", prediction_text)
        else:
            success_box("STABLE FORECAST", prediction_text)

    # ── 3. PERSONAL IMPACT ESTIMATION ──
    st.markdown("---")
    st.markdown("### 💼 Personal Impact & Readiness")
    
    i1, i2 = st.columns([1, 2])
    with i1:
        hourly_wage = st.number_input("Average Hourly Income (₹)", min_value=50, max_value=500, value=120, step=10)
    
    with i2:
        # Estimate downtime based on risk
        est_downtime = 0
        if risk_score > 60: est_downtime = 4
        elif risk_score > 30: est_downtime = 2
        
        income_loss = est_downtime * hourly_wage
        
        if est_downtime > 0:
            st.markdown(f"**Estimated Downtime:** {est_downtime} hours")
            st.markdown(f"**Expected Income Loss:** <span style='color:red;font-weight:bold;'>₹{income_loss}</span>", unsafe_allow_html=True)
            st.info("🛡️ **Coverage Readiness:** Active & Monitoring. JARVIS will auto-settle if parametric limits are breached.")
        else:
            st.markdown("**Estimated Downtime:** `0 hours`")
            st.markdown("**Expected Income Loss:** `₹0`")
            st.success("🛡️ **Coverage Readiness:** Active (Standby Mode)")

    # ── 4. ACTIONABLE SUGGESTIONS & EXPLAINABILITY ──
    st.markdown("---")
    s1, s2 = st.columns(2)
    
    with s1:
        st.markdown("#### 🎯 Actionable Guard Rails")
        sugs = generate_suggestions(risk_lvl, rain_val, temp_val, aqi_val)
        for s in sugs:
            st.markdown(s)
            
    with s2:
        st.markdown("#### 🧠 Why JARVIS Warned")
        with st.container(border=True):
            if risk_score <= 30:
                st.write("- All physical parameters within nominal operating ranges.")
                st.write("- No intersecting hazards detected in the local grid.")
            else:
                if rain_val > 20: st.write(f"- Rainfall volume ({rain_val}mm) crossed early disruption threshold.")
                if aqi_val > 200: st.write(f"- Air Quality Index ({int(aqi_val)}) is intersecting high-risk respiratory zones.")
                if temp_val > 38: st.write(f"- Thermal footprint ({temp_val}°C) reaching fatigue limitations.")
                st.write(f"- Combined spatial risk index escalated to **{risk_lvl}** probability.")
