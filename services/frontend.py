import json
import streamlit as st
import pandas as pd


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="COMPLY AI",
    page_icon="🛡️",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f7f8fc;
}

.block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

.title {
    font-size: 32px;
    font-weight: 700;
}

.subtitle {
    color: #777;
    margin-bottom: 25px;
}

.metric-box {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #eeeeee;
}

.metric-title {
    color: #777;
    font-size: 14px;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
}

.email-box {
    background: white;
    padding: 5px;
    border-radius: 12px;
    margin-bottom: 8px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD RESULTS
# --------------------------------------------------

def load_results():

    try:

        with open(
            "llm_ouput.json",
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except FileNotFoundError:

        return {}


results = load_results()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

col1, col2 = st.columns([5, 1])

with col1:

    st.markdown(
        '<div class="title">🛡️ COMPLY AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'AI-Powered Email Compliance & Risk Detection'
        '</div>',
        unsafe_allow_html=True
    )

with col2:

    if st.button("↻ Refresh"):

        st.rerun()


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

total = len(results)

high = 0
medium = 0
low = 0

for result in results.values():

    if not isinstance(result, dict):
        continue

    risk = str(
        result.get(
            "risk_level",
            ""
        )
    ).lower()

    if "high" in risk:
        high += 1

    elif "medium" in risk:
        medium += 1

    elif "low" in risk:
        low += 1


col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Total Emails</div>
            <div class="metric-value">{total}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">High Risk</div>
            <div class="metric-value">🔴 {high}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Medium Risk</div>
            <div class="metric-value">🟡 {medium}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:

    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Low Risk</div>
            <div class="metric-value">🟢 {low}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# --------------------------------------------------
# GRAPH + SUMMARY
# --------------------------------------------------

left, right = st.columns([2, 1])


with left:

    st.subheader("Compliance Overview")

    graph_data = pd.DataFrame({
        "Risk": [
            "High",
            "Medium",
            "Low"
        ],
        "Emails": [
            high,
            medium,
            low
        ]
    })

    st.bar_chart(
        graph_data.set_index("Risk"),
        height=280
    )


with right:

    st.subheader("Quick Summary")

    st.write(
        f"📧 **{total}** emails analyzed"
    )

    st.write(
        f"🔴 **{high}** high-risk emails"
    )

    st.write(
        f"🟡 **{medium}** medium-risk emails"
    )

    st.write(
        f"🟢 **{low}** low-risk emails"
    )


st.divider()


# --------------------------------------------------
# EMAILS
# --------------------------------------------------

st.subheader("Recent Emails")

for mail_id, result in results.items():

    if not isinstance(result, dict):
        continue

    risk = result.get(
        "risk_level",
        "Unknown"
    )

    category = result.get(
        "risk_category",
        "Unknown"
    )

    confidence = result.get(
        "confidence",
        result.get(
            "confidence_score",
            "N/A"
        )
    )

    risk_lower = str(
        risk
    ).lower()

    if "high" in risk_lower:
        icon = "🔴"

    elif "medium" in risk_lower:
        icon = "🟡"

    elif "low" in risk_lower:
        icon = "🟢"

    else:
        icon = "⚪"


    # --------------------------------------------------
    # EMAIL DROPDOWN
    # --------------------------------------------------

    with st.expander(
        f"{icon}  {mail_id}   •   {category}   •   {risk}"
    ):

        col1, col2, col3 = st.columns(3)

        with col1:

            st.caption("Risk Level")

            st.write(
                f"{icon} {risk}"
            )

        with col2:

            st.caption("Category")

            st.write(
                category
            )

        with col3:

            st.caption("Confidence")

            st.write(
                confidence
            )


        # --------------------------------------------------
        # AI ANALYSIS
        # --------------------------------------------------

        st.markdown("#### 🤖 AI Analysis")

        reason = result.get(
            "reasoning",
            result.get(
                "reason",
                result.get(
                    "explanation",
                    "No explanation available."
                )
            )
        )

        st.write(reason)


        # --------------------------------------------------
        # RETRIEVED POLICIES
        # --------------------------------------------------

        if "retrieved_policies" in result:

            st.markdown(
                "#### 🔍 Retrieved Policies"
            )

            for i, policy in enumerate(
                result["retrieved_policies"],
                1
            ):

                if isinstance(
                    policy,
                    dict
                ):

                    policy_id = policy.get(
                        "policy_id",
                        "Unknown"
                    )

                    score = policy.get(
                        "similarity_score",
                        ""
                    )

                    st.write(
                        f"**{i}. {policy_id}**"
                        f"  — similarity: {score}"
                    )


        # --------------------------------------------------
        # COMPLETE RESULT
        # --------------------------------------------------

        with st.expander(
            "View complete analysis"
        ):

            st.json(result)