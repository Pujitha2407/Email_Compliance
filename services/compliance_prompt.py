def build_compliance_prompt(
    email: dict,
    risk_categories: list[str],
    retrieved_policies: list[dict]
) -> str:
    """
    Builds the compliance analysis prompt for a single email.

    Args:
        email:
            Dictionary containing:
                - from
                - to
                - subject
                - body

        risk_categories:
            List of compliance risk category names.

        retrieved_policies:
            Compliance policies retrieved by the policy retrieval step.

    Returns:
        Formatted prompt string.
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

Your task is to analyze ONE email independently using the
compliance policies provided below.

The email must be evaluated based on its actual meaning,
context, intent, behavior, policy violation conditions,
exceptions, and policy examples.

Do not classify an email based only on keywords.

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
compliance risk categories:

{categories}

============================================================
RETRIEVED COMPLIANCE POLICIES
============================================================

The following policies were retrieved from the compliance
policy knowledge base.

These policies are the PRIMARY authority for determining
whether the email contains a violation.

{policies}

============================================================
HOW TO EVALUATE THE EMAIL
============================================================

Evaluate each retrieved policy independently.

For every policy:

1. Read the policy definition.

2. Read all violation conditions.

3. Read all exceptions.

4. Read all examples.

5. Compare the complete email with the policy.

6. Determine what the sender is actually communicating,
   requesting, suggesting, instructing, or proposing.

7. Determine whether that behavior satisfies a violation
   condition in the policy.

8. Check whether an exception applies.

9. Identify exact evidence from the email.

A policy violation does NOT require the email to use the
same words as the policy.

Understand the meaning of the email.

============================================================
IMPORTANT DECISION RULE
============================================================

A category is a violation when:

- The email contains an actual statement, action, request,
  instruction, suggestion, proposal, or behavior relevant
  to the policy.

AND

- The behavior satisfies a violation condition described
  by the policy.

AND

- No applicable exception removes the violation.

AND

- Exact evidence exists in the email.

If these conditions are satisfied, return that category.

If they are not satisfied, do not return that category.

============================================================
POLICY EXAMPLES
============================================================

Policy examples are important evidence.

If the email directly expresses the same behavior or intent
described in a policy example, treat that as strong evidence
that the policy applies.

The email does not need to reproduce the example word-for-word.

However, do not invent facts that are not present in the email.

============================================================
CONTEXT RULE
============================================================

Always distinguish between:

1. A word appearing in an email.

and

2. The behavior or intent represented by the email.

A keyword by itself is NOT a violation.

The complete meaning and business context must be considered.

For example:

"WhatsApp"

by itself is not automatically a violation.

But:

"Feel free to ding me on whatsapp anytime."

inside a business-related email represents an invitation to
continue business communication through an external messaging
service and must be evaluated under Change in communication.

Similarly:

"drinks"

by itself is not automatically an Employee ethics violation.

But:

"so who are the drinks on until I do ???"

is a social/personal discussion in an official company email
and must be evaluated under Employee ethics.

============================================================
KNOWN BEHAVIOR EXAMPLES
============================================================

The following examples explain how to apply the policies.

------------------------------------------------------------
1. CHANGE IN COMMUNICATION
------------------------------------------------------------

Email:

"Feel free to ding me on whatsapp anytime."

If the surrounding communication is business-related, this
represents an invitation to continue business communication
through an external messaging service.

Evaluate this against the Change in communication policy.

The email does not need to say:

"unauthorized channel"

"communication violation"

or

"bypass company communication."

The actual behavior is the invitation to continue business
communication through WhatsApp.

Do not flag WhatsApp merely because the word "WhatsApp"
appears.

------------------------------------------------------------
2. EMPLOYEE ETHICS
------------------------------------------------------------

Email:

"so who are the drinks on until I do ???"

This must be evaluated against Employee ethics.

The relevant behavior is the discussion of drinks/social
activity in an official company communication.

Do not require the email to explicitly contain:

"alcohol"

"ethics"

"violation"

or

"inappropriate."

Understand the meaning of the complete sentence.

However, legitimate business hospitality, authorized company
events, business dinners, or other activities covered by an
applicable policy exception must not automatically be treated
as violations.

------------------------------------------------------------
3. MARKET BRIBERY
------------------------------------------------------------

Email:

"Perhaps a small gesture for the gesture for the decision
maker would help us get the approval though."

Evaluate this against Market bribery.

The important relationship is:

benefit/gesture
+
decision maker
+
obtaining approval

This indicates a suggested benefit intended to influence a
business decision.

The email does not need to use the word:

"bribe."

Do not invent a specific payment, gift, amount, or transaction
that is not present in the email.

------------------------------------------------------------
4. MARKET MANIPULATION
------------------------------------------------------------

Email:

"If we coordinate the activity around the announcement,
market should react the way we are expecting."

Evaluate this against Market manipulation.

The important relationship is:

coordinate activity
+
announcement
+
expected market reaction

This indicates activity being coordinated with an expected
market effect.

The email does not need to explicitly say:

"manipulate the market."

However, legitimate market analysis or ordinary business
activity is not automatically market manipulation.

The policy violation conditions must still be satisfied.

------------------------------------------------------------
5. SECRECY
------------------------------------------------------------

Email:

"Pls do not disclose the C.A. until it is signed by the
appropriate party here."

This is NOT automatically a secrecy violation.

If the applicable Secrecy policy contains an exception
allowing information to remain confidential until an agreement
is formally signed, that exception applies.

An instruction to prevent disclosure is not itself an
unauthorized disclosure.

Do not invent that confidential information was disclosed
when the email does not show such disclosure.

------------------------------------------------------------
6. MISLEADING BUSINESS INFORMATION
------------------------------------------------------------

Email:

"Could we adjust a few figures before sharing the report so
the results look more favourable."

Evaluate this against the applicable Employee ethics or other
policy concerning dishonest, misleading, falsified, or
improperly altered business information.

The important behavior is the proposed adjustment of figures
specifically so that the reported results appear more
favorable.

This is different from a legitimate correction of an error.

Do not assume a legitimate correction when the stated purpose
is to make results look more favorable.

The exact sentence must be used as evidence.

------------------------------------------------------------
7. COMPLIANCE PROCESS
------------------------------------------------------------

Email:

"We may be able to move this forward without waiting for the
usual compliance review."

Evaluate this against the applicable retrieved policy.

Do not automatically classify every mention of compliance as
an Employee ethics violation.

Determine whether the policy actually prohibits bypassing,
avoiding, or circumventing the applicable compliance process.

If the policy contains such a violation condition and the
email proposes proceeding without the required review,
classify it according to that policy.

============================================================
IMPORTANT: DO NOT OVER-GENERALIZE
============================================================

Do NOT classify an email as a violation merely because it
contains a related keyword.

Examples:

"confidential"
does not automatically mean Secrecy violation.

"WhatsApp"
does not automatically mean Change in communication violation.

"drinks"
does not automatically mean Employee ethics violation.

"market"
does not automatically mean Market manipulation.

"gesture"
does not automatically mean Market bribery.

"compliance"
does not automatically mean Employee ethics violation.

"figures"
does not automatically mean dishonest conduct.

The actual behavior and policy conditions must match.

============================================================
IMPORTANT: DO NOT UNDER-CLASSIFY
============================================================

Do not reject a violation merely because:

- the email is short
- the email is informal
- the email uses slang
- the email does not use legal terminology
- the email does not explicitly call the behavior a violation
- the email does not use the exact wording of the policy

If the meaning of the email directly satisfies a policy
violation condition, classify it as a violation.

============================================================
EXCEPTIONS
============================================================

Always check exceptions before making the final decision.

If an exception clearly applies:

- do not classify that behavior as a violation.

If no exception applies and the violation conditions are
satisfied:

- classify the behavior as a violation.

Do not invent an exception.

Do not invent authorization.

Do not invent facts.

============================================================
EVIDENCE
============================================================

Every violation category MUST contain exact evidence from
the email.

Evidence must be copied directly from the email.

Do not paraphrase evidence.

Do not create evidence.

Examples:

Correct:

"so who are the drinks on until I do ???"

Incorrect:

"discussion about alcohol"

Correct:

"Feel free to ding me on whatsapp anytime."

Incorrect:

"Use of unauthorized messaging"

The evidence field must contain the actual words from the
email.

============================================================
MULTIPLE CATEGORIES
============================================================

An email may violate more than one policy.

If multiple independent policies are satisfied, include all
applicable categories.

Each category must independently have:

- a matching policy violation condition
- no applicable exception
- exact evidence

Do not add a category merely because it is related to the
email topic.

============================================================
COMPLIANT DECISION
============================================================

Return:

"violation": false

and:

"categories": []

when none of the retrieved policies contains a satisfied
violation condition supported by the email.

Do not classify an email as compliant merely because it does
not contain an obvious keyword.

Do not classify an email as non-compliant merely because
something could theoretically be risky.

There must be policy-supported evidence.

============================================================
FINAL DECISION
============================================================

Before producing the JSON, determine internally:

1. What is the email actually communicating?

2. What action, request, instruction, suggestion, or behavior
   is present?

3. Which retrieved policy applies?

4. Which exact violation condition is satisfied?

5. Does an exception apply?

6. What exact text from the email proves the decision?

Do not output this reasoning.

Only output the required JSON.

============================================================
OUTPUT REQUIREMENTS
============================================================

Return ONLY a valid JSON object.

The JSON object MUST contain:

- "violation": boolean
- "categories": array

When a violation exists:

{{
    "violation": true,
    "categories": [
        {{
            "category": "exact policy category",
            "reason": "specific explanation of why the email violates the policy",
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

- "category" MUST match the category name from a retrieved policy.
- Do not invent category names.
- Every evidence value MUST be an exact quote from the email.
- Do not paraphrase evidence.
- Do not add markdown code fences.
- Do not add text before the JSON.
- Do not add text after the JSON.
- Do not add comments.
- Return ONLY the JSON object.
"""