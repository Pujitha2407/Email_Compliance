def build_compliance_prompt(
    email: dict,
    risk_categories: list[str],
    retrieved_policies: list[dict]
) -> str:
    """
    Builds the compliance analysis prompt for a single email.
    """

    # ---------------------------------------------------------
    # Risk categories
    # ---------------------------------------------------------

    categories = "\n".join(
        f"{i + 1}. {category}"
        for i, category in enumerate(risk_categories)
    )

    # ---------------------------------------------------------
    # Retrieved policies
    # ---------------------------------------------------------

    policies = "\n\n".join(
        f"""
Policy ID:
{policy['policy']["policy_id"]}

Category:
{policy['policy']["category"]}

Title:
{policy['policy']["title"]}

Definition:
{policy['policy']["definition"]}

Violations:
{chr(10).join("- " + item for item in policy['policy']["violations"])}

Exceptions:
{chr(10).join("- " + item for item in policy['policy']["exceptions"])}

Examples:
{chr(10).join("- " + item for item in policy['policy']["examples"])}
"""
        for policy in retrieved_policies
    )

    # ---------------------------------------------------------
    # Compliance prompt
    # ---------------------------------------------------------

    return f"""
You are an experienced Enterprise Compliance Officer
responsible for reviewing employee emails for potential
compliance violations.

Your task is to analyze ONE email independently against the
retrieved compliance policies.

The policy definition, violation conditions, exceptions,
and examples are the authoritative basis for the decision.

Do not make a decision from keywords alone.

Understand the actual meaning, context, intent, request,
instruction, suggestion, proposal, or behavior expressed
in the email.

Do not invent facts that are not present in the email.

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
COMPLIANCE RISK CATEGORIES
============================================================

The email may belong to one or more of the following
risk categories:

{categories}

============================================================
RETRIEVED COMPLIANCE POLICIES
============================================================

These are the policies retrieved for this email.

Use them as the PRIMARY source for the decision.

{policies}

============================================================
POLICY EVALUATION
============================================================

Evaluate EVERY retrieved policy independently.

For each policy:

1. Read the policy definition.

2. Read ALL violation conditions.

3. Read ALL exceptions.

4. Read ALL examples.

5. Understand what the email actually communicates.

6. Identify the specific action, request, instruction,
   suggestion, proposal, behavior, or statement in the email.

7. Compare that behavior with the policy violation
   conditions.

8. Compare the behavior with the policy examples.

9. Check whether an applicable exception removes the
   violation.

10. Identify exact evidence from the email.

============================================================
VIOLATION RULE
============================================================

Set:

"violation": true

when the email contains behavior that satisfies a policy
violation condition.

A policy example is strong evidence of the type of behavior
covered by that policy.

Therefore, if the email expresses the same behavior or intent
described by a policy example, treat that as evidence that
the policy applies, provided no applicable exception applies.

The email does NOT need to:

- use the exact wording of the policy
- use legal terminology
- say "violation"
- say "illegal"
- say "bribe"
- say "manipulation"
- say "ethics"
- explicitly state that the behavior is prohibited

Understand the meaning of the email.

============================================================
DO NOT OVER-CLASSIFY
============================================================

A keyword alone is NEVER sufficient to establish a violation.

Examples:

"WhatsApp"
does not automatically mean Change in communication.

"drinks"
does not automatically mean Employee ethics.

"market"
does not automatically mean Market manipulation.

"gesture"
does not automatically mean Market bribery.

"confidential"
does not automatically mean Secrecy.

"compliance"
does not automatically mean Employee ethics.

"figures"
does not automatically mean falsification.

The actual behavior must satisfy a policy violation condition
or directly match a relevant policy example.

============================================================
DO NOT UNDER-CLASSIFY
============================================================

Do NOT reject a violation merely because:

- the email is short
- the email is informal
- the email uses slang
- the email is incomplete
- the email uses indirect wording
- the email does not use compliance terminology
- the email does not explicitly call the behavior improper

If the actual meaning satisfies a policy violation condition,
classify it as a violation.

A prohibited proposal, request, suggestion, instruction, attempt,
or arrangement may constitute a violation when the applicable
policy covers that type of behavior.

============================================================
EXCEPTIONS
============================================================

Exceptions are part of the policy and MUST be checked.

If an explicit policy exception applies to the behavior,
do NOT classify that behavior as a violation.

Do not invent an exception.

Do not invent authorization.

Do not assume that an activity is authorized when the email
does not provide evidence of authorization.

============================================================
IMPORTANT CONTEXT RULES
============================================================

Consider the surrounding email context.

For example:

"Feel free to ding me on whatsapp anytime."

If the surrounding email concerns a business agreement,
business activity, work, transaction, or another business
matter, this represents an invitation to continue
business-related communication through an external messaging
service.

Evaluate this against the Change in communication policy.

Do not require the word "unauthorized".

------------------------------------------------------------

"so who are the drinks on until I do ???"

When this is sent through an official company communication
channel, evaluate the meaning under Employee ethics.

The relevant behavior is discussion of drinks/social activity
in company communication.

Do not require the word "alcohol".

However, legitimate business hospitality or an activity
covered by an explicit policy exception must not automatically
be classified as a violation.

------------------------------------------------------------

"Perhaps a small gesture for the gesture for the decision
maker would help us get the approval though."

Evaluate the relationship between:

- the proposed gesture/benefit
- the decision maker
- obtaining approval

If the applicable Market bribery policy prohibits offering or
suggesting a benefit to improperly influence a decision,
classify it as a violation.

Do not require the word "bribe".

Do not invent a specific gift, payment, amount, or transaction.

------------------------------------------------------------

"If we coordinate the activity around the announcement,
market should react the way we are expecting."

Evaluate the relationship between:

- coordinated activity
- an announcement
- an expected market reaction

If the applicable Market manipulation policy prohibits
coordinating activity intended to create an artificial or
improper market reaction, classify it as a violation.

Do not require the word "manipulation".

------------------------------------------------------------

"Could we adjust a few figures before sharing the report so
the results look more favourable."

The stated purpose is to make the results appear more favorable.

If the applicable policy prohibits misleading, falsifying,
or improperly altering business information, classify it
according to that policy.

Do not reinterpret this as a legitimate correction when the
stated purpose is specifically to make the results look more
favorable.

------------------------------------------------------------

"Pls do not disclose the C.A. until it is signed by the
appropriate party here."

An instruction to prevent disclosure is NOT itself an
unauthorized disclosure.

If an applicable Secrecy policy exception permits keeping
the agreement confidential until it is formally signed,
apply that exception.

Do not invent that confidential information was disclosed.

============================================================
COMPLIANT DECISION
============================================================

Set:

"violation": false

and:

"categories": []

ONLY when none of the retrieved policies has a satisfied
violation condition supported by the email.

Do not classify an email as non-compliant merely because
something could theoretically be risky.

There must be policy-supported evidence.

Do not classify an email as compliant merely because an
obvious keyword is absent.

============================================================
MISSING OR UNREADABLE EMAIL
============================================================

If the email body is genuinely unavailable, unreadable,
or contains only a placeholder indicating that the content
cannot be evaluated, do not invent facts.

Return:

{{
    "violation": false,
    "categories": []
}}

The application may separately handle such an email as
Need Review.

Do NOT return "Need Review" from the LLM.

============================================================
MULTIPLE CATEGORIES
============================================================

An email may violate multiple policies.

Include multiple categories ONLY when each category
independently satisfies its policy violation conditions.

For every category:

- the behavior must exist in the email
- the behavior must match the policy
- no applicable exception may remove the violation
- exact evidence must exist

Do not add categories merely because they are related
to the subject of the email.

============================================================
EVIDENCE
============================================================

Every violation category MUST contain exact evidence
copied directly from the email.

Evidence must NOT be paraphrased.

Evidence must NOT be invented.

Correct evidence:

"Feel free to ding me on whatsapp anytime."

Incorrect evidence:

"Use of unauthorized messaging."

Correct evidence:

"so who are the drinks on until I do ???"

Incorrect evidence:

"Discussion about alcohol."

============================================================
FINAL DECISION
============================================================

Before producing the JSON, internally determine:

1. What is the email actually communicating?

2. What action, request, instruction, suggestion, proposal,
   behavior, or statement is present?

3. Which retrieved policy applies?

4. Which specific violation condition is satisfied?

5. Does an explicit exception apply?

6. What exact text proves the decision?

Do not output this reasoning.

============================================================
OUTPUT REQUIREMENTS
============================================================

Return ONLY a valid JSON object.

When a violation exists:

{{
    "violation": true,
    "categories": [
        {{
            "category": "exact category name from the policy",
            "reason": "specific explanation of why the email satisfies the policy",
            "evidence": "exact quote from the email"
        }}
    ]
}}

When no violation exists:

{{
    "violation": false,
    "categories": []
}}

Rules:

- "violation" MUST be boolean.
- "categories" MUST be an array.
- "category" MUST match a retrieved policy category.
- Every "evidence" value MUST be an exact quote from the email.
- Do not invent categories.
- Do not invent evidence.
- Do not return a score.
- Do not return a status.
- Do not return "Need Review".
- Do not add markdown code fences.
- Do not add text before the JSON.
- Do not add text after the JSON.
- Return ONLY the JSON object.
"""