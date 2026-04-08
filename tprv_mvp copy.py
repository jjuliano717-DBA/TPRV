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
if 'v15_state' not in st.session_state:
    st.session_state.v15_state = {
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
        "roster_df": None,
        "claims_df": None,
        "osha_df": None,
        "connectors_validated": False
    }

def log_event(outcome, rationale):
    s = st.session_state.v15_state
    s["log"].insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Context": f"{s['verified_title']} ({s['verified_jur']}) | Rev: {s['verified_reviewer']}",
        "Outcome": outcome,
        "Rationale": rationale
    })

# --- CONFIG & STYLING ---
st.set_page_config(page_title="TruRoles TPV: Governance Core V15", layout="wide")
st.markdown("""<style>
div.stButton > button:first-child { font-weight: 500; border: 1px solid #38bdf8; }
.metric-box { background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px; }
.sor-green { color: #10b981; font-weight: bold; }
.sor-red { color: #ef4444; font-weight: bold; }
.partner-box { border: 1px solid #475569; padding: 20px; border-radius: 8px; background-color: #1e293b; margin-bottom: 20px;}
</style>""", unsafe_allow_html=True)

s = st.session_state.v15_state

# --- SIDEBAR: DATA INGESTION & LLM SETUP ---
with st.sidebar:
    st.header("⚙️ POC Configuration")
    
    api_key = st.text_input("OpenAI API Key (Optional)", type="password", help="Enter a valid API key to replace hardcoded responses with real GenAI. TPRV will still act as the security firewall.")
    
    data_mode = st.radio("Data Source", ["Use Static Demo Data", "Upload Client CSVs (Full POC)"], help="Toggle between built-in demo data or ingest sanitized client CSV exports.")
    
    if data_mode == "Upload Client CSVs (Full POC)":
        st.info("Upload standard flat files to dynamically drive the LLM context and Analytics Dashboards.")
        
        f_roster = st.file_uploader("1. HR Roster (ADP)", type="csv", help="Upload Employee Roster")
        if f_roster:
            s["roster_df"] = pd.read_csv(f_roster)
            st.success(f"Roster Loaded: {len(s['roster_df'])} rows.")
            
        f_claims = st.file_uploader("2. Loss Runs (Sedgwick)", type="csv", help="Upload Claims Data")
        if f_claims:
            s["claims_df"] = pd.read_csv(f_claims)
            st.success(f"Claims Loaded: {len(s['claims_df'])} rows.")
            
        f_osha = st.file_uploader("3. OSHA Logs (Paycom)", type="csv", help="Upload OSHA Benchmarks")
        if f_osha:
            s["osha_df"] = pd.read_csv(f_osha)
            st.success(f"OSHA Data Loaded: {len(s['osha_df'])} rows.")

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
    rev = st.selectbox("Assigned Human Reviewer", ["Unassigned", "John Smith (VP HR)", "Sarah Lee (Chief Risk Officer)"],
                       index=["Unassigned", "John Smith (VP HR)", "Sarah Lee (Chief Risk Officer)"].index(s["reviewer"]))
    stat = st.selectbox("Service Validation Status", ["🟢 Green (Valid)", "🟡 Yellow (Pending)", "🔴 Red (Expired/Invalid)"],
                        index=["🟢 Green (Valid)", "🟡 Yellow (Pending)", "🔴 Red (Expired/Invalid)"].index(s["service_status"]))
    
    if st.button("Sync Federated Network"):
        with st.spinner("Aggregating Systems of Record..."):
            time.sleep(1)
            s.update({"title": t, "jurisdiction": j, "adp_status": adp_stat, "msp_status": msp_stat, "biddle_status": biddle_stat,
                      "tpa_linked": tpa, "reviewer": rev, "service_status": stat,
                      "verified_title": t, "verified_jur": j, "verified_adp": adp_stat, "verified_msp": msp_stat,
                      "verified_biddle": biddle_stat, "verified_tpa": tpa, "verified_reviewer": rev, "verified_status": stat})
            st.rerun()

