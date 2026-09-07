import secrets
from uuid import UUID

from fastapi import HTTPException

from app.database.client import supabase
from app.schemas.collection import Visibility


def _visibility_value(value):
    return value.value if isinstance(value, Visibility) else value


class CollectionService:

    @staticmethod
    def create_collection(
        user_id: str,
        data: dict
    ):
        data["user_id"] = user_id
        data["visibility"] = _visibility_value(data.get("visibility", Visibility.private))
        if data["visibility"] == Visibility.public.value:
            data["share_slug"] = secrets.token_urlsafe(8)

        response = (
            supabase
            .table("collections")
            .insert(data)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=400,
                detail="Failed to create collection"
            )

        return response.data[0]

    @staticmethod
    def get_collections(
        user_id: str
    ):
        response = (
            supabase
            .table("collections")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    @staticmethod
    def get_collection(
        user_id: str,
        collection_id: UUID
    ):
        response = (
            supabase
            .table("collections")
            .select("*")
            .eq("id", str(collection_id))
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Collection not found"
            )

        return response.data

    @staticmethod
    def update_collection(
        user_id: str,
        collection_id: UUID,
        data: dict
    ):
        data = {
            key: value
            for key, value in data.items()
            if value is not None
        }

        if not data:
            raise HTTPException(
                status_code=400,
                detail="No fields to update"
            )

        existing = (
            supabase
            .table("collections")
            .select("visibility, share_slug")
            .eq("id", str(collection_id))
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        if not existing.data:
            raise HTTPException(status_code=404, detail="Collection not found")

        if "visibility" in data:
            data["visibility"] = _visibility_value(data["visibility"])
            if data["visibility"] == Visibility.public.value and not existing.data.get("share_slug"):
                data["share_slug"] = secrets.token_urlsafe(8)
            elif data["visibility"] != Visibility.public.value:
                data["share_slug"] = None

        response = (
            supabase
            .table("collections")
            .update(data)
            .eq("id", str(collection_id))
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Collection not found")

        return response.data[0]

    @staticmethod
    def delete_collection(
        user_id: str,
        collection_id: UUID
    ):
        response = (
            supabase
            .table("collections")
            .delete()
            .eq("id", str(collection_id))
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Collection not found"
            )

        return {"message": "Collection deleted successfully"}

    @staticmethod
    def share_collection(user_id: str, collection_id: UUID):
        existing = (
            supabase.table("collections")
            .select("id, visibility, share_slug")
            .eq("id", str(collection_id))
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(status_code=404, detail="Collection not found")

        slug = existing.data.get("share_slug") or secrets.token_urlsafe(8)
        response = (
            supabase.table("collections")
            .update({"visibility": Visibility.public.value, "share_slug": slug})
            .eq("id", str(collection_id))
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create share link")

        return {
            "collection_id": str(collection_id),
            "visibility": Visibility.public.value,
            "share_slug": slug,
            "share_url": f"/collections/share/{slug}",
        }

    @staticmethod
    def get_shared_collection(share_slug: str):
        collection_response = (
            supabase.table("collections")
            .select("id, name, description, visibility, share_slug, created_at")
            .eq("share_slug", share_slug)
            .eq("visibility", Visibility.public.value)
            .maybe_single()
            .execute()
        )

        if not collection_response.data:
            raise HTTPException(status_code=404, detail="Shared collection not found")

        collection = collection_response.data
        prompts_response = (
            supabase.table("prompts")
            .select(
                "id, title, original_prompt, optimized_prompt, score, "
                "ai_model, prompt_type, visibility, share_slug, created_at"
            )
            .eq("collection_id", str(collection["id"]))
            .order("created_at", desc=True)
            .execute()
        )

        return {
            **collection,
            "prompts": prompts_response.data or [],
        }