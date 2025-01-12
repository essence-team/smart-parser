from database import get_db_session
from fastapi import APIRouter, Depends
from routers import check_api_key_access
from schemas.question import QuestionRequest
from services.qrag import qrag
from sqlalchemy.ext.asyncio import AsyncSession

question_router = APIRouter(prefix="/question", tags=["question"])


@question_router.post("/ask", response_model=str)
async def ask_question(
    question_request: QuestionRequest,
    db: AsyncSession = Depends(get_db_session),
    api_key=Depends(check_api_key_access),
) -> str:
    # Placeholder logic for answering the question
    answer = qrag.answer_question(
        clusters=question_request.clusters,
        digest_text=question_request.digest_text,
        query_history=question_request.query_history,
    )
    return answer
