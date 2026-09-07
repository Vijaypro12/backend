from enum import Enum
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class AIModel(str, Enum):
    chatgpt = "chatgpt"
    gemini = "gemini"
    claude = "claude"
    grok = "grok"
    deepseek = "deepseek"
    midjourney = "midjourney"
    flux = "flux"
    runway = "runway"
    veo = "veo"
    imagen = "imagen"
    other = "other"


class PromptType(str, Enum):
    text = "text"
    image = "image"
    video = "video"
    code = "code"
    marketing = "marketing"
    social = "social"
    design = "design"
    other = "other"


class Visibility(str, Enum):
    private = "private"
    unlisted = "unlisted"
    public = "public"


class PromptCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    original_prompt: str = Field(..., min_length=1)
    optimized_prompt: Optional[str] = None
    score: Optional[int] = Field(default=None, ge=0, le=100)
    ai_model: Optional[AIModel] = None
    prompt_type: Optional[PromptType] = None
    collection_id: Optional[UUID] = None
    visibility: Visibility = Visibility.private
    favorite: bool = False


class PromptUpdate(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200
    )
    original_prompt: Optional[str] = None
    optimized_prompt: Optional[str] = None
    score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100
    )
    ai_model: Optional[AIModel] = None
    prompt_type: Optional[PromptType] = None
    collection_id: Optional[UUID] = None
    visibility: Optional[Visibility] = None
    favorite: Optional[bool] = None


class PromptResponse(BaseModel):
    id: UUID
    user_id: UUID
    collection_id: Optional[UUID] = None

    title: str
    original_prompt: str
    optimized_prompt: Optional[str] = None

    score: Optional[int] = None

    ai_model: Optional[AIModel] = None
    prompt_type: Optional[PromptType] = None

    preview_url: Optional[str] = None

    visibility: Visibility
    share_slug: Optional[str] = None
    favorite: bool

    created_at: datetime
    updated_at: datetime

class SharedPromptResponse(BaseModel):
    id: UUID
    title: str
    original_prompt: str
    optimized_prompt: Optional[str] = None
    score: Optional[int] = None
    ai_model: Optional[AIModel] = None
    prompt_type: Optional[PromptType] = None
    visibility: Visibility
    share_slug: Optional[str] = None
    created_at: str

class OptimizePromptResponse(BaseModel):
    prompt: PromptResponse
    improvements: list[str]

class ScorePromptResponse(BaseModel):
    prompt: PromptResponse
    score: int
    feedback: list[str]    




    class Config:
        from_attributes = True