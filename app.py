import streamlit as st
from models import Case, CaseStatus, Paramedic
import proxy_service
import exotel_client

st.set_page_config(page_title="Call Masking", layout="wide")
st.title("Call Masking Demo")

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.subheader("Exotel Config")
    st.code(f"Account  : {exotel_client.ACCOUNT_SID}\nProxy #  : {exotel_client.VIRTUAL_NUMBER}")
    if st.button("Verify Credentials"):
        if exotel_client.verify_credentials():
            st.success("Connected to Exotel")
        else:
            st.error("Auth failed — check .env")

    st.divider()
    st.subheader("How it works")
    st.markdown("""
1. Assign MCO to a case
2. Either party dials the proxy number
3. Exotel hits the webhook
4. Webhook routes to the other party
5. Neither sees the other's real number
""")

# ── Seed session state ────────────────────────────────────────────────────────

if "cases" not in st.session_state:
    st.session_state.cases = {
        "C001": Case(id="C001", patient_name="Test Patient", patient_phone="+919492443995"),
    }

if "paramedics" not in st.session_state:
    st.session_state.paramedics = {
        "P001": Paramedic(id="P001", name="MCO", phone="+919573300791"),
    }

cases = st.session_state.cases
paramedics = st.session_state.paramedics

# ── Layout ────────────────────────────────────────────────────────────────────

left, right = st.columns([3, 2])

with left:
    st.subheader("Cases")

    for case_id, case in cases.items():
        badge = {"open": "🟡 OPEN", "assigned": "🟢 ASSIGNED", "closed": "⚫ CLOSED"}
        label = f"{case_id} — {case.patient_name}  {badge[case.status]}"

        with st.expander(label, expanded=(case.status == CaseStatus.assigned)):
            st.write(f"**Patient:** `{case.patient_phone}`")

            if case.status == CaseStatus.open:
                selected = st.selectbox(
                    "Assign MCO",
                    options=list(paramedics.keys()),
                    format_func=lambda x: f"{paramedics[x].name}  ({paramedics[x].phone})",
                    key=f"sel_{case_id}",
                )
                if st.button("Assign", key=f"assign_{case_id}"):
                    try:
                        updated = proxy_service.assign_paramedic(case, paramedics[selected])
                        cases[case_id] = updated
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

            elif case.status == CaseStatus.assigned:
                paramedic = paramedics[case.paramedic_id]
                st.success(f"Proxy number: `{case.proxy_number}`")
                st.write(f"**MCO:** {paramedic.name} · `{paramedic.phone}`")
                st.info("Either party dials the proxy number to connect.")

                if st.button("Close Case", key=f"close_{case_id}"):
                    updated = proxy_service.close_case(case)
                    cases[case_id] = updated
                    st.rerun()

            elif case.status == CaseStatus.closed:
                st.info("Case closed — proxy session cleared")

with right:
    st.subheader("Active Sessions")
    sessions = proxy_service.get_sessions()
    if sessions:
        for proxy, session in sessions.items():
            st.code(
                f"Proxy   : {proxy}\n"
                f"Patient : {session['patient_phone']}\n"
                f"MCO     : {session['paramedic_phone']}",
                language=None
            )
    else:
        st.caption("No active sessions")
