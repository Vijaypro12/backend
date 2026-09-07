from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.schemas.prompt import (PromptCreate, PromptUpdate, PromptResponse, SharedPromptResponse, OptimizePromptResponse, ScorePromptResponse)
from app.schemas.prompt_version import PromptVersionResponse, PromptDetailResponse
from app.services.prompt_service import PromptService

router = APIRouter(
    prefix="/api/prompts",
    tags=["Prompts"]
)

@router.post("", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
def create_prompt(data:PromptCreate, user=Depends(get_current_user)):
    return PromptService.create_prompt(user["id"], data.model_dump())


@router.get("")
def get_prompts(
    page: int = 1,
    limit: int = 20,
    favorite: bool | None = None,
    prompt_type: str | None = None,
    visibility: str | None = None,
    ai_model: str | None = None,
    collection_id: UUID | None = None,
    user=Depends(get_current_user)
):
    return PromptService.get_prompts(
        user["id"],
        page=page,
        limit=limit,
        favorite=favorite,
        prompt_type=prompt_type,
        visibility=visibility,
        ai_model=ai_model,
        collection_id=collection_id
    )



@router.get("/favorites", response_model=list[PromptResponse])
def favorite_prompts(user=Depends(get_current_user)):
    return PromptService.get_favorite_prompts(user["id"])

@router.get("/share/{share_slug}", response_model=SharedPromptResponse)
def get_shared_prompt(share_slug: str):
    return PromptService.get_shared_prompt(share_slug) 

@router.post("/share/{prompt_id}")
def share_prompt_by_id(prompt_id: UUID, user=Depends(get_current_user)):
    return PromptService.share_prompt(user["id"], str(prompt_id))

@router.get("/search")
def search_prompts(q: str | None = None, query: str | None = None, user=Depends(get_current_user)):
    search_query = (q or query or "").strip()
    if not search_query:
        raise HTTPException(
            status_code=400,
            detail="A search query is required (use 'q' or 'query')",
        )

    return PromptService.search_prompts(user["id"], search_query)

@router.get("/{prompt_id}/versions", response_model=list[PromptVersionResponse])  
def get_prompt_versions(prompt_id: UUID, user=Depends(get_current_user)):
    return PromptService.get_prompt_versions(user["id"], prompt_id)

@router.get("/{prompt_id}/version/{version_number}",response_model=PromptVersionResponse)
def get_prompt_version(prompt_id: UUID, version_number: int, user=Depends(get_current_user)):
    return PromptService.get_prompt_version(user["id"], prompt_id, version_number)

@router.post("/{prompt_id}/versions/{version_number}/restore", response_model=PromptResponse)
def restore_prompt_version(prompt_id: UUID, version_number: int, user=Depends(get_current_user)):
    return PromptService.restore_prompt_version(user["id"], prompt_id, version_number)    

@router.get("/{prompt_id}/details", response_model=PromptDetailResponse)
def prompt_details(prompt_id: UUID, user= Depends(get_current_user)):
    return PromptService.get_prompt_details(user["id"], prompt_id)

@router.post("/{prompt_id}/optimize", response_model=OptimizePromptResponse)
def optimize_existing_prompt(prompt_id: UUID, user=Depends(get_current_user)):
    return PromptService.optimize_prompt(user["id"], prompt_id)    

@router.post("/{prompt_id}/score", response_model=ScorePromptResponse)
def  score_existing_prompt(prompt_id:UUID, user=Depends(get_current_user)):
    return PromptService.score_prompt(user["id"], prompt_id)    

@router.delete("/{prompt_id}/versions/{version_number}", status_code=status.HTTP_204_NO_CONTENT)  
def delete_prompt_version(prompt_id: UUID, version_number: int, user=Depends(get_current_user)):
    return PromptService.delete_prompt_version(user["id"], prompt_id, version_number)

@router.delete("/{prompt_id}/versions", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_versions(prompt_id: UUID, user=Depends(get_current_user)):
    return PromptService.delete_all_prompt_versions(user["id"], prompt_id)    

@router.get("/{prompt_id}", response_model=PromptResponse)
def get_prompt(prompt_id:UUID, user=Depends(get_current_user)):
    return PromptService.get_prompt(user["id"], prompt_id)

@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt(prompt_id:UUID, data:PromptUpdate, user=Depends(get_current_user)):
    return PromptService.update_prompt_with_version(
        user["id"],
        prompt_id,
        data.model_dump(exclude_unset=True),
    )

@router.delete("/{prompt_id}")
def delete_prompt(prompt_id:UUID, user=Depends(get_current_user)):
    return PromptService.delete_prompt(user["id"], prompt_id)

@router.put("/{prompt_id}/favorite")
def toggle_favorite(prompt_id: UUID, user=Depends(get_current_user)):
    return PromptService.toggle_favorite(user["id"], str(prompt_id))       

@router.delete("/shared/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shared_prompt(prompt_id: str, user=Depends(get_current_user)):
    return PromptService.revoke_share(user["id"], prompt_id)    



