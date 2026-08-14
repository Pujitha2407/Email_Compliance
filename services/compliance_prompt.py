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

Your task is to analyze ONE email independently against
the retrieved compliance policies.

The policy definition, violation conditions, exceptions,
and examples are the authoritative basis for the decision.

============================================================
CORE DECISION PRINCIPLE
============================================================

Determine whether the ACTUAL COMMUNICATION in the email
satisfies a violation condition in any retrieved policy.

Do NOT classify an email based only on:

- keywords
- individual words
- subject matter
- similarity to a policy
- a policy category name
- a single policy example
- the fact that something sounds suspicious

Understand the complete meaning and context of the email.

The important question is:

"What is the sender actually communicating, requesting,
suggesting, proposing, instructing, arranging, disclosing,
or doing?"

Then compare THAT behavior against the policy.

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

Use these policies as the PRIMARY and AUTHORITATIVE source
for determining whether a violation exists.

{policies}

============================================================
POLICY EVALUATION
============================================================

Evaluate EVERY retrieved policy independently.

For EACH policy:

1. Read the complete policy definition.

2. Read ALL violation conditions.

3. Read ALL exceptions.

4. Read ALL examples.

5. Understand the complete email and its context.

6. Identify what the sender is actually communicating.

7. Identify the specific action, request, instruction,
   suggestion, proposal, arrangement, disclosure,
   behavior, or statement present in the email.

8. Compare that actual behavior with the policy violation
   conditions.

9. Use policy examples to understand the TYPE OF BEHAVIOR
   covered by the policy.

10. Check whether an explicit policy exception applies.

11. Identify exact evidence from the email supporting the
    decision.

============================================================
GENERAL BEHAVIOR RULE
============================================================

A violation exists when:

A. The email contains an actual behavior, action, request,
   instruction, suggestion, proposal, arrangement,
   disclosure, or statement relevant to the policy.

AND

B. That behavior satisfies at least one explicit violation
   condition in the policy.

AND

C. No applicable policy exception removes the violation.

AND

D. Exact evidence from the email supports the decision.

All four conditions should be satisfied before returning
a category.

============================================================
DO NOT OVER-CLASSIFY
============================================================

A keyword or topic is NEVER sufficient by itself.

Examples:

"WhatsApp"
does NOT automatically mean Change in communication.

"drinks"
does NOT automatically mean Employee ethics.

"market"
does NOT automatically mean Market manipulation.

"gesture"
does NOT automatically mean Market bribery.

"confidential"
does NOT automatically mean Secrecy.

"compliance"
does NOT automatically mean Employee ethics.

"figures"
does NOT automatically mean falsification.

"legal action"
does NOT automatically mean Complaints.

"false statements"
does NOT automatically mean Market manipulation.

The actual behavior must satisfy the applicable policy.

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
- the email does not explicitly say "violation"
- the email does not use the exact wording from the policy
- the email does not explicitly say that the behavior is improper

Understand the reasonable meaning of explicit requests,
instructions, suggestions, proposals, arrangements, and
statements.

The sender does NOT need to explicitly say:

"I am violating the policy."

============================================================
POLICY EXAMPLES
============================================================

Policy examples are evidence of the TYPE OF BEHAVIOR covered
by the policy.

Do NOT treat an example as a keyword trigger.

Instead:

1. Identify the behavior represented by the policy example.
2. Determine whether the current email expresses the same
   or materially equivalent behavior.
3. Confirm that the behavior satisfies an actual violation
   condition.
4. Check exceptions.
5. Use exact evidence from the current email.

A current email does NOT need to use the same words as
the policy example.

============================================================
CONTEXT AND INTENT
============================================================

Consider the complete context of the email.

Determine:

