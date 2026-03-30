import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- STATE MANAGEMENT ---
if 'v8_state' not in st.session_state:
    st.session_state.v8_state = {
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
        "log": []
    }

def log_event(outcome, rationale):
    s = st.session_state.v8_state
    s["log"].insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Context": f"{s['verified_title']} ({s['verified_jur']}) | Rev: {s['verified_reviewer']}",
        "Outcome": outcome,
        "Rationale": rationale
    })

# --- CONFIG & STYLING ---
st.set_page_config(page_title="TPRV Enterprise Platform V8", layout="wide")
st.markdown("""<style>
div.stButton > button:first-child { font-weight: 500; letter-spacing: 0.5px; border: 1px solid #38bdf8; }
.metric-box { background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px; }
.sor-green { color: #10b981; font-weight: bold; }
.sor-red { color: #ef4444; font-weight: bold; }
.partner-box { border: 1px solid #475569; padding: 20px; border-radius: 8px; background-color: #1e293b; margin-bottom: 20px;}
</style>""", unsafe_allow_html=True)

s = st.session_state.v8_state

# --- FEDERATED CONTROL PANEL (SIDEBAR) ---
with st.sidebar:
    st.header("🔌 Federated Systems of Record")
    st.markdown("*(Simulates Multi-Vendor APIs)*")
    
    st.subheader("1. ADP (HRIS & Payroll)")
    t = st.selectbox("Job Title & WC Code", ["L2 Helpdesk", "Claims Adjuster", "Safety Manager", "IT Security Manager", "Bank KYC Manager", "Risk Manager"], index=["L2 Helpdesk", "Claims Adjuster", "Safety Manager", "IT Security Manager", "Bank KYC Manager", "Risk Manager"].index(s["title"]))
    j = st.selectbox("Jurisdiction", ["Texas", "New York", "Pennsylvania"], index=["Texas", "New York", "Pennsylvania"].index(s["jurisdiction"]))
    adp_stat = st.selectbox("ADP Feed Status", ["🟢 Active", "🔴 Disconnected / Terminated"], index=["🟢 Active", "🔴 Disconnected / Terminated"].index(s["adp_status"]))
    
    st.subheader("2. MSP (IT & AI Access)")
    msp_stat = st.selectbox("MSP Entra ID Sync", ["🟢 Active", "🔴 Revoked / Offline"], index=["🟢 Active", "🔴 Revoked / Offline"].index(s["msp_status"]))
    
    st.subheader("3. Compliance & Vendor Links")
    biddle_stat = st.selectbox("Biddle EEO Audit Status", ["🟢 Verified", "🔴 Unsigned Policy"], index=["🟢 Verified", "🔴 Unsigned Policy"].index(s["biddle_status"]))
    tpa = st.checkbox("National TPA Data Link Active", value=s["tpa_linked"])
    
    st.subheader("4. TPRV Global Oversight")
    rev = st.selectbox("Assigned Human Reviewer", ["Unassigned", "John Smith (VP HR)", "Sarah Lee (Chief Risk Officer)"], index=["Unassigned", "John Smith (VP HR)", "Sarah Lee (Chief Risk Officer)"].index(s["reviewer"]))
    stat = st.selectbox("Service Validation Status", ["🟢 Green (Valid)", "🟡 Yellow (Pending)", "🔴 Red (Expired/Invalid)"], index=["🟢 Green (Valid)", "🟡 Yellow (Pending)", "🔴 Red (Expired/Invalid)"].index(s["service_status"]))
    
    if st.button("Sync Federated Network"):
        with st.spinner("Aggregating Systems of Record..."):
            time.sleep(1.5)
            s.update({"title": t, "jurisdiction": j, "reviewer": rev, "adp_status": adp_stat, "msp_status": msp_stat, "biddle_status": biddle_stat, "tpa_linked": tpa, "service_status": stat,
                      "verified_title": t, "verified_jur": j, "verified_reviewer": rev, "verified_adp": adp_stat, "verified_msp": msp_stat, "verified_biddle": biddle_stat, "verified_tpa": tpa, "verified_status": stat})
            st.rerun()

