import json
from services.email_ingestion import EmailIngestionService
from services.preprocessing import PreprocessingService
from services.rag_retriever import RAGRetriever
from services.compliance_analysis import ComplianceAnalysisService
from services.compliance_score import ComplainceScore


def run():
    # read user config json file 
    user_config = json.load(open("user_config/categories.json"))
    policies = json.load(open("uploads/policies.json"))
    # update risk categories in email ingestion service
    risk_categories = list(user_config["categories"].keys())

    # Initialize services
    email_ingestion = EmailIngestionService()
    preprocessing = PreprocessingService()
    rag_retriever = RAGRetriever()
    compliance = ComplianceAnalysisService()
    compliance_score = ComplainceScore(user_config)

    # Execute services
    email_ingestion.execute("uploads/SampleCategorisedEmails_all_data.csv")
    # print(json.dumps(email_ingestion.get_emails(), indent=2))
    preprocessing.execute(email_ingestion.get_emails())
    # print("After Preprocessing:");
    # print(json.dumps(email_ingestion.get_emails(), indent=2))
    rag_retriever.build_index(policies)
    mail_retrieved_policies = {}
    for mail_id, email in email_ingestion.get_emails().items():
        retrieved_policies = rag_retriever.retrieve(email, top_k=3)
        mail_retrieved_policies[mail_id] = [policy['policy'] for policy in retrieved_policies]
        # print(f"Mail {mail_id} - Retrieved policies:")
        # for policy in retrieved_policies:
        #     print(
        #         f"  {policy['policy']} "
        #         f"score={policy['similarity_score']}"
        #     )
    compliance.execute(email_ingestion.get_emails(), risk_categories, mail_retrieved_policies)
    compliance_score.execute(
        email_ingestion.get_emails(),
        compliance.get_results()
    )

if __name__ == "__main__":
    run()
