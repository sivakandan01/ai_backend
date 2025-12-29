from app.utils.ai_providers import AI_PROVIDERS
from fastapi import HTTPException

def get_model_and_url(provider_name: str, model_name: str):
    if not provider_name:
        provider_name = "ollama"

    if not model_name:
        model_name = "llama3.2"

    if provider_name not in AI_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: {provider_name}. Available providers: {', '.join(AI_PROVIDERS.keys())}"
        )

    provider = AI_PROVIDERS[provider_name]

    return {
        "model": model_name,
        "endpoint": provider.get("endpoint")
    }