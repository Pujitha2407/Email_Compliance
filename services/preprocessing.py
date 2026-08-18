import json
import re


class PreprocessingService:
    def execute(self, emails, export=False):
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
                if re.match(r"^from\s*:", line, re.IGNORECASE):
                    sender = line.split(":", 1)[1].strip()
                elif re.match(r"^to\s*:", line, re.IGNORECASE):
                    recipient = line.split(":", 1)[1].strip()
                elif re.match(r"^subject\s*:", line, re.IGNORECASE):
                    subject = line.split(":", 1)[1].strip()
                elif re.match(r"^body\s*:", line, re.IGNORECASE):
                    body_started = True
                    body_text = line.split(":", 1)[1].strip()
                    if body_text:
                        body.append(body_text)
                elif body_started:
                    body.append(line)

            emails[mail_id] = {
                "from": sender,
                "to": recipient,
                "subject": subject,
                "body": " ".join(body)
            }
        print("PreProcessing Finished")

        if export:
            with open("preprocessing_ouput.json", "w", encoding="utf-8") as f:
                json.dump(emails, f, indent=4)