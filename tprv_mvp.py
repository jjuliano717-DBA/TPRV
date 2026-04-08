import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
from datetime import datetime

# Try to import OpenAI for the Live LLM integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# --- PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Enterprise AI Risk Platform V21", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
div.stButton > button:first-child { font-weight: 500; border: 1px solid #38bdf8; }
.metric-box { background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px; }
.sor-green { color: #10b981; font-weight: bold; }
.sor-red { color: #ef4444; font-weight: bold; }
.partner-box { border: 1px solid #475569; padding: 20px; border-radius: 8px; background-color: #1e293b; margin-bottom: 20px;}
</style>""", unsafe_allow_html=True)

# --- MOCK DATA GENERATION (V21) ---
@st.cache_data
def generate_claims_data():
    """Generates the enhanced 200-row Loss Run dataset per Doc's requirements."""
    np.random.seed(42)
    n_claims = 200
    osha_roles = ["Warehouse Associate", "Forklift Operator", "Delivery Driver", "Office Manager", "Maintenance Tech"]
    genders = ["Male", "Female", "Non-Binary"]
    departments = ["Logistics", "Operations", "Admin", "Facilities"]
    
    data = {
        "Claim_ID": [f"CLM-{1000+i}" for i in range(n_claims)],
        "Date": pd.date_range(start="2024-01-01", periods=n_claims, freq="D"),
        "OSHA_Role": np.random.choice(osha_roles, n_claims),
        "Department": np.random.choice(departments, n_claims),
        "Claimant_Age": np.random.randint(19, 65, n_claims),
        "Claimant_Gender": np.random.choice(genders, n_claims, p=[0.6, 0.35, 0.05]),
        "COI_Coverage_Valid": np.random.choice(["Yes", "No"], n_claims, p=[0.85, 0.15]),
        "Incurred_Cost": np.random.uniform(1500, 75000, n_claims).round(2),
        "Status": np.random.choice(["Open", "Closed", "In Litigation"], n_claims, p=[0.3, 0.6, 0.1])
    }
    return pd.DataFrame(data)

# --- STATE MANAGEMENT ---
if 'app_state' not in st.session_state:
    st.session_state.app_state = {
        "title": "Claims Adjuster", 
        "jurisdiction": "Texas",
        "reviewer": "Sarah Lee (Chief Risk Officer)",
        "adp_status": "🟢 Active",
        "msp_status": "🟢 Active",
        "biddle_status": "🟢 Verified",
        "service_status": "🟢 Green (Valid)",
        "verified_title": "Claims Adjuster",
        "verified_jur": "Texas",
        "verified_reviewer": "Sarah Lee (Chief Risk Officer)",
        "verified_adp": "🟢 Active",
        "verified_msp": "🟢 Active",
        "verified_biddle": "🟢 Verified",
        "verified_status": "🟢 Green (Valid)",
        "log": [],
        "claims_df": generate_claims_data(),
        "baseline_df": pd.DataFrame({
            "ROLE VALIDATION - AI TOPICS": [
                "Legal Entity Filings",
                "Gross Revenue $",
                "Incident Recovery Plans",
                "Medical Services Codes Reconciliation",
                "Transitional Duty Job Descriptions",
                "OSHA Log Management"
            ],
            "OWNER": [
                "Executive Management", "Finance", "Risk Management", 
                "Risk Management", "Human Resources", "Executive Management"
            ],
            "AUDIT ACTIVITY": [
                "Regulatory Reporting", "Regulatory Reporting", "UW Stewardship", 
                "Healthcare Services Reconciliation", "UW Stewardship", "Regulatory Reporting"
            ],
            "REVIEWER": [
                "Attorney", "Accountant", "Broker", 
                "Medical Services", "HR Admin", "Safety Manager"
            ],
            "SYSTEM OF RECORD": ["Unmapped"] * 6,
            "REVIEWER SYSTEM": ["Unmapped"] * 6,
            "AI STATUS RATINGS": ["Low"] * 6
        }),
        "baseline_score": 0.0,
        "connectors_validated": False
    }

def log_event(outcome, rationale):
    s = st.session_state.app_state
    s["log"].insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Context": f"{s['verified_title']} ({s['verified_jur']}) | Rev: {s['verified_reviewer']}",
        "Outcome": outcome,
        "Rationale": rationale
    })

s = st.session_state.app_state

# --- SIDEBAR: CONFIG & IDENTITY MATRIX ---
with st.sidebar:
    st.header("⚙️ POC Configuration")
    api_key = st.text_input("OpenAI API Key (Optional)", type="password", help="Replace hardcoded responses with real GenAI.")
    
    st.divider()
    st.header("🔌 Federated Systems of Record")
    
    t = st.selectbox("Job Title & WC Code", ["L2 Helpdesk", "Claims Adjuster", "Safety Manager", "Risk Manager"], index=1)
    j = st.selectbox("Jurisdiction", ["Texas", "New York", "Pennsylvania"], index=0)
    adp_stat = st.selectbox("ADP Feed Status", ["🟢 Active", "🔴 Disconnected / Terminated"], index=0)
    msp_stat = st.selectbox("MSP Entra ID Sync", ["🟢 Active", "🔴 Revoked / Offline"], index=0)
    biddle_stat = st.selectbox("Biddle EEO Audit", ["🟢 Verified", "🔴 Unsigned Policy"], index=0)

    st.subheader("TPRV Global Oversight")
    rev = st.selectbox("Assigned Human Reviewer", ["Unassigned", "John Smith (VP HR)", "Sarah Lee (Chief Risk Officer)"], index=2)
    stat = st.selectbox("Service Validation Status", ["🟢 Green (Valid)", "🟡 Yellow (Pending)", "🔴 Red (Expired/Invalid)"], index=0)
    
    if st.button("Sync Federated Network"):
        with st.spinner("Aggregating Systems of Record..."):
            time.sleep(1)
            s.update({"title": t, "jurisdiction": j, "adp_status": adp_stat, "msp_status": msp_stat, "biddle_status": biddle_stat,
                      "reviewer": rev, "service_status": stat,
                      "verified_title": t, "verified_jur": j, "verified_adp": adp_stat, "verified_msp": msp_stat,
                      "verified_biddle": biddle_stat, "verified_reviewer": rev, "verified_status": stat})
            st.rerun()

# --- MAIN UI LAYOUT ---
st.title("🛡️ TruRoles TPV")
st.markdown("### Strategic Assessment, Actuarial Enrichment & Real-World Use Cases")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. AI Systems Baseline", 
    "2. Claims Explorer", 
    "3. AI Gatekeeper Copilot",
    "🏥 Revenue Impact",
    "⚖️ Audit Readiness",
    "📋 Underwriting Analytics"
])

