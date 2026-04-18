"""
Phase 3 Login Page - Role & Worker Selection
"""
import streamlit as st

def show():
    st.markdown("<h1 style='text-align: center;'>🛡️ JARVIS EnviroSense Assurance</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Autonomous Urban Resilience System</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container(border=True):
            st.subheader("🔑 Access Portal")
            
            tab_worker, tab_admin = st.tabs(["🚴 Worker Login", "🏢 Admin Login"])
            
            with tab_worker:
                workers = {
                    "Ramesh (W001)": "W001",
                    "Arjun (W002)": "W002",
                    "Priya (W003)": "W003",
                    "Surya (W004)": "W004",
                    "Karthik (W010)": "W010"
                }
                selected_name = st.selectbox("Select Worker Identity", options=list(workers.keys()))
                
                if st.button("Enter Worker Dashboard", type="primary", use_container_width=True):
                    st.session_state.role = "worker"
                    st.session_state.worker_id = workers[selected_name]
                    st.rerun()
            
            with tab_admin:
                st.info("Authorized personnel ONLY. Access is logged.")
                if st.button("Enter Admin Control Center", type="secondary", use_container_width=True):
                    st.session_state.role = "admin"
                    st.rerun()
                    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()
    st.caption("💡 **Phase 3 Scalability Note:** Login system now supports distinct identity-based routing while maintaining zero-touch automation across all profiles.")
