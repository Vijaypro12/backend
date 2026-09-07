from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.prompt import AIModel, PromptType, Visibility
from app.schemas.prompt import PromptResponse


class PromptVersionResponse(BaseModel):
    id: UUID
    prompt_id: UUID
    user_id: UUID
    version_number: int
    title: str
    original_prompt: str
    optimized_prompt: Optional[str] = None
    score: Optional[int] = None
    ai_model: Optional[AIModel] = None
    prompt_type: Optional[PromptType] = None
    visibility: Optional[Visibility] = None
    created_at: datetime

class PromptDetailResponse(BaseModel):
    prompt: PromptResponse
    versions: list[PromptVersionResponse]
    
