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

13. 🟨 IMPORTANT:
    Do not be overly conservative when the email explicitly
    requests, instructs, suggests, or arranges behavior that
    falls under a policy violation.

14. 🟨 IMPORTANT:
    A violation does NOT necessarily require that the
    prohibited action has already occurred.

    If the policy covers requests, instructions, attempts,
    invitations, arrangements, or proposals to perform
    prohibited behavior, the request itself may constitute
    a violation.

15. If an email contains business-related communication
    through a personal or external communication channel,
    determine whether this satisfies the Change in
    communication policy.

16. 🟨 For example:

    If an email says:

    "Feel free to ding me on WhatsApp anytime."

    do not automatically classify it as compliant simply
    because the actual WhatsApp conversation is not shown.

    Determine whether the email is inviting the recipient
    to move business-related communication to an external
    communication channel and evaluate that behavior against
    the retrieved Change in communication policy.

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
IMPORTANT DECISION RULE
============================================================

A category should be classified as a violation ONLY when:

- The email contains an actual action, request, instruction,
  behavior, or statement relevant to the policy.

AND

- That action, request, instruction, behavior, or statement
  satisfies one or more violation conditions in the policy.

AND

- No applicable exception removes the violation.

AND

- There is exact supporting evidence in the email.

🟨 IMPORTANT:

The model must evaluate the MEANING of the email, not just
search for policy keywords.

For example:

Email:
"Let's continue this discussion on WhatsApp."

If the retrieved policy prohibits moving business-related
communication to an external or unauthorized channel,
this may satisfy the policy even though the email does not
contain the words "violation", "unauthorized", or
"compliance".

Do not require the email to explicitly state that the
behavior is prohibited.

============================================================
CONTEXTUAL REASONING
============================================================

🟨 Before deciding violation=true or violation=false,
perform the following internal reasoning steps:

1. What is the sender communicating?

2. What is the recipient being asked, instructed, or invited
   to do?

3. Is the communication personal or business-related?

4. Is there a behavior relevant to any retrieved policy?

5. Which specific policy violation condition applies?

6. Does an exception apply?

7. What exact sentence or phrase proves the decision?

8. If the email is compliant, explain why none of the
   retrieved policy violation conditions are satisfied.

Do not output this internal reasoning.
Only return the required JSON.

============================================================
SPECIAL ATTENTION
============================================================

🟨 Pay particular attention to:

- requests to move communication to WhatsApp or other
  external messaging services
- personal email addresses
- personal phone numbers
- requests to avoid official communication channels
- requests to bypass approval processes
- requests to hide or avoid compliance controls
- confidential information
- improper gifts or benefits
- bribery or kickbacks
- market-related misconduct
- employee ethical concerns

However, do NOT flag these automatically.

They must still satisfy the retrieved policy.

============================================================
OUTPUT REQUIREMENTS
============================================================

Return ONLY a valid JSON object.

The JSON object MUST contain:

- "violation": a boolean value.
- "categories": an array.

When a violation exists:

- "violation" must be true.
- "categories" must contain each applicable risk category.
- Each category must contain:
    - "category"
    - "reason"
    - "evidence"

When no violation exists:

- "violation" must be false.
- "categories" must be an empty array.

Every evidence value must be an exact quote from the email.

Do not add markdown code fences.

Do not add any text before the JSON.

Do not add any text after the JSON.

Return ONLY the JSON object.
"""