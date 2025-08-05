# Configuration file for AI Research Buddy

# Rate Limiting Settings
RATE_LIMIT_CONFIG = {
    "MAX_REQUESTS_PER_SESSION": 2,  # Maximum requests per session
    "COOLDOWN_MINUTES": 10,  # Cooldown period between requests
    "ENABLE_RATE_LIMITING": True,  # Toggle rate limiting on/off
}

# API Configuration
API_CONFIG = {
    "OPENAI_MODEL": "gpt-4o-mini",  # Default OpenAI model
    "GOOGLE_MODEL": "gemini-2.0-flash-exp",  # Default Google model
    "MAX_TOKENS": 4000,  # Maximum tokens per request
    "TEMPERATURE": 0.7,  # Creativity level (0.0 to 1.0)
}

# UI Configuration
UI_CONFIG = {
    "PAGE_TITLE": "AI Research Buddy",
    "PAGE_ICON": "🤖",
    "LAYOUT": "wide",
    "SIDEBAR_STATE": "expanded",
}

# Example Topics
EXAMPLE_TOPICS = [
    "Machine Learning in Healthcare",
    "Blockchain Technology Applications", 
    "Quantum Computing Developments",
    "Sustainable Energy Solutions",
    "Space Exploration Technologies",
    "Climate Change Impact"
]

# Research Configuration
RESEARCH_CONFIG = {
    "MAX_WORDS": 1500,  # Maximum words in detailed research section
    "MIN_CITATIONS": 3,  # Minimum number of citations
    "SEARCH_DEPTH": 10,  # Number of search results to analyze
} 