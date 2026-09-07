import json

from fastapi import HTTPException
from app.services.ai.gemini import generate_text, is_quota_error
from app.database.client import supabase
from app.services.prompt_service import PromptService
from app.services.scorer_service import ScorerService

class OptimizerService:
    @staticmethod
    def optimize(prompt: str):
        allowed_models = {"chatgpt", "gemini", "claude", "grok", "deepseek", "midjourney", "flux", "runway", "veo", "imagen", "other"}
        allowed_prompt_types = {"text", "image", "video", "code", "marketing", "social", "design", "other"}
        system_prompt = f""" 
        You are PromptStudio's expert prompt optimizer.

        Your job is to analyze the user's prompt and improve it
        for better results from generative AI systems.

        Use this framework:

        1. Goal
        2. Context
        3. Subject
        4. Specific details
        5. Style
        6. Constraints
        7. Output format
        8. Quality requirements

        Do NOT unnecessarily make a simple prompt extremely long.

        Preserve the user's original intent.

        Analyze the prompt and return ONLY valid JSON.

        Required JSON structure:

        {{
            "title": "A concise, useful title for this prompt",
            "ai_model": "chatgpt",
            "prompt_type": "text",
            "score": 0,
            "optimized_prompt": "...",
            "improvements": [
                "...",
                "...",
                "..."
            ]
        }}

        Rules:

        - score must be an integer from 0 to 100
        - title must be 3 to 8 words and describe the prompt's actual goal
        - ai_model must be one of: chatgpt, gemini, claude, grok, deepseek, midjourney, flux, runway, veo, imagen, other
        - prompt_type must be one of: text, image, video, code, marketing, social, design, other
        - optimized_prompt must preserve the original intent
        - improvements should explain what was missing or improved
        - do not include markdown
        - do not include ```json
        - return valid JSON only

        User prompt:

        {prompt}
        """
        
        
        try:

            result = generate_text(system_prompt)
            result = result.strip()

            if result.startswith("```json"):
                result = result[7:]

            if result.startswith("```"):
                result = result[3:]

            if result.endswith("```"):
                result = result[:-3]    

            result = result.strip()

            data = json.loads(result)

            ai_model = str(data["ai_model"]).strip().lower()
            prompt_type = str(data["prompt_type"]).strip().lower()

            return {
                "title": data["title"],
                "ai_model": ai_model if ai_model in allowed_models else "other",
                "prompt_type": prompt_type if prompt_type in allowed_prompt_types else "other",
                "original_prompt": prompt,
                "optimized_prompt": data["optimized_prompt"],
                "score": int(data["score"]),
                "improvements": data["improvements"]
            }    

        except json.JSONDecodeError:
            raise HTTPException(
                status_code=502,
                detail="AI returned invalid JSON"
                )

        except KeyError as e:
            raise HTTPException(
                status_code=502,
                detail=f"AI response missing required field: {e}"
                )    

        except Exception as e:
            if is_quota_error(e):
                raise HTTPException(
                    status_code=429,
                    detail="AI quota exceeded. Please try again later or check your Groq API plan."
                )

            raise HTTPException(
                status_code=502,
                detail="Prompt optimization service failed. Please try again later."
            )

    @staticmethod
    def optimized_prompt(user_id: str, prompt_id: str):

        prompt = PromptService.get_prompt(user_id, prompt_id)

        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )

        original_prompt = prompt["original_prompt"]

        result = OptimizerService.optimize(original_prompt)

        update_data = {
            "optimized_prompt": result["optimized_prompt"],
            "score": result["score"],
        }

        PromptService.update_prompt(user_id, prompt_id, update_data)

        return {
            "prompt_id": prompt_id,
            "original_prompt": original_prompt,
            "optimized_prompt": result["optimized_prompt"],
            "score": result["score"],
            "improvements": result["improvements"]
        }
    
    @staticmethod
    def analyze(prompt: str):

        original_result = ScorerService.score(prompt)

        optimized_result = OptimizerService.optimize(prompt)

        optimized_score_result = ScorerService.score(
            optimized_result["optimized_prompt"]
        )

        original_score = original_result["score"]
        optimized_score = optimized_score_result["score"]

        improvement = optimized_score - original_score

        return {

            "title": optimized_result["title"],

            "ai_model": optimized_result["ai_model"],

            "prompt_type": optimized_result["prompt_type"],

            "original_prompt": prompt,

            "original_score": original_score,

            "optimized_prompt": optimized_result["optimized_prompt"],

            "optimized_score": optimized_score,

            "improvement": improvement,

            "improvements": optimized_result["improvements"],

            "original_analysis": original_result["analysis"],

            "optimized_analysis": optimized_score_result["analysis"],

            "strengths": original_result["strengths"],

            "weaknesses": original_result["weaknesses"],

            "suggestions": original_result["suggestions"]
    }
              