from uuid import UUID
import secrets
import string
from fastapi import HTTPException
from app.database.client import supabase

def make_json_serializable(data: dict) -> dict:
    return {
        key: str(value) if isinstance(value, UUID) else value
        for key, value in data.items()
    }

class PromptService:

    @staticmethod
    def create_prompt(user_id : str, data : dict):
        data["user_id"] = str(user_id)

        data = make_json_serializable(data)

        response = (supabase.table("prompts").insert(data).execute())

        if not response.data:
            raise HTTPException(
                static_method = 400,
                detail = "Failed to create prompt"
            )

        return response.data[0]    


    @staticmethod
    def get_prompt(user_id:str, prompt_id:UUID):
        response = (supabase.table("prompts").select("*").eq("id", str(prompt_id)).eq("user_id", str(user_id)).maybe_single().execute())

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="prompt not found"
            )

        return response.data


    @staticmethod
    def create_prompt_version(user_id: str, prompt: dict):
        
        prompt_id = str(prompt["id"])

        response = (supabase.table("prompt_versions").select("version_number").eq("prompt_id", prompt_id).eq("user_id", str(user_id)).order("version_number", desc=True).limit(1).execute())

        if response.data:
            next_version = response.data[0]["version_number"]+1
        else:
            next_version = 1    
        
        version_data = {
        "prompt_id": prompt_id,
        "user_id": str(user_id),
        "version_number": next_version,
        "title": prompt["title"],
        "original_prompt": prompt["original_prompt"],
        "optimized_prompt": prompt.get("optimized_prompt"),
        "score": prompt.get("score"),
        "ai_model": prompt.get("ai_model"),
        "prompt_type": prompt.get("prompt_type"),
        "visibility": prompt.get("visibility"),
        }


        try:
            response = (
                supabase.table("prompt_versions").insert(version_data).execute())

            if not response.data:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create prompt version"
                )

            return response.data[0]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create prompt version: {str(e)}"
            )   

    @staticmethod
    def get_prompt_versions(user_id: str, prompt_id: UUID):

    
        prompt_response = (supabase.table("prompts").select("id").eq("id", str(prompt_id))
        .eq("user_id", str(user_id)).maybe_single().execute())

        if not prompt_response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

   
        response = (supabase.table("prompt_versions").select("*").eq("prompt_id", str(prompt_id))
        .eq("user_id", str(user_id)).order("version_number", desc=True).execute())

        return response.data

    @staticmethod
    def get_prompt_version(user_id: str, prompt_id: UUID, version_number: int):
   
        prompt_response = (supabase.table("prompts").select("id").eq("id", str(prompt_id))
        .eq("user_id", str(user_id)).maybe_single().execute())

        if not prompt_response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

    
        response = (supabase.table("prompt_versions").select("*")
        .eq("prompt_id", str(prompt_id)).eq("user_id", str(user_id))
        .eq("version_number", version_number).maybe_single().execute())


        if not response:
            raise HTTPException(
                status_code=404,
                detail=f"Version {version_number} not found"
            )

        return response.data    

    @staticmethod
    def restore_prompt_version(user_id: str, prompt_id: UUID, version_number: int):
    
        prompt_response = (supabase.table("prompts").select("*")
        .eq("id", str(prompt_id)).eq("user_id", str(user_id))
        .maybe_single().execute())

        if not prompt_response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        current_prompt = prompt_response.data

        
        version_response = (supabase.table("prompt_versions").select("*")
        .eq("prompt_id", str(prompt_id)).eq("user_id", str(user_id)).eq("version_number", version_number)
        .maybe_single().execute())

        if not version_response.data:
            raise HTTPException(
                status_code=404,
                detail=f"Version {version_number} not found"
            )

        version = version_response.data

    
        PromptService.create_prompt_version(user_id, current_prompt)

   
        restored_data = {
            "title": version["title"],
            "original_prompt": version["original_prompt"],
            "optimized_prompt": version["optimized_prompt"],
            "score": version["score"],
            "ai_model": version["ai_model"],
            "prompt_type": version["prompt_type"],
            "visibility": version["visibility"],
        }

    
        update_response = (supabase.table("prompts").update(restored_data)
        .eq("id", str(prompt_id)).eq("user_id", str(user_id)).execute())

        if not update_response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to restore prompt version"
            )

        return update_response.data[0]    

    @staticmethod
    def delete_prompt_version(user_id: str, prompt_id: UUID, version_number: int):

        response = (supabase.table("prompts").select("id").eq("id", str(prompt_id)).eq("user_id", str(user_id)).maybe_single().execute())

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        response = (supabase.table("prompt_versions").delete().eq("prompt_id", str(prompt_id)).eq("user_id", str(user_id)).eq("version_number", version_number).execute())

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"Version {version_number} not found"
            )  

        return {
            "message": f"Version {version_number} deleted successfully",
            "prompt_id": str(prompt_id),
            "version_number": version_number
        }    

    @staticmethod
    def delete_all_prompt_versions(user_id: str, prompt_id: UUID):
        response = (supabase.table("prompts").select("id").eq("id", str(prompt_id)).eq("user_id", str(user_id)).maybe_single().execute())

        if not response.data:
            raise HTTPException (
                status_code=404,
                detail="prompt not found"
            )

        response = (supabase.table("prompt_versions").delete().eq("user_id", str(user_id)).eq("prompt_id", str(prompt_id)).execute())

        return {
            "message": "All versions deleted successfully",
        }    

    
    @staticmethod
    def update_prompt(user_id: str, prompt_id: UUID, data: dict):

   
        current_response = (
            supabase.table("prompts").select("*")
            .eq("id", str(prompt_id)).eq("user_id", str(user_id)).maybe_single().execute())

        if not current_response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        current_prompt = current_response.data

        
        data = {
        key: value
        for key, value in data.items()
        if value is not None
        }

        if not data:
            raise HTTPException(
                status_code=400,
                detail="No field to update"
            )

    
        PromptService.create_prompt_version(user_id,current_prompt)

        for key, value in data.items():
            if isinstance(value, UUID):
                data[key] = str(value)


        current_version = current_prompt.get("version", 1)

        data["version"] = current_version + 1


        response = (supabase.table("prompts")
        .update(data).eq("id", str(prompt_id))
        .eq("user_id", str(user_id)).execute())

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        return response.data[0]    



    @staticmethod
    def delete_prompt(user_id:str, prompt_id:UUID):
        response = (supabase.table("prompts").delete().eq("id", str(prompt_id)).eq("user_id", str(user_id)).execute())
        
        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            ) 

        return {
            "message" : "Prompt deleted successfuly"
        }
        
    @staticmethod
    def toggle_favorite(user_id: str, prompt_id: str):

        prompt = PromptService.get_prompt(user_id, prompt_id)

        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        new_value = not prompt["favorite"]    

        response = (supabase.table("prompts").update({"favorite": new_value}).eq("id", str(prompt_id)).eq("user_id", str(user_id)).execute())

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        return response.data[0]

     

    @staticmethod
    def get_favorite_prompts(user_id: str):

        response = (supabase.table("prompts").select("*").eq("user_id", str(user_id)).eq("favorite", True).execute())

        if not response.data:
            raise HTTPException (
                status_code=404,
                detail="prompt not found"
            )

        return response.data    


    @staticmethod
    def share_prompt(user_id: str, prompt_id: str):

        response = (
            supabase.table("prompts").select("id, visibility, share_slug")
            .eq("id", str(prompt_id)).eq("user_id", str(user_id))
            .single().execute())

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        slug = secrets.token_urlsafe(8)

        response = (supabase.table("prompts")
            .update({
                "visibility": "public",
                "share_slug": slug
            }).eq("id", str(prompt_id))
            .eq("user_id", str(user_id)).execute())

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create share link"
            )

        return {
            "prompt_id": str(prompt_id),
            "visibility": "public",
            "share_slug": slug,
            "share_url": f"/share/{slug}"
        } 

    @staticmethod
    def get_shared_prompt(share_slug: str):

        response = (supabase.table("prompts").select(
            "id,title,original_prompt,optimized_prompt,score,"
            "ai_model,prompt_type,visibility,share_slug,created_at"
        ).eq("share_slug", share_slug).eq("visibility", "public").single().execute())

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Shared prompt not found"
            )

        return response.data      

    @staticmethod
    def revoke_share(user_id: str, prompt_id: str):

        prompt = PromptService.get_prompt(user_id, prompt_id)

        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        response = supabase.table("prompts").update({"share_slug": None, "visibility": "private"}).eq("id", str(prompt_id)).eq("user_id", str(user_id)).execute()       

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        return {
            "prompt_id": prompt_id,
            "share_slug": None,
            "visibility": "private"
        }    

    @staticmethod
    def search_prompts(user_id: str, query: str):

        response = (
            supabase.table("prompts").select("*")
            .eq("user_id", str(user_id))
            .or_(
              f"title.ilike.%{query}%,"
              f"original_prompt.ilike.%{query}%,"
              f"optimized_prompt.ilike.%{query}%"
            ).order("updated_at", desc=True).execute())

        return response.data    

    @staticmethod
    def get_prompts(
        user_id: str,
        page: int = 1,
        limit: int = 20,
        favorite: bool = None,
        prompt_type: str = None,
        visibility: str = None,
        ai_model: str = None,
        collection_id: UUID = None
    ):
        if page < 1:
            page = 1

        if limit < 1:
            limit = 20

        if limit > 100:
            limit = 100

        start = (page - 1) * limit
        end = start + limit - 1

        query = (
            supabase.table("prompts").select("*", count="exact").eq("user_id", str(user_id)))

        if favorite is not None:
            query = query.eq("favorite", favorite)

        if prompt_type is not None:
            query = query.eq("prompt_type", prompt_type)

        if visibility is not None:
            query = query.eq("visibility", visibility)

        if ai_model is not None:
            query = query.eq("ai_model", ai_model)

        if collection_id is not None:
            query = query.eq("collection_id", str(collection_id))

        response = (query.order("updated_at", desc=True).range(start, end).execute())

        total = response.count or 0
        total_pages = (total + limit - 1) // limit

        return {
            "items": response.data,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }

    @staticmethod
    def save_current_version(user_id: str, prompt: dict):
        return PromptService.create_prompt_version(user_id=user_id, prompt=prompt)    

    @staticmethod
    def create_version(user_id: str, prompt_id: UUID):

        prompt = PromptService.get_prompt(user_id, prompt_id) 

        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )   

        existing = (supabase.table("prompt_versions").select("version_number")
                    .eq("prompt_id", str(prompt_id)).order("version_number", desc=True).limit(1).execute())


        if existing.data:
            next_version = existing.data[0]["version_number"]+1
        else:
            next_version = 1

        version_data = {
            "prompt_id": str(prompt_id),
            "user_id": str(user_id),
            "version_number": next_version,
            "original_prompt": prompt["original_prompt"],
            "optimized_prompt": prompt["optimized_prompt"],
            "score": prompt["score"],
        } 

        response = (supabase.table("prompt_versions").insert(version_data).execute())

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create prompt version"
            )                      

        return response.data[0]

    @staticmethod
    def get_prompt_versions(user_id: str, prompt_id: UUID):

        PromptService.get_prompt(user_id, prompt_id)

        response = (supabase.table("prompt_versions").select("*")
        .eq("prompt_id", str(prompt_id)).eq("user_id", str(user_id)).order("version_number", desc=True).execute())

        return response.data    

    @staticmethod
    def get_prompt_details(user_id: str, prompt_id: UUID):

    
        prompt_response = (supabase.table("prompts").select("*")
        .eq("id", str(prompt_id)).eq("user_id", str(user_id)).maybe_single().execute())

        if not prompt_response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

   
        versions_response = (supabase.table("prompt_versions").select("*")
        .eq("prompt_id", str(prompt_id)).eq("user_id", str(user_id))
        .order("version_number", desc=True).execute())

        return {
            "prompt": prompt_response.data,
            "versions": versions_response.data
        }    
    

    @staticmethod
    def update_prompt_with_version(user_id: str, prompt_id: UUID, update_data: dict):

        response = (supabase.table("prompts").select("*")
            .eq("id", str(prompt_id)).eq("user_id", str(user_id))
            .maybe_single().execute())

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        current_prompt = response.data

        PromptService.save_current_version(user_id, current_prompt)

        update_data = make_json_serializable(update_data)

        response = (supabase.table("prompts").update(update_data)
            .eq("id", str(prompt_id)).eq("user_id", str(user_id)).execute())


        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to update prompt"
            )

        return response.data[0]      

    @staticmethod
    def optimize_prompt(user_id: str, prompt_id: UUID):

    
        response = (supabase.table("prompts").select("*").eq("id", str(prompt_id)).eq("user_id", str(user_id))
        .maybe_single().execute())

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        prompt = response.data

    
        from app.services.optimizer_service import OptimizerService

        result = OptimizerService.optimize(prompt["original_prompt"])

        update_prompt = PromptService.update_prompt_with_version(user_id, prompt_id, {
            "optimized_prompt": result["optimized_prompt"],
            "score": result["score"]
        })
    

        return {
            "prompt": update_prompt,
            "improvements": result.get("improvements", [])
        }

    @staticmethod
    def score_prompt(user_id: str, prompt_id: UUID):

        response = (supabase.table("prompts").select("*").eq("id", str(prompt_id))
        .eq("user_id", str(user_id)).maybe_single().execute())

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        prompt = response.data

        from app.services.scorer_service import ScorerService

        result = ScorerService.score(prompt["original_prompt"])

        response = PromptService.update_prompt_with_version(user_id, prompt_id,
        {"score": result["score"]})


        return {
            "prompt": response,
            "feedback": result.get("feedback", []),
            "score": result["score"]
        }    


       

          