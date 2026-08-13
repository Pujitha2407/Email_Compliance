import streamlit as st
import json

st.set_page_config(
    page_title="COMPLY AI",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ COMPLY AI")
st.caption("Email Compliance Dashboard")

# Load latest results
with open("report.json", "r", encoding="utf-8") as f:
    results = json.load(f)

# Summary
total = len(results)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Emails", total)

with col2:
    st.metric("Critical", sum(
        1 for r in results.values()
        if str(r.get("status", "")).lower() == "critical"
    ))

with col3:
    st.metric("High", sum(
        1 for r in results.values()
        if str(r.get("status", "")).lower() == "high"
    ))

with col4:
    st.metric("Medium", sum(
        1 for r in results.values()
        if str(r.get("status", "")).lower() == "medium"
    ))

with col5:
    st.metric("Low", sum(
        1 for r in results.values()
        if str(r.get("status", "")).lower() == "low"
    ))

st.divider()

st.subheader("Emails")

# Email dropdowns
for mail_id, result in results.items():

    risk = result.get("risk_level", "Unknown")
    category = result.get("risk_category", "Unknown")

    with st.expander(
        f"📧 {mail_id}   |   {category}   |   {risk}"
    ):

        st.write("### AI Analysis")

        st.write(
            result.get(
                "reasoning",
                result.get("explanation", "No explanation available.")
            )
        )

        # Show extra information only when expanded
        with st.expander("View Details"):
            st.json(result)