# ==========================================
# TAB 1: AI SYSTEMS BASELINE (FRONT DOOR)
# ==========================================
with tab1:
    st.header("Step 1: AI Role Validation Baseline")
    st.markdown("Map your core enterprise activities to current IT systems and human reviewer systems to establish your initial AI Status Rating.")
    
    system_options = ["Unmapped", "ADP", "Workday", "Salesforce", "ServiceNow", "Excel/Manual", "Custom ERP", "Sedgwick TPA", "Paycom", "Bank Portal", "Legal FileNet"]

    # Visual Progress Bar
    st.progress(int(s["baseline_score"]), text=f"AI Readiness Optimization: {s['baseline_score']:.0f}%")

    edited_df = st.data_editor(
        s["baseline_df"],
        column_config={
            "ROLE VALIDATION - AI TOPICS": st.column_config.Column(disabled=True),
            "OWNER": st.column_config.Column(disabled=True),
            "AUDIT ACTIVITY": st.column_config.Column(disabled=True),
            "REVIEWER": st.column_config.Column(disabled=True),
            "SYSTEM OF RECORD": st.column_config.SelectboxColumn("SYSTEM OF RECORD", options=system_options, required=True),
            "REVIEWER SYSTEM": st.column_config.SelectboxColumn("REVIEWER SYSTEM", options=system_options, required=True),
            "AI STATUS RATINGS": st.column_config.Column(disabled=True)
        },
        use_container_width=True, hide_index=True, key="baseline_editor"
    )
    
    # Calculate Logic: Requires both System of Record and Reviewer System to be mapped to non-manual systems
    def calculate_status(row):
        sys_mapped = row['SYSTEM OF RECORD'] not in ["Unmapped", "Excel/Manual"]
        rev_mapped = row['REVIEWER SYSTEM'] not in ["Unmapped", "Excel/Manual"]
        if sys_mapped and rev_mapped: return "High"
        elif sys_mapped or rev_mapped: return "Medium"
        else: return "Low"
        
    edited_df['AI STATUS RATINGS'] = edited_df.apply(calculate_status, axis=1)
    s["baseline_df"] = edited_df
    
    high_count = len(edited_df[edited_df['AI STATUS RATINGS'] == 'High'])
    total = len(edited_df)
    s["baseline_score"] = (high_count / total) * 100

    cols = st.columns(3)
    cols[0].metric("Enterprise AI Readiness Score", f"{s['baseline_score']:.0f}%", delta=f"{high_count}/{total} Optimized")
    cols[1].metric("Automated Compliance Workflows", f"{int(s['baseline_score'] * 0.8)}%", delta="Projected Efficiency Gain")
    cols[2].metric("Incident Recovery Plan Test Ratio", f"{high_count * 2} / {total * 2}", delta="Audit Ready")

    col_btn1, col_btn2 = st.columns([1, 1])
    
    with col_btn1:
        if st.button("✅ Validate Systems & Establish Baseline", use_container_width=True):
            if s["baseline_score"] >= 40:
                s["connectors_validated"] = True
                st.success("✅ Connectors Aligned. Systems of Record baseline established. Actuarial data unlocked.")
            else:
                st.error("⚠️ Baseline Score too low. Map more systems before unlocking the Claims Engine.")

    with col_btn2:
        # Value-Add Feature: Consultant Export
        csv_export = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download AI Readiness Report (CSV)",
            data=csv_export,
            file_name="AI_Readiness_Baseline_Report.csv",
            mime="text/csv",
            use_container_width=True
        )

