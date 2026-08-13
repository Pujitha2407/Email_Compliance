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

Your task is to analyze EACH email independently using the
retrieved compliance policies provided below.

IMPORTANT:

Do not assume that the email is compliant.

Do not assume that the email is non-compliant.

Make the decision independently for every email based on:

1. The actual email content.
2. The retrieved policy.
3. The policy definition.
4. The policy violation conditions.
5. The policy exceptions.
6. The surrounding context of the email.
7. Exact evidence from the email.

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

Use these policies as the PRIMARY source for determining
whether a violation exists.

{policies}

============================================================
ANALYSIS INSTRUCTIONS
============================================================

1. Carefully understand the complete meaning and context
   of the email.

2. Compare the email against the retrieved policies.

3. Do NOT classify an email as a violation merely because
   a word or phrase in the email is related to a policy.

4. Identify an actual action, request, instruction, behavior,
   or statement in the email that satisfies the violation
   conditions of the applicable policy.

5. Do not require the exact wording of a policy to appear
   in the email.

6. Understand the meaning and context of the email when
   determining whether a policy applies.

7. Consider the policy definition, violations, exceptions,
   and examples before making the final decision.

8. An exception must be considered before classifying
   something as a violation.

9. Do not invent facts that are not supported by the email.

10. Do not invent authorization, wrongdoing, relationships,
    transactions, or events that are not supported by the
    email.

11. However, you MAY infer the reasonable meaning of an
    explicit request, instruction, suggestion, or action
    when that meaning is directly supported by the email.

12. Legitimate business activity must not automatically be
    treated as a compliance violation.

13. Do not be overly conservative when the email explicitly
    requests, instructs, suggests, or arranges behavior that
    falls under a policy violation.

14. A violation does NOT necessarily require that the
    prohibited action has already occurred.

    If the policy covers requests, instructions, attempts,
    invitations, arrangements, or proposals to perform
    prohibited behavior, the request itself may constitute
    a violation.

15. If an email contains business-related communication
    through a personal or external communication channel,
    determine whether this satisfies the Change in
    communication policy.

16. If an email says:

    "Feel free to ding me on whatsapp anytime."

    and the surrounding communication concerns business,
    an agreement, transaction, work, or another business
    matter, evaluate whether this is a request to continue
    business-related communication through an external
    messaging service.

17. If an email discusses confidentiality, agreements,
    or preventing disclosure, determine whether the email
    actually discloses confidential information.

18. An instruction to prevent disclosure is NOT itself an
    unauthorized disclosure.

19. If an email satisfies an exception in the applicable
    policy, do not classify that activity as a violation
    unless there is separate evidence of another violation.

20. An email may belong to multiple risk categories, but
    each category must independently satisfy the applicable
    policy violation conditions.

21. Every identified category MUST contain evidence directly
    quoted from the email.

22. Evidence MUST be an exact quote from the email.

23. The evidence must demonstrate the actual behavior,
    request, instruction, or statement relevant to the
    policy, not merely mention a related topic.

24. If the email does not contain sufficient evidence of
    an actual violation or policy-covered request,
    return violation as false.

============================================================
POLICY APPLICATION RULE
============================================================

Evaluate EVERY retrieved policy independently.

Do NOT assume that the highest similarity policy is the
correct policy.

The FAISS similarity score only determines which policies
are supplied to you. It is NOT evidence that a violation
exists.

For EACH retrieved policy:

1. Read the policy definition.
2. Read every violation condition.
3. Read every exception.
4. Read the examples.
5. Compare the complete email against all of them.
6. Determine whether the email actually satisfies a
   violation condition.
7. Check whether an exception applies.
8. Only then decide whether that category is a violation.

The policy definition, violations, exceptions, and examples
are the PRIMARY authority for your decision.

============================================================
POLICY EXAMPLES ARE STRONG EVIDENCE
============================================================

If the email directly matches the behavior described in a
policy example, treat that example as strong evidence that
the policy applies.

Do NOT ignore a violation merely because the email uses:

- informal wording
- short wording
- incomplete wording
- indirect wording
- slang
- abbreviations
- conversational wording

The email does NOT need to use the exact terminology from
the policy.

You must understand the meaning of the communication.

============================================================
IMPORTANT CATEGORY APPLICATIONS
============================================================

CHANGE IN COMMUNICATION
------------------------------------------------------------

Example:

"Feel free to ding me on whatsapp anytime."

If the surrounding email concerns business, an agreement,
transaction, work, or another business matter, this is an
invitation to continue business-related communication through
an external messaging service.

Evaluate it against the Change in communication policy.

Do not require the email to explicitly say:

"unauthorized channel"

"communication violation"

or

"bypass company communication."

The actual request to continue business communication through
the external channel is the relevant behavior.

