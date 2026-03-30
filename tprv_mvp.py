import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- STATE MANAGEMENT ---
if 'v6_state' not in st.session_state:
    st.session_state.v6_state = {
        "title": "Claims Adjuster", 
        "jurisdiction": "Texas",
        "eeo_signed": True,
        "tpa_linked": True,
        "reviewer": "Sarah Lee (Chief Risk Officer)",
        "service_status": "🟢 Green (Valid)",
        "verified_title": "Claims Adjuster",
        "verified_jur": "Texas",
        "verified_eeo": True,
        "verified_tpa": True,
        "verified_reviewer": "Sarah Lee (Chief Risk Officer)",
        "verified_status": "🟢 Green (Valid)",
        "partner_services": [],
        "log": []
    }

def log_event(outcome, rationale):
    s = st.session_state.v6_state
    s["log"].insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Context": f"{s['verified_title']} ({s['verified_jur']}) | Rev: {s['verified_reviewer']}",
        "Outcome": outcome,
        "Rationale": rationale
    })

# --- CONFIG & STYLING ---
st.set_page_config(page_title="TPRV Enterprise Platform", layout="wide")
st.markdown("""<style>
div.stButton > button:first-child { font-weight: 500; letter-spacing: 0.5px; border: 1px solid #38bdf8; }
.partner-box { border: 1px solid #475569; padding: 20px; border-radius: 8px; background-color: #1e293b; }
</style>""", unsafe_allow_html=True)

s = st.session_state.v6_state

# --- HRIS CONTROL PANEL (SIDEBAR) ---
with st.sidebar:
    st.header("🔑 Master HRIS Sync")
    st.markdown("*(Simulates ADP/System of Record)*")
    t = st.selectbox("Job Title", ["L2 Helpdesk", "Claims Adjuster", "Safety Manager", "IT Security Manager", "Bank KYC Manager", "Risk Manager"], index=["L2 Helpdesk", "Claims Adjuster", "Safety Manager", "IT Security Manager", "Bank KYC Manager", "Risk Manager"].index(s["title"]))
    j = st.selectbox("Jurisdiction", ["Texas", "New York", "Pennsylvania"], index=["Texas", "New York", "Pennsylvania"].index(s["jurisdiction"]))
    rev = st.selectbox("Assigned Human Reviewer", ["Unassigned", "John Smith (VP HR)", "Sarah Lee (Chief Risk Officer)"], index=["Unassigned", "John Smith (VP HR)", "Sarah Lee (Chief Risk Officer)"].index(s["reviewer"]))
    stat = st.selectbox("Service Validation Status", ["🟢 Green (Valid)", "🟡 Yellow (Pending)", "🔴 Red (Expired/Invalid)"], index=["🟢 Green (Valid)", "🟡 Yellow (Pending)", "🔴 Red (Expired/Invalid)"].index(s["service_status"]))
    
    e = st.checkbox("EEO Policy Signed (Biddle Audit)", value=s["eeo_signed"])
    tpa = st.checkbox("National TPA Data Link Active", value=s["tpa_linked"])
    
    if st.button("Sync Network Data"):
        with st.spinner("Syncing Identity & Roles..."):
            time.sleep(1)
            s.update({"title": t, "jurisdiction": j, "eeo_signed": e, "tpa_linked": tpa, "reviewer": rev, "service_status": stat, 
                      "verified_title": t, "verified_jur": j, "verified_eeo": e, "verified_tpa": tpa, "verified_reviewer": rev, "verified_status": stat})
            st.rerun()

# --- ENTERPRISE PORTALS (TABS) ---
st.title("🛡️ TPRV: Teams Planning Roles Validation")
tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI Gatekeeper", "🤝 Partner Data Hub", "⚖️ Litigation & Audit Readiness", "📊 Dynamic Network Report"])

