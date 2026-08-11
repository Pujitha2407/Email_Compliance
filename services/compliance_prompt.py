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
{policy["policy_id"]}

Category:
{policy["category"]}

Title:
{policy["title"]}

Definition:
{policy["definition"]}

Violations:
{chr(10).join("- " + item for item in policy["violations"])}

Exceptions:
{chr(10).join("- " + item for item in policy["exceptions"])}

Examples:
{chr(10).join("- " + item for item in policy["examples"])}
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

Use these policies as the primary source for determining
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

9. Do not infer facts, intent, authorization, or wrongdoing
   that are not supported by the email.

10. Legitimate business activity must not automatically be
    treated as a compliance violation.

11. If an email contains business-related communication
    through a personal or external communication channel,
    determine whether this satisfies the Change in
    communication policy.

12. For example, if an email asks or invites a recipient
    to continue business-related communication through
    an external messaging service, evaluate this against
    the Change in communication policy.

13. If an email discusses confidentiality, agreements,
    or preventing disclosure, determine whether the email
    actually discloses confidential information.

14. An instruction to prevent disclosure is NOT itself an
    unauthorized disclosure.

15. If an email satisfies an exception in the applicable
    policy, do not classify that activity as a violation
    unless there is separate evidence of another violation.

16. An email may belong to multiple risk categories, but
    each category must independently satisfy the applicable
    policy violation conditions.

17. Every identified category MUST contain evidence directly
    quoted from the email.

18. Evidence MUST be an exact quote from the email.

19. The evidence must demonstrate the actual violation,
    not merely mention a related topic.

20. If the email does not contain sufficient evidence of
    an actual violation, return violation as false.

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

Do not classify based only on keywords.

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