------------------------------------------------------------
EMPLOYEE ETHICS
------------------------------------------------------------

Example:

"so who are the drinks on until I do ???"

When this is sent through official company communication,
evaluate it against the Employee ethics policy.

The policy specifically covers inappropriate discussion of
drinks, alcohol, drinking, partying, personal entertainment,
social activities, and inappropriate personal arrangements.

Do NOT require the email to explicitly say:

"alcohol"

"ethics"

"violation"

or

"inappropriate."

Understand the meaning of the communication.

However, do NOT classify every mention of drinks as a violation.

For example, legitimate business-related hospitality,
authorized company events, business dinners, or other
activities covered by an applicable exception must be treated
according to the policy exception.

------------------------------------------------------------
MARKET BRIBERY
------------------------------------------------------------

Example:

"Perhaps a small gesture for the decision maker would help us
get the approval though."

Evaluate the COMPLETE meaning.

The combination of:

- a gesture or benefit
- a decision maker
- obtaining approval

may constitute an improper benefit intended to influence a
business decision.

Evaluate this against the Market bribery policy.

Do not require the email to explicitly use the word:

"bribe."

------------------------------------------------------------
MARKET MANIPULATION
------------------------------------------------------------

Example:

"If we coordinate the activity around the announcement,
market should react the way we are expecting."

Evaluate this against the Market manipulation policy.

The combination of:

- coordinated activity
- an announcement
- an intended or expected market reaction

must be evaluated against the policy conditions concerning
artificially influencing market activity.

Do not require the email to explicitly say:

"manipulate the market."

However, ordinary market analysis or legitimate trading
discussion is NOT automatically manipulation.

The policy violation conditions and exceptions must still
be satisfied.

------------------------------------------------------------
SECRECY
------------------------------------------------------------

Example:

"Pls do not disclose the C.A. until it is signed..."

This is NOT automatically a secrecy violation.

If the applicable policy explicitly contains an exception for
instructions preventing disclosure until an agreement,
contract, or authorization is formally completed, that
exception applies.

Therefore:

"Do not disclose the agreement until it is signed."

must NOT be treated as an unauthorized disclosure by itself.

The actual disclosure or unauthorized handling of protected
information must be supported by the email.

============================================================
FINAL CATEGORY DECISION RULE
============================================================

A category may be returned ONLY when ALL applicable conditions
below are satisfied:

1. The email contains an actual action, request, instruction,
   suggestion, behavior, or statement relevant to the policy.

2. That behavior satisfies at least one violation condition
   in the policy.

3. No applicable policy exception removes the violation.

4. There is exact supporting evidence in the email.

If these conditions are satisfied:

- "violation" MUST be true.
- The applicable category MUST be included.
- The reason MUST explain the policy violation.
- The evidence MUST quote the email exactly.

If these conditions are NOT satisfied:

- Do NOT include that category.

============================================================
DO NOT USE KEYWORD-ONLY CLASSIFICATION
============================================================

Never classify an email solely because it contains a word
associated with a policy.

Examples:

"confidential"
does NOT automatically mean Secrecy violation.

"WhatsApp"
does NOT automatically mean Change in communication violation.

"drinks"
does NOT automatically mean Employee ethics violation.

"market"
does NOT automatically mean Market manipulation.

"gesture"
does NOT automatically mean Market bribery.

"complaint"
does NOT automatically mean Complaints violation.

The complete meaning, context, policy violation conditions,
and exceptions must be considered.

============================================================
EVIDENCE REQUIREMENT
============================================================

Every non-compliant category MUST have exact evidence from
the email.

The evidence must show WHY the category applies.

Bad evidence:

"drinks"

Good evidence:

"so who are the drinks on until I do ???"

Bad evidence:

"WhatsApp"

Good evidence:

"Feel free to ding me on whatsapp anytime."

Do not create evidence that does not exist in the email.

============================================================
COMPLIANT DECISION
============================================================

Return:

"violation": false

ONLY when, after evaluating the retrieved policies, the email
does not satisfy any applicable violation condition.

Do not return violation=false merely because:

- a keyword was not found
- the policy wording is different
- the email is short
- the email uses informal language
- the email does not explicitly say that something is illegal
  or prohibited

If the email clearly matches a policy violation, classify it
as a violation even when the wording is indirect.

============================================================
OUTPUT REQUIREMENTS
============================================================

Return ONLY a valid JSON object.

The JSON object MUST contain:

- "violation": true or false
- "categories": an array

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

- Every category MUST correspond to one of the retrieved policies.
- Do NOT invent category names.
- Every evidence value MUST be an exact quote from the email.
- Do NOT paraphrase evidence.
- Do NOT add markdown.
- Do NOT add explanations outside the JSON.
- Do NOT add comments.
- Do NOT add trailing text.

Return ONLY the JSON object.
"""