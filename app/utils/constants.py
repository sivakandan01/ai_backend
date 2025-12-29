# Image Generation Constants

# Image Size Presets (width x height)
IMAGE_SIZE_SMALL = {"width": 360, "height": 360}
IMAGE_SIZE_MEDIUM = {"width": 480, "height": 480}
IMAGE_SIZE_LARGE = {"width": 720, "height": 720}
IMAGE_SIZE_XL = {"width": 1024, "height": 1024}

DEFAULT_IMAGE_SIZE = IMAGE_SIZE_SMALL

POLLINATIONS_MODELS = {
    "flux": "flux",
    "flux-realism": "flux-realism",
    "flux-anime": "flux-anime",
    "flux-3d": "flux-3d",
    "turbo": "turbo"
}
DEFAULT_POLLINATIONS_MODEL = "flux"

# HuggingFace Models
HUGGINGFACE_IMAGE_MODELS = {
    "sd-2.1": "stabilityai/stable-diffusion-2-1",
    "sd-xl": "stabilityai/stable-diffusion-xl-base-1.0",
    "sd-1.5": "runwayml/stable-diffusion-v1-5"
}
DEFAULT_HUGGINGFACE_IMAGE_MODEL = "stabilityai/stable-diffusion-2-1"

# Session Types
SESSION_TYPE_MESSAGE = "message"
SESSION_TYPE_IMAGE = "image"
SESSION_TYPE_MERMAID = "mermaid"
SESSION_TYPE_RAG = "rag"

# RAG Constants
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5
EMBEDDING_MODEL = "nomic-embed-text"

# LLM Providers
PROVIDER_GROQ = "groq"
PROVIDER_GEMINI = "gemini"
PROVIDER_HUGGINGFACE = "huggingface"
PROVIDER_OLLAMA = "ollama"
PROVIDER_POLLINATIONS = "pollinations"

# Default LLM Settings
DEFAULT_PROVIDER = PROVIDER_OLLAMA
DEFAULT_MODEL = "llama3.2"

# File Upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_EXTENSIONS = [".pdf"]

# JWT Settings
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 1440  # 24 hours

# Database Collections
COLLECTION_USERS = "users"
COLLECTION_SESSIONS = "sessions"
COLLECTION_MESSAGES = "messages"
COLLECTION_IMAGES = "images"
COLLECTION_MERMAID = "mermaid_diagrams"
COLLECTION_DOCUMENTS = "documents"

# Response Status
STATUS_SUCCESS = "success"
STATUS_LOADING = "loading"
STATUS_ERROR = "error"
STATUS_PENDING = "pending"

# Directory Paths
IMAGES_DIR = "./images"
UPLOADS_DIR = "./uploads"
CHROMA_DIR = "./chroma_data"