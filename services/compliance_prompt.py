def build_compliance_prompt(
    email: dict,
    risk_categories: list[str],
    retrieved_policies: list[dict]
) -> str:

    categories = "\n".join(
        f"{i + 1}. {category}"
        for i, category in enumerate(risk_categories)
    )

    policies = "\n\n".join(
        f"""
Policy ID: {policy['policy']['policy_id']}
Category: {policy['policy']['category']}
Title: {policy['policy']['title']}

Definition:
{policy['policy']['definition']}

Violations:
{chr(10).join("- " + x for x in policy['policy']['violations'])}

Exceptions:
{chr(10).join("- " + x for x in policy['policy']['exceptions'])}

Examples:
{chr(10).join("- " + x for x in policy['policy']['examples'])}
"""
        for policy in retrieved_policies
    )

    return f"""
You are an Enterprise Compliance Officer analyzing ONE email.

============================================================
ANALYSIS METHOD
============================================================

FIRST understand the complete email.

Determine internally:
- purpose
- sender and recipients
- actual intent
- actual action or behavior
- whether it is business, personal, or social
- what the sender is requesting, proposing, suggesting,
  instructing, arranging, disclosing, or doing

Do NOT classify yet.

THEN compare the actual behavior against EVERY retrieved
policy.

For each policy:
1. Check the definition.
2. Check the violation conditions.
3. Check the exceptions.
4. Determine whether the actual behavior satisfies the policy.
5. Identify exact supporting evidence from the email.

============================================================
IMPORTANT RULES
============================================================

Actual behavior + context determine the decision.

Do NOT classify from:
- keywords
- individual words
- topics
- subject lines
- policy similarity
- category names
- a single example

A keyword is only a possible retrieval signal, NEVER proof
of a violation.

Do not invent facts or intent.

Do not classify merely because something sounds suspicious.

A violation requires:
1. Actual relevant behavior.
2. An explicit policy violation condition is satisfied.
3. No applicable exception.
4. Exact evidence exists in the email.

Evaluate every category independently.

An email may have multiple violations.

Reporting, discussing, or mentioning misconduct is not
automatically the same as performing or facilitating it.

Personal/social content is not automatically Employee ethics.
Determine the actual workplace behavior and context.

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
RISK CATEGORIES
============================================================

{categories}

============================================================
RETRIEVED POLICIES
============================================================

{policies}

============================================================
FINAL OUTPUT
============================================================

Return ONLY valid JSON.

If violation exists:

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

If no violation:

{{
    "violation": false,
    "categories": []
}}

Rules:
- category must match a retrieved policy.
- evidence must be an exact quote from the email.
- do not invent evidence.
- do not invent categories.
- do not return scores.
- do not return Need Review.
- return ONLY JSON.
"""