import os
import json

from dotenv import load_dotenv
from openai import AzureOpenAI

from services.compliance_prompt import build_compliance_prompt


load_dotenv()


client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

model_deployment = os.getenv(
    "AZURE_OPENAI_MODEL_DEPLOYMENT"
)


class ComplianceAnalysisService:

    def __init__(self, votes_per_email=5):
        self.client = client
        self.results = {}
        self.votes_per_email = votes_per_email

    def _call_llm_once(self, prompt):
        """
        Single LLM call. Raises json.JSONDecodeError or
        ValueError on malformed output so the caller can
        catch and skip that vote.
        """
        response = self.client.responses.create(
            model=model_deployment,
            input=prompt,
            store=False,
            temperature=0.3
        )

        raw_output = response.output_text.strip()

        # Remove Markdown JSON fences if the model
        # still returns them.
        if raw_output.startswith("```"):
            lines = raw_output.splitlines()

            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            raw_output = "\n".join(lines).strip()

        result = json.loads(raw_output)

        if not isinstance(result, dict):
            raise ValueError("LLM response is not a JSON object")

        if "violation" not in result:
            raise ValueError("Missing violation field")

        if "categories" not in result:
            raise ValueError("Missing categories field")

        return result, response.output_text

    def classify_with_voting(self, prompt, n=5):
        """
        Calls the LLM n times and takes a majority vote on the
        violation verdict, then keeps only categories that agree
        with the majority verdict. This reduces run-to-run
        variance caused by sampling randomness on borderline
        emails.
        """
        votes = []
        raw_outputs = []

        for _ in range(n):
            try:
                result, raw_output = self._call_llm_once(prompt)
                votes.append(result)
                raw_outputs.append(raw_output)
            except (json.JSONDecodeError, ValueError):
                continue

        if not votes:
            return {
                "error": "Invalid JSON response",
                "raw_output": raw_outputs[-1] if raw_outputs else ""
            }

        violation_count = sum(
            1 for v in votes if v.get("violation") is True
        )
        final_violation = violation_count > len(votes) / 2

        # Tally categories only from votes that agree with the
        # majority verdict, so a minority vote's categories don't
        # leak into a majority "no violation" result or vice versa.
        category_tally = {}
        agreeing_votes = [
            v for v in votes if v.get("violation") is final_violation
        ]

        for v in agreeing_votes:
            for cat in v.get("categories", []):
                key = cat.get("category", "")
                if not key:
                    continue
                category_tally.setdefault(key, []).append(cat)

        final_categories = []
        if final_violation and agreeing_votes:
            # Keep a category if it appeared in at least half of
            # the votes that agreed with the majority verdict.
            threshold = len(agreeing_votes) / 2
            for key, entries in category_tally.items():
                if len(entries) >= threshold:
                    final_categories.append(entries[0])

        return {
            "violation": final_violation,
            "categories": final_categories
        }

    # Compliance Analysis
    def execute(
        self,
        emails,
        risk_categories,
        retriever,
        export=True
    ):

        print("Starting Compliance Analysis...")

        self.results = {}

        # Open llm_input fresh each run instead of appending
        # forever across runs.
        if export:
            open("llm_input", "w", encoding="utf-8").close()

        for mail_id, email in emails.items():

            retrieved_policies = retriever.retrieve(
                email,
                top_k=len(retriever.policies),
                min_score=0.05,
                min_results=3
            )

            print(
                "number of policies received:",
                len(retrieved_policies)
            )

            for i, item in enumerate(retrieved_policies, 1):
                print(
                    f"{i}: "
                    f"{item['policy']['policy_id']}"
                    f"-{item['similarity_score']}"
                )

            prompt = build_compliance_prompt(
                email,
                risk_categories,
                retrieved_policies
            )

            if export:
                with open("llm_input", "a", encoding="utf-8") as f:
                    f.write("\n" + "=" * 100 + "\n")
                    f.write(f"Mail: {mail_id}\n")
                    f.write("=" * 100 + "\n")
                    f.write("Retrieved policies:\n")

                    for item in retrieved_policies:
                        f.write(
                            f"{item['policy']['policy_id']}"
                            f"-score:{item['similarity_score']}\n"
                        )

                    f.write("\n")
                    f.write(prompt)
                    f.write("\n\n")

            result = self.classify_with_voting(
                prompt,
                n=self.votes_per_email
            )

            self.results[mail_id] = result

            if "error" in result:
                print(f"{mail_id}: all {self.votes_per_email} votes failed to parse")
            else:
                print(
                    f"{mail_id}: violation={result['violation']} "
                    f"categories={len(result['categories'])}"
                )

        print("Compliance Analysis Finished.")

        if export:
            with open("llm_ouput.json", "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=4)

    def get_results(self):
        return self.results