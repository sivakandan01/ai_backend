from fastapi import HTTPException
from passlib.context import CryptContext
import re
import unicodedata

from app.constants.validation import (
    PROMPT_MAX_LENGTH,
    VIOLENCE_KEYWORDS,
    ADULT_KEYWORDS,
    ILLEGAL_KEYWORDS,
    HATE_KEYWORDS,
    INVISIBLE_CHARS,
    DIRECTIONAL_OVERRIDES,
    MAX_INVISIBLE_CHARS,
    MAX_CONTROL_CHARS,
    MAX_NEWLINES,
    MAX_WORD_REPETITION,
    MAX_COMBINING_CHAR_RATIO,
    QUESTION_STARTERS,
)
from app.constants.mermaid import MERMAID_KEYWORDS, VALID_MERMAID_STARTS, MIN_MERMAID_OUTPUT_LENGTH
from app.constants.image import VALID_IMAGE_EXTENSIONS, MIN_IMAGE_OUTPUT_LENGTH

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def validate_prompt(prompt: str, intent: str):
    try:
        if not prompt or len(prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
        
        if len(prompt) > PROMPT_MAX_LENGTH:
            raise HTTPException(status_code=400, detail="Prompt is too long.")

        is_malicious, reason = detect_malicious_input(prompt)
        if is_malicious:
            raise HTTPException(status_code=400, detail=reason)

        if intent == "chat":
            validate_chat_prompt(prompt)
        elif intent == "image":
            validate_image_prompt(prompt)
        elif intent == "mermaid":
            validate_mermaid_prompt(prompt)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid intent '{intent}'. Must be one of: chat, image, mermaid"
            )
    except HTTPException:
        raise


def contains_harmful_content(prompt: str) -> tuple[bool, str]:
    prompt_lower = prompt.lower()

    for keyword in VIOLENCE_KEYWORDS:
        if keyword in prompt_lower:
            return True, "Content related to violence, weapons, or self-harm is not allowed."

    for keyword in ADULT_KEYWORDS:
        if keyword in prompt_lower:
            return True, "Adult or explicit content is not allowed."

    for keyword in ILLEGAL_KEYWORDS:
        if keyword in prompt_lower:
            return True, "Content promoting illegal activities is not allowed."

    for keyword in HATE_KEYWORDS:
        if keyword in prompt_lower:
            return True, "Hate speech or discriminatory content is not allowed."

    return False, ""


def detect_malicious_input(prompt: str) -> tuple[bool, str]:

    invisible_count = sum(prompt.count(char) for char in INVISIBLE_CHARS)
    if invisible_count > MAX_INVISIBLE_CHARS:
        return True, "Suspicious invisible characters detected in prompt."

    if any(char in prompt for char in DIRECTIONAL_OVERRIDES):
        return True, "Directional override characters are not allowed."

    control_char_count = sum(1 for char in prompt if unicodedata.category(char) == 'Cc' and char not in ['\n', '\r', '\t'])
    if control_char_count > MAX_CONTROL_CHARS:
        return True, "Excessive control characters detected."

    base64_pattern = r'[A-Za-z0-9+/=]{100,}'
    if re.search(base64_pattern, prompt):
        return True, "Suspicious encoded content detected."

    hex_pattern = r'(?:0x)?[0-9a-fA-F]{100,}'
    if re.search(hex_pattern, prompt):
        return True, "Suspicious hex-encoded content detected."

    if re.search(r'(.)\1{20,}', prompt):
        return True, "Excessive character repetition detected."

    words = prompt.split()
    if len(words) > 10:
        word_counts = {}
        for word in words:
            word_lower = word.lower()
            word_counts[word_lower] = word_counts.get(word_lower, 0) + 1
            if word_counts[word_lower] > MAX_WORD_REPETITION:
                return True, "Excessive word repetition detected."

    if '\x00' in prompt:
        return True, "Null bytes are not allowed."

    if prompt.count('\n') > MAX_NEWLINES:
        return True, "Excessive line breaks detected."

    combining_count = sum(1 for char in prompt if unicodedata.category(char) in ['Mn', 'Mc', 'Me'])
    if combining_count > len(prompt) * MAX_COMBINING_CHAR_RATIO:
        return True, "Excessive combining characters detected."

    return False, ""


def validate_chat_prompt(prompt: str):
    if not prompt or len(prompt.strip()) == 0:
        raise HTTPException(status_code=400, detail="Chat prompt cannot be empty.")

    is_harmful, reason = contains_harmful_content(prompt)
    if is_harmful:
        raise HTTPException(status_code=403, detail=reason)

    return True


def validate_image_prompt(prompt: str):
    if len(prompt.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Image prompt is too short. Please provide more details."
        )

    is_harmful, reason = contains_harmful_content(prompt)
    if is_harmful:
        raise HTTPException(status_code=403, detail=reason)

    prompt_lower = prompt.lower().strip()

    if any(prompt_lower.startswith(q) for q in QUESTION_STARTERS) and prompt.strip().endswith("?"):
        raise HTTPException(
            status_code=400,
            detail="This looks like a question for chat. For images, provide a description like 'A sunset over mountains' or 'Cyberpunk city at night'."
        )

    return True


def validate_mermaid_prompt(prompt: str):
    if len(prompt.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="Diagram prompt is too short. Please provide more details about what you want to visualize."
        )

    is_harmful, reason = contains_harmful_content(prompt)
    if is_harmful:
        raise HTTPException(status_code=403, detail=reason)

    prompt_lower = prompt.lower()

    has_mermaid_keyword = any(keyword in prompt_lower for keyword in MERMAID_KEYWORDS)

    if not has_mermaid_keyword:
        raise HTTPException(
            status_code=400,
            detail="Prompt doesn't appear to be a diagram request. Try using phrases like 'create a flowchart...', 'draw a diagram...', or 'sequence diagram for...'"
        )

    return True


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def validate_output_mermaid(response: str) -> bool:
    if not response or len(response.strip()) < MIN_MERMAID_OUTPUT_LENGTH:
        return False

    # Remove markdown code blocks
    cleaned = response.strip().replace("```mermaid", "").replace("```", "").strip()

    # Check if starts with valid Mermaid diagram type
    return any(cleaned.startswith(start) for start in VALID_MERMAID_STARTS)


def validate_output_image(response: str) -> bool:
    if not response or len(response.strip()) < MIN_IMAGE_OUTPUT_LENGTH:
        return False

    cleaned = response.strip()

    # Check if it's a URL
    if cleaned.startswith(('http://', 'https://')):
        return True

    # Check if it has valid image extension
    return any(cleaned.lower().endswith(ext) for ext in VALID_IMAGE_EXTENSIONS)