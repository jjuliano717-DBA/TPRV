import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os

# Try to import OpenAI for the Live LLM integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# --- STATE MANAGEMENT ---
if 'v11_state' not in st.session_state:
    st.session_state.v11_state = {
        "title": "Claims Adjuster", 
        "jurisdiction": "Texas",
        "reviewer": "Sarah Lee (Chief Risk Officer)",
        "adp_status": "🟢 Active",
        "msp_status": "🟢 Active",
        "biddle_status": "🟢 Verified",
        "tpa_linked": True,
        "service_status": "🟢 Green (Valid)",
        "verified_title": "Claims Adjuster",
        "verified_jur": "Texas",
        "verified_reviewer": "Sarah Lee (Chief Risk Officer)",
        "verified_adp": "🟢 Active",
        "verified_msp": "🟢 Active",
        "verified_biddle": "🟢 Verified",
        "verified_tpa": True,
        "verified_status": "🟢 Green (Valid)",
        "partner_services": [],
        "log": [],
        "roster_df": None
    }

def log_event(outcome, rationale):
    s = st.session_state.v11_state
    s["log"].insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Context": f"{s['verified_title']} ({s['verified_jur']}) | Rev: {s['verified_reviewer']}",
        "Outcome": outcome,
        "Rationale": rationale
    })

# --- CONFIG & STYLING ---
st.set_page_config(page_title="TPRV Master Enterprise Platform V11", layout="wide")
st.markdown("""<style>
div.stButton > button:first-child { font-weight: 500; border: 1px solid #38bdf8; }
.metric-box { background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px; }
.sor-green { color: #10b981; font-weight: bold; }
.sor-red { color: #ef4444; font-weight: bold; }
.partner-box { border: 1px solid #475569; padding: 20px; border-radius: 8px; background-color: #1e293b; margin-bottom: 20px;}
</style>""", unsafe_allow_html=True)

s = st.session_state.v11_state

# --- SIDEBAR: DATA INGESTION & LLM SETUP ---
with st.sidebar:
    st.header("⚙️ POC Configuration")
    
    api_key = st.text_input("OpenAI API Key (Optional)", type="password", help="Enter a valid API key to replace hardcoded responses with real GenAI. TPRV will still act as the security firewall.")
    
    data_mode = st.radio("Data Source", ["Use Static Demo Data", "Upload Client CSV Roster"], help="Toggle between built-in TPRV demo data or ingest a sanitized client CSV export.")
    
    if data_mode == "Upload Client CSV Roster":
        uploaded_file = st.file_uploader("Upload Sanitized Roster", type="csv", help="CSV should contain columns like: JobTitle, Location, Status. No PII required.")
        if uploaded_file:
            s["roster_df"] = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(s['roster_df'])} records.")
            job_titles = s["roster_df"].columns.tolist()
            st.info(f"Detected Columns: {', '.join(job_titles)}")

    st.divider()
    
    st.header("🔌 Federated Systems of Record")
    st.markdown("*(Hover over labels for Data Structure Notes)*")
    
    t = st.selectbox("Job Title & WC Code", ["L2 Helpdesk", "Claims Adjuster", "Safety Manager", "IT Security Manager", "Bank KYC Manager", "Risk Manager"], 
                     index=["L2 Helpdesk", "Claims Adjuster", "Safety Manager", "IT Security Manager", "Bank KYC Manager", "Risk Manager"].index(s["title"]),
                     help="Data Structure: String. Maps to ADP Payroll Tax Classifications and Workers Comp Rating Codes.")
    
    j = st.selectbox("Jurisdiction", ["Texas", "New York", "Pennsylvania"], 
                     index=["Texas", "New York", "Pennsylvania"].index(s["jurisdiction"]),
                     help="Data Structure: String (State Code). Critical for routing State First Reports of Injury (FROI) and localized data privacy laws.")
    
    adp_stat = st.selectbox("ADP Feed Status", ["🟢 Active", "🔴 Disconnected / Terminated"], 
                            index=["🟢 Active", "🔴 Disconnected / Terminated"].index(s["adp_status"]),
                            help="Data Structure: Boolean. The master 'Kill Switch' tied to HR employment status.")
    
    msp_stat = st.selectbox("MSP Entra ID Sync", ["🟢 Active", "🔴 Revoked / Offline"], 
                            index=["🟢 Active", "🔴 Revoked / Offline"].index(s["msp_status"]),
                            help="Data Structure: Boolean. Validates if the user currently holds an active Copilot IT License via the MSP.")
    
    biddle_stat = st.selectbox("Biddle EEO Audit Status", ["🟢 Verified", "🔴 Unsigned Policy"], 
                               index=["🟢 Verified", "🔴 Unsigned Policy"].index(s["biddle_status"]),
                               help="Data Structure: Boolean. Validates that the employee has digitally signed their EEO policies. Required for Litigation Defense.")

    st.subheader("TPRV Global Oversight")
    tpa = st.checkbox("National TPA Data Link Active", value=s["tpa_linked"])
    rev = st.selectbox("Assigned Human Reviewer", ["Unassigned", "John Smith (VP HR)", "Sarah Lee (Chief Risk Officer)"], index=["Unassigned", "John Smith (VP HR)", "Sarah Lee (Chief Risk Officer)"].index(s["reviewer"]))
    stat = st.selectbox("Service Validation Status", ["🟢 Green (Valid)", "🟡 Yellow (Pending)", "🔴 Red (Expired/Invalid)"], index=["🟢 Green (Valid)", "🟡 Yellow (Pending)", "🔴 Red (Expired/Invalid)"].index(s["service_status"]))
    
    if st.button("Sync Federated Network"):
        with st.spinner("Aggregating Systems of Record..."):
            time.sleep(1)
            s.update({"title": t, "jurisdiction": j, "adp_status": adp_stat, "msp_status": msp_stat, "biddle_status": biddle_stat, "tpa_linked": tpa, "reviewer": rev, "service_status": stat,
                      "verified_title": t, "verified_jur": j, "verified_adp": adp_stat, "verified_msp": msp_stat, "verified_biddle": biddle_stat, "verified_tpa": tpa, "verified_reviewer": rev, "verified_status": stat})
            st.rerun()

