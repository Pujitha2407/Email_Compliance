import os
import json

from openai import AzureOpenAI
from services.compliance_prompt import build_compliance_prompt


client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2025-01-01-preview"
)

model_deployment = "gpt-5.5s" 



class ComplianceAnalysisService:

    def __init__(self):

        self.client = client
        self.results = {}

        # Load policies from knowledge base
        with open(
            "uploadss/policies.json",
            "r",
            encoding="utf-8"
        ) as file:

            self.policies = json.load(file)

    # ---------------------------------------------
    # Policy Retrieval
    # ---------------------------------------------

    def retrieve_policies(
        self,
        email,
        top_k=3
    ):

        email_text = (
            email["subject"]
            + " "
            + email["body"]
        ).lower()

        results = []

        for policy in self.policies:

            score = 0

            # Search definition
            definition_words = (
                policy["definition"]
                .lower()
                .split()
            )

            for word in definition_words:

                if len(word) > 3 and word in email_text:
                    score += 1

            # Search violations
            for violation in policy["violations"]:

                if violation.lower() in email_text:
                    score += 3

            # Search examples
            for example in policy["examples"]:

                if example.lower() in email_text:
                    score += 2

            # Search exceptions
            for exception in policy["exceptions"]:

                if exception.lower() in email_text:
                    score += 2

            results.append({
                "policy_id": policy["policy_id"],
                "category": policy["category"],
                "title": policy["title"],
                "definition": policy["definition"],
                "violations": policy["violations"],
                "exceptions": policy["exceptions"],
                "examples": policy["examples"],
                "retrieval_score": score
            })

        # Highest matching policy first
        results.sort(
            key=lambda x: x["retrieval_score"],
            reverse=True
        )

        # If nothing matched, provide all policies
        # because we only have six policies.
        if all(
            policy["retrieval_score"] == 0
            for policy in results
        ):
            return results

        return results[:top_k]

    # ---------------------------------------------
    # Compliance Analysis
    # ---------------------------------------------

    def execute(
        self,
        emails,
        risk_categories
    ):

        print("Starting Compliance Analysis...")

        self.results = {}

        for mail_id, email in emails.items():

            email_data = email["email"]

            # -------------------------------------
            # Retrieve relevant policies
            # -------------------------------------

            retrieved_policies = (
                self.retrieve_policies(
                    email_data,
                    top_k=3
                )
            )

            print(
                f"Mail {mail_id} - Retrieved policies:"
            )

            for policy in retrieved_policies:

                print(
                    f"  {policy['category']} "
                    f"score={policy['retrieval_score']}"
                )

            # -------------------------------------
            # Build prompt
            # -------------------------------------

            prompt = build_compliance_prompt(
                email_data,
                risk_categories,
                retrieved_policies
            )

            # -------------------------------------
            # GPT-4o
            # -------------------------------------

            response = self.client.responses.create(
                model=model_deployment,
                input=prompt
            )

            # -------------------------------------
            # YOUR EXISTING TRY/EXCEPT
            # -------------------------------------

            try:
                res = response.output_text.strip()
                res = res.replace("```json", "")
                res = res.replace("```", "")
                res = res.strip()
                self.results[mail_id] = json.loads(res)
                print(mail_id)

            except json.JSONDecodeError:
                print(
                    f"Error decoding JSON for mail_id "
                    f"{mail_id}: {response.output_text}"
                )

                self.results[mail_id] = {
                    "error": "Invalid JSON response",
                    "raw_output": response.output_text
                }

        print("Compliance Analysis Finished.")

    def get_results(self):

        return self.results