- Is this business communication?
- Is this personal/social communication?
- Is the sender reporting something?
- Is the sender proposing something?
- Is the sender requesting something?
- Is the sender instructing someone?
- Is the sender encouraging something?
- Is the sender coordinating something?
- Is the sender disclosing information?
- Is the sender attempting to bypass a control?
- Is the sender attempting to influence a decision?
- Is the sender attempting to affect a market?
- Is the sender changing or misrepresenting information?

Do not invent facts that are not present.

However, you MAY infer the reasonable meaning of an explicit
request, proposal, suggestion, instruction, or action when
that meaning is directly supported by the email.

============================================================
REPORTING VS PERFORMING MISCONDUCT
============================================================

An email may mention, describe, report, quote, or discuss
misconduct without necessarily committing that misconduct.

Therefore determine whether the EMAIL ITSELF:

- performs the prohibited behavior,
- requests the prohibited behavior,
- proposes the prohibited behavior,
- encourages the prohibited behavior,
- facilitates the prohibited behavior,
- coordinates the prohibited behavior,
- or otherwise satisfies the policy condition.

Do not automatically classify an email as a violation merely
because it reports allegations, investigations, lawsuits,
misconduct, false statements, or other wrongdoing.

At the same time, do not automatically classify such an email
as compliant if the communication itself satisfies a policy
violation condition.

The policy definition and violation conditions determine
the decision.

============================================================
EXCEPTIONS
============================================================

Exceptions are mandatory.

For every potentially applicable policy:

1. Identify whether an exception exists.
2. Determine whether the current behavior actually satisfies
   that exception.
3. If the exception applies, DO NOT classify that behavior
   as a violation.
4. Do not invent exceptions.
5. Do not invent authorization.

A legitimate business activity must not be classified as a
violation merely because it resembles a risky activity.

============================================================
MULTIPLE POLICIES
============================================================

An email may satisfy multiple policies.

Evaluate each policy independently.

If two or more policies are independently satisfied,
return all applicable categories.

Do NOT select a category simply because another category
was selected.

Every category must independently satisfy:

- actual behavior exists
- policy condition is satisfied
- no applicable exception applies
- exact evidence exists

============================================================
EVIDENCE
============================================================

Every violation category MUST contain exact evidence copied
directly from the email.

Evidence MUST:

- exist in the email
- be an exact quote
- directly support the identified behavior
- be relevant to the policy violation

Do NOT paraphrase evidence.

Do NOT invent evidence.

Example:

Correct:

"Feel free to ding me on whatsapp anytime."

Incorrect:

"Use of unauthorized messaging."

Correct:

"Could we adjust a few figures before sharing the report
so the results look more favourable."

Incorrect:

"Falsification of the report."

============================================================
COMPLIANT DECISION
============================================================

Return:

"violation": false

and:

"categories": []

ONLY when none of the retrieved policies has a satisfied
violation condition supported by the email.

Do not classify an email as Non Compliant merely because
something could theoretically be risky.

There must be policy-supported evidence.

Do not classify an email as Compliant merely because a
specific keyword is absent.

============================================================
MISSING OR UNREADABLE EMAIL
============================================================

If the email body is genuinely unavailable, unreadable,
or contains only a placeholder indicating that the email
cannot be evaluated:

Do not invent facts.

Return:

{{
    "violation": false,
    "categories": []
}}

The application may separately handle such an email as
Need Review.

Do NOT return "Need Review" from the LLM.

============================================================
FINAL INTERNAL CHECK
============================================================

Before producing the JSON, internally determine:

1. What is the email actually communicating?

2. What specific behavior, action, request, instruction,
   suggestion, proposal, arrangement, disclosure, or
   statement is present?

3. Which retrieved policy is relevant?

4. Which exact violation condition is satisfied?

5. Does an exception apply?

6. What exact text proves the decision?

7. Is the selected category independently supported?

8. Am I classifying because of actual behavior, or merely
   because of a keyword/topic?

If the decision is based only on a keyword or topic,
DO NOT classify it as a violation.

Do not output this internal reasoning.

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