import pandas as pd
import json

class EmailIngestionService:
    def __init__(self):
        self.emails_db = {}
        self.email_b = {}

    def execute(self, file_path, export=False):
        print("Starting Email Ingestion...")
        df = pd.read_csv(file_path)
        mail_id = 1
        for _, row in df.iterrows():
            self.emails_db[str(mail_id)] = {
                "email": row["Email Sample"]
            }
            if mail_id == 4:
                self.email_b[str(mail_id)] = self.emails_db[str(mail_id)]
            mail_id += 1
        print("Email Ingestion Finished.")
        # export result
        if export == True:
            with open("ingestion_ouput.json", "w") as f:
                json.dump(self.emails_db, f, indent=4)

    def get_emails(self):
        return self.email_b
        