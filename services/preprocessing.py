class PreprocessingService:
    def execute(self, emails):
        # loop over dictionary of mails with mail_id as key and email as value
        for mail_id, email in emails.items():
            body = email["email"]["body"]
            # Normalize spaces
            body = " ".join(body.split())
            email["email"]["body"] = body