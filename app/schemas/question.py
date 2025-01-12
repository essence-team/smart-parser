from typing import List

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    user_id: str
    clusters: List[int]
    digest_text: str
    query_history: List[str]
