import os
from openai import AzureOpenAI
from services.compliance_prompt import build_compliance_prompt
import json

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2025-01-01-preview"
)

model_deployment = "gpt-5.5"  # Replace with your model deployment name

class ComplianceAnalysisService:
    def __init__(self):
        self.client = client
        self.results = {}

    def execute(self, emails, risk_categories):
        print("Starting Compliance Analysis...")
        self.results = {}
        for mail_id, email in emails.items():
            # email["email"] contains:
            # from, to, subject, body
            prompt = build_compliance_prompt(
                email["email"],
                risk_categories
            )
            response = self.client.responses.create(
                model=model_deployment,
                input=prompt
            )
            try :
                res = response.output_text.strip()
                res = res.replace("```json", "")
                res = res.replace("```", "")
                res = res.strip()
                self.results[mail_id] = json.loads(res)
                print(mail_id)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for mail_id {mail_id}: {response.output_text}")
                self.results[mail_id] = {"error": "Invalid JSON response", "raw_output": response.output_text}
        print("Compliance Analysis Finished.")

    def get_results(self):
        return self.results