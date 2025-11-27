from fastapi import APIRouter
from pydantic import BaseModel

from graphs.candidate_scores import invoke_candidate_scores
from schemas.candidate_scores import CandidateScores

router = APIRouter()


class CVRequest(BaseModel):
    cv_text: str


@router.post("/candidate-scores")
async def generate_candidate_scores(request: CVRequest) -> CandidateScores:
    """Generate candidate education and experience scores with detailed analysis"""
    return await invoke_candidate_scores(request.cv_text)
