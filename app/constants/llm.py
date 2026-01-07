# LLM Providers
PROVIDER_GROQ = "groq"
PROVIDER_GEMINI = "gemini"
PROVIDER_HUGGINGFACE = "huggingface"
PROVIDER_POLLINATIONS = "pollinations"

# Default LLM Settings
DEFAULT_PROVIDER = PROVIDER_GROQ
DEFAULT_MODEL = "llama-3.3-70b-versatile"

MERMAID_FALLBACK_CONFIGS = [
    {"provider": PROVIDER_GROQ, "model": "llama-3.3-70b-versatile"},
    {"provider": PROVIDER_GEMINI, "model": "gemini-2.5-flash"},
]