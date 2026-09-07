import json
import time
from fastapi import HTTPException
from app.services.ai.gemini import generate_text, is_quota_error
from app.services.prompt_service import PromptService


class ScorerService:
    @staticmethod
    def score(prompt: str):
        max_retries = 3
        system_prompt = f"""
You are PromptStudio's expert AI prompt evaluator.

Analyze the user's prompt and give it a quality score.

Evaluate these areas:

1. Clarity
2. Specificity
3. Context
4. Structure
5. Constraints
6. Output format
7. Quality requirements

Return ONLY valid JSON.

Required JSON structure:

{{
    "score": 0,
    "analysis": {{
        "clarity": 0,
        "specificity": 0,
        "context": 0,
        "structure": 0,
        "constraints": 0,
        "output_format": 0,
        "quality_requirements": 0
    }},
    "strengths": [
        "..."
    ],
    "weaknesses": [
        "..."
    ],
    "suggestions": [
        "..."
    ],
    "suggested_model": "chatgpt"
}}

Rules:

- score must be an integer from 0 to 100
- every analysis value must be an integer from 0 to 100
- strengths should identify what the prompt does well
- weaknesses should identify missing or weak areas
- suggestions should explain how to improve the prompt
- suggested_model must be one of: chatgpt, gemini, claude, grok, deepseek, midjourney, flux, runway, veo, imagen, or other
- choose the suggested_model based on the prompt's task and output type
- do not rewrite the prompt
- do not include markdown
- do not include ```json
- return valid JSON only

User prompt:

{prompt}
"""

        for attempt in range(max_retries):
            try:
                result = generate_text(system_prompt)
                break
            except Exception as e:
                error_message = str(e)

                if (
                    "503" in error_message
                    or "SERVICE_UNAVAILABLE" in error_message
                ) and attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue

                if (
                    "503" in error_message
                    or "SERVICE_UNAVAILABLE" in error_message
                ):
                    raise HTTPException(
                        status_code=503,
                        detail="AI scoring service is temporarily unavailable. Please try again later."
                    )

                if is_quota_error(e):
                    raise HTTPException(
                        status_code=429,
                        detail="AI quota exceeded. Please try again later or check your Groq API plan."
                    )

                raise HTTPException(
                    status_code=502,
                    detail="Prompt scoring service failed. Please try again later."
                )

        try:
            result = result.strip()

            if result.startswith("```json"):
                result = result[7:]

            if result.startswith("```"):
                result = result[3:]

            if result.endswith("```"):
                result = result[:-3]

            result = result.strip()

            data = json.loads(result)

            return {
                
                "score": int(data["score"]),
                "analysis": data["analysis"],
                "strengths": data["strengths"],
                "weaknesses": data["weaknesses"],
                "suggestions": data["suggestions"],
                "suggested_model": data.get("suggested_model", "chatgpt")
            }

        except Exception as e:
            error_message = str(e)
            raise HTTPException(
                status_code=500,
                detail=f"Prompt scoring failed: {error_message}"
            )


    @staticmethod
    def score_prompt(user_id: str, prompt_id: str):

        prompt = PromptService.get_prompt(user_id, prompt_id)

        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )        

        original_prompt = prompt["original_prompt"]

        result = ScorerService.score(original_prompt)

          

        return {
            "prompt_id": prompt_id,
            "original_prompt": original_prompt,
            "score": result["score"],
            "analysis": result["analysis"],
            "strengths": result["strengths"],
            "improvements": result["improvements"]
        }      



 