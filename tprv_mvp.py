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
tab1, tab2 = st.tabs(["🤖 AI Gatekeeper & Prompt Engine", "📊 Data Structure Explorer"])

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
        st.markdown("### Copilot Interface")
        
        prompt = st.chat_input("Prompt Enterprise Copilot... (Type anything if API Key is active)") 

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
                    st.success(f"✅ ROLE VALIDATED ({s['verified_title']}). (Simulated Response Mode).")
                    st.write(f"**AI Output:** Based on your authorized role as a {s['verified_title']} in {s['verified_jur']}, I have accessed the necessary records to process: '{prompt}'.")
                    st.info("💡 Enter an OpenAI API key in the sidebar to generate live, unscripted responses using TPRV's dynamic prompt injection.")
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
        * **`Jurisdiction_State`**: Required to enforce state-level compliance (e.g., Texas Data Privacy Act vs. NY Shield Act).
        * **`EEO_Audit_Flag`**: Boolean (True/False). Ensures the employee has signed compliance documentation before using AI.
        * **`Entra_ID_Status`**: Boolean (True/False). Confirms active IT licensing.
        """)