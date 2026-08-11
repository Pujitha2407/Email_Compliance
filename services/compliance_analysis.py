import os
import json
import numpy as np

from openai import AzureOpenAI
from services.compliance_prompt import build_compliance_prompt


client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2025-01-01-preview"
)

model_deployment = "gpt-5.5"

# This must be the name of your Azure embedding deployment
embedding_model = "text-embedding-3-small"


class ComplianceAnalysisService:

    def __init__(self):
        self.client = client
        self.results = {}

        # Load policies from JSON
        with open(
            "data/policies.json",
            "r",
            encoding="utf-8"
        ) as file:
            self.policies = json.load(file)

        # Store policy embeddings
        self.policy_embeddings = []

        self.create_policy_embeddings()

    def create_policy_embeddings(self):

        policy_texts = []

        for policy in self.policies:

            text = f"""
Category:
{policy["category"]}

Title:
{policy["title"]}

Definition:
{policy["definition"]}

Violations:
{policy["violations"]}

Exceptions:
{policy["exceptions"]}

Examples:
{policy["examples"]}
"""

            policy_texts.append(text)

        response = self.client.embeddings.create(
            model=embedding_model,
            input=policy_texts
        )

        self.policy_embeddings = [
            np.array(item.embedding)
            for item in response.data
        ]

        print("Policy embeddings created.")

    def cosine_similarity(self, vector1, vector2):

        denominator = (
            np.linalg.norm(vector1)
            * np.linalg.norm(vector2)
        )

        if denominator == 0:
            return 0

        return np.dot(
            vector1,
            vector2
        ) / denominator

    def retrieve_policies(
        self,
        email,
        top_k=3
    ):

        # Use the subject and body as the search query
        query = f"""
Subject:
{email["subject"]}

Body:
{email["body"]}
"""

        response = self.client.embeddings.create(
            model=embedding_model,
            input=[query]
        )

        email_embedding = np.array(
            response.data[0].embedding
        )

        policy_results = []

        for policy, policy_embedding in zip(
            self.policies,
            self.policy_embeddings
        ):

            similarity = self.cosine_similarity(
                email_embedding,
                policy_embedding
            )

            policy_results.append({
                "policy_id": policy["policy_id"],
                "category": policy["category"],
                "title": policy["title"],
                "definition": policy["definition"],
                "violations": policy["violations"],
                "exceptions": policy["exceptions"],
                "examples": policy["examples"],
                "similarity": float(similarity)
            })

        # Highest similarity first
        policy_results.sort(
            key=lambda x: x["similarity"],
            reverse=True
        )

        return policy_results[:top_k]

    def execute(self, emails, risk_categories):

        print("Starting Compliance Analysis...")

        self.results = {}

        for mail_id, email in emails.items():

            # email["email"] contains:
            # from, to, subject, body

            email_data = email["email"]

            # --------------------------------
            # RAG POLICY RETRIEVAL
            # --------------------------------

            retrieved_policies = self.retrieve_policies(
                email_data,
                top_k=3
            )

            print(
                f"Mail {mail_id} - Retrieved policies:"
            )

            for policy in retrieved_policies:
                print(
                    f"  {policy['category']} "
                    f"score={policy['similarity']:.3f}"
                )

            # --------------------------------
            # BUILD PROMPT
            # --------------------------------

            prompt = build_compliance_prompt(
                email_data,
                risk_categories,
                retrieved_policies
            )

            # --------------------------------
            # GPT-5.5
            # --------------------------------

            response = self.client.responses.create(
                model=model_deployment,
                input=prompt
            )

            # --------------------------------
            # KEEPING YOUR EXISTING TRY/EXCEPT
            # --------------------------------

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