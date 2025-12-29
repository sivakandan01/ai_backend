def get_prompt(message):
    return f"This is an users message. You have to give an answer related to that okay. User Message: {message}"

def get_quick_name(message: str) -> str | None:
    """
    Fast pattern matching for common message types.
    Returns a 3-word-or-less name, or None if no match.
    """
    message_lower = message.lower().strip()

    # Simple greetings
    greetings = ["hi", "hello", "hey", "hola", "greetings", "good morning", "good afternoon", "good evening"]
    if message_lower in greetings or len(message_lower.split()) <= 2:
        if any(word in message_lower for word in ["hi", "hello", "hey", "hola"]):
            return "Greeting"

    # Programming languages & frameworks
    programming = {
        "python": "Python Help",
        "javascript": "JavaScript Help",
        "typescript": "TypeScript Help",
        "java": "Java Help",
        "c++": "C++ Help",
        "c#": "C# Help",
        "react": "React Help",
        "vue": "Vue Help",
        "angular": "Angular Help",
        "node": "Node.js Help",
        "django": "Django Help",
        "flask": "Flask Help",
        "sql": "SQL Help",
        "mongodb": "MongoDB Help",
        "html": "HTML Help",
        "css": "CSS Help",
        "docker": "Docker Help",
        "kubernetes": "K8s Help",
        "git": "Git Help"
    }

    for tech, name in programming.items():
        if tech in message_lower:
            return name

    # Cities & locations (major cities worldwide)
    cities = {
        "new york": "New York",
        "london": "London",
        "paris": "Paris",
        "tokyo": "Tokyo",
        "beijing": "Beijing",
        "dubai": "Dubai",
        "singapore": "Singapore",
        "mumbai": "Mumbai",
        "delhi": "Delhi",
        "bangalore": "Bangalore",
        "chennai": "Chennai",
        "kolkata": "Kolkata",
        "hyderabad": "Hyderabad",
        "los angeles": "Los Angeles",
        "chicago": "Chicago",
        "san francisco": "San Francisco",
        "seattle": "Seattle",
        "sydney": "Sydney",
        "melbourne": "Melbourne",
        "toronto": "Toronto",
        "vancouver": "Vancouver"
    }

    for city, name in cities.items():
        if city in message_lower:
            return name

    # Weather related
    if any(word in message_lower for word in ["weather", "temperature", "forecast", "rain", "snow", "sunny", "cloudy"]):
        return "Weather"

    # Food & cooking
    if any(word in message_lower for word in ["recipe", "cook", "food", "meal", "dish", "restaurant", "cuisine"]):
        return "Food & Cooking"

    # Entertainment
    if any(word in message_lower for word in ["joke", "funny", "laugh", "story", "game", "play"]):
        return "Entertainment"

    # Math & calculations
    if any(word in message_lower for word in ["calculate", "math", "equation", "solve", "algebra", "geometry"]):
        return "Math Help"

    # Health & fitness
    if any(word in message_lower for word in ["health", "fitness", "exercise", "workout", "diet", "nutrition"]):
        return "Health & Fitness"

    # Travel
    if any(word in message_lower for word in ["travel", "trip", "vacation", "flight", "hotel", "tourist"]):
        return "Travel"

    # Shopping
    if any(word in message_lower for word in ["buy", "purchase", "shop", "product", "price", "discount"]):
        return "Shopping"

    # News & current events
    if any(word in message_lower for word in ["news", "current", "event", "happening", "today"]):
        return "News"

    # Technology general
    if any(word in message_lower for word in ["computer", "laptop", "phone", "device", "tech", "software"]):
        return "Technology"

    # Science topics
    science_topics = {
        "physics": "Physics",
        "chemistry": "Chemistry",
        "biology": "Biology",
        "astronomy": "Astronomy",
        "space": "Space",
        "quantum": "Quantum Physics",
        "genetics": "Genetics"
    }

    for topic, name in science_topics.items():
        if topic in message_lower:
            return name

    # AI & Machine Learning
    if any(word in message_lower for word in ["ai", "artificial intelligence", "machine learning", "ml", "deep learning", "neural network"]):
        return "AI & ML"

    # Business & finance
    if any(word in message_lower for word in ["business", "finance", "money", "investment", "stock", "market"]):
        return "Business & Finance"

    # Education
    if any(word in message_lower for word in ["learn", "study", "education", "course", "teach", "tutorial"]):
        return "Learning"

    # Books & reading
    if any(word in message_lower for word in ["book", "read", "novel", "author", "literature"]):
        return "Books"

    # Movies & TV
    if any(word in message_lower for word in ["movie", "film", "tv", "show", "series", "watch"]):
        return "Movies & TV"

    # Music
    if any(word in message_lower for word in ["music", "song", "album", "artist", "band", "listen"]):
        return "Music"

    # Sports
    if any(word in message_lower for word in ["sport", "football", "soccer", "basketball", "cricket", "tennis"]):
        return "Sports"

    return None  # No match found, use LLM 

