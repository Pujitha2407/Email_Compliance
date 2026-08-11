class PreprocessingService:
    def execute(self, emails):
        print("Starting PreProcessing...")
        for mail_id, email in emails.items():
            email_text = email["email"]
            lines = email_text.splitlines()

            sender = ""
            recipient = ""
            subject = ""
            body = []
            body_started = False
            for line in lines:
                line = line.strip()
                if line.lower().startswith("from"):
                    sender = line.split(":", 1)[1].strip()
                elif line.lower().startswith("to"):
                    recipient = line.split(":", 1)[1].strip()
                elif line.lower().startswith("subject"):
                    subject = line.split(":", 1)[1].strip()
                elif line.lower().startswith("body"):
                    body_started = True
                    body_text = line.split(":", 1)[1].strip()
                    if body_text:
                        body.append(body_text)
                elif body_started:
                    body.append(line)
            # Store parsed email
            emails[mail_id] = {
                "from": sender,
                "to": recipient,
                "subject": subject,
                "body": " ".join(body)
            }
        print("PreProcessing Finished")