from  fastapi import APIRouter, Depends
from uuid import UUID
from app.auth.dependencies import get_current_user
from app.services.optimizer_service import OptimizerService
from app.schemas.optimizer import AnalyzeResponse, AnalyzeRequest

router = APIRouter(
    prefix="/api/optimizer",
    tags=["Prompt Optimizer"]
)


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_prompt(data: AnalyzeRequest):
    return OptimizerService.analyze(data.prompt)