def get_name(message):
    """
    Generate a smart, concise session name based on the message content.
    Uses few-shot learning with examples to guide the LLM.
    """
    return f"""You are a session naming expert. Create a SHORT, descriptive name for this conversation.

RULES:
- Maximum 3 words
- Be specific and meaningful
- Categorize the topic clearly
- Use title case

EXAMPLES:
User: "Hi" or "Hello" → "Greeting"
User: "How are you?" → "Casual Chat"
User: "What is Python?" → "Python Basics"
User: "How to use loops in Python?" → "Python Loops"
User: "Explain machine learning" → "Machine Learning"
User: "Debug my React code" → "React Debugging"
User: "Best practices for API design" → "API Design"
User: "Help me with SQL queries" → "SQL Help"
User: "What's the weather?" → "Weather Query"
User: "Tell me a joke" → "Entertainment"

Now generate a name for this message:
"{message}"

RESPOND WITH ONLY THE NAME (3 words max, no explanation):"""

def get_rag_prompt(query: str, context: str) -> str:
    """
    Generate a prompt for RAG with retrieved context

    Args:
        query: User's question
        context: Retrieved relevant chunks from documents

    Returns:
        Formatted prompt for LLM
    """
    return f"""You are a helpful assistant. Use the following context from documents to answer the user's question.

If the answer can be found in the context, provide a detailed and accurate response.
If the answer is not in the context, clearly state that you don't have that information in the provided documents.
Always be honest about the limitations of your knowledge.

Context from documents:
{context}

User's Question: {query}

Answer:"""

def get_mermaid_prompt(description: str) -> str:
    """
    Generate a prompt for Mermaid diagram generation

    Args:
        description: User's description of what diagram they want

    Returns:
        Formatted prompt for LLM to generate Mermaid code
    """
    return f"""Generate a Mermaid diagram for: {description}

IMPORTANT RULES:
- Return ONLY valid Mermaid code
- NO markdown code blocks (no ```)
- NO explanations or additional text
- Use clear, descriptive labels
- Make it professional and well-structured

EXAMPLE FORMATS:

Flowchart:
graph TD
    A[Start] --> B[Process Step]
    B --> C{{Decision?}}
    C -->|Yes| D[Action 1]
    C -->|No| E[Action 2]
    D --> F[End]
    E --> F

Sequence Diagram:
sequenceDiagram
    User->>Server: Request
    Server->>Database: Query
    Database-->>Server: Result
    Server-->>User: Response

Class Diagram:
classDiagram
    class User {{
        +string name
        +string email
        +login()
    }}
    User --> Order

Entity Relationship:
erDiagram
    CUSTOMER ||--o{{ ORDER : places
    ORDER ||--|{{ PRODUCT : contains

Now generate the appropriate Mermaid diagram for: {description}"""