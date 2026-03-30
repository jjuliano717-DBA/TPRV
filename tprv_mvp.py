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
if 'v9_state' not in st.session_state:
    st.session_state.v9_state = {
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
    s = st.session_state.v9_state
    s["log"].insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Context": f"{s['verified_title']} ({s['verified_jur']})",
        "Outcome": outcome,
        "Rationale": rationale
    })

# --- CONFIG & STYLING ---
st.set_page_config(page_title="TPRV Enterprise POC", layout="wide")
st.markdown("""<style>
div.stButton > button:first-child { font-weight: 500; border: 1px solid #38bdf8; }
.metric-box { background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px; }
.sor-green { color: #10b981; font-weight: bold; }
.sor-red { color: #ef4444; font-weight: bold; }
</style>""", unsafe_allow_html=True)

s = st.session_state.v9_state

# --- SIDEBAR: DATA INGESTION & LLM SETUP ---
with st.sidebar:
    st.header("⚙️ POC Configuration")
    
    # Live LLM Integration
    api_key = st.text_input("OpenAI API Key (Optional for Live LLM)", type="password", help="Enter a valid API key to replace hardcoded responses with real GenAI. TPRV will still act as the security firewall.")
    
    # Data Ingestion Toggle
    data_mode = st.radio("Data Source", ["Use Static Demo Data", "Upload Client CSV Roster"], help="Toggle between built-in TPRV demo data or ingest a sanitized client CSV export.")
    
    if data_mode == "Upload Client CSV Roster":
        uploaded_file = st.file_uploader("Upload Sanitized Roster", type="csv", help="CSV should contain columns like: JobTitle, Location, Status. No PII required.")
        if uploaded_file:
            s["roster_df"] = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(s['roster_df'])} records.")
            # Dynamically pull titles from CSV if column exists
            job_titles = s["roster_df"].columns.tolist()
            st.info(f"Detected Columns: {', '.join(job_titles)}")

    st.divider()
    
    st.header("🔌 Federated Systems of Record")
    st.markdown("*(Hover over labels for Data Structure Notes)*")
    
    # Added 'help' parameters for Data Structure Hover Notes
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
                            help="Data Structure: Boolean. Validates if the user currently holds an active $30/mo Copilot IT License via the Managed Service Provider.")
    
    biddle_stat = st.selectbox("Biddle EEO Audit Status", ["🟢 Verified", "🔴 Unsigned Policy"], 
                               index=["🟢 Verified", "🔴 Unsigned Policy"].index(s["biddle_status"]),
                               help="Data Structure: Boolean. Validates that the employee has digitally signed their EEO & Code of Conduct policies. Required for Litigation Defense.")

    if st.button("Sync Federated Network"):
        with st.spinner("Aggregating Systems of Record..."):
            time.sleep(1)
            s.update({"title": t, "jurisdiction": j, "adp_status": adp_stat, "msp_status": msp_stat, "biddle_status": biddle_stat,
                      "verified_title": t, "verified_jur": j, "verified_adp": adp_stat, "verified_msp": msp_stat, "verified_biddle": biddle_stat})
            st.rerun()