# --- TAB 1: AI GATEKEEPER (Existing Core) ---
with tab1:
    st.markdown(f"**USER:** Jane Doe | **ROLE:** <span style='color:#10b981'>{s['verified_title']}</span> | **STATUS:** {s['verified_status']}", unsafe_allow_html=True)
    
    cols = st.columns(3)
    quick = None
    if cols[0].button("Analyze COI Exclusions"): quick = "Read Certificates of Insurance and identify underwriting exclusions."
    if cols[1].button("Generate Claims Trail of Evidence"): quick = "Build Trail of Evidence for Healthcare Billing (Billed vs Approved)"
    if cols[2].button("Verify Essential Duties Testing"): quick = "Cross-reference employee injury with ADA Essential Duties."

    prompt = st.chat_input("Prompt Enterprise Copilot...") or quick

    if prompt:
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"), st.status("Validating Role Context...", expanded=True) as status:
            time.sleep(1.5)
            
            if "🔴" in s["verified_status"]:
                st.error(f"🚨 ACCESS DENIED: Service Validation is RED. Mandatory human reviewer ({s['verified_reviewer']}) must approve updates.")
                status.update(label="Access Denied", state="error")
                st.stop()

            if not s["verified_eeo"]:
                st.error("🚨 ACCESS DENIED: Missing EEO policy signature. AI access suspended to prevent Biddle Consulting EEO Audit failure.")
                status.update(label="Access Denied", state="error")
                st.stop()

            if s["verified_title"] == "Claims Adjuster":
                st.success(f"✅ ROLE VALIDATED (Claims Adjuster). Authenticated by Reviewer: {s['verified_reviewer']}.")
                st.write("**AI Output: Trail of Evidence Generated.**\n* **Cost of Health Analysis:** David Lee (POL-10001)\n* **Billed Amount:** $15,258 | **Approved Amount:** $13,573\n* **Variance:** $1,685 flagged. Automated carrier denial intercepted.\n* **Essential Duties Test:** Verified. Employee meets physical requirements for Transitional Duty.")
                log_event("ALLOW", "Claims Evidence Grant")
                status.update(label="Authorized", state="complete")
            else:
                st.error("🚨 ACCESS DENIED: Your verified role lacks the authorized AI Knowledge Validation to query Financial or Claims Data.")
                status.update(label="Access Denied", state="error")
                st.stop()

# --- TAB 2: PARTNER DATA HUB ---
with tab2:
    st.markdown("### 🤝 Partner Services Integration Hub")
    st.write("Partners dump updated service data here, linking directly to the Human Purchaser to drive recurring revenue tracking.")
    
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
            st.markdown("#### 📄 Exhibit A: HR Validation Proof")
            st.code(f"""
Human Identity: Jane Doe
Assigned Role: Claims Adjuster
Assigned Reviewer: {s['verified_reviewer']}
EEO Audit Status (Biddle): PASS
HIPAA Training Status: PASS
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
        st.info("💡 **Litigation Value:** This packet proves to Underwriters and Courts that the claim was processed by a validated, EEO/HIPAA-compliant human, overriding automated carrier denials.")

# --- TAB 4: DYNAMIC NETWORK REPORT ---
with tab4:
    st.markdown("### 📊 Dynamic Role Validation Network")
    st.write("Constant validation of human roles and their review status within the organizational network.")
    
    # Mock Network Data
    network_data = pd.DataFrame([
        {"Employee": "Jane Doe", "Role": s['verified_title'], "Jurisdiction": s['verified_jur'], "Reviewer": s['verified_reviewer'], "Status": s['verified_status']},
        {"Employee": "John Smith", "Role": "VP HR", "Jurisdiction": "New York", "Reviewer": "Board of Directors", "Status": "🟢 Green (Valid)"},
        {"Employee": "Robert Chen", "Role": "L2 Helpdesk", "Jurisdiction": "Texas", "Reviewer": "IT Director", "Status": "🟡 Yellow (Pending EEO)"},
        {"Employee": "Alice Ford", "Role": "Bank KYC Manager", "Jurisdiction": "Pennsylvania", "Reviewer": "Sarah Lee (Chief Risk Officer)", "Status": "🔴 Red (TPA Link Down)"}
    ])
    
    st.dataframe(network_data, use_container_width=True, hide_index=True)

    if s["log"]:
        st.markdown("#### 📡 Recent Network Audit Logs")
        st.dataframe(pd.DataFrame(s["log"]), use_container_width=True, hide_index=True)