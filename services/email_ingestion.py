import pandas as pd


class EmailIngestionService:
    def __init__(self):
        self.emails_db = {}

    def execute(self, file_path):
        print("Starting Email Ingestion...")
        df = pd.read_csv(file_path)
        mail_id = 1
        for _, row in df.iterrows():
            self.emails_db[mail_id] = {
                "email": row["Email Sample"]
            }
            mail_id += 1
        print("Email Ingestion Finished.")

    def get_emails(self):
        return self.emails_db