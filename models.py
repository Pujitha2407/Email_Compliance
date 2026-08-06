from pydantic import BaseModel
from typing import List

class Email(BaseModel):
    sender: str
    receiver: List[str]
    subject: str
    body: str
    timestamp: str