"""
Claims Audit Ledger — JARVIS EnviroSense Assurance
Guidewire-Grade Technical Audit: DNA Math Settlement traces and Hyperlocal Identity.
"""
import streamlit as st
from services.repositories.claim_repository import ClaimRepository
from ui.theme import style_metric_card, badge

def show():
    st.markdown("## 🗒️ Global Settlement Ledger")
    st.caption("Immutable system-of-record with deterministic DNA math audit traces.")

    claim_repo = ClaimRepository()
    all_claims = claim_repo.find_many({}, limit=30, sort_field="created_at", sort_order=-1)
    
    if not all_claims:
        st.info("No system activations recorded yet in the current cycle.")
        return

    col_list, col_trace = st.columns([1, 1.8])

    with col_list:
        st.markdown("### Events")
        for c in all_claims:
            cid = c.get('claim_id', c.get('id', 'N/A'))
            with st.container(border=True):
                icon = "💸" if c.get('status') in ["PAID", "SETTLED_AFTER_REVIEW"] else "🛡️"
                res = "PAID" if c.get('status') in ["PAID", "SETTLED_AFTER_REVIEW"] else c.get('status', 'BLOCKED')
                btn_label = f"{icon} {cid} | {res}"
                if st.button(btn_label, key=f"btn_{cid}", use_container_width=True):
                    st.session_state.audit_trace_id = cid

    with col_trace:
        first_cid = all_claims[0].get('claim_id', all_claims[0].get('id', 'N/A')) if all_claims else 'N/A'
        trace_id = st.session_state.get('audit_trace_id', first_cid)
        c = next((item for item in all_claims if item.get("claim_id", item.get("id")) == trace_id), None)
        
        if c:
            st.markdown(f"### 🔍 Deep Trace Audit: `{trace_id}`")
            with st.container(border=True):
                # Regional HUD
                h1, h2, h3 = st.columns(3)
                h1.write(f"**City:** {c.get('city', 'Chennai')}")
                h2.write(f"**Zone:** {c.get('zone_id', 'South-Zone')}")
                dc = c.get('decision_confidence', 85.0)
                metric_label = "Decision Confidence"
                if c.get("decision_confidence_source") == "derived":
                    metric_label = "Decision Confidence (Derived)"
                
                h3.metric(metric_label, f"{dc}%")

                
                st.divider()

                # 📌 XAI DECISION EXPLAINABILITY
                st.markdown("**📌 Why this decision? (XAI Panel)**")
                with st.container(border=True):
                    st.write(f"✔ **Trigger:** {c.get('trigger_conditions', 'Disruption threshold met')}")
                    risk_score = round((100 - c.get("loyalty_score", 0.92)*100)/100, 2)
                    st.write(f"✔ **Risk Score:** {risk_score} (Zone: {c.get('zone_id', 'South-Zone')})")
                    fraud_score = c.get('fraud_score', 0)
                    if fraud_score > 60:
                        st.markdown(f"⚠ **Fraud Score:** <span style='color:red;'>{fraud_score} (CRITICAL)</span>", unsafe_allow_html=True)
                        st.markdown(f"⚠ **Fraud Reason:** {c.get('fraud_explanation', 'Anomalous pattern detected')}", unsafe_allow_html=True)
                        st.write(f"→ **Decision:** {c.get('status', 'BLOCKED')}")
                    else:
                        st.write(f"✔ **Fraud Score:** {fraud_score} (Safe)")
                        comp_tag = c.get('compliance', {}).get('decision', 'APPROVE') if isinstance(c.get('compliance'), dict) else 'Passed'
                        st.write(f"✔ **Compliance:** {comp_tag}")
                        st.write(f"→ **Decision:** {c.get('status', 'APPROVED')}")

                st.divider()

                # ⏱️ DECISION TIMELINE
                st.markdown("**⏱️ System Decision Timeline**")
                with st.container(border=True):
                    if c.get('audit_trail'):
                        for step in c['audit_trail']:
                            ts_str = step.get('ts', str(c.get('created_at', '')))
                            try:
                                if 'T' in ts_str:
                                    time_only = ts_str.split('T')[1][:8]
                                else:
                                    time_only = ts_str[11:19] if len(ts_str) > 15 else ts_str[:8]
                            except:
                                time_only = "00:00:00"
                            st.markdown(f"`[{time_only}]` {step.get('narration', 'Processing signal...')}")
                    else:
                        st.caption("`[00:00:00]` Direct autonomous execution via sensor trigger.")
                
                st.divider()

                # 🧮 DNA MATH
                st.markdown("**🧮 Settlement DNA Math**")
                if c.get('status') in ["FLAGGED", "BLOCKED", "REJECTED_COMPLIANCE", "REJECTED"]:
                    st.error(f"🛡️ **INTEGRITY GUARD: Transaction {c.get('status')}**")
                    st.write(f"**Reason:** {c.get('fraud_explanation', 'Anomalous behavior signature detected.')}")
                elif c.get('status') == "REVIEW":
                    st.warning("⚖️ **ROUTED TO MANUAL AUDIT (REVIEW)**")
                    st.write(f"**Status Info:** {c.get('governance_status', 'Pending offline confirmation')}")
                else:
                    st.success(f"✅ **AUTO-DISBURSEMENT: {c.get('status')}**")
                    st.code(c.get('payout_math', "Base \u00d7 Trust \u00d7 ECI \u00d7 Liquidity \u00d7 Zone"), language="text")
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Final Payout", f"₹{c.get('payout_amount', c.get('amount', 0)):,}")
                    m2.write(f"**Network Ref:** `{c.get('payout_ref', c.get('payout_id', 'N/A'))}`")
                    m3.write(f"**Latency:** {c.get('processing_time_ms', 0)}ms")

                if c.get('stress_response'):
                    st.warning(f"💡 {c['stress_response']}")

        else:
            st.info("Select a transaction from the ledger to view the technical DNA trace.")

    st.markdown("<br><br><div class='footer'>🛡️ JARVIS EnviroSense — Financial Orchestration Engine | Guidewire Hackathon Entry</div>", unsafe_allow_html=True)