# --- ENTERPRISE PORTALS (TABS) ---
st.title("🛡️ TPRV: Unified Enterprise Platform")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🤖 AI Gatekeeper", 
    "📊 Data Explorer", 
    "🏥 Revenue Impact", 
    "🤝 Partner Hub", 
    "⚖️ Audit Readiness", 
    "📈 Network Report"
])

# --- TAB 1: AI GATEKEEPER & PROMPT ENGINE ---
with tab1:
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
        
        # Bring back the executive quick prompts for smooth demos
        cols = st.columns(2)
        quick = None
        if cols[0].button("Query Cyber Incident Recovery Plans"): quick = "What is the Cyber Attack Incident Recovery Plan Test activities count in this time period?"
        if cols[0].button("Execute DORA/STP Payments Sync"): quick = "Execute DORA Smart Contract Reconciliation for Chiro Payments"
        if cols[1].button("Analyze Healthcare Services Billing"): quick = "What is the Emergency Room Treatment Services count in this time period?"
        if cols[1].button("Analyze COI Exclusions"): quick = "Read Certificates of Insurance and identify underwriting exclusions."

        prompt = st.chat_input("Prompt Enterprise Copilot... (Type anything if API Key is active)") or quick

        if prompt:
            st.chat_message("user").write(prompt)
            with st.chat_message("assistant"), st.status("TPRV Validating Identity...", expanded=True) as status:
                time.sleep(1.5)
                
                # --- FIREWALL BEFORE LLM ---
                if "🔴" in s["verified_status"]:
                    st.error(f"🚨 ACCESS DENIED: Service Validation Status is RED. Mandatory human reviewer ({s['verified_reviewer']}) must approve updates before AI access is restored.")
                    log_event("DENY", "Status Red (Expired/Invalid)")
                    status.update(label="Access Denied", state="error")
                    st.stop()
                if "🔴" in s["verified_adp"] or "🔴" in s["verified_msp"] or "🔴" in s["verified_biddle"]:
                    st.error("🚨 ACCESS DENIED: A federated System of Record indicates invalid status. Prompt blocked before reaching LLM.")
                    log_event("DENY", "SoR Kill Switch Activated")
                    status.update(label="Access Denied", state="error")
                    st.stop()
                    
                if s["verified_title"] == "L2 Helpdesk":
                    st.error("🚨 ACCESS DENIED: Role (L2 Helpdesk) lacks Data Validation clearance for open AI prompting.")
                    log_event("DENY", "Role Unauthorized")
                    status.update(label="Access Denied", state="error")
                    st.stop()

                # --- LIVE LLM EXECUTION ---
                status.update(label="TPRV Passed. Routing to LLM...", state="running")
                
                if api_key and OPENAI_AVAILABLE:
                    try:
                        client = OpenAI(api_key=api_key)
                        system_prompt = f"""
                        You are an Enterprise AI Assistant.
                        CRITICAL SECURITY CONTEXT: The user you are talking to has been HR-verified by the TPRV system as a '{s['verified_title']}' operating in '{s['verified_jur']}'.
                        You must tailor your answer specifically to their job role and state jurisdiction. 
                        If they ask for financial, medical, or HR data that a '{s['verified_title']}' should not see, refuse politely.
                        """
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        st.success(f"✅ ROLE VALIDATED ({s['verified_title']}). Live LLM Response Generated.")
                        st.write(response.choices[0].message.content)
                        log_event("ALLOW", "Live LLM API Called")
                        
                    except Exception as e:
                        st.error(f"LLM API Error: {str(e)}. (Check your API Key).")
                else:
                    st.success(f"✅ ROLE VALIDATED ({s['verified_title']}). (Simulated Response Mode).")
                    
                    # Hardcoded fallbacks for the quick prompts
                    if s["verified_title"] == "IT Security Manager" and "Cyber" in prompt:
                        st.write("**AI Output:** Accessing Incident Recovery Plans. There were 14 Cyber Attack Incident Recovery Plan Test activities logged. Integrating internal IT Security Policy Section 3 containment procedures with State Attorney General reporting requirements.")
                    elif s["verified_title"] == "Claims Adjuster" and "Emergency" in prompt:
                        st.write("**AI Output:** Accessing Healthcare Services Reconciliation Plan. There were 342 Emergency Room Treatment Services counts in this time period linked to Workers Comp.")
                    elif s["verified_title"] == "Bank KYC Manager" and "DORA" in prompt:
                        if not s["verified_tpa"]:
                            st.error("🚨 EXTERNAL DATA DENIED: National TPA Data Link is offline.")
                            st.stop()
                        st.write("**AI Output:** Executing DORA Compliance protocols. Reconciling National TPA Healthcare Services data with Blockchain Smart Contracts. STP validation successful.")
                    elif s["verified_title"] == "Risk Manager" and "COI" in prompt:
                        st.write("**AI Output: COI Document Analysis.**\n* Certificate #4029-TX Scanned.\n* **Exclusions Found:** Force Majeure property damage excluded.\n* **Endorsements Found:** Additional Insured coverage applies to Subcontractors.")
                    else:
                        st.write(f"**AI Output:** Based on your authorized role as a {s['verified_title']} in {s['verified_jur']}, I have accessed the necessary records to process: '{prompt}'.")
                        st.info("💡 Enter an OpenAI API key in the sidebar to generate live, unscripted responses.")
                    
                    log_event("ALLOW", "Simulated Grant")
                    
                status.update(label="Authorized", state="complete")

