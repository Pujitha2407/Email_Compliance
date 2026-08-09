def build_compliance_prompt(email: dict, risk_categories: list[str]) -> str:
    """
    Builds the compliance analysis prompt for a single email.

    Args:
        email: Dictionary containing:
            - from
            - to
            - subject
            - body
        risk_categories: List of compliance risk category names.

    Returns:
        Formatted prompt string.
    """

    categories = "\n".join(
        f"{i + 1}. {category}"
        for i, category in enumerate(risk_categories)
    )

    return f"""
You are an experienced Enterprise Compliance Officer responsible for reviewing employee emails for potential compliance violations.

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

The email may belong to one or more of the following compliance risk categories:

{categories}

## Instructions

1. Carefully analyze the email.
2. Compare the email only against the compliance risk categories listed above.
3. Determine whether the email indicates any compliance risk.
4. An email may belong to multiple risk categories.
5. Do not infer information that is not present in the email.
6. Every identified category must be supported by evidence quoted directly from the email.
7. If no compliance risk is found:
- Set "violation" to false.
- Return an empty list for "categories".
- Explain why no violation exists.
- Return an empty evidence list.

## Output

Return ONLY valid JSON.

{{
    "violation": true,
    "categories": [
        {{
            "category": "Risk Category",
            "reason": "Why this category applies",
            "evidence": [
                "Exact quote from the email",
                "Another supporting quote"
            ]
        }}
    ]
}}
"""