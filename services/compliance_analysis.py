import os
from openai import AzureOpenAI
import compliance_prompt
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

    def execute(self, emails, risk_categories):
        self.results = {}
        for mail_id, email in emails.items():
            prompt = compliance_prompt.build_compliance_prompt(email, risk_categories)
            response = self.client.responses.create(
                model=model_deployment,
                input=prompt
            )
            try :
                self.results[mail_id] = json.loads(response.output_text)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for mail_id {mail_id}: {response.output_text}")
                self.results[mail_id] = {"error": "Invalid JSON response", "raw_output": response.output_text}

    def get_results(self):
        return self.results