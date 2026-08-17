import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
from services.compliance_prompt import build_compliance_prompt, build_context_prompt


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
    def __init__(self, policies: dict = None):
        self.client = client
        self.policies = policies
        self.results = {}

    # Compliance Analysis
    def execute(self, emails, risk_categories, export=True):
        print("Starting Compliance Analysis...")
        self.results = {}
        for mail_id, email in emails.items():
            # Create a detailed email summary context
            context_prompt = build_context_prompt(email)
            context_response = self.client.responses.create(
                            model=model_deployment,
                            input=context_prompt,
                            store=False
                        )
            #print(context_response.output_text)
            # Build Compliance Check prompt
            prompt = build_compliance_prompt(
                # email,
                context_response.output_text,
                risk_categories,
                self.policies
            )
            # Save LLM input to file, if export true
            if export:
                with open("llm_input", "a", encoding="utf-8") as f:
                    f.write("\n" + "=" * 100 + "\n")
                    f.write(f"Mail: {mail_id}\n")
                    f.write("=" * 100 + "\n")
                    f.write("\n")
                    f.write(prompt)
                    f.write("\n\n")
            # LLM Model Call for Compliance Check
            response = self.client.responses.create(
                model=model_deployment,
                input=prompt,
                store=False
            )
            # Parse LLM response
            try:
                raw_output = response.output_text.strip()
                # Remove Markdown JSON fences if the model
                # still returns them.
                if raw_output.startswith("```"):
                    lines = raw_output.splitlines()
                    # Remove ```json
                    if (lines and lines[0].strip().startswith("```")):
                        lines = lines[1:]
                    # Remove closing ```
                    if (lines and lines[-1].strip() == "```"):
                        lines = lines[:-1]
                    raw_output = "\n".join(lines).strip()
                result = json.loads(raw_output)
                # Basic validation
                if not isinstance(result,dict):
                    raise ValueError("LLM response is not a JSON object")
                if "violation" not in result:
                    raise ValueError("Missing violation field")
                if "categories" not in result:
                    raise ValueError("Missing categories field")
                self.results[mail_id] = result
                print(f"{mail_id}: JSON parsed successfully")

            except (json.JSONDecodeError, ValueError) as error:
                print(
                    f"Error processing JSON for "
                    f"mail_id {mail_id}: {error}"
                )
                print(f"Raw LLM output: {response.output_text}")
                self.results[mail_id] = {
                    "error": "Invalid JSON response",
                    "raw_output": response.output_text
                }
        print("Compliance Analysis Finished.")

        # Export result
        if export:
            with open("llm_ouput.json", "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=4)

    def get_results(self):
        return self.results