# --- ENTERPRISE PORTALS (TABS) ---
st.title("🛡️ TPRV: Enterprise Data Sandbox")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 AI Gatekeeper & Prompt Engine", "🤝 Partner Data Hub", "⚖️ Litigation & Audit", "📊 Network Status", "🗂️ Data Schema Explorer"])

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
        """, unsafe_allow_html=True)

    with col_chat:
        st.markdown("### Executive Quick Prompts")
        cols = st.columns(2)
        quick = None
        if cols[0].button("Query Cyber Incident Plans"): quick = "What is the Cyber Attack Incident Recovery Plan Test activities count in this time period?"
        if cols[0].button("Execute DORA/STP Payments Sync"): quick = "Execute DORA Smart Contract Reconciliation for Chiro Payments"
        if cols[1].button("Analyze Healthcare Billing"): quick = "What is the Emergency Room Treatment Services count in this time period?"
        if cols[1].button("Analyze COI Exclusions"): quick = "Read Certificates of Insurance and identify underwriting exclusions."

        prompt = st.chat_input("Prompt Enterprise Copilot... (Type anything if API Key is active)") or quick

        if prompt:
            st.chat_message("user").write(prompt)
            with st.chat_message("assistant"), st.status("TPRV Validating Identity...", expanded=True) as status:
                time.sleep(1.5)
                
                # --- TPRV ARCHITECTURE: FIREWALL BEFORE THE LLM ---
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

                # --- LIVE LLM EXECUTION (If Key is Provided) ---
                status.update(label="TPRV Passed. Routing to LLM...", state="running")
                
                if api_key and OPENAI_AVAILABLE:
                    try:
                        client = OpenAI(api_key=api_key)
                        
                        # The System Prompt dynamically injects their verified HR data to "Ground" the AI
                        system_prompt = f"""
                        You are an Enterprise AI Assistant.
                        CRITICAL SECURITY CONTEXT: The user you are talking to has been HR-verified by the TPRV system as a '{s['verified_title']}' operating in '{s['verified_jur']}'.
                        You must tailor your answer specifically to their job role and state jurisdiction. 
                        If they ask for financial, medical, or HR data that a '{s['verified_title']}' should not see, refuse politely.
                        """
                        
                        stream = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            stream=True
                        )
                        st.success(f"✅ ROLE VALIDATED ({s['verified_title']}). Live LLM Response Streaming.")
                        st.write_stream(stream)
                        log_event("ALLOW", "Live LLM API Called (Stream)")
                        
                    except Exception as e:
                        st.error(f"LLM API Error: {str(e)}. (Check your API Key).")
                else:
                    # Fallback to smart simulated responses if no key is entered
                    if s["verified_title"] == "IT Security Manager" and "Cyber" in prompt:
                        st.success(f"✅ ROLE VALIDATED (IT Security Manager). All SoR checks GREEN.")
                        st.write("**AI Output:** Accessing Cyber Incident Recovery Plans.\n* **Data Point 1:** There were 14 Cyber Attack Incident Recovery Plan Test activities logged in Q1.\n* **Data Point 2:** 3 systems failed containment procedures within the State Attorney General 72-hour reporting compliance window.")
                        log_event("ALLOW", "Cyber Recovery Grant")
                    elif s["verified_title"] == "Claims Adjuster" and "Emergency" in prompt:
                        st.success(f"✅ ROLE VALIDATED (Claims Adjuster). Authenticated by Reviewer: {s['verified_reviewer']}.")
                        st.write("**AI Output:** Accessing Healthcare Services Billing Data.\n* **Data Point 1:** 342 Emergency Room Treatment Services counts in this time period linked to Workers Comp.\n* **Data Point 2:** $1.2M in billed healthcare charges flagged for excessive diagnostic coding variance.")
                        log_event("ALLOW", "Healthcare Claims Grant")
                    elif s["verified_title"] == "Bank KYC Manager" and "DORA" in prompt:
                        if not s["verified_tpa"]:
                            st.error("🚨 EXTERNAL DATA DENIED: National TPA Data Link is offline. Cannot execute Straight Through Processing (STP) for Chiro Payments without verified Claims Administrator data.")
                            log_event("DENY", "Missing TPA Data Link")
                            status.update(label="Access Denied", state="error")
                            st.stop()
                        st.success(f"✅ ROLE VALIDATED (Bank KYC Manager) & TPA LINK VERIFIED.")
                        st.write("**AI Output:** Executing DORA Compliance protocols.\n* **Data Point 1:** Reconciled 402 National TPA Healthcare invoices with local Rehab Center Blockchain Smart Contracts.\n* **Data Point 2:** Flagged 3 payments due to missing Bank KYC validation; STP halted on exceptions.")
                        log_event("ALLOW", "DORA STP Sync Grant")
                    elif s["verified_title"] == "Risk Manager" and "COI" in prompt:
                        st.success(f"✅ ROLE VALIDATED (Risk Manager). Authenticated by Reviewer: {s['verified_reviewer']}.")
                        st.write("**AI Output: COI Document Analysis.**\n* **Data Point 1:** Certificate #4029-TX Scanned. Exclusions Found: Force Majeure property damage explicitly excluded.\n* **Data Point 2:** Endorsements Found: Additional Insured coverage applies to Tier 1 Subcontractors exclusively.")
                        log_event("ALLOW", "COI Analysis Grant")
                    else:
                        st.error(f"🚨 ACCESS DENIED: Your validated role ({s['verified_title']}) does not map to the AI Topic required for this query. (See Prompts Library mapping).")
                        log_event("DENY", "Topic Mismatch")
                        status.update(label="Access Denied", state="error")
                        st.stop()
                        
                    st.info("💡 Enter an OpenAI API key in the sidebar to generate live, unscripted responses using TPRV's dynamic prompt injection.")
                    
                status.update(label="Authorized", state="complete")

# --- TAB 2: PARTNER DATA HUB ---
with tab2:
    st.markdown("### 🤝 Partner Services Integration Hub")
    st.write("Partners update service data here, linking directly to the Human Purchaser to drive recurring revenue tracking.")
    
    with st.container():
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
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

# --- TAB 3: LITIGATION & AUDIT READINESS ---
with tab3:
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
        st.info("💡 **Litigation Value:** This packet proves to Underwriters and Courts that the claim was processed by a federated, EEO/HIPAA-compliant human, overriding automated carrier denials.")

# --- TAB 4: DYNAMIC NETWORK REPORT ---
with tab4:
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

# --- TAB 5: DATA STRUCTURE EXPLORER ---
with tab5:
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
        * **`Jurisdiction_State`**: Required to enforce state-level compliance (e.g., Texas Data Privacy Act vs. NY Shield Act).
        * **`EEO_Audit_Flag`**: Boolean (True/False). Ensures the employee has signed compliance documentation before using AI.
        * **`Entra_ID_Status`**: Boolean (True/False). Confirms active IT licensing.
        """)