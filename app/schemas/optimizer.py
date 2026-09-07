from pydantic import BaseModel, Field
from typing import List


class AnalyzeRequest(BaseModel):
    prompt: str


class AnalyzeResponse(BaseModel):
    title: str
    ai_model: str
    prompt_type: str
    original_prompt: str
    original_score: int
    optimized_prompt: str
    optimized_score: int
    improvement: int
    improvements: List[str]
    original_analysis: dict
    optimized_analysis: dict
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    
        