# --- ENTERPRISE PORTALS (TABS) ---
st.title("🛡️ TruRoles TPV: Enterprise Governance Core")
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🤖 AI Gatekeeper",
    "📊 Data Explorer",
    "🏥 Revenue Impact",
    "🤝 Partner Hub",
    "⚖️ Audit Readiness",
    "📈 Network Report",
    "📋 Underwriting Stewardship",
    "🔗 Connector Hub"
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
        
        cols = st.columns(2)
        quick = None
        if cols[0].button("Query Cyber Incident Recovery Plans"): quick = "What is the Cyber Attack Incident Recovery Plan Test activities count in this time period?"
        if cols[0].button("Execute DORA/STP Payments Sync"): quick = "Execute DORA Smart Contract Reconciliation for Chiro Payments"
        if cols[0].button("Generate OSHA 300A TRIR/DART Report", help="Authorized for Safety Manager / Risk Manager"): quick = "Generate OSHA 300A TRIR/DART Report"
        if cols[1].button("Analyze Healthcare Services Billing"): quick = "What is the Emergency Room Treatment Services count in this time period?"
        if cols[1].button("Analyze COI Exclusions"): quick = "Read Certificates of Insurance and identify underwriting exclusions."
        if cols[1].button("Generate EEO-1 Demographics & Tenure", help="Authorized for Risk Manager / HR"): quick = "Generate EEO-1 Report with Demographics and Tenure."
        if cols[1].button("Review ADA Essential Duties & Return-to-Work Plan", help="Authorized for Claims Adjuster / Safety Manager"): quick = "Review ADA Essential Duties & Return-to-Work Plan"

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
                        
                        # Dynamic Context Variables derived from uploaded CSVs
                        dynamic_claims_count = len(s["claims_df"]) if s["claims_df"] is not None else 71
                        
                        system_prompt = f"""
                        You are an Enterprise AI Assistant for the TPRV TruRoles TPV platform.
                        CRITICAL SECURITY CONTEXT: The user has been HR-verified as a '{s['verified_title']}' operating in '{s['verified_jur']}'.
                        You must tailor your answer specifically to their job role and state jurisdiction.
                        If they ask for financial, medical, or HR data that a '{s['verified_title']}' should not see, refuse politely.

                        SYSTEM_DATA_CONTEXT (Paycom & Sedgwick API — Live Feed):
                        - Total WC Claims on file: {dynamic_claims_count}
                        - Pharmacy Generic Fill Rate: 100% (industry benchmark: 85%)
                        - Pharmacy Duplicate Extraction Savings: 95%
                        - TRIR by Location: Texas=2.4, Pennsylvania=1.9, New York=3.1
                        - DART by Location: Texas=1.8, Pennsylvania=1.2, New York=2.5
                        - Top Injury Causes: Strain/Overexertion=45%, Slip/Fall=30%, Ergonomic=25%
                        - Active Claimant (ADA RTW): David Lee | Injury: Musculoskeletal Strain | Sedgwick Case: SDG-2026-TX-00419
                        - Essential Duties verified via Biddle Job Analysis | RTW Clearance: Approved for Modified Duty
                        - ADA Accommodation: Ergonomic workstation adjustment
                        Use this data to answer OSHA 300A, TRIR/DART, ADA, EEO-1, and Workers Comp premium questions accurately.
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
                    elif "EEO-1" in prompt:
                        if s["verified_title"] in ["Risk Manager", "VP HR"]:
                            st.write("**AI Output — EEO-1 Demographics & Tenure Report (via Paycom API):**\n\nEmployment liability parameters mapped successfully. National Origin and Handicap Status compliance verified against local jurisdiction laws. No demographic anomalies detected that would trigger elevated Employment Liability insurance premiums.")
                        else:
                            st.error(f"🚨 ACCESS DENIED: EEO-1 Reports require Risk Manager or VP HR authorization. Current role ({s['verified_title']}) is restricted from PII/Demographic data.")
                    elif "OSHA 300A" in prompt:
                        if s["verified_title"] in ["Safety Manager", "Risk Manager"]:
                            dynamic_claims = len(s["claims_df"]) if s["claims_df"] is not None else 71
                            st.write("**AI Output — OSHA 300A TRIR/DART Report Generated (via Paycom API Connector):**")
                            st.markdown(f"""
