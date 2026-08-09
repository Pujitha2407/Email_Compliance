import json
from services.email_ingestion import EmailIngestionService
from services.preprocessing import PreprocessingService
from services.compliance_analysis import ComplianceAnalysisService
from services.compliance_score import ComplainceScore


def run():
    # read user config json file 
    user_config = json.load(open("user_config/categories.json"))
    # update risk categories in email ingestion service
    risk_categories = list(user_config["categories"].keys())

    # Initialize services
    email_ingestion = EmailIngestionService()
    preprocessing = PreprocessingService()
    compliance = ComplianceAnalysisService()
    compliance_score = ComplainceScore(user_config)

    # Execute services
    email_ingestion.execute("uploads/SampleCategorisedEmails_all_data.csv")
    preprocessing.execute(email_ingestion.get_emails())
    compliance.execute(email_ingestion.get_emails(), risk_categories)
    compliance_score.execute(
        email_ingestion.get_emails(),
        compliance.get_results()
    )

if __name__ == "__main__":
    run()
