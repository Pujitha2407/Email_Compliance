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

    def __init__(self):

        self.client = client
        self.results = {}

    def _validate_result(
        self,
        result,
        email,
        retrieved_policies
    ):

        valid_categories = {
            item["policy"]["category"]
            for item in retrieved_policies
        }

        valid_policy_ids = {
            item["policy"]["policy_id"]
            for item in retrieved_policies
        }

        decision = result.get(
            "decision"
        )

        if decision not in {
            "COMPLIANT",
            "NON_COMPLIANT",
            "HUMAN_REVIEW"
        }:

            raise ValueError(
                f"Invalid decision: {decision}"
            )

        categories = result.get(
            "categories"
        )

        if not isinstance(
            categories,
            list
        ):

            raise ValueError(
                "categories must be a list"
            )

        confidence = result.get(
            "confidence"
        )

        if not isinstance(
            confidence,
            (int, float)
        ):

            raise ValueError(
                "confidence must be numeric"
            )

        if not 0 <= confidence <= 1:

            raise ValueError(
                "confidence must be between 0 and 1"
            )

        if decision == "COMPLIANT":

            result["violation"] = False
            result["categories"] = []
            result["needs_review"] = False

        elif decision == "NON_COMPLIANT":

            if not categories:

                raise ValueError(
                    "NON_COMPLIANT requires at least one category"
                )

            for category_result in categories:

                category = category_result.get(
                    "category",
                    ""
                )

                policy_id = category_result.get(
                    "policy_id",
                    ""
                )

                evidence = category_result.get(
                    "evidence",
                    ""
                )

                if category not in valid_categories:

                    raise ValueError(
                        f"Category '{category}' "
                        f"was not retrieved by RAG"
                    )

                if policy_id not in valid_policy_ids:

                    raise ValueError(
                        f"Policy ID '{policy_id}' "
                        f"was not retrieved by RAG"
                    )

                if not evidence:

                    raise ValueError(
                        "Violation must contain evidence"
                    )

                if evidence not in email["body"]:

                    raise ValueError(
                        "Evidence is not an exact "
                        "quote from the email body"
                    )

            result["violation"] = True
            result["needs_review"] = False

        elif decision == "HUMAN_REVIEW":

            result["violation"] = False
            result["categories"] = []
            result["needs_review"] = True

        return result

    def execute(
        self,
        emails,
        risk_categories,
        retriever,
        export=True
    ):

        print(
            "Starting Compliance Analysis..."
        )

        self.results = {}

        for mail_id, email in emails.items():

            retrieved_policies = retriever.retrieve(
                email,
                top_k=4,
                min_similarity=0.20
            )

            print(
                "number of policies recieved:",
                len(retrieved_policies)
            )

            print(
                "\n-----retrieved policies-------"
            )

            for i, item in enumerate(
                retrieved_policies,
                1
            ):

                print(
                    f"{i}: "
                    f"{item['policy']['policy_id']} - "
                    f"{item['policy']['category']} - "
                    f"{item['similarity_score']:.4f}"
                )

            prompt = build_compliance_prompt(
                email,
                risk_categories,
                retrieved_policies
            )

            with open(
                "llm_input",
                "a",
                encoding="utf-8"
            ) as f:

                f.write(
                    "\n" + "=" * 100 + "\n"
                )

                f.write(
                    f"Mail: {mail_id}\n"
                )

                f.write(
                    "=" * 100 + "\n"
                )

                f.write(
                    "Retrieved policies:\n"
                )

                for item in retrieved_policies:

                    f.write(
                        f"{item['policy']['policy_id']} "
                        f"- {item['policy']['category']} "
                        f"- score:"
                        f"{item['similarity_score']:.4f}\n"
                    )

                f.write("\n")
                f.write(prompt)
                f.write("\n\n")

            output = ""

            try:

                response = self.client.responses.create(
                    model=model_deployment,
                    input=prompt
                )

                output = response.output_text.strip()

                print(
                    f"\nLLM Output - Mail {mail_id}:"
                )

                print(output)

                result = json.loads(output)

                result = self._validate_result(
                    result,
                    email,
                    retrieved_policies
                )

                if (
                    result["decision"] != "HUMAN_REVIEW"
                    and result["confidence"] < 0.70
                ):

                    result["decision"] = (
                        "HUMAN_REVIEW"
                    )

                    result["needs_review"] = True

                    result["review_reason"] = (
                        "Confidence below threshold"
                    )

                self.results[mail_id] = result

                print(
                    f"Mail {mail_id}: "
                    f"{result['decision']}"
                )

            except json.JSONDecodeError:

                print(
                    f"Error decoding JSON for mail_id "
                    f"{mail_id}: {output}"
                )

                self.results[mail_id] = {
                    "decision": "HUMAN_REVIEW",
                    "violation": False,
                    "categories": [],
                    "confidence": 0.0,
                    "needs_review": True,
                    "review_reason": "Invalid JSON response",
                    "raw_output": output
                }

            except Exception as error:

                print(
                    f"Error analyzing mail_id "
                    f"{mail_id}: {error}"
                )

                self.results[mail_id] = {
                    "decision": "HUMAN_REVIEW",
                    "violation": False,
                    "categories": [],
                    "confidence": 0.0,
                    "needs_review": True,
                    "review_reason": str(error)
                }

        print(
            "Compliance Analysis Finished."
        )

        if export:

            with open(
                "llm_ouput.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.results,
                    f,
                    indent=4
                )

        return self.results

    def get_results(self):
        return self.results