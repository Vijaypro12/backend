from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from app.auth.dependencies import get_current_user
from app.schemas.scorer import ScoreRequest, ScoreResponse
from app.services.scorer_service import ScorerService

router = APIRouter(
    prefix="/api/scorer",
    tags=["Prompt Scorer"]
)


@router.post("", response_model=ScoreResponse)
def score_prompt(data: ScoreRequest):
    return ScorerService.score(data.prompt)