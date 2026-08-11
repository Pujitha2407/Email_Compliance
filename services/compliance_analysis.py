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

    # Compliance Analysis
    def execute(self, emails, risk_categories, retrieved_policies):
        print("Starting Compliance Analysis...")
        self.results = {}
        for mail_id, email in emails.items():
            # Build prompt
            prompt = build_compliance_prompt(
                email,
                risk_categories,
                retrieved_policies[mail_id]
            )
            # LLM Model Call
            response = self.client.responses.create(
                model=model_deployment,
                input=prompt
            )
            try:
                # res = response.output_text.strip()
                # res = res.replace("```json", "")
                # res = res.replace("```", "")
                # res = res.strip()
                self.results[mail_id] = json.loads(response.output_text)
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