# --- TAB 2: DATA STRUCTURE EXPLORER ---
with tab2:
    st.markdown("### 📊 Enterprise Data Structure Explorer")
    st.write("For POC testing: Review the required data schema and upload your own sanitized CSVs.")
    
    if s["roster_df"] is not None:
        st.subheader("Client Roster Data Ingested")
        st.dataframe(s["roster_df"], use_container_width=True)
    else:
        st.info("👈 Upload a Client CSV in the sidebar to view it here.")
        
    with st.expander("📖 TPRV Required Data Dictionary (Hover for details)", expanded=True):
        st.markdown("""
        * **`Employee_ID`**: Unique alphanumeric identifier (No SSN or Names required).
        * **`Job_Title`**: Maps to the 'AI Topics Knowledge' matrix to gate AI responses.
        * **`Jurisdiction_State`**: Required to enforce state-level compliance.
        * **`EEO_Audit_Flag`**: Boolean. Ensures the employee has signed compliance documentation.
        * **`Entra_ID_Status`**: Boolean. Confirms active IT licensing.
        """)

# --- TAB 3: PROVIDER REVENUE IMPACT ---
with tab3:
    st.markdown("### 🏥 Provider Revenue Impact Calculator")
    st.write("Demonstrate the top-line revenue recovery for Healthcare Providers by overturning automated carrier denials using TPRV's immutable Trail of Evidence.")
    
    st.markdown("#### Baseline Parameters")
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        billed = st.slider("Total Annual Billed ($)", min_value=1000000, max_value=50000000, value=10000000, step=500000, format="$%d")
    with col_in2:
        denial_rate = st.slider("Carrier Auto-Denial Rate (%)", min_value=5, max_value=40, value=18, step=1)
    with col_in3:
        reversal_rate = st.slider("TPRV Denial Reversal Rate (%)", min_value=10, max_value=95, value=65, step=1)

    risk_revenue = billed * (denial_rate / 100)
    recovered = risk_revenue * (reversal_rate / 100)
    base_realized = billed - risk_revenue
    final_realized = base_realized + recovered

    st.markdown("#### Financial Impact Metrics")
    col_out1, col_out2, col_out3 = st.columns(3)
    col_out1.metric("Gross Revenue at Risk (Auto-Denials)", f"${risk_revenue:,.0f}")
    col_out2.metric("Revenue Recovered via TPRV Evidence", f"${recovered:,.0f}", f"+{(recovered/billed)*100:.1f}% Margin Impact")
    col_out3.metric("Final Realized Revenue", f"${final_realized:,.0f}")

    st.markdown("#### Realized Revenue Comparison")
    chart_data = pd.DataFrame({
        "Scenario": ["Without TPRV (Carrier Denies)", "With TPRV (Recovered)"],
        "Revenue": [base_realized, final_realized]
    }).set_index("Scenario")
    st.bar_chart(chart_data)

