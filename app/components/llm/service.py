import os
import httpx
import aiofiles
import logging
from dotenv import load_dotenv
from fastapi import HTTPException
from app.helpers.ai import get_model_and_url
from urllib.parse import quote
from app.utils.constants import (
    DEFAULT_IMAGE_SIZE,
    DEFAULT_POLLINATIONS_MODEL,
    DEFAULT_HUGGINGFACE_IMAGE_MODEL,
    IMAGES_DIR,
    STATUS_LOADING
)

load_dotenv()

logger = logging.getLogger(__name__)

class LlmService:

    def __init__(self, db):
        self.db = db
        self.http_client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        await self.http_client.aclose()

    async def generate_llm_text(self, messages: list, provider: str, model: str):
        try:
            model_details = get_model_and_url(provider, model)

            if not model_details or not model_details.get("endpoint"):
                logger.error(f"Invalid model or endpoint not configured for: {model}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid model or endpoint not configured for: {model}"
                )

            endpoint = model_details["endpoint"]
            if endpoint is None:
                logger.error(f"Endpoint is None for provider: {provider}, model: {model}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Endpoint is None for provider: {provider}, model: {model}"
                )

            headers = {}
            payload = {}

            if provider == "groq":
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    raise HTTPException(status_code=400, detail="GROQ_API_KEY not configured in environment")
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": model_details["model"],
                    "messages": messages,
                    "stream": False
                }

            elif provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise HTTPException(status_code=400, detail="GEMINI_API_KEY not configured in environment")
                endpoint = f"{endpoint}/models/{model_details['model']}:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                contents = []
                for msg in messages:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": msg["content"]}]})
                payload = {"contents": contents}

            elif provider == "huggingface":
                api_key = os.getenv("HUGGINGFACE_API_KEY")
                if not api_key:
                    raise HTTPException(status_code=400, detail="HUGGINGFACE_API_KEY not configured in environment")
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": model_details["model"],
                    "messages": messages,
                    "stream": False
                }

            elif provider == "ollama":
                endpoint = endpoint.replace("/api/generate", "/api/chat")
                payload = {
                    "model": model_details["model"],
                    "messages": messages,
                    "stream": False
                }

            response = await self.http_client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()

            if provider == "groq":
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            elif provider == "gemini":
                return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            elif provider == "huggingface":
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            elif provider == "ollama":
                return result.get("message", {}).get("content", "")

            return ""

        except httpx.ConnectError as e:
            logger.error(f"Connection error for {provider}: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to {provider}. Make sure {provider} is running and accessible."
            )
        except httpx.TimeoutException as e:
            logger.error(f"Timeout error for {provider}: {str(e)}")
            raise HTTPException(
                status_code=504,
                detail=f"{provider} took too long to respond. Try a simpler question."
            )
        except httpx.HTTPStatusError as e:
            error_detail = str(e)
            if e.response is not None:
                try:
                    error_json = e.response.json()
                    if "error" in error_json:
                        error_info = error_json["error"]
                        if error_info.get("code") == "invalid_api_key":
                            error_detail = f"Invalid API Key for {provider}. Please check your API key configuration."
                        else:
                            error_detail = error_info.get("message", str(e))
                except:
                    error_detail = e.response.text or str(e)

            logger.error(f"{provider} API error: {error_detail}")
            raise HTTPException(
                status_code=e.response.status_code if e.response else 500,
                detail=f"{provider} API error: {error_detail}"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating answer with {provider}/{model}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error generating answer: {str(e)}"
            )
        
    async def generate_llm_image(self, prompt: str, provider: str):
        try:
            image = ""
            if provider == "pollinations":
                image = await self.pollination(prompt)
            else:
                image = await self.hugging_face(prompt)
            return image
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating image with {provider}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")

    async def hugging_face(self, prompt: str):
        try:
            url = f"https://api-inference.huggingface.co/models/{DEFAULT_HUGGINGFACE_IMAGE_MODEL}"

            headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
            payload = {"inputs": prompt}

            response = await self.http_client.post(url, headers=headers, json=payload)

            if response.status_code == 503:
                return {"status": STATUS_LOADING, "message": "Model is loading, try again in 20 seconds"}

            filename = f"generated_{hash(prompt)}.png"
            filepath = f"{IMAGES_DIR}/{filename}"

            os.makedirs(IMAGES_DIR, exist_ok=True)

            async with aiofiles.open(filepath, "wb") as f:
                await f.write(response.content)

            return {"image_url": f"/images/{filename}"}
        except httpx.TimeoutException as e:
            logger.error(f"Timeout generating HuggingFace image: {str(e)}")
            raise HTTPException(status_code=504, detail="Image generation timed out. Please try again with a simpler prompt.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating HuggingFace image: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating HuggingFace image: {str(e)}")

    async def pollination(self, prompt: str):
        try:
            url = f"https://image.pollinations.ai/prompt/{quote(prompt)}"
            params = {
                "width": DEFAULT_IMAGE_SIZE["width"],
                "height": DEFAULT_IMAGE_SIZE["height"],
                "model": DEFAULT_POLLINATIONS_MODEL
            }

            response = await self.http_client.get(url, params=params)

            filename = f"generated_{hash(prompt)}.png"
            filepath = f"{IMAGES_DIR}/{filename}"

            os.makedirs(IMAGES_DIR, exist_ok=True)

            async with aiofiles.open(filepath, "wb") as f:
                await f.write(response.content)

            return {"image_url": f"/images/{filename}"}
        except httpx.TimeoutException as e:
            logger.error(f"Timeout generating Pollinations image: {str(e)}")
            raise HTTPException(status_code=504, detail="Image generation timed out. Please try again with a simpler prompt.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating Pollinations image: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating Pollinations image: {str(e)}")

    async def generate_llm_flowchart(self, prompt: str, provider: str, model: str):
        try:
            from app.utils.prompt import get_mermaid_prompt

            system_prompt = get_mermaid_prompt(prompt)
            messages = [{"role": "user", "content": system_prompt}]

            mermaid_code = await self.generate_llm_text(messages, provider, model)

            mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()

            return {"mermaid_code": mermaid_code}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating flowchart: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating flowchart: {str(e)}")