| Establishment | TRIR | DART |
|---|---|---|
| Texas          | 2.4  | 1.8  |
| Pennsylvania   | 1.9  | 1.2  |
| New York       | 3.1  | 2.5  |

**Summary:** TRIR is currently **2.4** across all Texas establishments. Total recordable claims: **{dynamic_claims}**. Pharmacy Generic Fill Rate: **100%**. Data sourced via Paycom/Sedgwick API connectors.""")
                        else:
                            st.error(f"🚨 ACCESS DENIED: OSHA 300A reports require Safety Manager or Risk Manager authorization. Current role ({s['verified_title']}) is not authorized.")
                            log_event("DENY", "Insufficient role for OSHA 300A")
                    elif "ADA Essential Duties" in prompt:
                        if s["verified_title"] in ["Claims Adjuster", "Safety Manager"]:
                            st.write("**AI Output — ADA Essential Duties & Return-to-Work Plan (via Sedgwick TPA Connector):**")
                            st.markdown("""
**Claimant:** David Lee  
**Injury Classification:** Musculoskeletal Strain (Transitional Duty Eligible)  
**Essential Duties Verified:** ✅ Physical demand level confirmed via Biddle Job Analysis  
**Return-to-Work Clearance:** ✅ Approved for Modified Duty — effective immediately  
**ADA Accommodation Required:** Ergonomic workstation adjustment (low cost)  
**Sedgwick Case #:** SDG-2026-TX-00419  

