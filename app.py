import json
import argparse
from services.email_ingestion import EmailIngestionService
from services.preprocessing import PreprocessingService
from services.rag_retriever import RAGRetriever
from services.compliance_analysis import ComplianceAnalysisService
from services.compliance_score import ComplainceScore
parser = argparse.ArgumentParser()

def run():
    parser.add_argument(
        "--export",
        action="store_true",
        help="Enables export of each stage"
    )
    args = parser.parse_args()
    # read user config json file 
    user_config = json.load(open("user_config/categories.json"))
    policies = json.load(open("uploads/policies.json"))
    # update risk categories in email ingestion service
    risk_categories = list(user_config["categories"].keys())

    # Initialize services
    email_ingestion = EmailIngestionService()
    preprocessing = PreprocessingService()
    retriever = RAGRetriever()
    compliance = ComplianceAnalysisService()
    compliance_score = ComplainceScore(user_config)

    # Execute services
    email_ingestion.execute("uploads/SampleCategorisedEmails_all_data.csv", args.export)
    preprocessing.execute(email_ingestion.get_emails(), args.export)
    retriever.build_index(policies)
    compliance.execute(email_ingestion.get_emails(), risk_categories, retriever, args.export)
    # compliance.results = json.load(open("llm_output.json"))
    compliance_score.execute(
        email_ingestion.get_emails(),
        compliance.get_results()
    )

if __name__ == "__main__":
    run()
