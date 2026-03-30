import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- STATE MANAGEMENT ---
if 'v4_state' not in st.session_state:
    st.session_state.v4_state = {
        "title": "L2 Helpdesk", 
        "jurisdiction": "New York",
        "eeo_signed": True,
        "tpa_linked": True,
        "reviewer": "Unassigned",
        "service_status": "🟢 Green (Valid)",
        "verified_title": "L2 Helpdesk",
        "verified_jur": "New York",
        "verified_eeo": True,
        "verified_tpa": True,
        "verified_reviewer": "Unassigned",
        "verified_status": "🟢 Green (Valid)",
        "log": []
    }

def log_event(outcome, rationale):
    s = st.session_state.v4_state
    s["log"].insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Context": f"{s['verified_title']} ({s['verified_jur']}) | Rev: {s['verified_reviewer']}",
        "Outcome": outcome,
        "Rationale": rationale
    })

# --- CONFIG & STYLING ---
st.set_page_config(page_title="Enterprise AI Gatekeeper V4", layout="wide")
st.markdown("""<style>
.metric-container { background: #334155; padding: 15px; border-radius: 10px; }
div.stButton > button:first-child { font-weight: 500; letter-spacing: 0.5px; border: 1px solid #38bdf8; }
</style>""", unsafe_allow_html=True)

s = st.session_state.v4_state

# --- HRIS CONTROL PANEL (SIDEBAR) ---
with st.sidebar:
    st.header("🔑 HRIS Control Panel")
    st.markdown("*(Simulates ADP Source of Truth)*")
    t = st.selectbox("Job Title", ["L2 Helpdesk", "Claims Adjuster", "Safety Manager", "IT Security Manager", "Bank KYC Manager", "Risk Manager"], index=["L2 Helpdesk", "Claims Adjuster", "Safety Manager", "IT Security Manager", "Bank KYC Manager", "Risk Manager"].index(s["title"]))
    j = st.selectbox("Jurisdiction", ["Texas", "New York", "Pennsylvania"], index=["Texas", "New York", "Pennsylvania"].index(s["jurisdiction"]))
    rev = st.selectbox("Assigned Human Reviewer", ["Unassigned", "John Smith (VP HR)", "Sarah Lee (Chief Risk Officer)"], index=["Unassigned", "John Smith (VP HR)", "Sarah Lee (Chief Risk Officer)"].index(s["reviewer"]))
    stat = st.selectbox("Service Validation Status", ["🟢 Green (Valid)", "🟡 Yellow (Pending)", "🔴 Red (Expired/Invalid)"], index=["🟢 Green (Valid)", "🟡 Yellow (Pending)", "🔴 Red (Expired/Invalid)"].index(s["service_status"]))
    
    e = st.checkbox("EEO Policy Signed (Biddle Audit)", value=s["eeo_signed"])
    tpa = st.checkbox("National TPA Data Link Active", value=s["tpa_linked"])
    
    if st.button("Sync to Entra ID (Update Roles)"):
        with st.spinner("Syncing middleware..."):
            time.sleep(1)
            s.update({"title": t, "jurisdiction": j, "eeo_signed": e, "tpa_linked": tpa, "reviewer": rev, "service_status": stat, "verified_title": t, "verified_jur": j, "verified_eeo": e, "verified_tpa": tpa, "verified_reviewer": rev, "verified_status": stat})
            st.rerun()

# --- AI GATEKEEPER TERMINAL ---
st.title("🛡️ TPRV AI Gatekeeper Terminal")
st.markdown(f"**USER:** Jane Doe | **ROLE:** <span style='color:#10b981'>{s['verified_title']}</span> | **REVIEWER:** {s['verified_reviewer']} | **STATUS:** {s['verified_status']} | **EEO:** {'✅' if s['verified_eeo'] else '❌'} | **TPA LINK:** {'✅' if s['verified_tpa'] else '❌'}", unsafe_allow_html=True)

st.markdown("### Executive Quick Prompts")
cols = st.columns(4)
quick = None
if cols[0].button("Query Texas Data Breach Protocols"): quick = "Query Texas Data Breach Protocols"
if cols[1].button("Execute DORA/STP Payments Sync"): quick = "Execute DORA Smart Contract Reconciliation for Chiro Payments"
if cols[2].button("Analyze COI Exclusions & Endorsements"): quick = "Read Certificates of Insurance and identify underwriting exclusions."
if cols[3].button("Generate Claims Trail of Evidence"): quick = "Build Trail of Evidence for Healthcare Billing (Billed vs Approved)"

prompt = st.chat_input("Prompt Enterprise Copilot...") or quick