# ==========================================
# TAB 2: CLAIMS ENRICHMENT EXPLORER
# ==========================================
with tab2:
    st.header("Step 2: Actuarial Claims Ingestion")
    
    if not s["connectors_validated"]:
        st.warning("🔒 **Data Pipeline Not Established.** Complete the AI Systems Baseline in Tab 1 to unlock this dataset.")
    else:
        st.success("✅ Baseline Approved. Analyzing 200-claim Loss Run with OSHA and Demographic dimensions.")
        
        df_claims = s["claims_df"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Claims Processed", len(df_claims))
        c2.metric("Avg Incurred Cost", f"${df_claims['Incurred_Cost'].mean():,.2f}")
        c3.metric("Missing COI Flags", len(df_claims[df_claims['COI_Coverage_Valid'] == 'No']))
        c4.metric("Litigation Rate", f"{(len(df_claims[df_claims['Status'] == 'In Litigation']) / len(df_claims)) * 100:.1f}%")

        st.dataframe(df_claims, use_container_width=True, height=400)

# ==========================================
# TAB 3: AI GATEKEEPER & COPILOT
# ==========================================
with tab3:
    st.header("Step 3: AI Gatekeeper Copilot")
    
    if not s["connectors_validated"]:
         st.warning("🔒 **Data Pipeline Not Established.** Complete the AI Systems Baseline in Tab 1 to unlock the AI Copilot.")
    else:
        col_matrix, col_chat = st.columns([1, 2.2])
        
        with col_matrix:
            st.markdown("### 🧬 Identity Matrix")
            st.markdown(f"""
            <div class="metric-box">
                <small style="color:#94a3b8">ADP System (HR & Payroll)</small><br>
                <strong>Role:</strong> {s['verified_title']}<br>
                <strong>Location:</strong> {s['verified_jur']}<br>
                <strong>Status:</strong> <span class="{'sor-green' if '🟢' in s['verified_adp'] else 'sor-red'}">{s['verified_adp']}</span>
            </div>
            <div class="metric-box">
                <small style="color:#94a3b8">MSP & Biddle Compliance</small><br>
                <strong>IT Access:</strong> <span class="{'sor-green' if '🟢' in s['verified_msp'] else 'sor-red'}">{s['verified_msp']}</span><br>
                <strong>EEO Signature:</strong> <span class="{'sor-green' if '🟢' in s['verified_biddle'] else 'sor-red'}">{s['verified_biddle']}</span>
            </div>
            <div class="metric-box" style="border-color: #38bdf8;">
                <small style="color:#38bdf8">TPRV Global Validation</small><br>
                <strong>Reviewer:</strong> {s['verified_reviewer']}<br>
                <strong>Service:</strong> {s['verified_status']}
            </div>
            """, unsafe_allow_html=True)

        with col_chat:
            st.markdown("### Copilot Interface")
            cols = st.columns(2)
            quick = None
            if cols[0].button("What EEO Demographics have the most injuries?"): quick = "demo_1"
            if cols[0].button("Correlate OSHA Roles with Costs"): quick = "demo_2"
            if cols[1].button("Identify Risk Management gaps (Missing COI)"): quick = "demo_3"

            prompt = st.chat_input("Ask the AI Gatekeeper about the claims data...") or quick

            if prompt:
                df_claims = s["claims_df"]
                st.chat_message("user").write("Executing Actuarial Query..." if prompt.startswith("demo_") else prompt)
                
                with st.chat_message("assistant"), st.status("TPRV Validating Identity...", expanded=True) as status:
                    time.sleep(1)
                    
                    # --- FIREWALL ---
                    if "🔴" in s["verified_status"] or "🔴" in s["verified_adp"] or "🔴" in s["verified_msp"] or "🔴" in s["verified_biddle"]:
                        st.error("🚨 ACCESS DENIED: A federated System of Record indicates invalid status. Prompt blocked.")
                        log_event("DENY", "SoR Kill Switch Activated")
                        status.update(label="Access Denied", state="error")
                        st.stop()

                    status.update(label="TPRV Passed. Executing Query...", state="running")
                    time.sleep(1)
                    
                    if prompt == "demo_1":
                        st.markdown("**AI Analysis:** Forklift Operators within the Male demographic represent the highest incident frequency.")
                        fig = px.histogram(df_claims, x="Claimant_Age", color="Claimant_Gender", facet_col="Department", barmode="group")
                        st.plotly_chart(fig, use_container_width=True)
                    elif prompt == "demo_2":
                        st.markdown("**AI Analysis:** 'Warehouse Associate' yields the highest cumulative risk cost.")
                        fig = px.box(df_claims, x="OSHA_Role", y="Incurred_Cost", color="Status")
                        st.plotly_chart(fig, use_container_width=True)
                    elif prompt == "demo_3":
                        st.markdown("**AI Analysis:** Flagging high-severity claims lacking valid Certificate of Insurance (COI).")
                        risk_df = df_claims[(df_claims['COI_Coverage_Valid'] == 'No') & (df_claims['Incurred_Cost'] > 40000)]
                        st.dataframe(risk_df, use_container_width=True)
                        if not risk_df.empty:
                            st.error(f"Action Required: {len(risk_df)} critical gap(s) identified. Route to {s['verified_reviewer']}.")
                    else:
                        st.write(f"Processed custom query for {s['verified_title']} in {s['verified_jur']}.")
                    
                    status.update(label="Authorized & Completed", state="complete")
                    log_event("ALLOW", "Actuarial Query Executed")

# ==========================================
# TAB 4: REVENUE IMPACT USE CASE
# ==========================================
with tab4:
    st.markdown("### 🏥 Provider Revenue Impact Calculator")
    st.write("Demonstrate the top-line revenue recovery for Healthcare Providers by overturning automated carrier denials using TPRV's immutable Trail of Evidence.")
    
    st.markdown("#### Baseline Parameters")
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1: billed = st.slider("Total Annual Billed ($)", 1000000, 50000000, 10000000, 500000, "$%d")
    with col_in2: denial_rate = st.slider("Carrier Auto-Denial Rate (%)", 5, 40, 18, 1)
    with col_in3: reversal_rate = st.slider("TPRV Denial Reversal Rate (%)", 10, 95, 65, 1)

    risk_revenue = billed * (denial_rate / 100)
    recovered = risk_revenue * (reversal_rate / 100)
    base_realized = billed - risk_revenue
    final_realized = base_realized + recovered

    col_out1, col_out2, col_out3 = st.columns(3)
    col_out1.metric("Gross Revenue at Risk", f"${risk_revenue:,.0f}")
    col_out2.metric("Revenue Recovered via TPRV", f"${recovered:,.0f}", f"+{(recovered/billed)*100:.1f}% Margin Impact")
    col_out3.metric("Final Realized Revenue", f"${final_realized:,.0f}")

    chart_data = pd.DataFrame({"Scenario": ["Without TPRV", "With TPRV"], "Revenue": [base_realized, final_realized]}).set_index("Scenario")
    st.bar_chart(chart_data)

# ==========================================
# TAB 5: AUDIT READINESS USE CASE
# ==========================================
with tab5:
    st.markdown("### ⚖️ Litigation Defense & Claims Readiness")
    st.write("Generate immutable trails of evidence combining HR compliance, Medical Billing, and AI activity logs to win legal cases and reverse insurance denials.")
    
    if st.button("Generate Litigation Defense Packet (Claim: POL-10001)"):
        with st.spinner("Compiling Evidence Trail..."):
            time.sleep(1.5)
        st.success("Defense Packet Compiled Successfully")
        colA, colB = st.columns(2)
        with colA:
            st.markdown("#### 📄 Exhibit A: HR Validation Proof")
            st.code(f"Human Identity: Validated\nAssigned Role: {s['verified_title']}\nAssigned Reviewer: {s['verified_reviewer']}\nADP Employment Status: {s['verified_adp']}\nEEO Audit Status: {s['verified_biddle']}")
        with colB:
            st.markdown("#### 🏥 Exhibit B: Cost of Health Evidence")
            st.code("Claimant: David Lee\nInjury: Return-to-Work (Transitional)\nInsurance Billed: $15,258\nInsurance Approved: $13,573\nAutomated Denial Reason: CPT Code Mismatch\nTPRV AI Rebuttal: Medical necessity matched to ADA requirements.")

# ==========================================
# TAB 6: UNDERWRITING ANALYTICS USE CASE
# ==========================================
with tab6:
    st.markdown("### 📋 Underwriting Stewardship & Premium Analytics")
    st.write("Workers Compensation performance dashboard for Insurance Underwriters and CFOs.")

    if not s["connectors_validated"]:
        st.warning("🔒 **Data Pipeline Not Established.** Complete the AI Systems Baseline in Tab 1 to unlock analytics.")
    else:
        df = s["claims_df"]
        m1, m2, m3 = st.columns(3)
        m1.metric("Total WC Claims", len(df), "Calculated from Baseline")
        m2.metric("Pharmacy Generic Fill Rate", "100%", "Industry benchmark: 85%", delta_color="normal")
        m3.metric("Total Incurred Risk Cost", f"${df['Incurred_Cost'].sum():,.0f}")

        st.divider()
        col_trir, col_injury = st.columns(2)
        with col_trir:
            st.markdown("#### 📊 Litigation Distribution by Department")
            lit_df = df[df['Status'] == 'In Litigation'].groupby('Department').size().reset_index(name='Count')
            st.bar_chart(lit_df.set_index('Department'))

        with col_injury:
            st.markdown("#### 🩹 Top Injury Causes (% of All Claims)")
            st.bar_chart(pd.DataFrame({"Injury Cause": ["Strain/Overexertion", "Slip/Fall", "Ergonomic"], "Percentage": [45, 30, 25]}).set_index("Injury Cause"))