*ADA Essential Duties verified for Return-to-Work clearance. Claim routed to transitional duty program.*""")
                        else:
                            st.error(f"🚨 ACCESS DENIED: ADA Return-to-Work plans require Claims Adjuster or Safety Manager authorization. Current role ({s['verified_title']}) is not authorized.")
                            log_event("DENY", "Insufficient role for ADA RTW")
                    else:
                        st.write(f"**AI Output:** Based on your authorized role as a {s['verified_title']} in {s['verified_jur']}, I have accessed the necessary records to process: '{prompt}'.")
                        st.info("💡 Enter an OpenAI API key in the sidebar to generate live, unscripted responses.")
                    
                    log_event("ALLOW", "Simulated Grant")
                    
                status.update(label="Authorized", state="complete")

# --- TAB 2: DATA STRUCTURE EXPLORER ---
with tab2:
    st.markdown("### 📊 Enterprise Data Structure Explorer")
    st.write("For POC testing: Review the required data schema and upload your own sanitized CSVs.")
    
    col_view1, col_view2 = st.columns(2)
    
    with col_view1:
        if s["roster_df"] is not None:
            st.subheader("HR Roster Data Ingested")
            st.dataframe(s["roster_df"], use_container_width=True)
        else:
            st.info("👈 Upload an HR Roster CSV in the sidebar to view it here.")
            
    with col_view2:
        if s["claims_df"] is not None:
            st.subheader("Loss Run / Claims Data Ingested")
            st.dataframe(s["claims_df"], use_container_width=True)
        else:
            st.info("👈 Upload a Claims CSV in the sidebar to view it here.")
        
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

# --- TAB 4: PARTNER DATA HUB ---
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

# --- TAB 5: LITIGATION & AUDIT READINESS ---
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

# --- TAB 6: DYNAMIC NETWORK REPORT ---
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

# --- TAB 7: UNDERWRITING STEWARDSHIP & PREMIUM ANALYTICS ---
with tab7:
    st.markdown("### 📋 Underwriting Stewardship & Premium Analytics")
    st.write("Workers Compensation performance dashboard for Insurance Underwriters and CFOs. Data aggregated via Paycom and Sedgwick API connectors.")

    if not s["connectors_validated"]:
        st.warning(
            "🔒 **Data Pipeline Not Established.**\n\n"
            "This dashboard requires active API connector field mappings before analytics can render. "
            "Navigate to the **🔗 Connector Hub** tab, complete the field mapping for ADP, Paycom, Sedgwick, and Biddle, "
            "then click **✅ Validate Connectors** to unlock this dashboard."
        )
    else:
        # Dynamic Data Bindings — automatically switch from demo to live CSV data
        dynamic_claims_count = len(s["claims_df"]) if s["claims_df"] is not None else 71
        claims_delta = "Calculated from Loss Run Data" if s["claims_df"] is not None else "+32 from last year"
        
        # Top Row: KPI Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total WC Claims", f"{dynamic_claims_count}", claims_delta)
        m2.metric("Pharmacy Generic Fill Rate", "100%", "Industry benchmark: 85%", delta_color="normal")
        m3.metric("Pharmacy Duplicate Extraction Savings", "95%", "Duplicate scripts eliminated")

        st.divider()

        # 2-Column Layout: TRIR/DART Chart + Injury Causes
        col_trir, col_injury = st.columns(2)

        with col_trir:
            st.markdown("#### 📊 TRIR & DART by Location")
            st.caption("TRIR = Total Recordable Injury Rate | DART = Days Away, Restricted, or Transferred")
            trir_dart_df = pd.DataFrame({
                "Location": ["Texas", "Pennsylvania", "New York"],
                "TRIR": [2.4, 1.9, 3.1],
                "DART": [1.8, 1.2, 2.5]
            }).set_index("Location")
            st.bar_chart(trir_dart_df)

        with col_injury:
            st.markdown("#### 🩹 Top Injury Causes (% of All Claims)")
            st.caption("Based on OSHA 300 Log categorization via Sedgwick TPA")
            injury_df = pd.DataFrame({
                "Injury Cause": ["Strain / Overexertion", "Slip / Fall", "Ergonomic"],
                "Percentage": [45, 30, 25]
            }).set_index("Injury Cause")
            st.bar_chart(injury_df)

        st.divider()
        st.info("""
        📡 **Data Source:** This dashboard is powered by live API connectors to **Paycom** (OSHA 300 logs, employee hours worked)
        and **Sedgwick** (Claims TPA — injury classification, pharmacy data, return-to-work status).

        This aggregated data is used by TPRV to provide actuarially defensible metrics to your Workers Compensation carrier
        during annual premium negotiation, directly reducing Experience Modification Rate (EMR) and lowering overall WC spend.
        """)

# --- TAB 8: CONNECTOR HUB (FIELD MAPPING) ---
with tab8:
    st.markdown("### 🔗 The Gallaher Connector Hub — Legacy Field Mapping")
    st.write("Consultant interface for mapping legacy system fields to the TruRoles TPV platform. Complete vendor mappings and click Validate to establish the data baseline.")

    st.divider()

    col_adp, col_paycom, col_sedgwick, col_biddle = st.columns(4)

    with col_adp:
        st.markdown("#### 🟦 ADP (HRIS)")
        st.caption("Human Resource Information System")
        st.selectbox("Map ADP Employee Status to TruRoles TPV:", ["Employment_Active_Flag", "HR_Kill_Switch", "ADP_Status_Code"], key="map_adp_status")
        st.selectbox("Map ADP Job Title to WC Code:", ["WC_Rating_Code", "Job_Classification_ID", "NCCI_Class_Code"], key="map_adp_jobtitle")
        st.selectbox("Map ADP Pay Group to Jurisdiction:", ["Jurisdiction_State", "Tax_State_Code", "FROI_Routing_State"], key="map_adp_paygroup")
        st.selectbox("Map ADP Termination to Kill Switch:", ["Access_Revocation_Timestamp", "Termination_Date", "HR_Offboarding_Flag"], key="map_adp_termdate")

    with col_paycom:
        st.markdown("#### 🟩 Paycom (Payroll)")
        st.caption("Payroll Processing & OSHA Compliance")
        st.selectbox("Map Paycom OSHA Field to TruRoles TPV Metric:", ["TRIR", "DART", "EEO-1", "WC Rating Code"], key="map_paycom_osha")
        st.selectbox("Map Paycom Hours Worked to TRIR Calc:", ["Total_Hours_Worked", "FTE_Count", "Annualized_Hours"], key="map_paycom_hours")
        st.selectbox("Map Paycom Pay Period to Audit Cycle:", ["Quarterly_Audit_Window", "Biweekly_Pay_Period", "Annual_Review_Date"], key="map_paycom_period")
        st.selectbox("Map Paycom EEO-1 to Compliance Flag:", ["EEO_Audit_Flag", "Biddle_Signature_Status", "EEO1_Job_Category"], key="map_paycom_eeo")

    with col_sedgwick:
        st.markdown("#### 🟧 Sedgwick (Claims TPA)")
        st.caption("Third Party Claims Administrator")
        st.selectbox("Map Sedgwick Claim Type to Injury Cause:", ["Strain", "Slip/Fall", "Ergonomic", "Other"], key="map_sedgwick_claim")
        st.selectbox("Map Sedgwick RTW Status to ADA Flag:", ["ADA_Accommodation_Required", "RTW_Clearance_Flag", "Transitional_Duty_Eligible"], key="map_sedgwick_rtw")
        st.selectbox("Map Sedgwick Pharmacy to Savings Metric:", ["Generic_Fill_Rate", "Duplicate_Script_Flag", "Formulary_Compliance_Rate"], key="map_sedgwick_rx")
        st.selectbox("Map Sedgwick Case # to Evidence Packet:", ["TPRV_Evidence_ID", "Claim_Reference_Number", "Litigation_Defense_Bundle"], key="map_sedgwick_case")

    with col_biddle:
        st.markdown("#### 🟪 Biddle (Job Analysis)")
        st.caption("ADA & EEO Compliance Consulting")
        st.selectbox("Map Biddle Job Analysis to ADA Duty Standard:", ["Essential_Duty_List", "Physical_Demand_Level", "ADA_Functional_Assessment"], key="map_biddle_jta")
        st.selectbox("Map Biddle EEO Policy to Audit Flag:", ["EEO_Signed_Flag", "Policy_Acknowledgement_Date", "Biddle_Compliance_Status"], key="map_biddle_eeo")
        st.selectbox("Map Biddle RTW Assessment to TruRoles TPV:", ["RTW_Functional_Capacity", "Modified_Duty_Eligible", "Transitional_Work_Plan"], key="map_biddle_rtw")
        st.selectbox("Map Biddle Litigation File to Evidence Bundle:", ["Litigation_Defense_Record", "Expert_Witness_Report", "TPRV_Exhibit_C"], key="map_biddle_lit")

    st.divider()

    # State-Render Fix: button sets state and reruns; all UI renders from state outside button block
    if st.button("✅ Validate Connectors", use_container_width=True):
        with st.spinner("Validating field maps across ADP, Paycom, Sedgwick, and Biddle..."):
            time.sleep(1.5)
        s["connectors_validated"] = True
        st.rerun()

    # Persistent validated UI — survives all reruns because it reads from session state
    if s["connectors_validated"]:
        st.success("✅ Connectors Aligned. Systems of Record baseline established.")
        
        # Gallaher Implementation & Billing Tracker (Doc's April 2 requirement)
        st.info("⏱️ **Gallaher Implementation Tracking:** API connections mapped successfully. 4.5 Consulting Hours logged to Training Services.")
        
        st.markdown("""
        | Connector        | Status    | Fields Mapped | Data Sync Status |
        |------------------|-----------|---------------|------------------|
        | ADP (HRIS)       | 🟢 Active  | 4             | Live Feed        |
        | Paycom           | 🟢 Active  | 4             | Live Feed        |
        | Sedgwick TPA     | 🟢 Active  | 4             | Live Feed        |
        | Biddle Job Anal. | 🟢 Active  | 4             | Live Feed        |
        """)
        
        # Dynamic payload — reflects actual uploaded CSV row count if available
        preview_count = len(s["claims_df"]) if s["claims_df"] is not None else 71
        with st.expander("🔍 View JSON Data Payload Preview", expanded=False):
            st.json({
                "adp_payroll_sync": "SUCCESS",
                "paycom_osha_trir": 2.4,
                "sedgwick_claims_ytd": preview_count,
                "biddle_eeo_signatures_missing": 0
            })