# --- TAB 4: PARTNER DATA HUB (Restored from V8) ---
with tab4:
    st.markdown("### 🤝 Partner Services Integration Hub")
    st.write("Partners update service data here, linking directly to the Human Purchaser to drive recurring revenue tracking.")
    
    with st.container():
        st.markdown('<div class="partner-box">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            partner_name = st.selectbox("Select Partner API", ["Biddle Consulting (EEO)", "National Healthcare TPA", "Sedgwick Claims Admin"])
            service_name = st.text_input("Service/Product Update Name", "2026 Enhanced Wellness Benefits Plan")
        with col2:
            target_human = st.selectbox("Link to Human Purchaser (Role)", ["Jane Doe (Claims Adjuster)", "John Smith (VP HR)"])
            if st.button("Push Data to TPRV Network"):
                s["partner_services"].append({"Partner": partner_name, "Service": service_name, "Purchaser": target_human, "Date": datetime.now().strftime("%Y-%m-%d")})
                st.success(f"Service '{service_name}' successfully linked to {target_human}. Recurring Revenue Tracking Updated.")
        st.markdown('</div>', unsafe_allow_html=True)

    if s["partner_services"]:
        st.markdown("#### Active Partner Services Linked to Humans")
        st.dataframe(pd.DataFrame(s["partner_services"]), use_container_width=True)

# --- TAB 5: LITIGATION & AUDIT READINESS (Restored from V8) ---
with tab5:
    st.markdown("### ⚖️ Litigation Defense & Claims Readiness")
    st.write("Generate immutable trails of evidence combining HR compliance, Medical Billing, and AI activity logs to win legal cases and reverse insurance denials.")
    
    if st.button("Generate Litigation Defense Packet (Claim: POL-10001)"):
        with st.spinner("Compiling Evidence Trail..."):
            time.sleep(2)
        
        st.success("Defense Packet Compiled Successfully")
        colA, colB = st.columns(2)
        with colA:
            st.markdown("#### 📄 Exhibit A: Federated HR Validation Proof")
            st.code(f"""
Human Identity: Jane Doe
Assigned Role: Claims Adjuster
Assigned Reviewer: {s['verified_reviewer']}
ADP Employment Status: {s['verified_adp']}
MSP License Status: {s['verified_msp']}
EEO Audit Status (Biddle): {s['verified_biddle']}
AI Knowledge Validation: TRUE
            """)
        with colB:
            st.markdown("#### 🏥 Exhibit B: Cost of Health Evidence")
            st.code("""
Claimant: David Lee
Injury: Return-to-Work (Transitional)
Essential Duties Testing: COMPLETED
Insurance Billed: $15,258
Insurance Approved: $13,573
Automated Denial Reason: CPT Code Mismatch
TPRV AI Rebuttal: Medical necessity matched to ADA requirements.
            """)

# --- TAB 6: DYNAMIC NETWORK REPORT (Restored from V8) ---
with tab6:
    st.markdown("### 📊 Dynamic Role Validation Network")
    st.write("Constant validation of human roles across federated Systems of Record.")
    
    network_data = pd.DataFrame([
        {"Employee": "Jane Doe", "Role": s['verified_title'], "Reviewer": s['verified_reviewer'], "ADP (HR)": s['verified_adp'], "MSP (IT)": s['verified_msp'], "Biddle (EEO)": s['verified_biddle'], "Status": s['verified_status']},
        {"Employee": "John Smith", "Role": "VP HR", "Reviewer": "Board of Directors", "ADP (HR)": "🟢 Active", "MSP (IT)": "🟢 Active", "Biddle (EEO)": "🟢 Verified", "Status": "🟢 Green (Valid)"},
        {"Employee": "Robert Chen", "Role": "L2 Helpdesk", "Reviewer": "IT Director", "ADP (HR)": "🟢 Active", "MSP (IT)": "🟢 Active", "Biddle (EEO)": "🔴 Unsigned Policy", "Status": "🟡 Yellow (Pending)"},
        {"Employee": "Alice Ford", "Role": "Bank KYC Manager", "Reviewer": "Sarah Lee", "ADP (HR)": "🔴 Terminated", "MSP (IT)": "🔴 Revoked", "Biddle (EEO)": "🟢 Verified", "Status": "🔴 Red (Invalid)"}
    ])
    
    st.dataframe(network_data, use_container_width=True, hide_index=True)

    if s["log"]:
        st.markdown("#### 📡 Real-Time Federated Security Logs")
        st.dataframe(pd.DataFrame(s["log"]), use_container_width=True, hide_index=True)