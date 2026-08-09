import pandas as pd

## Columns
# Date, From, To, Subject, Body, Category, Classification, Column1

class EmailIngestionService:
    def __init__(self):
        self.risk_categories = []
        self.emails_db = {}

    def execute(self, file_path):
        print("Starting Email Ingestion...")
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()
        df['Category'] = df['Category'].str.split().str.join(' ')
        df['Classification'] = df['Classification'].str.split().str.join(' ')
        self.risk_categories = df['Category'].unique().tolist()

        ## iterate each row from dataframe
        mail_id = 1
        for _, row in df.iterrows():
            email = {
                "email": {
                    "from": row["From"],
                    "to": row["To"],
                    "subject": row["Subject"],
                    "body": row["Body"]
                },
                "metadata": {
                    "date": str(row["Date"])
                },
                "risk" : {
                    "category": row["Category"],
                    "classification": row["Classification"]
                }
            }
            self.emails_db[mail_id] = email
            mail_id += 1
        print("Email Ingestion Finished.")

    def get_emails(self):
        return self.emails_db

    def get_risk_categories(self):
        return self.risk_categories