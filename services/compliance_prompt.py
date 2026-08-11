def build_compliance_prompt(
    email: dict,
    risk_categories: list[str],
    retrieved_policies: list[dict]
) -> str:
    """
    Builds the compliance analysis prompt for a single email.
    """

    categories = "\n".join(
        f"{i + 1}. {category}"
        for i, category in enumerate(risk_categories)
    )

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

    return f"""
You are an experienced Enterprise Compliance Officer responsible
for reviewing employee emails for potential compliance violations.

## Email

From:
{email['from']}

To:
{email['to']}

Subject:
{email['subject']}

Body:
{email['body']}

## Compliance Risk Categories

{categories}

## Retrieved Compliance Policies

{policies}

## Instructions

1. Analyze the email carefully.

2. Compare the email against the retrieved policies.

3. A category MUST NOT be classified as a violation merely
   because the email contains a related keyword or phrase.

4. Identify an actual action, behavior, request, or statement
   in the email that satisfies the violation conditions of
   the policy.

5. The policy definition, violations, and exceptions must all
   be considered before deciding whether a violation exists.

6. An exception takes precedence when the email clearly
   satisfies that exception.

7. Do not treat an instruction to PREVENT disclosure as an
   unauthorized disclosure.

8. Do not infer facts, intent, authorization, or wrongdoing
   that are not explicitly supported by the email.

9. If the email does not contain evidence of an actual
   violation, classify it as non-violation.

10. An email may belong to multiple risk categories only when
    each category has independent supporting evidence.

11. Every identified category MUST contain exact evidence
    copied from the email.

12. The evidence must demonstrate the violation itself,
    not merely mention a related topic.

13. If no violation is supported by the email:

    - Set "violation" to false.
    - Return an empty list for "categories".

14. Return ONLY valid JSON.

Do not add markdown code fences.
Do not add any text before or after the JSON.

## Output

{{
    "violation": false,
    "categories": []
}}
"""