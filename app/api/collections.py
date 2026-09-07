from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user

from app.schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    SharedCollectionResponse,
)
from app.services.collection_service import CollectionService


router = APIRouter(
    prefix="/api/collections",
    tags=["Collections"]
)


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(data: CollectionCreate, user=Depends(get_current_user)):
    return CollectionService.create_collection(user["id"], data.model_dump())


@router.get("", response_model=list[CollectionResponse])
def get_collections(user=Depends(get_current_user)):
    return CollectionService.get_collections(user["id"])


@router.get("/share/{collection_id}")
def share_collection(collection_id: UUID, user=Depends(get_current_user)):
    return CollectionService.share_collection(user["id"], collection_id)


@router.get("/shared/{share_slug}", response_model=SharedCollectionResponse)
def get_shared_collection(share_slug: str):
    return CollectionService.get_shared_collection(share_slug)


@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection(collection_id: UUID, user=Depends(get_current_user)):
    return CollectionService.get_collection(user["id"], collection_id)


@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(collection_id: UUID, data: CollectionUpdate, user=Depends(get_current_user)):
    return CollectionService.update_collection(user["id"], collection_id, data.model_dump(exclude_unset=True))


@router.delete("/{collection_id}")
def delete_collection(collection_id: UUID, user=Depends(get_current_user)):
    return CollectionService.delete_collection(user["id"], collection_id)