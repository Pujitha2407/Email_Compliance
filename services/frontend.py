import json
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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    /* HEADER */

    .title {
        font-size: 32px;
        font-weight: 700;
    }

    .subtitle {
        color: #888888;
        font-size: 15px;
        margin-top: 4px;
        margin-bottom: 25px;
    }


    /* METRIC CARDS */

    .metric-box {
        background-color: #ffffff;
        padding: 18px 20px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        min-height: 95px;
    }

    .metric-title {
        color: #737983;
        font-size: 14px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 700;
        margin-top: 6px;
    }


    /* EMAIL INFO */

    .email-box {
        background-color: #f8f9fb;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
    }


    /* ANALYSIS */

    .analysis-box {
        background-color: #f8f9fb;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        line-height: 1.5;
    }


    /* EVIDENCE */

    .evidence-box {
        background-color: #fff8e6;
        padding: 14px;
        border-radius: 10px;
        border-left: 4px solid #d29b18;
    }


    /* POLICY */

    .policy-box {
        background-color: #fafbfc;
        padding: 12px 15px;
        margin-bottom: 8px;
        border-left: 3px solid #7c83fd;
        border-radius: 6px;
    }


    /* RISK BADGE */

    .risk-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        color: white;
        font-size: 12px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FIND REPORT.JSON
# ============================================================

# Project structure:
#
# EMAIL_COMPLIANCE/
#
#     report.json
#
#     services/
#         frontend.py
#
# Therefore:
# frontend.py -> parent = services
# parent.parent = EMAIL_COMPLIANCE

BASE_DIR = Path(__file__).resolve().parent.parent

REPORT_FILE = BASE_DIR / "report.json"


# ============================================================
# LOAD REPORT
# ============================================================

def load_results():

    if not REPORT_FILE.exists():

        st.error(
            f"report.json not found:\n{REPORT_FILE}"
        )

        return {}

    try:

        with open(
            REPORT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, dict):

            st.error(
                "report.json must contain a JSON object."
            )

            return {}

        return data

    except json.JSONDecodeError as error:

        st.error(
            f"Invalid JSON in report.json: {error}"
        )

        return {}

    except Exception as error:

        st.error(
            f"Unable to read report.json: {error}"
        )

        return {}


results = load_results()


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
# RISK CONFIGURATION
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
# EXTRACT EMAIL DATA
# ============================================================

def extract_email_data(mail_id, result):

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    email = result.get(
        "email",
        {}
    )

    if not isinstance(email, dict):

        email = {}


    sender = email.get(
        "from",
        "Unknown"
    )

    recipient = email.get(
        "to",
        "Unknown"
    )

    subject = email.get(
        "subject",
        "No subject"
    )

    body = email.get(
        "body",
        ""
    )


    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    status = result.get(
        "status",
        "Unknown"
    )

    risk = normalize_risk(
        status
    )


    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    classification = result.get(
        "classification",
        "Unknown"
    )


    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    score = result.get(
        "score",
        "N/A"
    )


    # --------------------------------------------------------
    # RISK CATEGORIES
    # --------------------------------------------------------

    risk_categories = result.get(
        "risk_categories",
        []
    )

    if not isinstance(
        risk_categories,
        list
    ):

        risk_categories = []


    categories = []

    reasons = []

    evidences = []


    for risk_item in risk_categories:

        if not isinstance(
            risk_item,
            dict
        ):
            continue


        category = risk_item.get(
            "category"
        )

        reason = risk_item.get(
            "reason"
        )

        evidence = risk_item.get(
            "evidence"
        )


        if category:

            categories.append(
                str(category)
            )


        if reason:

            reasons.append(
                str(reason)
            )


        if evidence:

            evidences.append(
                str(evidence)
            )


    # --------------------------------------------------------
    # DEFAULT VALUES
    # --------------------------------------------------------

    if not categories:

        categories = [
            "No risk category identified"
        ]


    if not reasons:

        reasons = [
            "No AI analysis available."
        ]


    return {
        "mail_id": mail_id,
        "result": result,
        "sender": sender,
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "risk": risk,
        "classification": classification,
        "score": score,
        "categories": categories,
        "reasons": reasons,
        "evidences": evidences
    }


