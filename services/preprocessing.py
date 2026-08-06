from bs4 import BeautifulSoup
from langdetect import detect

class PreprocessingService:

    def remove_html(self, text):
        return BeautifulSoup(text, "html.parser").get_text()

    def detect_language(self, text):
        return detect(text)

    def execute(self, ingestion_result):

        email = ingestion_result["email"]
        metadata = ingestion_result["metadata"]

        clean_body = self.remove_html(email.body)
        language = self.detect_language(clean_body)

        email.body = clean_body
        metadata["language"] = language

        return {
            "email": email,
            "metadata": metadata
        }