if prompt:
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"), st.status("Analyzing Authorization Context...", expanded=True) as status:
        time.sleep(1.5)
        
        # RULE 0: Status Color-Coding Kill Switch
        if "🔴" in s["verified_status"]:
            st.error(f"🚨 ACCESS DENIED: Service Validation Status is RED. Mandatory human reviewer ({s['verified_reviewer']}) must approve updates before AI access is restored.")
            log_event("DENY", "Status Red (Expired/Invalid)")
            status.update(label="Access Denied", state="error")
            st.stop()

        # RULE 0.5: The Universal Compliance Kill Switch
        if not s["verified_eeo"]:
            st.error("🚨 ACCESS DENIED: HRIS flag indicates missing EEO policy signature. AI access suspended to prevent Biddle Consulting EEO Audit failure.")
            log_event("DENY", "Missing Policy Signature (Biddle)")
            status.update(label="Access Denied", state="error")
            st.stop()

        # RULE 1: State Compliance Block (Jurisdiction Mismatch)
        if "texas" in prompt.lower() and s["verified_jur"] != "Texas":
            st.error(f"🚨 JURISDICTION DENIED: Your HR profile maps to {s['verified_jur']}. You lack authorized AI Role Validation for Texas State Compliance reporting.")
            log_event("DENY", "Jurisdiction Mismatch")
            status.update(label="Access Denied", state="error")
            st.stop()
            
        # RULE 2: IT Security Grant (Data Breach)
        elif s["verified_title"] == "IT Security Manager" and s["verified_jur"] == "Texas":
            st.success("✅ ROLE VALIDATED (IT Security Manager - TX).")
            st.write("**AI Output:** Initiating Texas Data Privacy Act protocols. Integrating internal IT Security Policy Section 3 containment procedures with State Attorney General reporting requirements.")
            log_event("ALLOW", "IT Sec TX Grant")
            status.update(label="Authorized", state="complete")

        # RULE 3: Safety Manager Grant (FROI & Transitional Duty)
        elif s["verified_title"] == "Safety Manager" and s["verified_jur"] == "Texas":
            st.success("✅ ROLE VALIDATED (Safety Manager - TX).")
            st.write("**AI Output:** Generating Texas State First Report of Injury (FROI). Cross-referencing incident with internal Transitional Duty Policy to ensure 90-day temporary assignment compliance. Biddle EEO parameters verified.")
            log_event("ALLOW", "Safety FROI Grant")
            status.update(label="Authorized", state="complete")
            
        # RULE 4: Bank KYC Manager (DORA/STP Reconciliation)
        elif s["verified_title"] == "Bank KYC Manager":
            if not s["verified_tpa"]:
                st.error("🚨 EXTERNAL DATA DENIED: National TPA Data Link is offline. Cannot execute Straight Through Processing (STP) for Chiro Payments without verified Claims Administrator data.")
                log_event("DENY", "Missing TPA Data Link")
                status.update(label="Access Denied", state="error")
                st.stop()
            else:
                st.success(f"✅ ROLE VALIDATED (Bank KYC Manager) & TPA LINK VERIFIED. Logged to Human Reviewer: {s['verified_reviewer']}.")
                st.write("**AI Output:** Executing DORA Compliance protocols. Reconciling National TPA Healthcare Services data with Texas/PA Rehab Center Blockchain Smart Contracts for Chiro Payments. STP validation successful.")
                log_event("ALLOW", "DORA STP Sync Grant")
                status.update(label="Authorized", state="complete")

        # RULE 5: Claims Adjuster Grant (Trail of Evidence & Cost of Health)
        elif s["verified_title"] == "Claims Adjuster":
            st.success(f"✅ ROLE VALIDATED (Claims Adjuster). Authenticated by Reviewer: {s['verified_reviewer']}.")
            st.write("**AI Output: Trail of Evidence Generated.**\n* Cross-referencing Healthcare Billing vs. Insurance Approvals.\n* David Lee (POL-10001): Billed $15,258 | Approved $13,573 | Variance flagged for automated denial review.\n* Medical necessity documentation appended to legal defense file.")
            log_event("ALLOW", "Claims Evidence Grant")
            status.update(label="Authorized", state="complete")

        # RULE 6: Risk Manager Grant (COI Analysis)
        elif s["verified_title"] == "Risk Manager":
            st.success(f"✅ ROLE VALIDATED (Risk Manager). Authenticated by Reviewer: {s['verified_reviewer']}.")
            st.write("**AI Output: COI Document Analysis.**\n* Certificate #4029-TX Scanned.\n* **Exclusions Found:** Force Majeure property damage excluded.\n* **Endorsements Found:** Additional Insured coverage applies to Subcontractors.\n* Underwriting conditions verified against corporate risk profile.")
            log_event("ALLOW", "COI Analysis Grant")
            status.update(label="Authorized", state="complete")
            
        # RULE 7: Default Helpdesk Block (Shadow AI Prevention)
        elif s["verified_title"] == "L2 Helpdesk":
            st.error("🚨 ACCESS DENIED: Your verified role (L2 Helpdesk) lacks the authorized AI Knowledge Validation to query HR Policies, OSHA Logs, or Financial Data.")
            log_event("DENY", "Helpdesk Block")
            status.update(label="Access Denied", state="error")
            st.stop()
            
        else:
            st.success(f"✅ ROLE VALIDATED ({s['verified_title']}). Accessing standard policies...")
            log_event("ALLOW", "Standard Access")
            status.update(label="Authorized", state="complete")

# --- DASHBOARD & LOGS ---
st.divider()
st.subheader("📈 C-Suite Risk Management Telemetry")
m1, m2, m3 = st.columns(3)
m1.metric("Systems AI Alignment Review %", "94%", "+12%")
m2.metric("TEAMS Network Roles Validated", "88%", "+5%")
m3.metric("FTE AI Productivity Index", "8.4", "+1.2")

if s["log"]:
    st.markdown("### 📡 Real-Time Entra ID Security Audit Log")
    st.dataframe(pd.DataFrame(s["log"]), use_container_width=True, hide_index=True)