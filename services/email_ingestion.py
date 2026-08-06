class EmailIngestionService:

    def receive_email(self, email):
        print("Receiving email...")
        return email

    def capture_metadata(self, email):

        metadata = {
            "sender": email.sender,
            "receiver": email.receiver,
            "subject": email.subject,
            "timestamp": email.timestamp
        }

        return metadata

    def store_raw_email(self, email):
        print("Store raw email")

    def execute(self, email):

        self.receive_email(email)

        metadata = self.capture_metadata(email)

        self.store_raw_email(email)

        return {
            "email": email,
            "metadata": metadata
        }