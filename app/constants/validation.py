# Prompt length limits
PROMPT_MAX_LENGTH = 500
MIN_CHAT_PROMPT_LENGTH = 1
MIN_IMAGE_PROMPT_LENGTH = 3
MIN_MERMAID_PROMPT_LENGTH = 5

# Harmful content keywords - Violence and weapons
VIOLENCE_KEYWORDS = [
    "bomb", "explosive", "weapon", "grenade", "missile",
    "how to kill", "murder", "assassinate", "poison someone",
    "build a gun", "make a weapon", "terrorist", "attack plan",
    "mass shooting", "suicide method", "self harm", "hurt myself"
]

# Harmful content keywords - Adult content
ADULT_KEYWORDS = [
    "porn", "pornography", "xxx", "nsfw", "nude", "naked",
    "sex scene", "explicit content", "adult content", "erotic"
]

# Harmful content keywords - Illegal activities
ILLEGAL_KEYWORDS = [
    "hack into", "steal credit card", "phishing", "scam people",
    "fake id", "counterfeit", "money laundering", "drug dealer",
    "how to rob", "break into", "bypass security", "crack password"
]

# Harmful content keywords - Hate speech
HATE_KEYWORDS = [
    "hate speech", "racial slur", "discriminate against"
]

# Malicious input - Invisible Unicode characters
INVISIBLE_CHARS = [
    '\u200B',  # Zero Width Space
    '\u200C',  # Zero Width Non-Joiner
    '\u200D',  # Zero Width Joiner
    '\u2060',  # Word Joiner
    '\uFEFF',  # Zero Width No-Break Space
    '\u180E',  # Mongolian Vowel Separator
    '\u034F',  # Combining Grapheme Joiner
]

# Malicious input - Directional override characters
DIRECTIONAL_OVERRIDES = [
    '\u202A',  # Left-to-Right Embedding
    '\u202B',  # Right-to-Left Embedding
    '\u202C',  # Pop Directional Formatting
    '\u202D',  # Left-to-Right Override
    '\u202E',  # Right-to-Left Override
    '\u2066',  # Left-to-Right Isolate
    '\u2067',  # Right-to-Left Isolate
    '\u2068',  # First Strong Isolate
    '\u2069',  # Pop Directional Isolate
]

# Malicious input detection limits
MAX_INVISIBLE_CHARS = 3
MAX_CONTROL_CHARS = 2
MAX_NEWLINES = 50
MAX_WORD_REPETITION = 10
MAX_COMBINING_CHAR_RATIO = 0.3  # 30% of total characters

# Question starters (for detecting questions in image prompts)
QUESTION_STARTERS = ["what", "how", "why", "when", "where", "who", "explain", "tell me"]

# Output validation retry settings
MAX_RETRY_ATTEMPTS = 2  # How many times to retry if output validation fails