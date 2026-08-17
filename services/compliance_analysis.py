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

        for mail_id, email in emails.items():

            # Retrieve all available policies.
            # Current policy set is small, so this prevents
            # the correct policy from being excluded by top-k.
            retrieved_policies = retriever.retrieve(
                email,
                top_k=len(retriever.policies)
            )

            print(
                "number of policies received:",
                len(retrieved_policies)
            )

            print(
                "\n----- retrieved policies -------"
            )

            for i, item in enumerate(
                retrieved_policies,
                1
            ):

                print(
                    f"{i}: "
                    f"{item['policy']['policy_id']}"
                    f"-{item['similarity_score']}"
                )

            # Build prompt
            prompt = build_compliance_prompt(
                email,
                risk_categories,
                retrieved_policies
            )

            # Save LLM input
            if export:

                with open(
                    "llm_input",
                    "a",
                    encoding="utf-8"
                ) as f:

                    f.write(
                        "\n"
                        + "=" * 100
                        + "\n"
                    )

                    f.write(
                        f"Mail: {mail_id}\n"
                    )

                    f.write(
                        "=" * 100
                        + "\n"
                    )

                    f.write(
                        "Retrieved policies:\n"
                    )

                    for item in retrieved_policies:

                        f.write(
                            f"{item['policy']['policy_id']}"
                            f"-score:"
                            f"{item['similarity_score']}\n"
                        )

                    f.write("\n")
                    f.write(prompt)
                    f.write("\n\n")

            # LLM Model Call
            response = self.client.responses.create(
                model=model_deployment,
                input=prompt
            )

            # Parse LLM response
            try:

                raw_output = response.output_text.strip()

                # Remove Markdown JSON fences if the model
                # still returns them.
                if raw_output.startswith("```"):

                    lines = raw_output.splitlines()

                    # Remove ```json
                    if (
                        lines
                        and lines[0]
                        .strip()
                        .startswith("```")
                    ):
                        lines = lines[1:]

                    # Remove closing ```
                    if (
                        lines
                        and lines[-1]
                        .strip() == "```"
                    ):
                        lines = lines[:-1]

                    raw_output = "\n".join(
                        lines
                    ).strip()

                result = json.loads(
                    raw_output
                )

                # Basic validation
                if not isinstance(
                    result,
                    dict
                ):
                    raise ValueError(
                        "LLM response is not a JSON object"
                    )

                if "violation" not in result:
                    raise ValueError(
                        "Missing violation field"
                    )

                if "categories" not in result:
                    raise ValueError(
                        "Missing categories field"
                    )

                self.results[mail_id] = result

                print(
                    f"{mail_id}: JSON parsed successfully"
                )

            except (
                json.JSONDecodeError,
                ValueError
            ) as error:

                print(
                    f"Error processing JSON for "
                    f"mail_id {mail_id}: {error}"
                )

                print(
                    "Raw LLM output:"
                )

                print(
                    response.output_text
                )

                self.results[mail_id] = {
                    "error": "Invalid JSON response",
                    "raw_output": response.output_text
                }

        print(
            "Compliance Analysis Finished."
        )

        # Export result
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

    def get_results(self):
        return self.results