import json
import html
from pathlib import Path

import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="COMPLY AI",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    .title {
        font-size: 32px;
        font-weight: 700;
        color: #18202a;
    }

    .subtitle {
        color: #777777;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .metric-box {
        background-color: white;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        min-height: 90px;
    }

    .metric-title {
        color: #737983;
        font-size: 14px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 700;
        margin-top: 5px;
    }

    .info-box {
        background-color: #f8f9fb;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
    }

    .analysis-box {
        background-color: #f8f9fb;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
    }

    .policy-box {
        background-color: #fafbfc;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-left: 3px solid #7c83fd;
        border-radius: 6px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD REPORT
# ============================================================

# frontend.py is inside:
#
# EMAIL_COMPLIANCE/
#       services/
#           frontend.py
#
# report.json is inside:
#
# EMAIL_COMPLIANCE/
#       report.json

BASE_DIR = Path(__file__).resolve().parent.parent

REPORT_FILE = BASE_DIR / "report.json"


def load_results():

    if not REPORT_FILE.exists():

        st.error(
            f"report.json not found at: {REPORT_FILE}"
        )

        return {}

    try:

        with open(
            REPORT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data

    except json.JSONDecodeError as error:

        st.error(
            f"report.json contains invalid JSON: {error}"
        )

        return {}

    except Exception as error:

        st.error(
            f"Error reading report.json: {error}"
        )

        return {}


results = load_results()


# ============================================================
# HELPER - GET VALUE
# ============================================================

def get_value(data, possible_keys, default="Unknown"):

    if not isinstance(data, dict):
        return default

    for key in possible_keys:

        value = data.get(key)

        if value is not None:

            value = str(value).strip()

            if value:

                return value

    return default


# ============================================================
# GET SENDER AND SUBJECT
# ============================================================

def get_email_details(result):

    sender = get_value(
        result,
        [
            "sender",
            "sender_email",
            "from",
            "from_email",
            "email_sender",
            "sender_address"
        ]
    )

    subject = get_value(
        result,
        [
            "subject",
            "email_subject",
            "title",
            "email_title"
        ]
    )

    # --------------------------------------------------------
    # Check nested email object
    # --------------------------------------------------------

    email_data = result.get("email")

    if isinstance(email_data, dict):

        if sender == "Unknown":

            sender = get_value(
                email_data,
                [
                    "sender",
                    "sender_email",
                    "from",
                    "from_email"
                ]
            )

        if subject == "Unknown":

            subject = get_value(
                email_data,
                [
                    "subject",
                    "email_subject",
                    "title"
                ]
            )

    return sender, subject


# ============================================================
# NORMALIZE RISK
# ============================================================

def normalize_risk(value):

    risk = str(value).strip().lower()

    if "critical" in risk:
        return "Critical"

    if "high" in risk:
        return "High"

    if "medium" in risk:
        return "Medium"

    if "low" in risk:
        return "Low"

    return "Unknown"


# ============================================================
# RISK SETTINGS
# ============================================================

RISK_PRIORITY = {
    "Critical": 0,
    "High": 1,
    "Medium": 2,
    "Low": 3,
    "Unknown": 4
}


RISK_COLOR = {
    "Critical": "#d9363e",
    "High": "#e87522",
    "Medium": "#d29b18",
    "Low": "#319463",
    "Unknown": "#7b8188"
}


RISK_ICON = {
    "Critical": "🔴",
    "High": "🟠",
    "Medium": "🟡",
    "Low": "🟢",
    "Unknown": "⚪"
}


# ============================================================
# HEADER
# ============================================================

header_col, refresh_col = st.columns([6, 1])

with header_col:

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


with refresh_col:

    if st.button(
        "↻ Refresh",
        use_container_width=True
    ):

        st.rerun()


# ============================================================
# PREPARE EMAIL DATA
# ============================================================

email_data = []


if isinstance(results, dict):

    for mail_id, result in results.items():

        if not isinstance(result, dict):
            continue

        # ----------------------------------------------------
        # Risk
        # ----------------------------------------------------

        risk = normalize_risk(
            result.get(
                "risk_level",
                result.get(
                    "status",
                    "Unknown"
                )
            )
        )

        # ----------------------------------------------------
        # Category
        # ----------------------------------------------------

        category = get_value(
            result,
            [
                "risk_category",
                "category",
                "compliance_category"
            ]
        )

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        confidence = get_value(
            result,
            [
                "confidence",
                "confidence_score"
            ],
            default="N/A"
        )

        # ----------------------------------------------------
        # Sender / Subject
        # ----------------------------------------------------

        sender, subject = get_email_details(result)

        # ----------------------------------------------------
        # Store
        # ----------------------------------------------------

        email_data.append(
            {
                "mail_id": mail_id,
                "result": result,
                "risk": risk,
                "category": category,
                "confidence": confidence,
                "sender": sender,
                "subject": subject
            }
        )


# ============================================================
# SORT EMAILS
# ============================================================

email_data.sort(
    key=lambda email: RISK_PRIORITY.get(
        email["risk"],
        4
    )
)


# ============================================================
# COUNTS
# ============================================================

total = len(email_data)

critical = sum(
    1
    for email in email_data
    if email["risk"] == "Critical"
)

high = sum(
    1
    for email in email_data
    if email["risk"] == "High"
)

medium = sum(
    1
    for email in email_data
    if email["risk"] == "Medium"
)

low = sum(
    1
    for email in email_data
    if email["risk"] == "Low"
)


# ============================================================
# METRIC CARD FUNCTION
# ============================================================

def show_metric(column, title, value, color):

    with column:

        st.markdown(
            f"""
<div class="metric-box">
    <div class="metric-title">{title}</div>
    <div class="metric-value" style="color: {color};">
        {value}
    </div>
</div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# SUMMARY
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)


show_metric(
    col1,
    "Total Emails",
    total,
    "#27313b"
)

show_metric(
    col2,
    "Critical",
    critical,
    RISK_COLOR["Critical"]
)

show_metric(
    col3,
    "High",
    high,
    RISK_COLOR["High"]
)

show_metric(
    col4,
    "Medium",
    medium,
    RISK_COLOR["Medium"]
)

show_metric(
    col5,
    "Low",
    low,
    RISK_COLOR["Low"]
)


st.divider()


# ============================================================
# EMAIL SECTION
# ============================================================

st.subheader("Recent Emails")

st.caption(
    "Sorted by risk priority: Critical → High → Medium → Low"
)


# ============================================================
# DISPLAY EMAILS
# ============================================================

for index, email in enumerate(
    email_data,
    start=1
):

    result = email["result"]

    risk = email["risk"]

    category = email["category"]

    confidence = email["confidence"]

    sender = email["sender"]

    subject = email["subject"]

    icon = RISK_ICON[risk]

    color = RISK_COLOR[risk]


    # --------------------------------------------------------
    # EMAIL DROPDOWN
    # --------------------------------------------------------

    with st.expander(
        f"{icon}  {index} | {sender} | {subject} | {risk}"
    ):

        # ----------------------------------------------------
        # Sender / Subject
        # ----------------------------------------------------

        sender_safe = html.escape(
            str(sender)
        )

        subject_safe = html.escape(
            str(subject)
        )

        st.markdown(
            f"""
<div class="info-box">

<b>📧 Sender</b><br>
{sender_safe}

<br><br>

<b>Subject</b><br>
{subject_safe}

</div>
            """,
            unsafe_allow_html=True
        )


        st.write("")


        # ----------------------------------------------------
        # Risk Information
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)


        with col1:

            st.caption("Risk Level")

            st.markdown(
                f"""
<span style="
background-color:{color};
color:white;
padding:5px 12px;
border-radius:20px;
font-size:12px;
font-weight:600;
">
{icon} {risk}
</span>
                """,
                unsafe_allow_html=True
            )


        with col2:

            st.caption("Risk Category")

            st.write(category)


        with col3:

            st.caption("Confidence")

            st.write(confidence)


        st.divider()


        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        st.markdown(
            "#### 🤖 AI Analysis"
        )


        reason = get_value(
            result,
            [
                "reasoning",
                "reason",
                "explanation",
                "analysis"
            ],
            default="No explanation available."
        )


        reason_safe = html.escape(
            str(reason)
        )


        st.markdown(
            f"""
<div class="analysis-box">
{reason_safe}
</div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # RETRIEVED POLICIES
        # ----------------------------------------------------

        policies = result.get(
            "retrieved_policies"
        )


        if policies:

            st.markdown(
                "#### 🔍 Retrieved Policies"
            )


            for policy_index, policy in enumerate(
                policies,
                start=1
            ):

                if not isinstance(
                    policy,
                    dict
                ):
                    continue


                policy_id = policy.get(
                    "policy_id",
                    "Unknown"
                )


                similarity = policy.get(
                    "similarity_score",
                    "N/A"
                )


                st.markdown(
                    f"""
<div class="policy-box">

<b>{policy_index}. {policy_id}</b>
<br>
Similarity: {similarity}

</div>
                    """,
                    unsafe_allow_html=True
                )


        # ----------------------------------------------------
        # COMPLETE RESULT
        # ----------------------------------------------------

        with st.expander(
            "View complete analysis"
        ):

            st.json(result)