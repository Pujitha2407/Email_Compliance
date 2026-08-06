from openai import OpenAI
import json

client = OpenAI()


class ComplianceAnalysisService:

    def execute(self, rag_result):

        email = rag_result["email"]

        metadata = rag_result["metadata"]

        policies = rag_result["retrieved_policies"]

        policy_text = ""

        for policy in policies:

            policy_text += policy["content"] + "\n\n"

        prompt = f"""
You are a compliance officer.

Email:

Subject:
{email.subject}

Body:
{email.body}

Relevant Policies:

{policy_text}

Return JSON only.

Required Format:

{{
 "violation": true/false,
 "categories": [],
 "confidence": 0.0,
 "reason": "",
 "evidence": []
}}
"""

        response = client.responses.create(
            model="gpt-5.5",
            input=prompt
        )

        result = json.loads(response.output_text)

        return {

            "email": email,

            "metadata": metadata,

            "analysis": result
        }