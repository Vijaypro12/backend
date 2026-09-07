from typing import Optional
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.prompt import SharedPromptResponse


class Visibility(str, Enum):
    private = "private"
    unlisted = "unlisted"
    public = "public"


class CollectionCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    description: Optional[str] = None
    visibility: Visibility = Visibility.private


class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    description: Optional[str] = None
    visibility: Optional[Visibility] = None


class CollectionResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str] = None
    visibility: Visibility
    share_slug: Optional[str] = None
    created_at: str
    updated_at: str


class SharedCollectionResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    visibility: Visibility
    share_slug: str
    created_at: str
    prompts: list[SharedPromptResponse] = Field(default_factory=list)