# ============================================================
# PREPARE ALL EMAILS
# ============================================================

email_data = []


for mail_id, result in results.items():

    if not isinstance(
        result,
        dict
    ):

        continue


    email = extract_email_data(
        mail_id,
        result
    )


    email_data.append(
        email
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
# HEADER
# ============================================================

header_col, refresh_col = st.columns(
    [6, 1]
)


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
# SUMMARY COUNTS
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
# METRIC CARD
# ============================================================

def show_metric(
    column,
    title,
    value,
    color
):

    with column:

        st.markdown(
            f"""
            <div class="metric-box">

                <div class="metric-title">
                    {title}
                </div>

                <div
                    class="metric-value"
                    style="color: {color};"
                >
                    {value}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# SUMMARY CARDS
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

st.subheader(
    "Recent Emails"
)


st.caption(
    "Sorted by risk priority: "
    "Critical → High → Medium → Low"
)


# ============================================================
# EMAIL LIST
# ============================================================

for index, email in enumerate(
    email_data,
    start=1
):

    risk = email["risk"]

    icon = RISK_ICON[risk]

    color = RISK_COLOR[risk]


    # --------------------------------------------------------
    # EMAIL HEADER
    # --------------------------------------------------------

    with st.expander(
        f"{icon}  {index} | "
        f"{email['sender']} | "
        f"{email['subject']} | "
        f"{risk}"
    ):


        # ====================================================
        # EMAIL INFORMATION
        # ====================================================

        st.markdown(
            "### 📧 Email Details"
        )


        col1, col2 = st.columns(2)


        with col1:

            st.caption(
                "From"
            )

            st.write(
                email["sender"]
            )


        with col2:

            st.caption(
                "To"
            )

            st.write(
                email["recipient"]
            )


        st.caption(
            "Subject"
        )

        st.write(
            email["subject"]
        )


        # ====================================================
        # RISK INFORMATION
        # ====================================================

        st.divider()


        col1, col2, col3 = st.columns(3)


        with col1:

            st.caption(
                "Risk Level"
            )

            st.markdown(
                f"""
                <span
                    class="risk-badge"
                    style="background:{color};"
                >
                    {icon} {risk}
                </span>
                """,
                unsafe_allow_html=True
            )


        with col2:

            st.caption(
                "Classification"
            )

            st.write(
                email["classification"]
            )


        with col3:

            st.caption(
                "Score"
            )

            st.write(
                email["score"]
            )


        # ====================================================
        # RISK CATEGORIES
        # ====================================================

        st.markdown(
            "### 🏷️ Risk Category"
        )


        for category in email["categories"]:

            st.write(
                f"• {category}"
            )


        # ====================================================
        # AI ANALYSIS
        # ====================================================

        st.markdown(
            "### 🤖 AI Analysis"
        )


        for reason in email["reasons"]:

            st.markdown(
                f"""
                <div class="analysis-box">
                    {reason}
                </div>
                """,
                unsafe_allow_html=True
            )


        # ====================================================
        # EVIDENCE
        # ====================================================

        if email["evidences"]:

            st.markdown(
                "### 🔎 Evidence"
            )


            for evidence in email["evidences"]:

                st.markdown(
                    f"""
                    <div class="evidence-box">
                        {evidence}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # ====================================================
        # EMAIL BODY
        # ====================================================

        with st.expander(
            "View Email Body"
        ):

            if email["body"]:

                st.write(
                    email["body"]
                )

            else:

                st.caption(
                    "No email body available."
                )


        # ====================================================
        # COMPLETE ANALYSIS
        # ====================================================

        with st.expander(
            "View Complete Analysis"
        ):

            st.json(
                email["result"]
            )