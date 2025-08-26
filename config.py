# Configuration file for AI Research Buddy

# Rate Limiting Settings
RATE_LIMIT_CONFIG = {
    "MAX_REQUESTS_PER_SESSION": 4,  # Maximum requests per session
    "COOLDOWN_MINUTES": 10,  # Cooldown period between requests
    "ENABLE_RATE_LIMITING": True,  # Toggle rate limiting on/off
}

# API Configuration
API_CONFIG = {
    "OPENAI_MODEL": "gpt-4o-mini",  # Default OpenAI model
    "GOOGLE_MODEL": "gemini-1.5-flash",  # Default Google model
    "MAX_TOKENS": 10000,  # Maximum tokens per request
    "TEMPERATURE": 0.0,  # Creativity level (0.0 to 1.0)
}

# UI Configuration
UI_CONFIG = {
    "PAGE_TITLE": "AI Research Buddy",
    "PAGE_ICON": "🤖",
    "LAYOUT": "wide",
    "SIDEBAR_STATE": "expanded",
    "COLUMN_LAYOUT": [1, 2, 1],  # Layout ratios for main content
    "TEXT_AREA_HEIGHT": 400,  # Height for text area in pixels
    "PROGRESS_STEPS": [0, 50, 100],  # Progress bar steps
    "SHOW_DEBUG": False,  # Toggle developer diagnostics in UI
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