# --- ENTERPRISE PORTALS (TABS) ---
st.title("🛡️ TPRV: Teams Planning Roles Validation")
tab1, tab2, tab3, tab4 = st.tabs(["🤖 Federated AI Gatekeeper", "🤝 Partner Data Hub", "⚖️ Litigation & Audit Readiness", "📊 Dynamic Network Report"])

# --- TAB 1: FEDERATED AI GATEKEEPER ---
with tab1:
    col_matrix, col_chat = st.columns([1, 2.2])
    
    with col_matrix:
        st.markdown("### 🧬 Identity Matrix")
        st.write("Real-time assembly of SoR compliance.")
        
        st.markdown(f"""
        <div class="metric-box">
            <small style="color:#94a3b8">ADP System (HR & Payroll)</small><br>
            <strong>Role:</strong> {s['verified_title']}<br>
            <strong>Location:</strong> {s['verified_jur']}<br>
            <strong>Status:</strong> <span class="{'sor-green' if '🟢' in s['verified_adp'] else 'sor-red'}">{s['verified_adp']}</span>
        </div>
        <div class="metric-box">
            <small style="color:#94a3b8">MSP (IT Security)</small><br>
            <strong>M365/Copilot Access:</strong> <span class="{'sor-green' if '🟢' in s['verified_msp'] else 'sor-red'}">{'Granted' if '🟢' in s['verified_msp'] else 'Revoked'}</span><br>
            <strong>Status:</strong> <span class="{'sor-green' if '🟢' in s['verified_msp'] else 'sor-red'}">{s['verified_msp']}</span>
        </div>
        <div class="metric-box">
            <small style="color:#94a3b8">Biddle Consulting</small><br>
            <strong>EEO Signature:</strong> <span class="{'sor-green' if '🟢' in s['verified_biddle'] else 'sor-red'}">{'On File' if '🟢' in s['verified_biddle'] else 'Missing'}</span><br>
            <strong>Status:</strong> <span class="{'sor-green' if '🟢' in s['verified_biddle'] else 'sor-red'}">{s['verified_biddle']}</span>
        </div>
        <div class="metric-box" style="border-color: #38bdf8;">
            <small style="color:#38bdf8">TPRV Global Validation</small><br>
            <strong>Reviewer:</strong> {s['verified_reviewer']}<br>
            <strong>Service:</strong> {s['verified_status']}
        </div>
        """, unsafe_allow_html=True)

    with col_chat:
        st.markdown("### Executive Quick Prompts")
        cols = st.columns(2)
        quick = None
        if cols[0].button("Query Cyber Incident Recovery Plans"): quick = "What is the Cyber Attack Incident Recovery Plan Test activities count in this time period?"
        if cols[0].button("Execute DORA/STP Payments Sync"): quick = "Execute DORA Smart Contract Reconciliation for Chiro Payments"
        if cols[1].button("Analyze Healthcare Services Billing"): quick = "What is the Emergency Room Treatment Services count in this time period?"
        if cols[1].button("Analyze COI Exclusions"): quick = "Read Certificates of Insurance and identify underwriting exclusions."

        prompt = st.chat_input("Prompt Enterprise Copilot...") or quick

        if prompt:
            st.chat_message("user").write(prompt)
            with st.chat_message("assistant"), st.status("Verifying Federated Identity...", expanded=True) as status:
                time.sleep(1.5)
                
                # UNIVERSAL KILL SWITCHES
                if "🔴" in s["verified_status"]:
                    st.error(f"🚨 ACCESS DENIED: Service Validation Status is RED. Mandatory human reviewer ({s['verified_reviewer']}) must approve updates before AI access is restored.")
                    log_event("DENY", "Status Red (Expired/Invalid)")
                    status.update(label="Access Denied", state="error")
                    st.stop()
                if "🔴" in s["verified_adp"]:
                    st.error("🚨 ACCESS DENIED: ADP Feed indicates user is terminated/disconnected. All M365/Copilot access revoked.")
                    log_event("DENY", "ADP Terminated")
                    status.update(label="Access Denied", state="error")
                    st.stop()
                if "🔴" in s["verified_msp"]:
                    st.error("🚨 ACCESS DENIED: MSP indicates IT/AI licensing is suspended. Copilot execution blocked.")
                    log_event("DENY", "MSP Revoked")
                    status.update(label="Access Denied", state="error")
                    st.stop()
                if "🔴" in s["verified_biddle"]:
                    st.error("🚨 ACCESS DENIED: Biddle EEO Audit failed. Policy signature missing. Access suspended to mitigate liability.")
                    log_event("DENY", "Biddle EEO Unsigned")
                    status.update(label="Access Denied", state="error")
                    st.stop()

                # ROLE VALIDATION GRANTS
                if s["verified_title"] == "IT Security Manager" and "Cyber" in prompt:
                    st.success(f"✅ ROLE VALIDATED (IT Security Manager). All SoR checks GREEN.")
                    st.write("**AI Output:** Accessing Incident Recovery Plans. There were 14 Cyber Attack Incident Recovery Plan Test activities logged. Integrating internal IT Security Policy Section 3 containment procedures with State Attorney General reporting requirements.")
                    log_event("ALLOW", "Cyber Recovery Grant")
                    status.update(label="Authorized", state="complete")
                    
                elif s["verified_title"] == "Claims Adjuster" and "Emergency" in prompt:
                    st.success(f"✅ ROLE VALIDATED (Claims Adjuster). Authenticated by Reviewer: {s['verified_reviewer']}.")
                    st.write("**AI Output:** Accessing Healthcare Services Reconciliation Plan. There were 342 Emergency Room Treatment Services counts in this time period linked to Workers Comp.")
                    log_event("ALLOW", "Healthcare Claims Grant")
                    status.update(label="Authorized", state="complete")

                elif s["verified_title"] == "Bank KYC Manager" and "DORA" in prompt:
                    if not s["verified_tpa"]:
                        st.error("🚨 EXTERNAL DATA DENIED: National TPA Data Link is offline. Cannot execute Straight Through Processing (STP) for Chiro Payments without verified Claims Administrator data.")
                        log_event("DENY", "Missing TPA Data Link")
                        status.update(label="Access Denied", state="error")
                        st.stop()
                    else:
                        st.success(f"✅ ROLE VALIDATED (Bank KYC Manager) & TPA LINK VERIFIED.")
                        st.write("**AI Output:** Executing DORA Compliance protocols. Reconciling National TPA Healthcare Services data with Texas/PA Rehab Center Blockchain Smart Contracts for Chiro Payments. STP validation successful.")
                        log_event("ALLOW", "DORA STP Sync Grant")
                        status.update(label="Authorized", state="complete")

                elif s["verified_title"] == "Risk Manager" and "COI" in prompt:
                    st.success(f"✅ ROLE VALIDATED (Risk Manager). Authenticated by Reviewer: {s['verified_reviewer']}.")
                    st.write("**AI Output: COI Document Analysis.**\n* Certificate #4029-TX Scanned.\n* **Exclusions Found:** Force Majeure property damage excluded.\n* **Endorsements Found:** Additional Insured coverage applies to Subcontractors.\n* Underwriting conditions verified against corporate risk profile.")
                    log_event("ALLOW", "COI Analysis Grant")
                    status.update(label="Authorized", state="complete")

                elif s["verified_title"] == "L2 Helpdesk":
                    st.error("🚨 ACCESS DENIED: Your verified role (L2 Helpdesk) lacks the authorized AI Knowledge Validation to query sensitive enterprise data.")
                    log_event("DENY", "Helpdesk Block")
                    status.update(label="Access Denied", state="error")
                    st.stop()
                    
                else:
                    st.error(f"🚨 ACCESS DENIED: Your validated role ({s['verified_title']}) does not map to the AI Topic Knowledge required for this query. (See Prompts Library mapping).")
                    log_event("DENY", "Topic Mismatch")
                    status.update(label="Access Denied", state="error")
                    st.stop()

# --- TAB 2: PARTNER DATA HUB ---
with tab2:
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