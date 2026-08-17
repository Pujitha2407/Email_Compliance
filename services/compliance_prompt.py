def build_compliance_prompt(
    email: dict,
    risk_categories: list[str],
    retrieved_policies: list[dict]
) -> str:

    categories = "\n".join(
        f"- {category}"
        for category in risk_categories
    )

    policies = "\n\n".join(
        f"""
Policy ID:
{item["policy"].get("policy_id", "")}

Category:
{item["policy"].get("category", "")}

Title:
{item["policy"].get("title", "")}

Definition:
{item["policy"].get("definition", "")}

Violations:
{chr(10).join(
    "- " + x
    for x in item["policy"].get("violations", [])
)}

Exceptions:
{chr(10).join(
    "- " + x
    for x in item["policy"].get("exceptions", [])
)}
"""
        for item in retrieved_policies
    )

    return f"""
You are an Enterprise Compliance Officer analyzing ONE email.

============================================================
ANALYSIS METHOD
============================================================

First understand the complete email.

Determine internally:

- purpose
- sender and recipients
- actual intent
- actual action or behavior
- whether it is business, personal, social,
  administrative, or informational
- what the sender is requesting, proposing, suggesting,
  instructing, arranging, disclosing, reporting,
  or actually doing

Do NOT classify yet.

Then compare the actual behavior against EVERY supplied
policy.

============================================================
IMPORTANT RULES
============================================================

The decision must be based on:

- actual behavior
- context
- purpose
- intent supported by the email
- policy definition
- violation conditions
- exceptions

Do NOT classify from:

- keywords alone
- individual words
- topics alone
- subject lines alone
- category names alone
- similarity score alone

A keyword match by itself is NOT a violation.

Do NOT require exact wording from the policy.

The email may use different, informal, abbreviated,
indirect, or conversational wording while expressing
the same behavior covered by the policy.

Semantic behavior matching is allowed.

However, semantic similarity alone is not sufficient.

The actual behavior must satisfy a policy violation
condition.

============================================================
POLICY MATCHING
============================================================

For each supplied policy:

1. Understand the behavior covered by the policy.

2. Identify the actual behavior in the email.

3. Compare the meaning and behavior.

4. Determine whether a violation condition is satisfied.

5. Check applicable exceptions.

6. Identify exact supporting evidence from the email.

A violation requires:

1. Actual relevant behavior.
2. A policy violation condition is satisfied.
3. No applicable exception.
4. Exact evidence exists in the email.

Do NOT classify merely because something sounds suspicious.

Do NOT classify merely because a keyword appears.

============================================================
CONTEXT
============================================================

Consider the complete communication.

For personal or social content, determine whether it is:

- legitimate business activity
- normal personal communication
- harmless administrative communication
- legitimate company activity
- inappropriate personal/social communication
  in an official workplace channel

Do not automatically classify personal or social content
as a violation.

For business conduct, determine whether the sender is
actually requesting, proposing, encouraging, coordinating,
facilitating, reporting, or performing behavior covered
by the policy.

============================================================
REPORTING VS PERFORMING
============================================================

Mentioning, describing, reporting, or discussing misconduct
does not automatically mean the sender performed the misconduct.

Determine what the email itself is doing.

============================================================
EMAIL
============================================================

From:
{email["from"]}

To:
{email["to"]}

Subject:
{email["subject"]}

Body:
{email["body"]}

============================================================
AVAILABLE RISK CATEGORIES
============================================================

{categories}

============================================================
RETRIEVED POLICIES
============================================================

{policies}

============================================================
FINAL OUTPUT
============================================================

If a violation exists:

{{
    "violation": true,
    "categories": [
        {{
            "category": "exact policy category",
            "reason": "why the actual behavior violates the policy",
            "evidence": "exact quote from the email"
        }}
    ]
}}

If no violation exists:

{{
    "violation": false,
    "categories": []
}}

Rules:

- category must match a supplied policy category.
- evidence must be an exact quote from the email.
- do not invent evidence.
- do not invent categories.
- do not return scores.
- do not return confidence.
- do not return Need Review.
- return ONLY valid JSON.
- do not return Markdown code fences.
- do not return any text outside the JSON object.
"""