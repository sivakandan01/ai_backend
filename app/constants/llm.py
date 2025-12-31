# LLM Providers
PROVIDER_GROQ = "groq"
PROVIDER_GEMINI = "gemini"
PROVIDER_HUGGINGFACE = "huggingface"
PROVIDER_OLLAMA = "ollama"
PROVIDER_POLLINATIONS = "pollinations"

# Default LLM Settings
DEFAULT_PROVIDER = PROVIDER_OLLAMA
DEFAULT_MODEL = "llama3.2"

MERMAID_FALLBACK_CONFIGS = [
    {"provider": PROVIDER_OLLAMA, "model": "llama3.2"},
    {"provider": PROVIDER_GROQ, "model": "llama-3.1-70b-versatile"},
    {"provider": PROVIDER_GEMINI, "model": "gemini-1.5-flash"},
]