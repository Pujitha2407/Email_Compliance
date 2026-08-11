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
            Compliance policies retrieved by RAG.

    Returns:
        Formatted prompt string.
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

The email may belong to one or more of the following compliance
risk categories:

{categories}

## Retrieved Compliance Policies

The following policies were retrieved using the compliance
policy knowledge base. Use these policies as the primary
source for determining whether a violation exists.

{policies}

## Instructions

1. Carefully analyze the email.

2. Determine whether any of the retrieved compliance policies
   actually apply to the email.

3. Do NOT classify an email as a violation simply because
   it contains a word or phrase associated with a risk category.

4. Determine whether the email contains an actual behavior
   that violates the applicable policy.

5. Consider the policy definition, violations, exceptions,
   and examples before making a decision.

6. Legitimate business activity or legitimate confidentiality
   instructions should NOT be classified as violations unless
   the policy specifically indicates otherwise.

7. Do not infer information that is not present in the email.

8. An email may belong to multiple risk categories.

9. Every identified category must be supported by evidence
   quoted directly from the email.

10. Evidence must be an exact quote from the email.

11. If the evidence does not demonstrate an actual violation,
    do not classify the category as a violation.

12. If no compliance risk is found:
    - Set "violation" to false.
    - Return an empty list for "categories".

13. Return ONLY valid JSON.
    Do not add markdown code fences.
    Do not add any text before or after the JSON.

## Output

{{
    "violation": false,
    "categories": []
}}
"""