from pydantic import BaseModel, Field
from typing import List


class ScoreRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)

class CategoryScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    feedback: str

class ScoreResponse(BaseModel):
    score: int
    analysis: dict
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    suggested_model: str

    