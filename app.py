from fastapi import FastAPI

from models import Email

from services.email_ingestion import EmailIngestionService
from services.preprocessing import PreprocessingService
from services.rag_retrieval import RAGRetrievalService

app = FastAPI()

ingestion_service = EmailIngestionService()
preprocessing_service = PreprocessingService()
rag_service = RAGRetrievalService()


@app.post("/email")
def receive_email(email: Email):

    ingestion_result = ingestion_service.execute(email)

    preprocessing_result = preprocessing_service.execute(
        ingestion_result
    )

    rag_result = rag_service.execute(
        preprocessing_result
    )

    return rag_result