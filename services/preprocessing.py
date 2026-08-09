class PreprocessingService:
    def execute(self, emails):
        print("Starting PreProcessing...")
        # loop over dictionary of mails with mail_id as key and email as value
        for mail_id, email in emails.items():
            body = email["email"]["body"]
            # Normalize spaces
            body = " ".join(body.split())
            email["email"]["body"] = body
        print("PreProcessing Finished")