def build_compliance_prompt(
    email: str,
    risk_categories: list[str],
    retrieved_policies: list[dict]
) -> str:

    categories = ", ".join(
        f"{category}"
        for category in risk_categories
    )

    policies = "\n\n".join(
        f"""
Policy ID:
{item.get("policy_id", "")}

Category:
{item.get("category", "")}

Title:
{item.get("title", "")}

Definition:
{item.get("definition", "")}

Violations:
{chr(10).join(
    "- " + x
    for x in item.get("violations", [])
)}
"""
        for item in retrieved_policies
    )

    return f"""
You are an Enterprise Compliance Officer analyzing emails.

You are provided with list of policies for each risk category 
explaining what can result in violation causing mail to be non compliance.

As a first step, Understand each policy for every risk category.
Remember the reason for violations for each policy.

# Policies
{policies}

# Risk Categories
{categories}

# Email
Second step, Read this below detailed email context summary 

==========================================================
{email}
==========================================================

then, compare your mail understanding against EVERY supplied
policy description, violations and exceptions.

# Decision Rules

The decision must be based on:

- actual behavior
- context
- purpose
- intent supported by the email
- policy definition
- violation conditions

A keyword match by itself is NOT a violation.
Not necessary to require exact wording from the policy.

The email may use different, informal, abbreviated,
indirect, or conversational wording while expressing
the same behavior covered by the policy.
Semantic behavior matching is allowed.

The actual behavior must satisfy a policy violation
condition.


# Final Output

If a violation exists:

{{
    "violation": true,
    "categories": [
        {{
            "category": "exact policy risk category name",
            "reason": "why the actual behavior violates the policy",
            "evidence": "exact quote from the email"
        }}
    ]
}}
note: one mail can violate multiple policies resulting in output with multiple category with their reason and evidence.

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


def build_context_prompt(email: dict) -> str:
    return f"""
Understand the complete email and generate a context detaile analysis summary

From:
{email["from"]}
To:
{email["to"]}
Subject:
{email["subject"]}
Body:
{email["body"]}

Determine:

- purpose
- sender and recipients
- actual intent
- actual action or behavior
- whether it is business, personal, social,
  administrative, or informational
- what the sender is requesting, proposing, suggesting,
  instructing, arranging, disclosing, reporting,
  or actually doing
"""