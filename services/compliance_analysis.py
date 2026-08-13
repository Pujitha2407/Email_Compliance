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
model_deployment = os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT")

class ComplianceAnalysisService:
    def __init__(self):
        self.client = client
        self.results = {}

    # Compliance Analysis
    def execute(self, emails, risk_categories, retriever, export=False):
        print("Starting Compliance Analysis...")
        self.results = {}
        for mail_id, email in emails.items():
            retrieved_policies=retriever.retrieve(email,top_k=6)
            print("number of policies recieved:",len(retrieved_policies))
            print("\n-----retrieved policies-------")
            for i ,item in enumerate(retrieved_policies,1):
                print(f"{i}: {item['policy']['policy_id']}"
                      f"-{item['similarity_score']}")
            # Build prompt
            prompt = build_compliance_prompt(
                email,
                risk_categories,
                retrieved_policies
            )
            # LLM Model Call
            with open("llm_input","a",encoding="utf-8") as f:
                f.write("\n" + "=" * 100 +"\n")
                f.write(f"Mail: {mail_id}\n")
                f.write("=" * 100 +"\n")
                f.write("Retrieved policies:\n")
                for item in retrieved_policies:
                    f.write(f"{item['policy']['policy_id']}"
                            f"-score:{item['similarity_score']}\n")
                f.write("\n")
                f.write(prompt)
                f.write("\n\n")
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
        # export result
        if export == True:
            with open("llm_ouput.json", "w") as f:
                json.dump(self.results, f, indent=4)

    def get_results(self):
        return self.results