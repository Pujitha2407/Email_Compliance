import json
import html
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

/* ---------- Header ---------- */

.title {
    font-size: 32px;
    font-weight: 700;
    color: #18202a;
}

.subtitle {
    color: #777;
    margin-bottom: 25px;
}


/* ---------- Metric Cards ---------- */

.metric-box {
    background: white;
    padding: 18px 20px;
    border-radius: 14px;
    border: 1px solid #e8eaee;
    min-height: 100px;
}

.metric-title {
    color: #777;
    font-size: 14px;
}

.metric-value {
    font-size: 30px;
    font-weight: 700;
}


/* ---------- Email ---------- */

.email-info {
    padding: 4px 0;
}

.sender {
    font-size: 15px;
    font-weight: 600;
    color: #20262d;
}

.subject {
    font-size: 13px;
    color: #7a818a;
    margin-top: 3px;
}


/* ---------- Risk Badge ---------- */

.risk-badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}


/* ---------- Analysis ---------- */

.analysis-box {
    background: #f7f8fc;
    border-radius: 10px;
    padding: 14px;
    border: 1px solid #e7e9ed;
}


/* ---------- Policy ---------- */

.policy-box {
    background: #fafbfc;
    border-left: 3px solid #7c8cff;
    padding: 10px 14px;
    margin-bottom: 8px;
    border-radius: 5px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD RESULTS
# ============================================================

def load_results():

    try:

        with open(
            "report.json",
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except FileNotFoundError:

        st.error("report.json not found.")

        return {}


results = load_results()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_first_value(data, keys, default="Unknown"):

    if not isinstance(data, dict):
        return default

    for key in keys:

        value = data.get(key)

        if value is not None:

            value = str(value).strip()

            if value:
                return value

    return default


def get_email_details(result):

    """
    Try different possible field names so the UI does not
    unnecessarily show Unknown.
    """

    sender = get_first_value(
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

    subject = get_first_value(
        result,
        [
            "subject",
            "email_subject",
            "title",
            "email_title"
        ]
    )

    # Check nested email object if present
    if isinstance(result.get("email"), dict):

        email_data = result["email"]

        if sender == "Unknown":

            sender = get_first_value(
                email_data,
                [
                    "sender",
                    "sender_email",
                    "from",
                    "from_email"
                ]
            )

        if subject == "Unknown":

            subject = get_first_value(
                email_data,
                [
                    "subject",
                    "email_subject",
                    "title"
                ]
            )

    return sender, subject


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
# HEADER
# ============================================================

col1, col2 = st.columns([6, 1])

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

    if st.button("↻ Refresh", use_container_width=True):

        st.rerun()


# ============================================================
# PREPARE EMAIL DATA
# ============================================================

email_data = []

for mail_id, result in results.items():

    if not isinstance(result, dict):
        continue

    risk = normalize_risk(
        result.get(
            "risk_level",
            result.get("status", "Unknown")
        )
    )

    category = get_first_value(
        result,
        [
            "risk_category",
            "category",
            "compliance_category"
        ]
    )

    confidence = get_first_value(
        result,
        [
            "confidence",
            "confidence_score"
        ],
        default="N/A"
    )

    sender, subject = get_email_details(result)

    email_data.append({
        "mail_id": mail_id,
        "result": result,
        "risk": risk,
        "category": category,
        "confidence": confidence,
        "sender": sender,
        "subject": subject
    })


# ============================================================
# SORT
# ============================================================

email_data.sort(
    key=lambda x: RISK_PRIORITY.get(
        x["risk"],
        4
    )
)


# ============================================================
# SUMMARY COUNTS
# ============================================================

total = len(email_data)

critical = sum(
    1 for x in email_data
    if x["risk"] == "Critical"
)

high = sum(
    1 for x in email_data
    if x["risk"] == "High"
)

medium = sum(
    1 for x in email_data
    if x["risk"] == "Medium"
)

low = sum(
    1 for x in email_data
    if x["risk"] == "Low"
)


# ============================================================
# SUMMARY
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)


def metric_card(column, title, value, color):

    with column:

        st.markdown(
            f"""
            <div class="metric-box">

                <div class="metric-title">
                    {title}
                </div>

                <div class="metric-value"
                     style="color:{color};">
                    {value}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


metric_card(
    col1,
    "Total Emails",
    total,
    "#27313b"
)

metric_card(
    col2,
    "Critical",
    critical,
    RISK_COLOR["Critical"]
)

metric_card(
    col3,
    "High",
    high,
    RISK_COLOR["High"]
)

metric_card(
    col4,
    "Medium",
    medium,
    RISK_COLOR["Medium"]
)

metric_card(
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
# EMAIL LIST
# ============================================================

for index, mail in enumerate(email_data, 1):

    result = mail["result"]

    risk = mail["risk"]
    category = mail["category"]
    confidence = mail["confidence"]

    sender = mail["sender"]
    subject = mail["subject"]

    icon = RISK_ICON[risk]
    color = RISK_COLOR[risk]

    # Escape HTML-sensitive values
    sender_safe = html.escape(str(sender))
    subject_safe = html.escape(str(subject))
    category_safe = html.escape(str(category))

    # --------------------------------------------------------
    # EMAIL HEADER
    # --------------------------------------------------------

    with st.expander(
        f"{icon}  {index} | {sender} | {subject}     •     {risk}"
    ):

        # ----------------------------------------------------
        # EMAIL INFORMATION
        # ----------------------------------------------------

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:

            st.caption("Sender")

            st.markdown(
                f"**📧 {sender_safe}**"
            )

        with col2:

            st.caption("Subject")

            st.markdown(
                f"**{subject_safe}**"
            )

        with col3:

            st.caption("Risk")

            st.markdown(
                f"""
                <span class="risk-badge"
                      style="
                      color:white;
                      background:{color};
                      ">
                    {icon} {risk}
                </span>
                """,
                unsafe_allow_html=True
            )


        st.divider()


        # ----------------------------------------------------
        # RISK DETAILS
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.caption("Risk Category")

            st.write(
                category_safe
            )

        with col2:

            st.caption("Confidence")

            st.write(
                confidence
            )


        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        st.markdown("#### 🤖 AI Analysis")

        reason = get_first_value(
            result,
            [
                "reasoning",
                "reason",
                "explanation",
                "analysis"
            ],
            default="No explanation available."
        )

        st.markdown(
            f"""
            <div class="analysis-box">
                {html.escape(str(reason))}
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

            for i, policy in enumerate(
                policies,
                1
            ):

                if isinstance(policy, dict):

                    policy_id = policy.get(
                        "policy_id",
                        "Unknown"
                    )

                    score = policy.get(
                        "similarity_score",
                        "N/A"
                    )

                    st.markdown(
                        f"""
                        <div class="policy-box">

                        <b>{i}. {policy_id}</b>
                        <br>
                        Similarity: {score}

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


        # ----------------------------------------------------
        # COMPLETE ANALYSIS
        # ----------------------------------------------------

        with st.expander(
            "View complete analysis"
        ):

            st.json(result)