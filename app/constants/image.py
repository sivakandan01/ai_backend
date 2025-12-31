# Image Size Presets (width x height)
IMAGE_SIZE_SMALL = {"width": 360, "height": 360}
IMAGE_SIZE_MEDIUM = {"width": 480, "height": 480}
IMAGE_SIZE_LARGE = {"width": 720, "height": 720}
IMAGE_SIZE_XL = {"width": 1024, "height": 1024}

DEFAULT_IMAGE_SIZE = IMAGE_SIZE_SMALL

# Pollinations AI Models
POLLINATIONS_MODELS = {
    "flux": "flux",
    "flux-realism": "flux-realism",
    "flux-anime": "flux-anime",
    "flux-3d": "flux-3d",
    "turbo": "turbo"
}
DEFAULT_POLLINATIONS_MODEL = "flux"

# HuggingFace Image Models
HUGGINGFACE_IMAGE_MODELS = {
    "sd-2.1": "stabilityai/stable-diffusion-2-1",
    "sd-xl": "stabilityai/stable-diffusion-xl-base-1.0",
    "sd-1.5": "runwayml/stable-diffusion-v1-5"
}
DEFAULT_HUGGINGFACE_IMAGE_MODEL = "stabilityai/stable-diffusion-2-1"

# Valid image extensions for output validation
VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')

# Minimum lengths for output validation
MIN_IMAGE_OUTPUT_LENGTH = 10

# Fallback providers (if primary fails validation)
IMAGE_FALLBACK_PROVIDERS = ["pollinations", "huggingface"]